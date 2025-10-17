import json
from dotenv import load_dotenv
import requests
from os import getenv
from src.models.character import (
    CharacterEquipmentModel,
    CharacterModel,
    CharacterStatisticModel,
    RatingModel,
)
from src.models.guild import GuildModel
from src.models.icon import IconModel
from src.models.item import ItemModel
from src.models.specialization import SpecializationModel
from src.helper.glyphs import glyphs
from src.helper.talents import talents
from src.helper.enchantments import enchantments
from src.helper.items import items

slotNames = {
    "head": 0,
    "neck": 1,
    "shoulders": 2,
    "shirt": 3,
    "chest": 4,
    "waist": 5,
    "legs": 6,
    "feet": 7,
    "wrist": 8,
    "hands": 9,
    "ring_1": 10,
    "ring_2": 11,
    "trinket_1": 12,
    "trinket_2": 13,
    "back": 14,
    "main_hand": 15,
    "off_hand": 16,
    "ranged": 17,
    "tabard": 18,
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

class_enum = {
    "Warrior": 1,
    "Paladin": 2,
    "Hunter": 4,
    "Rogue": 8,
    "Priest": 16,
    "Deathknight": 32,
    "Shaman": 64,
    "Mage": 128,
    "Warlock": 256,
    "Monk": 512,
    "Druid": 1024,
}


class BlizzardParser:
    def __init__(
        self,
        namespace: str = None,
        region: str = "eu",
        version: str = "mop",
        token=None,
    ):
        self.headers = {"Authorization": None}
        self.base_url = "https://eu.api.blizzard.com/"
        if not namespace:
            match version.lower():
                case "classic" | "tbc" | "cata" | "wotlk":
                    self.namespace = "classic1x"
                case "wod" | "mop":
                    self.namespace = "classic"
                case _:
                    self.namespace = namespace
        else:
            self.namespace = namespace
        self.region = region
        self.version = version
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
    def __init__(
        self,
        character: str,
        realm: str,
        namespace: str = None,
        region: str = "eu",
        version: str = "mop",
        token=None,
    ):
        super().__init__(namespace, region, version, token)
        self.character = character
        self.character_class = None
        self.realm = realm.replace(" ", "-")
        self.base_url = "https://REGION.api.blizzard.com/profile/wow/character/REALM/CHARACTERNAME/TYPE?namespace=profile-NAMESPACE-REGION&locale=en_GB&access_token="

    def get_base_url(self, url_type=""):
        return (
            super()
            .get_base_url(url_type)
            .replace("CHARACTERNAME", self.character.lower())
            .replace("REALM", self.realm.lower())
            .replace("NAMESPACE", self.namespace.lower())
            .replace("REGION", self.region.lower())
        )

    def get_character(self):
        character = requests.get(
            self.get_base_url(),
            headers=self.headers,
        ).json()
        if character.get("detail"):
            return {"error": character["detail"]}

        character_template = CharacterModel().model_dump()
        character_template["id"] = character["id"]
        character_template["name"] = character["name"]
        character_template["gender"] = character["gender"]["name"]
        character_template["faction"] = character["faction"]["name"]
        character_template["race"] = (
            character["race"]["name"].replace(" ", "").capitalize()
        )
        character_template["character_class"] = (
            character["character_class"]["name"].replace(" ", "").capitalize()
        )
        character_template["active_spec"] = character.get("active_spec", {}).get(
            "name", "Adventurer"
        )
        self.character_class = (
            character["character_class"]["name"].replace(" ", "").capitalize()
        )
        if (
            character_template["active_spec"]
            and character_template["active_spec"] != "Adventurer"
        ):
            character_template["active_spec"] = (
                character_template["active_spec"].replace(" ", "").capitalize()
            )
        character_template["realm"] = character["realm"]["name"]
        character_template["guild"] = character.get("guild", {"id": None})["id"]
        character_template["level"] = character["level"]
        character_template["achievement_points"] = character.get(
            "achievement_points", 0
        )
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
        character_template["region"] = self.region.lower()
        character_template["version"] = self.version.lower()

        return character_template

    def get_sorted_equipment(self):
        equipment = requests.get(
            self.get_base_url("equipment"),
            headers=self.headers,
        ).json()
        sortedEquipment = CharacterEquipmentModel().model_dump()
        items = equipment["equipped_items"]

        item_parser = ItemParser(self.namespace, self.region, self.version)
        for item in items:
            sortedEquipment[item["slot"]["name"].lower().replace(" ", "_")] = (
                item_parser.parse_item(item)
            )

        return sortedEquipment

    def get_talents(self):
        specializations = requests.get(
            self.get_base_url("specializations"),
            headers=self.headers,
        ).json()
        if self.version == "classic":
            return self.get_talents_classic_fresh(specializations)

        specs = []

        for specialization in specializations.get("specializations", []):
            current_spec = SpecializationModel().model_dump()
            current_spec["name"] = (
                specialization["specialization_name"].replace(" ", "").capitalize()
            )
            current_spec["talents"] = []

            for talent in specialization.get("talents", []):
                if (
                    not talents.get(talent["spell_tooltip"]["spell"]["id"])
                    or self.version
                    not in talents.get(
                        talent["spell_tooltip"]["spell"]["id"], {}
                    ).keys()
                    or not talents.get(talent["spell_tooltip"]["spell"]["id"], {})
                    .get(self.version, {})
                    .get("icon")
                ):
                    print(f"Talent {talent['spell_tooltip']['spell']} is missing")
                    save_talent(talent["spell_tooltip"]["spell"], self.version)
                current_spec["talents"].append(
                    {"id": talent["spell_tooltip"]["spell"]["id"]}
                )
            specs.append(current_spec)

        for index, specialization in enumerate(specs):
            for glyph in specializations["specialization_groups"][index].get(
                "glyphs", []
            ):
                if (
                    not glyphs.get(glyph["id"])
                    or self.version not in glyphs.get(glyph["id"], {}).keys()
                    or not glyphs.get(glyph["id"], {}).get(self.version, {}).get("icon")
                    or not glyphs.get(glyph["id"], {}).get(self.version, {}).get("type")
                ):
                    print(f"Glyph {glyph} is missing")
                    find_glyph(glyph, self.version, self.character_class)
                specialization["glyphs"].append(glyphs[glyph["id"]][self.version]["id"])
            specialization["active"] = specializations["specialization_groups"][index][
                "is_active"
            ]
        return specs

    def get_talents_classic_fresh(self, specializations):
        specs = []
        for specialization in specializations.get("specialization_groups", []):
            current_spec = SpecializationModel().model_dump()
            current_spec["name"] = max(
                specialization.get("specializations", []),
                key=lambda x: x["spent_points"],
            )["specialization_name"]
            current_spec["talents"] = []
            for spec in specialization.get("specializations", []):

                for talent in spec.get("talents", []):
                    if (
                        not talents.get(talent["spell_tooltip"]["spell"]["id"])
                        or self.version
                        not in talents.get(
                            talent["spell_tooltip"]["spell"]["id"], {}
                        ).keys()
                        or not talents.get(talent["spell_tooltip"]["spell"]["id"], {})
                        .get(self.version, {})
                        .get("icon")
                    ):
                        print(f"Talent {talent['spell_tooltip']['spell']} is missing")
                        save_talent(talent["spell_tooltip"]["spell"], self.version)
                    current_spec["talents"].append(
                        {
                            "id": talent["spell_tooltip"]["spell"]["id"],
                            "rank": talent["talent_rank"],
                        }
                    )
            current_spec["active"] = specialization.get("is_active", False)
            specs.append(current_spec)
        return specs

    def get_statistics(self):
        statistics = requests.get(
            self.get_base_url("statistics"),
            headers=self.headers,
        ).json()
        statistic_template = CharacterStatisticModel().model_dump()

        statistic_template["health"] = statistics.get("health")
        statistic_template["power"] = statistics.get("power")
        statistic_template["strength"] = statistics.get("strength", {}).get("effective")
        statistic_template["agility"] = statistics.get("agility", {}).get("effective")
        statistic_template["intellect"] = statistics.get("intellect", {}).get(
            "effective"
        )
        statistic_template["stamina"] = statistics.get("stamina", {}).get("effective")
        statistic_template["spirit"] = statistics.get("spirit", {}).get("effective")
        statistic_template["attack_power"] = statistics.get("attack_power", 0)
        statistic_template["spell_power"] = statistics.get("spell_power", 0)
        statistic_template["power_type"] = statistics.get("power_type", {}).get("name")
        statistic_template["armor"] = statistics.get("armor", {}).get("effective")
        statistic_template["defense"] = statistics.get("defense", {}).get("effective")
        statistic_template["mana_regen"] = statistics.get("mana_regen")
        statistic_template["arcane_resistance"] = statistics.get(
            "arcane_resistance", {}
        ).get("effective")
        statistic_template["fire_resistance"] = statistics.get(
            "fire_resistance", {}
        ).get("effective")
        statistic_template["nature_resistance"] = statistics.get(
            "nature_resistance", {}
        ).get("effective")
        statistic_template["shadow_resistance"] = statistics.get(
            "shadow_resistance", {}
        ).get("effective")
        statistic_template["holy_resistance"] = statistics.get(
            "holy_resistance", {}
        ).get("effective")
        statistic_template["frost_resistance"] = statistics.get(
            "frost_resistance", {}
        ).get("effective")
        rating_template = RatingModel().model_dump()

        rating_template["value"] = statistics.get("melee_crit", {}).get("value")
        rating_template["rating"] = statistics.get("melee_crit", {}).get(
            "rating_normalized"
        )
        statistic_template["melee_crit"] = rating_template.copy()

        rating_template["value"] = statistics.get("ranged_crit", {}).get("value")
        rating_template["rating"] = statistics.get("ranged_crit", {}).get(
            "rating_normalized"
        )
        statistic_template["ranged_crit"] = rating_template.copy()

        rating_template["value"] = statistics.get("spell_crit", {}).get("value")
        rating_template["rating"] = statistics.get("spell_crit", {}).get(
            "rating_normalized"
        )
        statistic_template["spell_crit"] = rating_template.copy()

        rating_template["value"] = statistics.get("melee_haste", {}).get("value")
        rating_template["rating"] = statistics.get("melee_haste", {}).get(
            "rating_normalized"
        )
        statistic_template["melee_haste"] = rating_template.copy()

        rating_template["value"] = statistics.get("ranged_haste", {}).get("value")
        rating_template["rating"] = statistics.get("ranged_haste", {}).get(
            "rating_normalized"
        )
        statistic_template["ranged_haste"] = rating_template.copy()

        rating_template["value"] = statistics.get("spell_haste", {}).get("value")
        rating_template["rating"] = statistics.get("spell_haste", {}).get(
            "rating_normalized"
        )
        statistic_template["spell_haste"] = rating_template.copy()

        rating_template["value"] = statistics.get("mastery", {}).get("value")
        rating_template["rating"] = statistics.get("mastery", {}).get(
            "rating_normalized"
        )
        statistic_template["mastery"] = rating_template.copy()

        rating_template["value"] = statistics.get("dodge", {}).get("value")
        rating_template["rating"] = statistics.get("dodge", {}).get("rating_normalized")
        statistic_template["dodge"] = rating_template.copy()

        rating_template["value"] = statistics.get("block", {}).get("value")
        rating_template["rating"] = statistics.get("block", {}).get("rating_normalized")
        statistic_template["block"] = rating_template.copy()

        rating_template["value"] = statistics.get("parry", {}).get("value")
        rating_template["rating"] = statistics.get("parry", {}).get("rating_normalized")
        statistic_template["parry"] = rating_template.copy()

        return statistic_template


class GuildParser(BlizzardParser):
    def __init__(
        self,
        guild: str,
        realm: str,
        namespace: str = None,
        region: str = "eu",
        version: str = "mop",
        token=None,
    ):
        super().__init__(namespace, region, version, token)
        self.guild = guild.replace(" ", "-")
        self.realm = realm = realm.replace(" ", "-")
        self.base_url = "https://REGION.api.blizzard.com/data/wow/guild/REALM/GUILDNAME?namespace=profile-NAMESPACE-REGION&locale=en_GB&access_token="

    def get_base_url(self, url_type=""):
        return (
            super()
            .get_base_url(url_type)
            .replace("GUILDNAME", self.guild.lower())
            .replace("REALM", self.realm.lower())
            .replace("NAMESPACE", self.namespace.lower())
            .replace("REGION", self.region.lower())
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
        guild_template["region"] = self.region.lower()
        guild_template["version"] = self.version.lower()

        return guild_template


class IconParser(BlizzardParser):
    def __init__(
        self,
        id: str,
        media_type: str,
        namespace: str = None,
        token=None,
    ):
        super().__init__(namespace, token)
        self.id = str(id)
        self.media_type = media_type
        self.base_url = "https://us.api.blizzard.com/data/wow/media/MEDIATYPE/MEDIAID?namespace=NAMESPACE&locale=en_GB&access_token="

    def get_base_url(self, url_type=""):
        return (
            super()
            .get_base_url(url_type)
            .replace("MEDIATYPE", self.media_type.lower())
            .replace("MEDIAID", self.id)
            .replace("NAMESPACE", self.namespace.lower())
        )

    def get_icon(self):
        icon = requests.get(
            self.get_base_url(),
            headers=self.headers,
        ).json()

        icon_template = IconModel().model_dump()
        icon_template["id"] = icon["id"]
        try:
            if icon.get("results"):
                icon_template["icon"] = icon["results"][0]["data"]["assets"][0]["value"]
            else:
                icon_template["icon"] = icon["assets"][0]["value"]
            icon_template["icon"] = icon_template["icon"].replace("classic_", "")
        except KeyError:
            icon_template["icon"] = None

        return icon_template


class ItemParser(BlizzardParser):
    def __init__(self, namespace=None, region="eu", version="mop", token=None):
        super().__init__(namespace, region, version, token)
        self.base_url = "https://REGION.api.blizzard.com/data/wow/item/ITEMID?namespace=static-NAMESPACE-REGION&locale=en_GB&access_token="

    def get_base_url(self, url_type=""):
        return (
            super()
            .get_base_url(url_type)
            .replace("NAMESPACE", self.namespace.lower())
            .replace("REGION", self.region.lower())
        )

    def get_item(self, id: int):
        if items.get(id, {}).get(self.version):
            if items[id][self.version]["slot"]["name"] == "item":
                return items[id][self.version]
            return self.parse_item(items[id][self.version])
        item: dict = requests.get(
            self.get_base_url().replace("ITEMID", str(id)),
            headers=self.headers,
        ).json()
        if item.get("code") == 404:
            return "Error 404"
        item["slot"] = {
            "name": self.match_slot(
                item["inventory_type"]["name"].replace("-", "_").lower()
            )
        }

        item["item"] = item["preview_item"]["item"]

        if not items.get(item["id"]):
            items[item["id"]] = {}

        items[item["id"]][self.version] = item.copy()
        new_dict = dict(sorted(items.items()))
        with open("src/helper/items.py", "w") as f:
            f.write(f"items = {str(new_dict)}")

        if item["slot"]["name"] == "item":
            iconparser = IconParser(
                item["item"]["id"],
                "item",
                namespace=get_namespace(item["item"]["key"]["href"]) or self.namespace,
            )
            icon = iconparser.get_icon()
            return {
                "name": item["name"],
                "id": item["id"],
                "icon": icon["icon"],
                "quality": item["quality"]["name"],
                "inventory_type": item["inventory_type"]["name"],
            }
        return self.parse_item(item)

    def parse_item(
        self,
        item,
    ) -> ItemModel:
        affixes = requests.get(
            "https://raw.githubusercontent.com/fuantomu/envy-armory/main/affix.json"
        ).json()
        item["link"] = ""
        slot_name = item["slot"]["name"].lower().replace(" ", "_")
        if not slotNames[slot_name] in ignore_enchant:
            if item.get("enchantments"):

                if any(
                    enchant["enchantment_slot"]["id"] in [0, 7, 8, 9]
                    for enchant in item["enchantments"]
                ):
                    item["link"] += "&ench="

                for enchant in item["enchantments"]:
                    if enchant["enchantment_slot"]["id"] == 5:
                        continue
                    if (
                        not enchantments.get(enchant["enchantment_id"])
                        or self.version
                        not in enchantments[enchant["enchantment_id"]].keys()
                    ):
                        print(f"Enchant {enchant} is missing")
                        save_enchant(enchant, self.version)

                filtered = [
                    enchantments[enchant][self.version]
                    for enchant in enchantments
                    if enchantments[enchant].get(self.version)
                    and any(
                        enchantments[enchant][self.version]["id"]
                        == item_enchant["enchantment_id"]
                        and item_enchant["enchantment_slot"]["id"] in [0, 7, 8, 9]
                        for item_enchant in item["enchantments"]
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
                    [
                        str(_item["item"]["id"])
                        for _item in item["set"]["items"]
                        if _item.get("is_equipped")
                    ]
                )

            if item.get("upgrade_id"):
                item["link"] += "&upgd="
                if item["upgrade_id"] == 446:
                    item["link"] += "1"
                elif item["upgrade_id"] == 447:
                    item["link"] += "2"
                else:
                    item["link"] += "0"

            if len(item["link"]) > 0:
                item["link"] = item["link"][1:]

        iconparser = IconParser(
            item["item"]["id"],
            "item",
            namespace=get_namespace(item["item"]["key"]["href"]) or self.namespace,
        )
        icon = iconparser.get_icon()

        item_model = ItemModel().model_dump()
        item_model["id"] = item["item"]["id"]
        item_model["name"] = item["name"]
        item_model["slot"] = item["slot"]["name"]
        item_model["quality"] = item["quality"]["name"]
        item_model["wowhead_link"] = item["link"]
        item_model["icon"] = icon["icon"]
        item_model["inventory_type"] = item["inventory_type"]["name"]
        item_model["enchantment"] = None
        if item.get("enchants"):
            item_model["enchantment"] = "##".join(
                [enchant["display_string"] for enchant in item["enchants"]]
            )
        item_model["version"] = self.version.lower()

        return item_model

    def match_slot(self, inventory_type):
        match inventory_type:
            case "two_hand" | "one_hand":
                return "main_hand"
            case "off hand":
                return "off_hand"
            case "non_equippable":
                return "item"
            case "trinket":
                return "trinket_1"
            case "shoulder":
                return "shoulders"
            case "finger":
                return "ring_1"
            case _:
                return inventory_type


def find_glyph(glyph, version, player_class):
    print(f"Trying to extract {glyph} from wowhead/{version}")
    wowhead_url = f"https://www.wowhead.com/{version}/"

    import re

    response = requests.get(
        f'{wowhead_url}search?q={glyph['name'].replace(" ", "+")}#glyphs'
    )

    found = re.search(
        r"WH\.SearchPage\.showTopResults\s*\(\s*(\[\s*[\s\S]*?\s*\])\s*\);",
        response.text,
    )

    if found:
        array_text = found.group(1)
        array_text = array_text.replace(r"\/", "/")

        try:
            data = json.loads(array_text)
            for obj in data:
                print(obj)
                if (
                    obj["type"] == 6
                    and obj["lvjson"]["cat"] in [-13, 0]
                    and obj["lvjson"]["name"] == glyph["name"]
                    and obj["lvjson"].get("chrclass", class_enum[player_class])
                    == class_enum[player_class]
                ):
                    if not glyphs.get(glyph["id"]):
                        glyphs[glyph["id"]] = {}
                    glyphs[glyph["id"]][version] = {
                        "name": glyph["name"],
                        "id": obj["typeId"],
                        "icon": None,
                        "type": None,
                    }
                    response = requests.get(f'{wowhead_url}spell={obj["typeId"]}')
                    found = re.search(r"Icon\.create\((.*?)\)", response.text)
                    if found:
                        icon_text = found.group(1)
                        icon_text = (
                            icon_text.replace(" ", "").replace('"', "").split(",")
                        )
                        icon_text = icon_text[0].replace("classic_", "")
                        glyphs[glyph["id"]][version]["icon"] = icon_text
                        break

        except json.JSONDecodeError as e:
            print("JSON parsing error:", e)

    found = re.search(
        r"Glyph type: (\w+)",
        response.text,
    )
    if found:
        glyph_type = found.group(1)
        glyphs[glyph["id"]][version]["type"] = glyph_type

    new_dict = dict(sorted(glyphs.items()))
    with open("src/helper/glyphs.py", "w") as f:
        f.write(f"glyphs = {str(new_dict)}")


def save_talent(talent, version):
    print(f"Trying to extract {talent} from wowhead/{version}")
    wowhead_url = f"https://www.wowhead.com/{version}/"

    import re

    if not talents.get(talent["id"]):
        talents[talent["id"]] = {}

    talents[talent["id"]][version] = {
        "id": talent["id"],
        "name": talent["name"],
        "icon": None,
    }

    response = requests.get(f'{wowhead_url}spell={talent["id"]}')
    found = re.search(r"Icon\.create\((.*?)\)", response.text)
    if found:
        icon_text = found.group(1)
        icon_text = icon_text.replace(" ", "").replace('"', "").split(",")
        talents[talent["id"]][version]["icon"] = icon_text[0]

    new_dict = dict(sorted(talents.items()))
    with open("src/helper/talents.py", "w") as f:
        f.write(f"talents = {str(new_dict)}")


def save_enchant(enchant, version):

    if not enchantments.get(enchant["enchantment_id"]):
        enchantments[enchant["enchantment_id"]] = {}
    enchantments[enchant["enchantment_id"]][version] = {
        "id": enchant["enchantment_id"],
        "name": enchant.get("source_item", {})
        .get("name", enchant.get("spell", {}).get("name", "Unknown"))
        .replace("QA", ""),
        "display_string": enchant.get(
            "display_string", enchant.get("source_item", {}).get("name", "Unknown")
        ).replace("Enchanted ", ""),
    }

    new_dict = dict(sorted(enchantments.items()))
    with open("src/helper/enchantments.py", "w") as f:
        f.write(f"enchantments = {str(new_dict)}")


def get_namespace(link: str):
    namespace = link.split("?namespace=")[1].replace("-eu", "-us")
    return namespace


if __name__ == "__main__":
    load_dotenv(".env")
    load_dotenv(".env.local", override=True)
    # test = CharacterParser(
    #     "Feral",
    #     "Everlook",
    #     region="eu",
    #     version="mop",
    # )
    # print(test.get_character())
    # print(test.get_sorted_equipment())
    # print(test.get_talents())
    # test2 = CharacterParser("Zoo", "nazgrim", namespace="classic", region="us")
    # print(test2.get_talents())
    # test3 = CharacterParser(
    #     "Boj",
    #     "Dreamscythe",
    #     region="us",
    #     version="classic",
    # )
    # print(test3.get_character())
    # print(test3.get_sorted_equipment())
    # print(test3.get_talents())
    # print(test3.get_statistics())
    test4 = ItemParser(region="eu", version="mop")
    print(test4.get_item(76642))
