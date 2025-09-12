from uuid import UUID
import psycopg
from database.helper.statement import generate_statement
from logger.log import get_logger


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
                (self.schema, table_name or self.name)
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
    
    def insert(self, request: dict, table_name : str = None, return_key : str = "id") -> str:
        if not table_name:
            table_name = self.name

        if not self.exists(table_name=table_name):
            raise Exception(f"Table '{table_name}' does not exist")
        
        self.logger.debug(f"Trying to insert {request} into '{table_name}'")

        with self.connection.cursor() as cursor:
            try:
                query = psycopg.sql.SQL("INSERT INTO {table} ({rows}) VALUES ({fields}) RETURNING {return_key}").format(
                    fields=psycopg.sql.SQL(", ").join([psycopg.sql.Placeholder(entry) for entry in request.keys() if entry is not "id"]), 
                    rows=psycopg.sql.SQL(",").join([psycopg.sql.Identifier(entry) for entry in request.keys() if entry is not "id"]),
                    table=psycopg.sql.Identifier(table_name),
                    return_key=psycopg.sql.Identifier(return_key))
                cursor.execute(query, request)
                self.connection.commit()
                return cursor.fetchone()[0]
            except psycopg.errors.UniqueViolation as e:
                raise e
    
    def select(self, request: str|list[str], where: list[tuple] = None, table_name : str = None) -> list[psycopg.rows.Row]:
        if not table_name:
            table_name = self.name

        if not self.exists(table_name=table_name):
            raise Exception(f"Table '{table_name}' does not exist")
        
        self.logger.debug(f"Trying to select {request} from '{table_name}'")

        with self.connection.cursor() as cursor:
            try:
                if isinstance(request,str):
                    if request == "ALL":
                        query = psycopg.sql.SQL("SELECT * FROM {table}").format(table=psycopg.sql.Identifier(table_name))
                    else:
                        query = psycopg.sql.SQL("SELECT {field} FROM {table}").format(field=psycopg.sql.Identifier(request), table=psycopg.sql.Identifier(table_name))
                else:
                    query = psycopg.sql.SQL("SELECT {fields} FROM {table}").format(fields=psycopg.sql.SQL(",").join([psycopg.sql.Identifier(entry) for entry in request]), table=psycopg.sql.Identifier(table_name))
                
                
                if where:
                    query += psycopg.sql.SQL(" WHERE ")
                    params = {}
                    for item in where:
                        query += psycopg.sql.SQL(" AND ").join([psycopg.sql.SQL("{field} {equal} {value}").format(field=psycopg.sql.Identifier(item[0]),equal=psycopg.sql.SQL(item[1]),value=psycopg.sql.Placeholder(item[0]))])
                        params[item[0]] = item[2]
                    cursor.execute(query, params)
                    return cursor.fetchall()
                else:
                    cursor.execute(query)
                    return cursor.fetchall()
            except Exception as e:
                self.logger.exception(e)
                raise e

    def delete(self, request: str|list[tuple], where: list[tuple] = None, table_name : str = None):
        if not table_name:
            table_name = self.name

        if not self.exists(table_name=table_name):
            raise Exception(f"Table '{table_name}' does not exist")
        
        self.logger.debug(f"Trying to delete {request} from '{table_name}'")

        with self.connection.cursor() as cursor:
            try:
                if not request == "ALL":
                    query += psycopg.sql.SQL(" WHERE ")
                    params = {}
                    for item in request:
                        query += psycopg.sql.SQL(" OR ").join([psycopg.sql.SQL("{field} {equal} {value}").format(field=psycopg.sql.Identifier(item[0]),equal=psycopg.sql.SQL("=") if item[1] == "=" else psycopg.sql.SQL("like"),value=psycopg.sql.Placeholder(item[0]))])
                        params[item[0]] = item[2]
                    cursor.execute(query,params)
                else:
                    query = psycopg.sql.SQL("DELETE FROM {table}").format(table=psycopg.sql.Identifier(table_name))
                    cursor.execute(query)
            except Exception as e:
                self.logger.error(e)
                raise

    def update(self, request: str|list[str], where: list[tuple] = None, table_name : str = None, return_key : str = "id") -> None:
        if not table_name:
            table_name = self.name

        if not self.exists(table_name=table_name):
            raise Exception(f"Table '{table_name}' does not exist")
        
        self.logger.debug(f"Trying to update {request} from '{table_name}'")

        with self.connection.cursor() as cursor:
            try:
                set_clause = psycopg.sql.SQL(", ").join([
                    psycopg.sql.SQL("{} = {}").format(
                        psycopg.sql.Identifier(k),
                        psycopg.sql.Placeholder(k)
                    ) for k in request.keys() if k is not "id" and k is not "name"
                ])

                query = psycopg.sql.SQL(
                    "UPDATE {table} SET {set_clause}"
                ).format(
                    table=psycopg.sql.Identifier(table_name),
                    set_clause=set_clause
                )

                params = {}
                for k in request.keys():
                    if k == "id":
                        continue
                    params[k] = request[k]
                
                if where:
                    query += psycopg.sql.SQL(" WHERE ")
                    
                    for item in where:
                        query += psycopg.sql.SQL(" AND ").join([psycopg.sql.SQL("{field} {equal} {value}").format(field=psycopg.sql.Identifier(item[0]),equal=psycopg.sql.SQL("=") if item[1] == "=" else psycopg.sql.SQL("like"),value=psycopg.sql.Placeholder(item[0]))])
                        params[item[0]] = item[2]

                query += psycopg.sql.SQL(" RETURNING {return_key}").format(
                    return_key=psycopg.sql.Identifier(return_key)
                )
                cursor.execute(query,params)
                cursor.connection.commit()
                return str(cursor.fetchone()[0])
            except Exception as e:
                self.logger.exception(e)
                raise
    
    def format_result(self, result: list[tuple], columns:list[str] = None) -> list[dict]:
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
    
    def set_function(self, name : str, function) -> None:
        self.functions[name] = function
    
    def get(self, request : str|dict):
        if not request["value"]:
            return self.format_result(self.select("ALL"))
        return self.format_result(self.select("ALL", [(request["key"],"=",request["value"])]))
    
    def update_functions(self):
        pass

    def check_for_key(self, request: dict) -> str | None:
        if(request.get("id")):
            try:
                UUID(request["id"])
                return "id"
            except:
                pass
        if(request.get("name")):
            return "name"
        return None
    
    def add_or_update(self, request: dict):
        key = self.check_for_key(request)
        if not key:
            raise Exception(f"No id or name found in request")
        
        existing_entry = self.select("ALL", [(key,"=",request[key])])
        self.logger.info(f"Found existing entry {existing_entry}")
        
        if existing_entry:
            request["id"] = existing_entry[0][0]
            return f"Updated '{self.name}' with id '{self.update(request, [("id","=",request['id'])])}'"
        else:
            if not request.get("name"):
                raise Exception(f"No name found in request")
            return f"Created '{self.name}' with id '{self.insert(request)}'"