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
from src.models.item import EnchantmentModel, ItemModel
from src.models.specialization import GlyphModel, SpecializationModel
from src.helper.glyphs import glyphs
from src.helper.talents import talents
from src.helper.enchantments import enchantments
from src.helper.item_search import item_search
from src.helper.icons import icons

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
    "item": -1,
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
ignore_enchant = [-1, 3, 18]

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

SEARCH_LIMIT = 10


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
        self.base_search_url = "https://eu.api.blizzard.com/data/wow/search/"
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

        item_parser = ItemParser(
            "1.15.8_63631-classic1x" if self.version == "mop" else self.namespace,
            self.region,
            self.version,
        )
        for item in items:
            sortedEquipment[item["slot"]["name"].lower().replace(" ", "_")] = (
                item_parser.parse_item(item)
            )

        return sortedEquipment

    def get_talents(self, player_class: str = None):
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

        glyph_parser = GlyphParser(self.version, self.character_class or player_class)
        for index, specialization in enumerate(specs):
            for glyph in specializations["specialization_groups"][index].get(
                "glyphs", []
            ):
                specialization["glyphs"].append(
                    glyph_parser.fetch_search(glyph["name"], "glyph")[0]["id"]
                )
            specialization["spec_id"] = index
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
            current_spec["spec_id"] = len(specs)
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
        existing_icon = [
            icons[_icon][self.version]
            for _icon in icons
            if icons.get(_icon, {}).get(self.version)
            and (int(self.id) in icons[_icon][self.version])
        ]
        if existing_icon:
            return existing_icon
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

        if not icons.get(icon["id"]):
            icons[icon["id"]] = {}

        icons[icon["id"]][self.version] = icon_template.copy()
        new_dict = dict(sorted(icons.items()))
        with open("src/helper/icons.py", "w") as f:
            f.write(f"icons = {str(new_dict)}")

        return icon_template


