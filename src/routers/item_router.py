from itertools import islice
from src.database.helper.blizzard_parser import ItemParser
from src.helper.item_search import item_search
from src.models.response_model import BaseResponseModel, ItemResponseModel
from src.routers.base_router import Router


class Item(Router):

    def __init__(self):
        super().__init__()

    def get(
        self,
        version: str,
        search: str = None,
        id: str = None,
        slot: str = None,
        limit: int = 100,
    ) -> ItemResponseModel | BaseResponseModel:
        if version:
            version = version.lower()
        self.logger.info(f"Received GET request on {self.name}")
        self.logger.debug(
            f"search: {search}, id: {id}, version: {version}, limit: {limit}"
        )

        result = []

        if id:
            result = [
                item_search[__item][version]
                for __item in item_search
                if item_search[__item].get(version)
                and (
                    (search and search in item_search[__item][version].get("name"))
                    or id == item_search[__item][version].get("id")
                )
            ]
        elif (id or search) and slot:
            item_parser = ItemParser(version=version)
            result = item_parser.fetch_search(search=search, id=id, slot=slot)
        else:
            result = [
                item_search[item][version]
                for item in dict(
                    islice(
                        item_search.items(),
                        len(item_search.keys()) if limit == -1 else limit,
                    )
                )
                if item_search[item].get(version, {})
                and (item_search[item].get("slot") == slot if slot else 1)
            ]
        return self.return_result(result)
