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
        request["name"] = request["name"].lower().capitalize()
        request["realm"] = request["realm"].lower().capitalize()
        return super().redirect_request("Post", request)

    def get(
        self,
        id: str = None,
        name: str = None,
        realm: str = None,
        region: str = None,
        version: str = None,
    ) -> GuildResponseModel:
        if name:
            name = name.lower().capitalize()
        if realm:
            realm = realm.lower().capitalize()
        if region:
            region = region.lower()
        if version:
            version = version.lower()
        return super().redirect_request(
            "Get",
            {
                "key": "id" if id else "name",
                "value": id or name,
                "realm": realm,
                "version": version,
            },
        )