class ItemParser(BlizzardParser):
    def __init__(self, namespace=None, region="eu", version="mop", token=None):
        super().__init__(namespace, region, version, token)
        self.base_url = "https://REGION.api.blizzard.com/data/wow/item/ITEMID?namespace=static-NAMESPACE-REGION&locale=en_GB&access_token="
        self.base_search_url = "https://REGION.api.blizzard.com/data/wow/search/item?namespace=static-NAMESPACE-REGION&name.en_GB=SEARCH&orderby=id:desc&_page=1&inventory_type.type=ITEMTYPE&access_token="

    def get_base_url(self, url_type=""):
        return (
            super()
            .get_base_url(url_type)
            .replace("NAMESPACE", self.namespace.lower())
            .replace("REGION", self.region.lower())
        )

    def get_base_search_url(self):
        return self.base_search_url.replace(
            "NAMESPACE", self.namespace.lower()
        ).replace("REGION", self.region.lower())

    def fetch_search(self, search=None, id=None, slot=None):
        if search:
            print(
                f"Trying to fetch '{search}' from blizzard api/{self.get_base_search_url().replace('SEARCH', str(search)).replace('ITEMTYPE', self.get_slot_identifier(slot))}"
            )
            item: dict = requests.get(
                self.get_base_search_url()
                .replace("SEARCH", str(search))
                .replace("ITEMTYPE", self.get_slot_identifier(slot)),
                headers=self.headers,
            ).json()
        elif id:
            print(
                f"Trying to fetch '{id}' from blizzard api/{self.get_base_url().replace('ITEMID', str(id))}"
            )
            item: dict = requests.get(
                self.get_base_url().replace("ITEMID", str(id)),
                headers=self.headers,
            ).json()
            item["slot"] = {"name": self.match_slot(item["inventory_type"]["name"])}
            item["item"] = item["preview_item"]["item"]
        if item.get("code") == 404:
            return "Error 404"
        return self.parse_search(item["results"]) if search else [self.parse_item(item)]

    def parse_search(self, result: list[dict]):
        out = []
        for item in result[:SEARCH_LIMIT]:
            if item_search.get(item["data"]["id"], {}).get(self.version):
                out.append(item_search[item["data"]["id"]][self.version])
                continue
            base_item = ItemModel().model_dump()
            base_item["character_id"] = -1
            base_item["id"] = item["data"]["id"]
            base_item["name"] = item["data"]["name"]["en_GB"]
            slot = self.match_slot(item["data"]["inventory_type"]["name"]["en_GB"])
            base_item["slot"] = " ".join(
                [_slot.capitalize() for _slot in slot.split("_")]
            )
            if item.get("slot", {}).get("name"):
                if (
                    item.get("slot", {}).get("name")
                    not in ItemModel.model_json_schema()["properties"]["slot"]["enum"]
                ):
                    base_item["slot"] = " ".join(
                        [elem.capitalize() for elem in item["slot"]["name"].split("_")]
                    )
                else:
                    base_item["slot"] = item["slot"]["name"]
            base_item["quality"] = (
                item["data"].get("quality", {}).get("name", {}).get("en_GB", {})
            )
            base_item["version"] = self.version
            if item["data"]["item_class"]["id"] == 3:
                base_item["inventory_type"] = "Gem"
            elif item["data"]["item_subclass"]["id"] == 6:
                base_item["inventory_type"] = "Enchant"
            else:
                base_item["inventory_type"] = item["data"]["inventory_type"]["name"][
                    "en_GB"
                ]
            icon_parser = IconParser(
                item["data"]["id"], "item", namespace=get_namespace(item["key"]["href"])
            )
            base_item["icon"] = icon_parser.get_icon().get("icon")
            out.append(base_item)

            if not item_search.get(base_item["id"]):
                item_search[base_item["id"]] = {}

            item_search[base_item["id"]][self.version] = base_item

        print("Writing search to file")
        new_dict = dict(sorted(item_search.items()))
        with open("src/helper/item_search.py", "w") as f:
            f.write(f"item_search = {str(new_dict)}")

        return out

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
                    or (
                        enchant["enchantment_slot"]["id"] == 1
                        and self.version == "classic"
                    )
                    for enchant in item["enchantments"]
                ):
                    item["link"] += "&ench="

                for enchant in item["enchantments"]:
                    if enchant["enchantment_slot"]["id"] == 5:
                        continue
                    elif enchant["enchantment_slot"]["id"] == 7:
                        key = None
                        try:
                            key = enchant.get("spell", {}).get("spell", {}).get("id")
                        except Exception:
                            key = enchant.get("spell", {}).get("id")
                    else:
                        if not enchant.get("source_item", {}).get("id"):
                            key = enchant.get("enchantment_id")
                        else:
                            key = enchant.get("source_item")["id"]
                    if (
                        not enchantments.get(key)
                        or self.version not in enchantments[key].keys()
                    ):
                        print(f"Enchant {enchant} is missing")
                        save_enchant(enchant, self.version, slot_name)

                filtered = []
                added_ids = []
                for enchant in enchantments:
                    if enchantments[enchant].get(self.version) and any(
                        enchantments[enchant][self.version]["id"]
                        == item_enchant["enchantment_id"]
                        and (
                            item_enchant["enchantment_slot"]["id"] in [0, 7, 8, 9]
                            or (
                                item_enchant["enchantment_slot"]["id"] == 1
                                and self.version == "classic"
                            )
                        )
                        and enchantments[enchant][self.version]["id"] not in added_ids
                        for item_enchant in item["enchantments"]
                    ):
                        added_ids.append(enchantments[enchant][self.version]["id"])
                        filtered.append(enchantments[enchant][self.version])
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
        if (
            item["slot"]["name"]
            not in ItemModel.model_json_schema()["properties"]["slot"]["enum"]
        ):
            item_model["slot"] = " ".join(
                [elem.capitalize() for elem in item["slot"]["name"].split("_")]
            )
        else:
            item_model["slot"] = item["slot"]["name"]

        item_model["quality"] = item["quality"]["name"]
        item_model["wowhead_link"] = item["link"]
        item_model["icon"] = icon["icon"]
        item_model["inventory_type"] = item["inventory_type"]["name"]
        item_model["enchantment"] = ""
        if item.get("enchants"):
            for idx, enchant in enumerate(item["enchants"]):
                if (
                    enchant.get("display_string", enchant["name"])
                    and enchant.get("display_string", enchant["name"])
                    not in item_model["enchantment"]
                ):
                    item_model["enchantment"] += enchant.get(
                        "display_string", enchant["name"]
                    )
                    if idx < len(item["enchants"]):
                        item_model["enchantment"] += "##"
        item_model["version"] = self.version.lower()

        return item_model

    def match_slot(self, inventory_type: str):
        match inventory_type.lower().replace("-", "_"):
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

    def get_slot_identifier(self, inventory_slot: str):
        match inventory_slot:
            case "main_hand":
                if self.version in ["mop", "wod"]:
                    return "WEAPON||TWOHWEAPON||WEAPONMAINHAND||RANGEDRIGHT||RANGED"
                else:
                    return "WEAPON||TWOHWEAPON||WEAPONMAINHAND"
            case "shoulders":
                return "SHOULDER"
            case "back":
                return "CLOAK"
            case "shirt":
                return "BODY"
            case "hands":
                return "HAND"
            case "ring_1" | "ring_2":
                return "FINGER"
            case "trinket_1" | "trinket_1":
                return "TRINKET"
            case "off_hand":
                return "SHIELD||HOLDABLE||WEAPONOFFHAND"
            case "ranged":
                return "RANGEDRIGHT||RANGED"
            case _:
                return inventory_slot.upper()


