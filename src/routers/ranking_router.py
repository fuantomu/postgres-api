import json
from src.database.helper.wcl_parser import WCLParser
from src.models.response_model import (
    BaseResponseModel,
    RankingResponseModel,
)
from src.routers.base_router import Router


class Ranking(Router):

    def __init__(self):
        super().__init__()

    def get(
        self,
        character: str,
        server: str,
        region: str,
        wcl_version: str = "classic",
    ) -> RankingResponseModel | BaseResponseModel:
        if wcl_version:
            wcl_version = wcl_version.lower()
        if region:
            region = region.lower()
        wcl_parser = WCLParser(wcl_version)
        result = wcl_parser.get_character(character, server, region)
        return self.return_result(result)
