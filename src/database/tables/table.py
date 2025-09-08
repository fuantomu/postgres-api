import psycopg
from database.helper.statement import generate_statement
from logger.log import get_logger

class Table:
    logger = get_logger("database")

    columns = {}

    def __init__(self, connection: psycopg.Connection, name: str):
        self.connection = connection
        self.name = name.lower()
        self.schema = "public"

    def exists(self):
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
                (self.schema, self.name)
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
    
    def insert(self, request: dict) -> None:
        if not self.exists():
            self.logger.error(f"Table '{self.name}' does not exist")
            return
        
        self.logger.debug(f"Trying to insert {request} into '{self.name}'")

        with self.connection.cursor() as cursor:
            try:
                query = psycopg.sql.SQL("INSERT INTO {table} ({rows}) VALUES ({fields})").format(fields=psycopg.sql.SQL(", ").join([psycopg.sql.Placeholder(entry) for entry in request.keys()]), rows=psycopg.sql.SQL(",").join([psycopg.sql.Identifier(entry) for entry in request.keys()]), table=psycopg.sql.Identifier(self.name))
                cursor.execute(query, request)
                self.connection.commit()
            except psycopg.errors.UniqueViolation as e:
                self.logger.error(e)
                raise
    
    def select(self, request: str|list[str], where: list[tuple] = None) -> list[psycopg.rows.Row]:
        if not self.exists():
            self.logger.error(f"Table '{self.name}' does not exist")
            return
        
        self.logger.debug(f"Trying to select {request} from '{self.name}'")

        with self.connection.cursor() as cursor:
            try:
                if isinstance(request,str):
                    if request == "ALL":
                        query = psycopg.sql.SQL("SELECT * FROM {table}").format(table=psycopg.sql.Identifier(self.name))
                    else:
                        query = psycopg.sql.SQL("SELECT {field} FROM {table}").format(field=psycopg.sql.Identifier(request), table=psycopg.sql.Identifier(self.name))
                else:
                    query = psycopg.sql.SQL("SELECT {fields} FROM {table}").format(fields=psycopg.sql.SQL(",").join([psycopg.sql.Identifier(entry) for entry in request]), table=psycopg.sql.Identifier(self.name))
                
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
            except psycopg.errors.UniqueViolation as e:
                self.logger.error(e)
                raise
                
    
    def format_request(self, request : dict) -> dict:
        formatted_request = {}
        for key in self.columns.keys():
            formatted_request[key] = request.get(key, "")
            if formatted_request[key] == "":
                formatted_request.pop(key)
        return formatted_request
    
    def format_result(self, result: list[tuple], columns:list[str] = None) -> list[dict]:
        output = []
        if not columns:
            columns = list(self.columns.keys())
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
    
    def get(self, request : str|dict):
        return self.format_result(self.select("ALL", [("id","=",request)]))

    def find(self, request : str|dict):
        return self.format_result(self.select("ALL", [("name","=",request)]))
    
    def get_all(self, request : str|dict):
        return self.format_result(self.select(request))
    
    functions = {
        "GetAll" : get_all,
        "Get": get,
        "Find": find,
        "Add": insert
    }