class WowheadParser:

    def __init__(self, version: str):
        self.game_version = version
        match version:
            case "mop":
                self.wowhead_version = "mop-classic"
            case _:
                self.wowhead_version = version
        self.url = f"https://www.wowhead.com/{self.wowhead_version}/"

    def fetch_id(self, id, search_type: str):
        print(
            f"Trying to fetch '{id}' from wowhead/{self.wowhead_version}/{search_type}"
        )
        response = requests.get(f"{self.url}/{search_type}={id}")
        return response

    def fetch_search(self, search, search_type: str | None = None):
        existing_glyph = [
            glyphs[_glyph][self.game_version]
            for _glyph in glyphs
            if glyphs.get(_glyph, {}).get(self.game_version)
            and (search in glyphs[_glyph][self.game_version].get("name"))
        ]
        if existing_glyph:
            return existing_glyph

        print(f"Trying to fetch '{search}' from wowhead/{self.wowhead_version}")
        import re

        response = requests.get(f'{self.url}search?q={search.replace(" ", "+")}')

        found = re.search(
            r"WH\.SearchPage\.showTopResults\s*\(\s*(\[\s*[\s\S]*?\s*\])\s*\);",
            response.text,
        )

        if found:
            array_text = found.group(1)
            array_text = array_text.replace(r"\/", "/")

            try:
                data = json.loads(array_text)
                if search_type:
                    search_id = -1
                    match search_type:
                        case "npc":
                            search_id = 1
                        case "item":
                            search_id = 3
                        case "spell" | "glyph":
                            search_id = 6
                        case _:
                            search_id = 0
                    filtered_data = [
                        self.parse_result(element, search_type)
                        for element in data
                        if element.get("type") == search_id
                    ]
                    return filtered_data
                return data
            except json.JSONDecodeError as e:
                print("JSON parsing error:", e)
                return []

        return []

    def parse_result(self, result, result_type):
        match result_type:
            case _:
                return result


