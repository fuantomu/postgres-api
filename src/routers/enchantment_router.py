from src.database.helper.blizzard_parser import EnchantmentParser
from src.models.response_model import BaseResponseModel, EnchantmentResponseModel
from src.routers.base_router import Router
from src.helper.enchantments import enchantments
from itertools import islice


class Enchantment(Router):

    def __init__(self):
        super().__init__()

    def get(
        self,
        version: str,
        id: str = None,
        search: str = None,
        slot: str = None,
        limit: int = 100,
    ) -> EnchantmentResponseModel | BaseResponseModel:
        self.logger.info(f"Received GET request on {self.name}")
        self.logger.debug(
            f"id: {id}, search: {search}, slot: {slot}, version: {version}, limit: {limit}"
        )
        if version:
            version = version.lower()
        if slot:
            slot = slot.lower().replace(" ", "_")
        result = []

        if id:
            result = [
                enchantments[enchantment][version]
                for enchantment in dict(
                    islice(
                        enchantments.items(),
                        len(enchantments.keys()) if limit == -1 else limit,
                    )
                )
                if enchantments[enchantment].get(version, {}).get("id", -1) == int(id)
                or enchantments[enchantment].get(version, {}).get("source_id", -1)
                == int(id)
            ]
        elif (id or search) and slot:
            if slot == "gem":
                enchantment_parser = EnchantmentParser(version=version)
                result = enchantment_parser.fetch_gem(search=search, id=id)
            elif slot == "enchant":
                if version == "classic":
                    enchantment_parser = EnchantmentParser(
                        namespace="1.15.8_63631-classic1x", version=version
                    )
                else:
                    enchantment_parser = EnchantmentParser(version=version)
                result = enchantment_parser.fetch_enchant(search=search, id=id)
        else:
            result = [
                enchantments[enchantment][version]
                for enchantment in dict(
                    islice(
                        enchantments.items(),
                        len(enchantments.keys()) if limit == -1 else limit,
                    )
                )
                if enchantments[enchantment].get(version, {})
            ]
        return self.return_result(result)
