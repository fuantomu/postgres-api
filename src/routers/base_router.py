from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from src.logger.log import get_logger
from src.database.database import Database
from src.helper.exception import handle_exception
from src.models.response_model import BaseResponseModel


class Router:

    logger = get_logger("router")

    def __init__(self):
        self.name = self.__class__.__name__
        self.router = APIRouter()
        self.database = None
        self.router.add_api_route(
            "/",
            self.get,
            methods=["GET"],
            status_code=202,
            summary=f"Get details for a {self.name}",
            responses={400: {"model": BaseResponseModel}},
        )
        self.router.add_api_route(
            "/",
            self.delete,
            methods=["DELETE"],
            status_code=200,
            summary=f"Delete the specified {self.name}",
            response_model=BaseResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )

    def set_database(self, database: Database) -> None:
        self.database = database

    def return_result(self, result=None):
        return {"Result": result}

    def get(self, id: str = None, name: str = None):
        self.logger.info(f"Received GET request on {self.name}")
        return self.redirect_request(
            "Get", {"key": "id" if id else "name", "value": id or name}
        )

    def delete(
        self, id: str = None, name: str = None, realm: str = None, version: str = None
    ):
        self.logger.info(f"Received DELETE request on {self.name}")
        return self.redirect_request(
            "Delete",
            {
                "key": "id" if id else "name",
                "value": id or name,
                "realm": realm,
                "version": version,
            },
        )

    def missing_parameters(self, parameters: list[str]) -> Response:
        return Response(
            status_code=400,
            content=f"Missing one or more required parameters in: '{','.join(parameters)}'",
            media_type="text/plain",
        )

    def redirect_request(
        self, _func: str, request: str | dict
    ) -> JSONResponse | Response:
        self.logger.info("Redirecting request to database")
        with self.database as database:
            try:
                result = database.manage_request(_func, self.name, request)
                return self.return_result(result)
            except Exception as e:
                self.logger.exception(e)
                return JSONResponse({"Result": handle_exception(e)}, 400)
