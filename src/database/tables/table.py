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
        self.functions["Add"] = self.post
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
                query = psycopg.sql.SQL("INSERT INTO {table} ({rows}) VALUES ({fields}) RETURNING {return_key}").format(fields=psycopg.sql.SQL(", ").join([psycopg.sql.Placeholder(entry) for entry in request.keys()]), rows=psycopg.sql.SQL(",").join([psycopg.sql.Identifier(entry) for entry in request.keys()]), table=psycopg.sql.Identifier(table_name), return_key=psycopg.sql.Identifier(return_key))
                cursor.execute(query, request)
                self.connection.commit()
                return cursor.fetchone()[0]
            except psycopg.errors.UniqueViolation as e:
                self.logger.error(e)
                raise
    
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
                        query += psycopg.sql.SQL(" AND ").join([psycopg.sql.SQL("{field} {equal} {value}").format(field=psycopg.sql.Identifier(item[0]),equal=psycopg.sql.SQL("=") if item[1] == "=" else psycopg.sql.SQL("like"),value=psycopg.sql.Placeholder(item[0]))])
                        params[item[0]] = item[2]
                    cursor.execute(query, params)
                    return cursor.fetchall()
                else:
                    cursor.execute(query)
                    return cursor.fetchall()
            except Exception as e:
                self.logger.exception(e)
                raise

    def delete(self, request: str|list[tuple], table_name : str = None):
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
                temp[columns[col]] = result[idx][col]
            output.append(temp)
        return output
    
    def get_columns(self) -> dict:
        return self.columns
    
    def get_functions(self) -> dict:
        return self.functions
    
    def set_function(self, name : str, function) -> None:
        self.functions[name] = function
    
    def get(self, request : str|dict):
        if not request["value"]:
            return self.format_result(self.select("ALL"))
        return self.format_result(self.select("ALL", [(request["key"],"=",request["value"])]))
    
    def post(self, request : str|dict):
        return str(self.insert(request))
    
    def update_functions(self):
        pass