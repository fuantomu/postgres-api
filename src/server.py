from fastapi import FastAPI
import uvicorn
from os import getenv
from models.exception import handle_exception
import routers
from logger.log import get_logger
import logging
from database.database import Database


class Server:
    logger = get_logger("server")

    def __init__(self):
        self.port = int(getenv("SERVICE_PORT"))
        self.app = FastAPI(title="Cookbook",version="0.1",contact={"name":"fuantomu","email":"fuantomuw@gmail.com"},docs_url='/',root_path="/api")
        self.routers = {}

    def initialize_logging(self):
        logging.getLogger("asyncio").propagate = False
        logging.getLogger("fastapi").propagate = False
        logging.getLogger("uvicorn.access").propagate = False
        self.uvicorn_logger = get_logger("uvicorn.error")

    def initialize_endpoints(self):
        self.routers["Recipe"] = routers.Recipe()
        self.routers["Ingredient"] = routers.Ingredient()

        for key,value in self.routers.items():
            self.app.include_router(value.router, prefix=f"/{key}", tags=[key])

    def initialize_database(self):
        self.database = Database(getenv("POSTGRES_HOST"), getenv("POSTGRES_USERNAME"), getenv("POSTGRES_PASSWORD"), getenv("POSTGRES_DATABASE"))
        with self.database as d:
            d.initialize()
        
        for _,router in self.routers.items():
            router.database = self.database

    def run(self):
        self.logger.info(f"Running on port {self.port}")
        uvicorn.run(self.app, port=self.port, host='0.0.0.0', reload=False, log_config=None)


if __name__ == '__main__':
    server = Server()
    server.initialize_endpoints()
    server.initialize_logging()
    try:
        server.initialize_database()
    except Exception as e:
        server.logger.error(handle_exception(e))
        server.logger.info("Exiting program")
        exit(0)

    server.run()