class GlyphParser(WowheadParser):
    def __init__(self, version, player_class):
        super().__init__(version)
        self.character_class = player_class

    def fetch_glyph(self, glyph_id: str):
        glyph = GlyphModel().model_dump()
        glyph["id"] = int(glyph_id)
        glyph["name"] = "Unknown"
        glyph["character_class"] = self.character_class

        response = requests.get(f"{self.url}spell={glyph_id}")

        import re

        found = re.findall(
            r"WH\.Gatherer\.addData\(\d+,\s\d+,\s(.+)\);",
            response.text,
        )

        if found:
            found: list[dict] = [json.loads(element) for element in found]
            for obj in found:
                if obj.get(str(glyph_id)):
                    glyph["name"] = obj[str(glyph_id)].get("name_enus", "Unknown")
                    glyph["icon"] = (
                        obj[str(glyph_id)]
                        .get("icon", "Unknown")
                        .replace("classic_", "")
                    )
                    break

        found = re.search(
            r"Glyph type: (\w+)",
            response.text,
        )
        if found:
            glyph_type = found.group(1)
            glyph["type"] = glyph_type

        return glyph

    def find_glyph(self, glyph_id: str):
        existing_glyph = [
            glyphs[_glyph][self.game_version]
            for _glyph in glyphs
            if glyphs[_glyph].get(self.game_version)
            and (glyphs[_glyph][self.game_version].get("id") == glyph_id)
        ]
        if existing_glyph:
            return existing_glyph

        glyph = self.fetch_glyph(glyph_id)
        glyph["character_class"] = self.character_class

        if not glyphs.get(glyph["id"]):
            glyphs[glyph["id"]] = {}
        glyphs[glyph["id"]][self.game_version] = glyph

        new_dict = dict(sorted(glyphs.items()))
        print(f"Writing glyph to file {glyph}")
        with open("src/helper/glyphs.py", "w") as f:
            f.write(f"glyphs = {str(new_dict)}")

        return glyphs[glyph["id"]][self.game_version]

    def get_class_name(self, class_name: str):
        match class_name:
            case "Deathknight":
                return "death-knight"
            case _:
                return class_name.lower()

    def get_glyph_type(self, glyph_type: int):
        match glyph_type:
            case 0:
                return "Prime"
            case 1:
                return "Major"
            case 2:
                return "Minor"
            case _:
                return "Unknown"

    def find_class_glyphs(self, class_name: str):
        response = requests.get(
            f"{self.url}spells/glyphs/{self.get_class_name(class_name)}"
        )

        import re

        glyph_icons = re.findall(
            r"WH\.Gatherer\.addData\(\d+,\s\d+,\s(.+)\);",
            response.text,
        )
        if glyph_icons:
            glyph_icons: list[dict] = json.loads(glyph_icons[0])

        found = re.findall(
            r"var\slistviewspells\s\=\s(\[.*\])",
            response.text,
        )

        result = []

        if found:
            found: list[dict] = json.loads(
                found[0]
                .replace("quality", '"quality"')
                .replace("popularity", '"popularity"')
            )
            for item in found:
                glyph = GlyphModel().model_dump()
                glyph["id"] = int(item.get("id"))
                glyph["name"] = item.get("name", "Unknown")
                glyph["icon"] = (
                    glyph_icons.get(str(item["id"]), {})
                    .get("icon", "")
                    .replace("classic_", "")
                )
                glyph["type"] = self.get_glyph_type(item["glyphtype"])
                glyph["character_class"] = class_name
                if not glyphs.get(glyph["id"]):
                    glyphs[glyph["id"]] = {}
                glyphs[glyph["id"]][self.game_version] = glyph
                result.append(glyph)

        new_dict = dict(sorted(glyphs.items()))
        print(f"Writing glyph to file {glyph}")
        with open("src/helper/glyphs.py", "w") as f:
            f.write(f"glyphs = {str(new_dict)}")

        return result

    def parse_result(self, result, result_type):
        match result_type:
            case "glyph":
                return self.fetch_glyph(result["typeId"])
            case _:
                return self.parse_result(result, result_type)


