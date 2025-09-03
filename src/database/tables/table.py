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
                cursor.execute(
                    f"""
                    INSERT INTO {self.name} ({",".join(request.keys())})
                    VALUES {str(tuple(request.values()))}
                    """
                )
                self.connection.commit()
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
        