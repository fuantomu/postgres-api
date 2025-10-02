from src.models.guild import GuildModel
from src.models.response_model import BaseResponseModel, GuildResponseModel
from src.routers.base_router import Router


class Guild(Router):

    def __init__(self):
        super().__init__()
        self.router.add_api_route(
            "/",
            self.post,
            methods=["POST"],
            status_code=201,
            summary="Add a new or update an existing guild",
            response_model=BaseResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )

    async def post(self, guild: GuildModel):
        self.logger.info(f"Received POST request on {self.name}")
        self.logger.debug(f"Parameters: {guild}")
        request = guild.model_dump()
        for key in request.copy().keys():
            if request[key] is None:
                request.pop(key)
        return super().redirect_request("Post", request)

    def get(self, id: str = None, name: str = None) -> GuildResponseModel:
        return super().redirect_request(
            "Get", {"key": "id" if id else "name", "value": id or name}
        )
