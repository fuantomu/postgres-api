from src.models.character import CharacterModel, CharacterParseModel
from src.models.response_model import (
    BaseResponseModel,
    CharacterEquipmentResponseModel,
    CharacterResponseModel,
    CharacterSpecializationResponseModel,
    CharacterStatisticResponseModel,
)
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
            "/Specialization",
            self.get_specialization,
            methods=["GET"],
            status_code=201,
            summary="Retrieve player specializations",
            response_model=CharacterSpecializationResponseModel,
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

    async def post(self, character: CharacterModel):
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
