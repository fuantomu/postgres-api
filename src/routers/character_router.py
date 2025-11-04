from fastapi.responses import JSONResponse
from src.database.helper.blizzard_parser import CharacterParser
from src.models.character import (
    CharacterEquipmentModel,
    CharacterModel,
    CharacterParseModel,
    CharacterSearchModel,
)
from src.models.response_model import (
    BaseResponseModel,
    CharacterEquipmentResponseModel,
    CharacterResponseModel,
    CharacterSearchResponseModel,
    CharacterSpecializationResponseModel,
    CharacterStatisticResponseModel,
)
from src.models.specialization import SpecializationModel
from src.routers.base_router import Router


class Character(Router):

    def __init__(self):
        super().__init__()
        self.router.add_api_route(
            "/",
            self.post,
            methods=["POST"],
            status_code=201,
            summary="Add a new or update an existing character",
            response_model=BaseResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )
        self.router.add_api_route(
            "/Parse",
            self.parse,
            methods=["POST"],
            status_code=201,
            summary="Retrieve players and parse to the database",
            response_model=BaseResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )
        self.router.add_api_route(
            "/Equipment",
            self.get_equipment,
            methods=["GET"],
            status_code=201,
            summary="Retrieve player equipment",
            response_model=CharacterEquipmentResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )
        self.router.add_api_route(
            "/Equipment",
            self.post_equipment,
            methods=["Post"],
            status_code=201,
            summary="Add or update player equipment",
            response_model=BaseResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )
        self.router.add_api_route(
            "/Specialization",
            self.get_specialization,
            methods=["GET"],
            status_code=201,
            summary="Retrieve player specializations",
            response_model=CharacterSpecializationResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )
        self.router.add_api_route(
            "/Specialization",
            self.post_specialization,
            methods=["POST"],
            status_code=201,
            summary="Add or update player specializations",
            response_model=BaseResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )
        self.router.add_api_route(
            "/Statistic",
            self.get_statistic,
            methods=["GET"],
            status_code=201,
            summary="Retrieve player stats",
            response_model=CharacterStatisticResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )
        self.router.add_api_route(
            "/Search",
            self.search_character,
            methods=["GET"],
            status_code=201,
            summary="Search for a character profile",
            response_model=CharacterSearchResponseModel,
            responses={400: {"model": BaseResponseModel}},
        )

    async def post(self, character: CharacterModel | CharacterSearchModel):
        self.logger.info(f"Received POST request on {self.name}")
        self.logger.debug(f"Parameters: {character}")
        request = character.model_dump()
        for key in request.copy().keys():
            if request[key] is None:
                request.pop(key)
        if request["name"]:
            request["name"] = request["name"].lower().capitalize()
        if request["realm"]:
            request["realm"] = " ".join(
                [
                    realm_part.lower().capitalize()
                    for realm_part in request["realm"].split(" ")
                ]
            )
        return super().redirect_request("Post", request)

    def parse(self, characters: CharacterParseModel):
        return super().redirect_request(
            "Parse",
            characters,
        )

    def get_equipment(
        self,
        id: str = None,
        name: str = None,
        realm: str = None,
        region: str = None,
        version: str = None,
    ) -> CharacterEquipmentResponseModel | BaseResponseModel:
        if name:
            name = name.lower().capitalize()
        if realm:
            realm = " ".join(
                [realm_part.lower().capitalize() for realm_part in "realm".split(" ")]
            )
        if region:
            region = region.lower()
        if version:
            version = version.lower()
        return super().redirect_request(
            "GetEquipment",
            {
                "key": "id" if id else "name",
                "value": id or name,
                "realm": realm,
                "region": region,
                "version": version,
            },
        )

    async def post_equipment(
        self, item: CharacterEquipmentModel, id: str = None, version: str = None
    ):
        self.logger.info(f"Received POST request on {self.name}")
        self.logger.debug(f"Parameters: {item},{id}")
        request = item.model_dump()
        request["id"] = id
        if version:
            version = version.lower()
        request["version"] = version
        return super().redirect_request("PostEquipment", request)

    def get_specialization(
        self,
        id: str = None,
        name: str = None,
        realm: str = None,
        region: str = None,
        version: str = None,
    ) -> CharacterSpecializationResponseModel | BaseResponseModel:
        if name:
            name = name.lower().capitalize()
        if realm:
            realm = " ".join(
                [realm_part.lower().capitalize() for realm_part in "realm".split(" ")]
            )
        if region:
            region = region.lower()
        if version:
            version = version.lower()
        return super().redirect_request(
            "GetSpecialization",
            {
                "key": "id" if id else "name",
                "value": id or name,
                "realm": realm,
                "region": region,
                "version": version,
            },
        )

    async def post_specialization(self, specialization: SpecializationModel):
        self.logger.info(f"Received POST request on {self.name}")
        self.logger.debug(f"Parameters: {specialization},{id}")
        request = specialization.model_dump()
        return super().redirect_request("PostSpecialization", request)

    def get_statistic(
        self,
        id: str = None,
        name: str = None,
        realm: str = None,
        region: str = None,
        version: str = None,
    ) -> CharacterStatisticResponseModel | BaseResponseModel:
        if name:
            name = name.lower().capitalize()
        if realm:
            realm = " ".join(
                [realm_part.lower().capitalize() for realm_part in "realm".split(" ")]
            )
        if region:
            region = region.lower()
        if version:
            version = version.lower()
        return super().redirect_request(
            "GetStatistic",
            {
                "key": "id" if id else "name",
                "value": id or name,
                "realm": realm,
                "region": region,
                "version": version,
            },
        )

    def get(
        self,
        id: str = None,
        name: str = None,
        realm: str = None,
        region: str = None,
        version: str = None,
    ) -> CharacterResponseModel | BaseResponseModel:
        if name:
            name = name.lower().capitalize()
        if realm:
            realm = " ".join(
                [realm_part.lower().capitalize() for realm_part in "realm".split(" ")]
            )
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
                "region": region,
                "version": version,
            },
        )

    def search_character(
        self, name: str, realm: str, region: str, version: str = "mop"
    ):
        self.logger.info(f"Received GET request on {self.name}")
        self.logger.debug(f"Parameters: {name},{realm},{region}")
        character_parser = CharacterParser(name, realm, region=region, version=version)
        result = character_parser.get_character()
        if result.get("error"):
            return JSONResponse(self.return_result(result["error"]), 404)
        return self.return_result(result)