class EnchantmentParser(BlizzardParser):
    def __init__(self, namespace=None, region="eu", version="mop", token=None):
        super().__init__(namespace, region, version, token)
        self.base_url = "https://REGION.api.blizzard.com/data/wow/item/ITEMID?namespace=static-NAMESPACE-REGION&locale=en_GB&access_token="
        self.base_search_url = "https://REGION.api.blizzard.com/data/wow/search/item?namespace=static-NAMESPACE-REGION&name.en_GB=SEARCH&orderby=id:desc&_page=1&item_class.id=ITEMCLASS&access_token="

    def get_base_url(self, url_type=""):
        return (
            super()
            .get_base_url(url_type)
            .replace("NAMESPACE", self.namespace.lower())
            .replace("REGION", self.region.lower())
        )

    def get_base_search_url(self):
        return self.base_search_url.replace(
            "NAMESPACE", self.namespace.lower()
        ).replace("REGION", self.region.lower())

    def fetch_gem(self, search=None, id=None):
        if search:
            print(
                f"Trying to fetch gem '{search}' from blizzard api/{self.get_base_search_url().replace('SEARCH', str(search)).replace('ITEMCLASS', "3")}"
            )
            gem: dict = requests.get(
                self.get_base_search_url()
                .replace("SEARCH", str(search))
                .replace("ITEMCLASS", "3"),
                headers=self.headers,
            ).json()
        elif id:
            print(
                f"Trying to fetch gem '{id}' from blizzard api/{self.get_base_url().replace('ITEMID', str(id))}"
            )
            gem: dict = requests.get(
                self.get_base_url().replace("ITEMID", str(id)),
                headers=self.headers,
            ).json()
        if gem.get("code") == 404:
            return "Error 404"
        return self.parse_search(gem["results"]) if search else [self.parse_gem(gem)]

    def fetch_enchant(self, search=None, id=None):
        if search:
            print(
                f"Trying to fetch enchant '{search}' from blizzard api/{self.get_base_search_url().replace('SEARCH', str(search)).replace('ITEMCLASS', "0")}"
            )
            enchant: dict = requests.get(
                self.get_base_search_url()
                .replace("SEARCH", str(search))
                .replace("ITEMCLASS", "0"),
                headers=self.headers,
            ).json()
        elif id:
            print(
                f"Trying to fetch enchant '{id}' from blizzard api/{self.get_base_url().replace('ITEMID', str(id))}"
            )
            enchant: dict = requests.get(
                self.get_base_url().replace("ITEMID", str(id)),
                headers=self.headers,
            ).json()
        if enchant.get("code") == 404:
            return "Error 404"
        return (
            self.parse_search(enchant["results"], search_type="Enchant")
            if search
            else [self.parse_enchant(enchant)]
        )

    def parse_search(self, result: list[dict], search_type="Gem"):
        item_parser = ItemParser(self.namespace, self.region, self.version)
        wowhead_parser = WowheadParser(self.version)
        out = []
        import re

        for enchantment in item_parser.parse_search(result):
            if enchantments.get(enchantment["id"], {}).get(self.version):
                out.append(enchantments[enchantment["id"]][self.version])
                continue
            if search_type == "Enchant" and "Enchant" not in enchantment.get(
                "name", ""
            ):
                continue
            if not enchantments.get(enchantment["id"]):
                enchantments[enchantment["id"]] = {}

            temp_enchantment: EnchantmentModel = EnchantmentModel().model_dump()
            temp_enchantment["id"] = int(enchantment["id"])
            temp_enchantment["name"] = (
                enchantment.get("name").replace("QA", "").replace("Enchant Weapon", "")
            )
            temp_enchantment["display_string"] = temp_enchantment["name"]
            temp_enchantment["source_id"] = enchantment["id"]
            temp_enchantment["type"] = 2
            temp_enchantment["slot"] = "Other"

            response = wowhead_parser.fetch_id(enchantment["id"], "item")
            if search_type == "Gem":
                found = re.findall(
                    r"\+<!--gem\d+-->\s*(\d+)\s*<!---->\s*([A-Za-z\s'-]+)(?:\s*and\s*\+<!--gem\d+-->\s*(\d+)\s*<!---->\s*([A-Za-z\s'-]+))?",
                    response.text,
                )

                if len(found) > 1:
                    boni = [item.strip() for item in list(found[0]) if item != ""]
                    boni.extend([item.strip() for item in list(found[1]) if item != ""])
                    temp_enchantment["display_string"] = f'+{" ".join(boni)}'
            elif search_type == "Enchant":
                found = re.search(
                    rf'<a href="\/{wowhead_parser.wowhead_version}\/spell=(\d+)\/enchant-',
                    response.text,
                )
                if found:
                    response = wowhead_parser.fetch_id(found.group(1), "spell")
                    found = re.search(
                        r'<span class="q2">[^<]+</span>\s*&nbsp;\((\d+)\)',
                        response.text,
                    )
                    if found:
                        temp_enchantment["id"] = found.group(1)

            out.append(temp_enchantment)
            enchantments[enchantment["id"]][self.version] = temp_enchantment

        new_dict = dict(sorted(enchantments.items()))
        with open("src/helper/enchantments.py", "w") as f:
            f.write(f"enchantments = {str(new_dict)}")
        return out

    def parse_enchant(self, enchant: dict):
        temp_enchant: EnchantmentModel = EnchantmentModel().model_dump()
        temp_enchant["name"] = enchant.get("name")
        temp_enchant["source_id"] = enchant["id"]
        temp_enchant["type"] = 2
        temp_enchant["slot"] = "Other"

        wowhead_parser = WowheadParser(self.version)
        response = wowhead_parser.fetch_id(enchant["id"], "item")

        import re

        found = re.search(
            rf'<a href="\/{wowhead_parser.wowhead_version}\/spell=(\d+)\/enchant-',
            response.text,
        )
        if found:
            response = wowhead_parser.fetch_id(found.group(1), "spell")
            found = re.search(
                r'<span class="q2">[^<]+</span>\s*&nbsp;\((\d+)\)',
                response.text,
            )
            if found:
                temp_enchant["id"] = int(found.group(1))
        if not enchantments.get(enchant["id"]):
            enchantments[enchant["id"]] = {}
        enchantments[enchant["id"]][self.version] = temp_enchant

        new_dict = dict(sorted(enchantments.items()))
        with open("src/helper/enchantments.py", "w") as f:
            f.write(f"enchantments = {str(new_dict)}")
        return temp_enchant

    def parse_gem(self, gem: dict):
        if not enchantments.get(gem["id"]):
            enchantments[gem["id"]] = {}
        temp_gem: EnchantmentModel = EnchantmentModel().model_dump()
        temp_gem["id"] = int(gem["id"])
        temp_gem["name"] = gem.get("name")
        temp_gem["source_id"] = gem["id"]
        temp_gem["type"] = 2
        temp_gem["slot"] = "Other"

        wowhead_parser = WowheadParser(self.version)
        response = wowhead_parser.fetch_id(gem["id"], "item")

        import re

        found = re.findall(
            r"\+<!--gem\d+-->\s*(\d+)\s*<!---->\s*([A-Za-z\s'-]+)(?:\s*and\s*\+<!--gem\d+-->\s*(\d+)\s*<!---->\s*([A-Za-z\s'-]+))?",
            response.text,
        )

        if len(found) > 1:
            boni = [item.strip() for item in list(found[0]) if item != ""]
            boni.extend([item.strip() for item in list(found[1]) if item != ""])
            temp_gem["display_string"] = f'+{" ".join(boni)}'

        enchantments[gem["id"]][self.version] = temp_gem

        new_dict = dict(sorted(enchantments.items()))
        with open("src/helper/enchantments.py", "w") as f:
            f.write(f"enchantments = {str(new_dict)}")
        return temp_gem


