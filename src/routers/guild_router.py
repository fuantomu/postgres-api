from fastapi.responses import JSONResponse
from src.database.helper.blizzard_parser import GuildParser
from src.models.guild import GuildModel
from src.models.response_model import (
    BaseResponseModel,
    GuildResponseModel,
    GuildRosterResponseModel,
    GuildSearchResponseModel,
)
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
        self.router.add_api_route(
            "/Search",
            self.search_guild,
            methods=["GET"],
            status_code=201,
            summary="Search for a guild profile",
            response_model=GuildSearchResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )
        self.router.add_api_route(
            "/Roster",
            self.get_roster,
            methods=["GET"],
            status_code=201,
            summary="Get guild roster",
            response_model=GuildRosterResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )

    async def post(self, guild: GuildModel):
        self.logger.info(f"Received POST request on {self.name}")
        self.logger.debug(f"Parameters: {guild}")
        request = guild.model_dump()
        for key in request.copy().keys():
            if request[key] is None:
                request.pop(key)
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

    def search_guild(self, name: str, realm: str, region: str, version: str = "mop"):
        self.logger.info(f"Received GET request on {self.name}")
        self.logger.debug(f"Parameters: {name},{realm},{region}")
        guild_parser = GuildParser(name, realm, region=region, version=version)
        result = guild_parser.get_guild()
        if result.get("error"):
            return JSONResponse(self.return_result(result["error"]), 404)
        return self.return_result(result)

    def get_roster(self, name: str, realm: str, region: str, version: str = "mop"):
        self.logger.info(f"Received GET request on {self.name}")
        self.logger.debug(f"Parameters: {name},{realm},{region}")
        guild_parser = GuildParser(name, realm, region=region, version=version)
        result = guild_parser.get_roster()
        return self.return_result(result)
