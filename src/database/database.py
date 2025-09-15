import psycopg
from src.logger.log import get_logger
from src.database.structure.initialize import add_ingredients, add_recipes, find_table, initialize_tables

class Database:
    logger = get_logger("database")

    def __init__(self, host, username, password, database_name):
        self.host = host
        self.username = username
        self.password = password
        self.database_name = database_name
        self.create_if_not_exists()
        self.logger.debug(f"Creating connection to database '{self.database_name}'")

    def __enter__(self):
        self.logger.info("Opening connection to database")
        self.connection = psycopg.connect(
            host=self.host,
            port=5432,
            dbname=self.database_name,
            user=self.username,
            password=self.password,
            connect_timeout=5
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.info("Closing connection to database")
        self.connection.close()
        if exc_type is not None:
            raise
        return True
    
    def initialize(self) -> None:
        self.logger.info("Initializing database")
        initialize_tables(self.connection)

    def drop_tables(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE';
            """)
            tables = cursor.fetchall()
            cursor.execute("""
                SELECT conname, conrelid::regclass AS table_from
                FROM pg_constraint
                WHERE contype = 'f';
            """)
            foreign_keys = cursor.fetchall()
            for fk in foreign_keys:
                constraint_name, table_from = fk
                self.logger.debug(f"Dropping foreign key constraint: {constraint_name} on table {table_from}")
                cursor.execute(f"ALTER TABLE {table_from} DROP CONSTRAINT {constraint_name};")

            for table in tables:
                table_name = table[0]
                self.logger.debug(f"Dropping table: {table_name}")
                cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
            self.connection.commit()

    def add_test_data(self) -> None:
        self.logger.debug("Adding test data")
        add_ingredients(self.connection)
        add_recipes(self.connection)

    def manage_request(self, function: str, router : str, request : str|dict):
        table_class = find_table(f"{router}table")
        if table_class:
            new_table = table_class(self.connection, router)
            new_table.update_functions()
            return new_table.get_functions()[function](request)
        
    def create_if_not_exists(self):
        with psycopg.connect(dbname="postgres", user=self.username, password=self.password, host=self.host, port=5432, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.database_name,))
                exists = cur.fetchone()

                if not exists:
                    cur.execute(f'CREATE DATABASE "{self.database_name}"')
                    self.logger.info(f"Database '{self.database_name}' created.")
            