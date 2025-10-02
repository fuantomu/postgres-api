import json
from dotenv import load_dotenv
import requests
from os import getenv
from src.models.character import CharacterEquipmentModel, CharacterModel
from src.models.guild import GuildModel
from src.models.item import ItemModel
from src.models.specialization import SpecializationModel

slotNames = {
    "HEAD": 0,
    "NECK": 1,
    "SHOULDER": 2,
    "SHIRT": 3,
    "CHEST": 4,
    "WAIST": 5,
    "LEGS": 6,
    "FEET": 7,
    "WRIST": 8,
    "HANDS": 9,
    "FINGER_1": 10,
    "FINGER_2": 11,
    "TRINKET_1": 12,
    "TRINKET_2": 13,
    "BACK": 14,
    "MAIN_HAND": 15,
    "OFF_HAND": 16,
    "RANGED": 17,
    "TABARD": 18,
}

affixStats = {
    2802: "AGILITY",
    2803: "STAMINA",
    2804: "INTELLECT",
    2805: "STRENGTH",
    2806: "SPIRIT",
    2815: "DODGE_RATING",
    2822: "CRIT_RATING",
    3726: "HASTE_RATING",
    3727: "HIT_RATING",
    4058: "EXPERTISE_RATING",
    4059: "MASTERY_RATING",
    4060: "PARRY_RATING",
}
ignore_enchant = [3, 18]


class BlizzardParser:
    def __init__(self, token=None):
        self.headers = {"Authorization": None}
        self.base_url = "https://eu.api.blizzard.com/"
        self.get_token(token)

    def get_token(self, token=None):
        if token is None:
            url = "https://eu.battle.net/oauth/token"
            result = json.loads(
                requests.post(
                    url,
                    data={
                        "client_id": getenv("BATTLE_NET_CLIENT_ID"),
                        "client_secret": getenv("BATTLE_NET_CLIENT_SECRET"),
                        "grant_type": "client_credentials",
                    },
                ).text
            )
            token = result.get("access_token")
        self.headers["Authorization"] = f"Bearer {token}"

    def get_base_url(self, url_type=""):
        return f"{self.base_url}".replace(
            "/TYPE" if url_type == "" else "TYPE", url_type
        )