def save_talent(talent, version):
    print(f"Trying to extract {talent} from wowhead/{version}")
    wowhead_parser = WowheadParser(version)

    import re

    if not talents.get(talent["id"]):
        talents[talent["id"]] = {}

    talents[talent["id"]][version] = {
        "id": talent["id"],
        "name": talent["name"],
        "icon": None,
    }

    response = requests.get(f'{wowhead_parser.url}spell={talent["id"]}')
    found = re.search(r"Icon\.create\((.*?)\)", response.text)
    if found:
        icon_text = found.group(1)
        icon_text = icon_text.replace(" ", "").replace('"', "").split(",")
        talents[talent["id"]][version]["icon"] = icon_text[0]

    new_dict = dict(sorted(talents.items()))
    with open("src/helper/talents.py", "w") as f:
        f.write(f"talents = {str(new_dict)}")


def save_enchant(enchant, version: str, slot: str):
    if enchant.get("enchantment_slot", {}).get("id") == 7:
        try:
            key = enchant["spell"]["spell"]["id"]
        except Exception:
            key = enchant["spell"]["id"]
    else:
        try:
            key = enchant["source_item"]["id"]
        except Exception:
            key = enchant["enchantment_id"]
    if not enchantments.get(key):
        enchantments[key] = {}
    enchantments[key][version] = {
        "id": int(enchant["enchantment_id"]),
        "name": enchant.get("source_item", {})
        .get(
            "name",
            enchant.get("spell", {}).get(
                "name", enchant.get("spell", {}).get("spell", {}).get("name", "Unknown")
            ),
        )
        .replace("QA", ""),
        "display_string": enchant.get(
            "display_string", enchant.get("source_item", {}).get("name", "Unknown")
        ).replace("Enchanted ", ""),
        "source_id": enchant.get("source_item", {}).get("id", None),
        "type": enchant.get("enchantment_slot", {}).get("id", None),
        "slot": (
            slot
            if enchant.get("enchantment_slot", {}).get("id", None) in [0, 6, 7, 8, 9]
            else "Other"
        ),
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
    #     "Heavenstamp",
    #     "Everlook",
    #     region="eu",
    #     version="mop",
    # )
    # print(test.get_character())
    # print(test.get_sorted_equipment())
    # print(test.get_talents(player_class="Druid"))
    # test2 = CharacterParser("Zoo", "nazgrim", namespace="classic", region="us")
    # print(test2.get_talents())
    test3 = CharacterParser(
        "Xippm",
        "Crusader Strike",
        region="us",
        version="classic",
    )
    # print(test3.get_character())
    print(test3.get_sorted_equipment())
    # print(test3.get_talents())
    # print(test3.get_statistics())
    # test4 = ItemParser(region="eu", version="mop")
    # print(test4.get_item(76642))
    # find_glyph(146959, "mop", "Paladin")
    # test5 = ItemParser(version="mop")
    # out = test5.fetch_search("Thunderfury")
    # print(out)
    # test6 = EnchantmentParser(version="mop")
    # out = test6.fetch_gem(search="Tiger Opal")
    # print(out)
    # out2 = test6.fetch_enchant(search="dancing steel")
    # print(out2)
