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
        self.router.add_api_route("/", self.get, methods=["GET"])

    def set_database(self, database : Database):
        self.database = database
        
    def return_result(self, result=None):
        return result
    
    def get(self, id: str = None, name: str = None):
        self.logger.info(f"Received GET request on {self.name}")
        return self.redirect_request('Get', {"key": "id" if id else "name", "value": id or name})

    
    def redirect_request(self, _func : str, request: str|dict) -> Response:
        self.logger.info("Redirecting request to database")
        with self.database as _:
            try:
                result = self.database.manage_request(_func, self.name, request)
                return self.return_result(result)
            except Exception as e:
                self.logger.exception(e)
                return Response(status_code=400, content = handle_exception(e), media_type="text/plain")
                