class CharacterParser(BlizzardParser):
    def __init__(self, character: str, realm: str, token=None):
        super().__init__(token)
        self.character = character
        self.realm = realm
        self.base_url = "https://eu.api.blizzard.com/profile/wow/character/REALM/CHARACTERNAME/TYPE?namespace=profile-classic-eu&locale=en_GB&access_token="

    def get_base_url(self, url_type=""):
        return (
            super()
            .get_base_url(url_type)
            .replace("CHARACTERNAME", self.character.lower())
            .replace("REALM", self.realm.lower())
        )

    def get_character(self):
        character = requests.get(
            self.get_base_url(),
            headers=self.headers,
        ).json()
        character_template = CharacterModel().model_dump()

        character_template["id"] = character["id"]
        character_template["name"] = character["name"]
        character_template["gender"] = character["gender"]["name"]
        character_template["faction"] = character["faction"]["name"]
        character_template["race"] = character["race"]["name"]
        character_template["character_class"] = character["character_class"]["name"]
        character_template["active_spec"] = character["active_spec"]["name"]
        character_template["realm"] = character["realm"]["name"]
        character_template["guild"] = character.get("guild", {"id": None})["id"]
        character_template["level"] = character["level"]
        character_template["achievement_points"] = character["achievement_points"]
        character_template["last_login_timestamp"] = character.get(
            "last_login_timestamp"
        )
        character_template["average_item_level"] = character["average_item_level"]
        character_template["equipped_item_level"] = character["equipped_item_level"]
        character_template["active_title"] = character.get(
            "active_title", {"name": None}
        )["name"]
        character_template["guild_name"] = character.get("guild", {"name": None})[
            "name"
        ]

        return character_template

    def get_sorted_equipment(self):
        character = requests.get(
            self.get_base_url("equipment"),
            headers=self.headers,
        ).json()
        enchants = requests.get(
            "https://raw.githubusercontent.com/fuantomu/envy-armory/main/enchants.json"
        ).json()
        affixes = requests.get(
            "https://raw.githubusercontent.com/fuantomu/envy-armory/main/affix.json"
        ).json()
        sortedEquipment = CharacterEquipmentModel().model_dump()
        items = character["equipped_items"]
        for item in items:
            item["link"] = ""
            if not slotNames[item["slot"]["type"]] in ignore_enchant:
                if item.get("enchantments"):

                    if item["enchantments"][0]["enchantment_slot"]["id"] == 0:
                        item["link"] += "&ench="

                    filtered = [
                        enchant
                        for enchant in enchants[str(slotNames[item["slot"]["type"]])]
                        if any(
                            enchant["id"] == item_enchant["enchantment_id"]
                            for item_enchant in item["enchantments"]
                        )
                        or any(
                            entry.get("enchantment_id") == 3729
                            for entry in item["enchantments"]
                        )
                    ]
                    item["enchants"] = filtered
                    if len(filtered) > 0:
                        item["link"] += ":".join(str(entry["id"]) for entry in filtered)

                    if len(item["enchantments"]) > 0:
                        filtered = [
                            entry
                            for entry in item["enchantments"]
                            if entry["enchantment_slot"]["id"] == 2
                            or entry["enchantment_slot"]["id"] == 3
                            or entry["enchantment_slot"]["id"] == 4
                        ]
                        item["gems"] = [
                            {"id": entry["source_item"]["id"]} for entry in filtered
                        ]
                        if len(filtered) > 0:
                            item["link"] += "&gems="

                        for gem in filtered:
                            item["link"] += str(gem["source_item"]["id"])

                            if gem != filtered[-1]:
                                item["link"] += ":"

                        if "WEAPON" in item["inventory_type"]["type"]:
                            item["inventory_type"]["type"] = "WEAPON"

                        found_affixes = None
                        for phase in affixes.get(item["inventory_type"]["type"], []):
                            if (
                                item["item"]["id"]
                                in affixes[item["inventory_type"]["type"]][phase]["ids"]
                            ):
                                found_affixes = affixes[item["inventory_type"]["type"]][
                                    phase
                                ]["affix"]
                                break

                        if found_affixes:
                            filtered = [
                                entry
                                for entry in item["enchantments"]
                                if entry["enchantment_slot"]["id"] in [8, 9, 10, 11]
                            ]
                            if len(filtered) > 0:
                                item["link"] += "&rand="
                            affixNames = [
                                affixStats[entry.get("enchantment_id")]
                                for entry in filtered
                            ]
                            for affix in found_affixes:
                                if all(
                                    [
                                        stat in found_affixes[affix]["stats"]
                                        for stat in affixNames
                                    ]
                                ):
                                    item["link"] += str(affix)
                                    break

                if item.get("set"):
                    item["link"] += "&pcs="
                    item["link"] += ":".join(
                        [str(item["item"]["id"]) for item in items]
                    )

                if len(item["link"]) > 0:
                    item["link"] = item["link"][1:]
            item_model = ItemModel().model_dump()
            item_model["id"] = item["item"]["id"]
            item_model["name"] = item["name"]
            item_model["slot"] = item["slot"]["name"]
            item_model["quality"] = item["quality"]["name"]
            item_model["wowhead_link"] = item["link"]
            sortedEquipment[item["slot"]["type"].lower()] = item_model

        return sortedEquipment

    def get_talents(self):
        talents = requests.get(
            self.get_base_url("specializations"),
            headers=self.headers,
        ).json()

        specs = []

        for specialization in talents["specializations"]:
            current_spec = SpecializationModel().model_dump()
            current_spec["name"] = specialization["specialization_name"]
            current_spec["talents"] = [
                talent["talent"]["id"] for talent in specialization.get("talents", [])
            ]
            specs.append(current_spec)

        for index, specialization in enumerate(specs):
            specialization["glyphs"] = [
                glyph["id"]
                for glyph in talents["specialization_groups"][index].get("glyphs", [])
            ]
            specialization["active"] = talents["specialization_groups"][index][
                "is_active"
            ]
        return specs


class GuildParser(BlizzardParser):
    def __init__(self, guild: str, realm: str, token=None):
        super().__init__(token)
        self.guild = guild.replace(" ", "-")
        self.realm = realm
        self.base_url = "https://eu.api.blizzard.com/data/wow/guild/REALM/GUILDNAME?namespace=profile-classic-eu&locale=en_GB&access_token="

    def get_base_url(self, url_type=""):
        return (
            super()
            .get_base_url(url_type)
            .replace("GUILDNAME", self.guild.lower())
            .replace("REALM", self.realm.lower())
        )

    def get_guild(self):
        guild = requests.get(
            self.get_base_url(),
            headers=self.headers,
        ).json()

        guild_template = GuildModel().model_dump()

        guild_template["id"] = guild["id"]
        guild_template["name"] = guild["name"]
        guild_template["faction"] = guild["faction"]["name"]
        guild_template["realm"] = guild["realm"]["name"]
        guild_template["achievement_points"] = guild["achievement_points"]
        guild_template["member_count"] = guild["member_count"]
        guild_template["created_timestamp"] = guild.get("created_timestamp")

        return guild_template


if __name__ == "__main__":
    load_dotenv(".env")
    load_dotenv(".env.local", override=True)
    parser = CharacterParser("Yoloschîît", "Everlook")
    parser.get_talents()
