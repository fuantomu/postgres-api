from uuid import UUID
import psycopg
from src.database.helper.statement import generate_statement
from src.logger.log import get_logger


class Table:
    logger = get_logger("database")

    columns = {}
    functions = {}

    def __init__(self, connection: psycopg.Connection, name: str):
        self.connection = connection
        self.name = name.lower()
        self.schema = "public"
        self.functions["Post"] = self.add_or_update
        self.functions["Get"] = self.get
        self.functions["Delete"] = self.delete_entry

    def exists(self, table_name: str = None):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables 
                    WHERE table_schema = %s
                    AND table_name = %s
                );
                """,
                (self.schema, table_name or self.name),
            )
            return cursor.fetchone()[0]

    def create(self) -> None:
        if self.exists():
            self.logger.debug(f"Table '{self.name}' already exists. Skipping")
            return

        self.logger.debug(f"Trying to create table '{self.name}'")

        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
            CREATE TABLE IF NOT EXISTS {self.name} ({generate_statement(self.columns)});
            """
            )
            self.connection.commit()

    def insert(
        self, request: dict, table_name: str = None, return_key: str = "id"
    ) -> str:
        if not table_name:
            table_name = self.name

        if not self.exists(table_name=table_name):
            raise Exception(f"Table '{table_name}' does not exist")

        self.logger.debug(f"Trying to insert {request} into '{table_name}'")

        with self.connection.cursor() as cursor:
            try:
                query = psycopg.sql.SQL(
                    "INSERT INTO {table} ({rows}) VALUES ({fields}) RETURNING {return_key}"
                ).format(
                    fields=psycopg.sql.SQL(", ").join(
                        [psycopg.sql.Placeholder(entry) for entry in request.keys()]
                    ),
                    rows=psycopg.sql.SQL(",").join(
                        [psycopg.sql.Identifier(entry) for entry in request.keys()]
                    ),
                    table=psycopg.sql.Identifier(table_name),
                    return_key=psycopg.sql.Identifier(return_key),
                )
                cursor.execute(query, request)
                self.connection.commit()
                return cursor.fetchone()[0]
            except psycopg.errors.UniqueViolation as e:
                raise e

    def select(
        self,
        request: str | list[str],
        where: list[tuple] = None,
        table_name: str = None,
        inner_join: str = None,
    ) -> list[psycopg.rows.Row]:
        if not table_name:
            table_name = self.name

        if not self.exists(table_name=table_name):
            raise Exception(f"Table '{table_name}' does not exist")

        self.logger.debug(f"Trying to select {request} from '{table_name}'")

        with self.connection.cursor() as cursor:
            try:
                if isinstance(request, str):
                    if request == "ALL":
                        query = psycopg.sql.SQL("SELECT * FROM {table}").format(
                            table=psycopg.sql.Identifier(table_name)
                        )
                    elif request.startswith("MAX"):
                        query = psycopg.sql.SQL("SELECT {field} FROM {table}").format(
                            field=psycopg.sql.SQL(request),
                            table=psycopg.sql.Identifier(table_name),
                        )
                    else:
                        query = psycopg.sql.SQL("SELECT {field} FROM {table}").format(
                            field=psycopg.sql.Identifier(request),
                            table=psycopg.sql.Identifier(table_name),
                        )
                else:
                    query = psycopg.sql.SQL("SELECT {fields} FROM {table}").format(
                        fields=psycopg.sql.SQL(",").join(
                            [psycopg.sql.Identifier(entry) for entry in request]
                        ),
                        table=psycopg.sql.Identifier(table_name),
                    )

                if inner_join:
                    query += psycopg.sql.SQL(
                        " INNER JOIN {inner_join}".format(inner_join=inner_join)
                    )

                if where:
                    query, params = self.format_where(query, where, {})
                    cursor.execute(query, params)
                    return cursor.fetchall()
                else:
                    cursor.execute(query)
                    return cursor.fetchall()
            except Exception as e:
                raise e

    def delete(self, where: str | list[tuple], table_name: str = None):
        if not table_name:
            table_name = self.name

        if not self.exists(table_name=table_name):
            raise Exception(f"Table '{table_name}' does not exist")

        self.logger.debug(f"Trying to delete {where} from '{table_name}'")
        query = psycopg.sql.SQL("DELETE FROM {table}").format(
            table=psycopg.sql.Identifier(table_name)
        )
        with self.connection.cursor() as cursor:
            try:
                if not where == "ALL":
                    query, params = self.format_where(query, where, {})
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                cursor.connection.commit()
            except Exception as e:
                raise e

    def update(
        self,
        request: str | list[str],
        where: list[tuple] = None,
        table_name: str = None,
        return_key: str = "id",
    ) -> None:
        if not table_name:
            table_name = self.name

        if not self.exists(table_name=table_name):
            raise Exception(f"Table '{table_name}' does not exist")

        self.logger.debug(f"Trying to update {request} from '{table_name}'")

        with self.connection.cursor() as cursor:
            try:
                set_clause = psycopg.sql.SQL(", ").join(
                    [
                        psycopg.sql.SQL("{} = {}").format(
                            psycopg.sql.Identifier(k), psycopg.sql.Placeholder(k)
                        )
                        for k in request.keys()
                        if k != "id"
                    ]
                )

                query = psycopg.sql.SQL("UPDATE {table} SET {set_clause}").format(
                    table=psycopg.sql.Identifier(table_name), set_clause=set_clause
                )

                params = {}
                for k in request.keys():
                    if k == "id":
                        continue
                    params[k] = request[k]

                if where:
                    query, params = self.format_where(query, where, params)

                query += psycopg.sql.SQL(" RETURNING {return_key}").format(
                    return_key=psycopg.sql.Identifier(return_key)
                )
                cursor.execute(query, params)
                cursor.connection.commit()
                return str(cursor.fetchone()[0])
            except Exception as e:
                raise e

    def format_result(
        self, result: list[tuple], columns: list[str] = None
    ) -> list[dict]:
        output = []
        if not columns:
            columns = list(self.columns.keys())
            try:
                columns.remove("PRIMARY KEY")
            except Exception:
                pass
        for idx in range(len(result)):
            temp = {}
            for col in range(len(columns)):
                if isinstance(result[idx][col], UUID):
                    temp[columns[col]] = str(result[idx][col])
                else:
                    temp[columns[col]] = result[idx][col]
            output.append(temp)
        return output

    def get_functions(self) -> dict:
        return self.functions

    def set_function(self, name: str, function) -> None:
        self.functions[name] = function

    def get(self, request: str | dict):
        if not request["value"]:
            return self.format_result(self.select("ALL"))
        result = self.format_result(
            self.select("ALL", [(request["key"], "=", request["value"])])
        )

        return result

    def update_functions(self):
        pass

    def check_for_key(self, request: dict) -> str | None:
        if request.get("id"):
            try:
                UUID(request["id"])
                return "id"
            except Exception:
                pass
        if request.get("name"):
            return "name"
        return None

    def add_or_update(self, request: dict):
        key = self.check_for_key(request)
        if not key:
            raise Exception("No name found in request")

        existing_entry = self.select("ALL", [(key, "=", request[key])])
        if existing_entry:
            self.logger.info(f"Found existing entry {existing_entry}")

            if not request.get("id"):
                request["id"] = existing_entry[0][0]
            return f"Updated '{self.name}' with id '{self.update(request, [('id', '=', request['id'])])}'"
        else:
            if not request.get("name"):
                raise Exception("No name found in request")
            return f"Created '{self.name}' with id '{self.insert(request)}'"

    def format_where(self, query, where: list[tuple | str], params={}):
        query += psycopg.sql.SQL(" WHERE ")

        connector = "OR"
        if isinstance(where[-1], str):
            connector = where[-1]
            where = where[:-1]

        query += psycopg.sql.SQL(" {connector} ".format(connector=connector)).join(
            [
                psycopg.sql.SQL("{field} {equal} {value}").format(
                    field=psycopg.sql.Identifier(item[0]),
                    equal=psycopg.sql.SQL(item[1]),
                    value=psycopg.sql.Placeholder(f"{item[0]}_{idx}"),
                )
                for idx, item in enumerate(where)
            ]
        )
        for idx, item in enumerate(where):
            params[f"{item[0]}_{idx}"] = item[2]
        return query, params

    def delete_entry(self, request: dict):
        self.delete([(request["key"], "=", request["value"])])
        return f"Deleted {self.name} with {request['key']} '{request['value']}'"
