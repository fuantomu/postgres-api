import json
from src.database.helper.blizzard_parser import ItemParser
from src.models.response_model import BaseResponseModel, ItemResponseModel
from src.routers.base_router import Router


class Item(Router):

    def __init__(self):
        super().__init__()

    def get(
        self,
        id: str = None,
        region: str = None,
        version: str = None,
    ) -> ItemResponseModel | BaseResponseModel:
        if version:
            version = version.lower()
        if region:
            region = region.lower()
        item_parser = ItemParser(
            region=region if region else "eu", version=version if version else "mop"
        )
        item = item_parser.get_item(id)
        return self.return_result(json.dumps(item))
