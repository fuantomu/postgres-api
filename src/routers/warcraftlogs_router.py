from fastapi import APIRouter
from src.database.helper.wcl_parser import WCLParser
from src.models.response_model import (
    BaseResponseModel,
    RankingResponseModel,
    ZoneResponseModel,
)
from src.routers.base_router import Router


class Warcraftlogs(Router):

    def __init__(self):
        self.name = self.__class__.__name__
        self.router = APIRouter()
        self.database = None
        self.router.add_api_route(
            "/Ranking",
            self.get_ranking,
            methods=["GET"],
            status_code=201,
            summary="Get the current ranking for the specified character",
            responses={400: {"model": BaseResponseModel}},
        )
        self.router.add_api_route(
            "/Zone",
            self.get_zone,
            methods=["GET"],
            status_code=201,
            summary="Get zone information for the specified id",
            responses={400: {"model": BaseResponseModel}},
        )

    def get_ranking(
        self,
        character: str,
        server: str,
        region: str,
        wcl_version: str = "classic",
    ) -> RankingResponseModel | BaseResponseModel:
        self.logger.info(f"Received GET-Ranking request on {self.name}")
        self.logger.debug(
            f"character: {character}, server: {server}, region: {region}, wcl_version: {wcl_version}"
        )
        if wcl_version:
            wcl_version = wcl_version.lower()
        if region:
            region = region.lower()
        wcl_parser = WCLParser(wcl_version)
        result = wcl_parser.get_character(character, server, region)
        if not result:
            return self.return_result("Character not found")
        return self.return_result(result)

    def get_zone(
        self,
        zone: int,
        wcl_version: str = "classic",
    ) -> ZoneResponseModel | BaseResponseModel:
        self.logger.info(f"Received GET-Zone request on {self.name}")
        self.logger.debug(f"zone: {zone}, wcl_version: {wcl_version}")
        if wcl_version:
            wcl_version = wcl_version.lower()
        wcl_parser = WCLParser(wcl_version)
        result = wcl_parser.get_zone(zone)
        if not result:
            return self.return_result("Zone not found")
        return self.return_result(result)
