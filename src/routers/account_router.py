from src.models.account import AccountLoginModel, AccountModel
from src.models.response_model import (
    AccountLoginResponseModel,
    AccountResponseModel,
    BaseResponseModel,
    SessionResponseModel,
)
from src.routers.base_router import Router


class Account(Router):

    def __init__(self):
        super().__init__()
        self.router.add_api_route(
            "/Register",
            self.register,
            methods=["POST"],
            status_code=201,
            summary="Add a new account",
            response_model=BaseResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )
        self.router.add_api_route(
            "/Login",
            self.login,
            methods=["POST"],
            status_code=201,
            summary="Login to the given account",
            response_model=AccountLoginResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )
        self.router.add_api_route(
            "/Session",
            self.get_session,
            methods=["GET"],
            status_code=201,
            summary="Get session state",
            response_model=SessionResponseModel | BaseResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )

    async def register(self, account: AccountModel):
        self.logger.info(f"Received POST request on {self.name}")
        self.logger.debug(f"Parameters: {account}")

        account = account.model_dump()
        account["username"] = account["username"].lower().strip()
        return super().redirect_request("PostRegister", account)

    async def login(self, account: AccountLoginModel):
        self.logger.info(f"Received POST request on {self.name}")
        self.logger.debug(f"Parameters: {account}")

        account = account.model_dump()
        account["username"] = account["username"].lower().strip()
        return super().redirect_request("PostLogin", account)

    def get(self, username: str) -> AccountResponseModel | BaseResponseModel:
        return super().redirect_request(
            "Get",
            {"username": username},
        )

    def get_session(self, session: str) -> SessionResponseModel | BaseResponseModel:
        return super().redirect_request(
            "GetSession",
            {"session": session},
        )
