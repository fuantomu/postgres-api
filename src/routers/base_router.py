from fastapi import APIRouter
from fastapi.responses import Response
from logger.log import get_logger
from database.database import Database
from helper.exception import handle_exception

class Router:

    logger = get_logger("router")

    def __init__(self):
        self.name = self.__class__.__name__
        self.router = APIRouter()
        self.database = None

    def set_database(self, database : Database):
        self.database = database
        
    def get(self):
        return Response(status_code=200)

    def post(self):
        return Response(status_code=201)
    
    def redirect_request(self, request) -> None:
        self.logger.info("Redirecting request to database")
        with self.database as _:
            try:
                self.database.manage_request(self.name, request)
                return self.post()
            except Exception as e:
                return Response(status_code=400, content = handle_exception(e), media_type="text/plain")