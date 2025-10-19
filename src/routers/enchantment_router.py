from src.models.response_model import BaseResponseModel, EnchantmentResponseModel
from src.routers.base_router import Router
from src.helper.enchantments import enchantments
from itertools import islice


class Enchantment(Router):

    def __init__(self):
        super().__init__()

    def get(
        self, id: str = None, version: str = None, slot: str = None, limit: int = 100
    ) -> EnchantmentResponseModel | BaseResponseModel:
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
            ]
        elif slot:
            result = [
                enchantments[enchantment][version]
                for enchantment in dict(
                    islice(
                        enchantments.items(),
                        len(enchantments.keys()) if limit == -1 else limit,
                    )
                )
                if slot
                in enchantments[enchantment].get(version, {}).get("slot", "").lower()
            ]
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
