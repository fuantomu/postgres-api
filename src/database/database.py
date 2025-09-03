import psycopg
from logger.log import get_logger
from database.structure.initialize import find_table, initialize_tables

class Database:
    logger = get_logger("database")

    def __init__(self, host, username, password, database_name):
        self.host = host
        self.username = username
        self.password = password
        self.database_name = database_name

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

    def manage_request(self, router : str, request):
        table_class = find_table(f"{router}table")

        if table_class:
            new_table = table_class(self.connection, router)
            request = new_table.format_request(request.model_dump())
            new_table.insert(request)
            