import json
from dotenv import load_dotenv
import requests
from os import getenv
from src.models.character import CharacterEquipmentModel, CharacterModel
from src.models.guild import GuildModel
from src.models.icon import IconModel
from src.models.item import ItemModel
from src.models.specialization import SpecializationModel
from src.helper.glyphs import glyphs
from src.helper.talents import talents

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
        if character.get("detail"):
            return {"error": character["detail"]}
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
            slot_name = item["slot"]["name"].lower().replace(" ", "_")
            if not slotNames[slot_name] in ignore_enchant:
                if item.get("enchantments"):

                    if item["enchantments"][0]["enchantment_slot"]["id"] == 0:
                        item["link"] += "&ench="

                    filtered = [
                        enchant
                        for enchant in enchants[str(slotNames[slot_name])]
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

            iconparser = IconParser(item["item"]["id"], "item")
            icon = iconparser.get_icon()

            item_model = ItemModel().model_dump()
            item_model["id"] = item["item"]["id"]
            item_model["name"] = item["name"]
            item_model["slot"] = item["slot"]["name"]
            item_model["quality"] = item["quality"]["name"]
            item_model["wowhead_link"] = item["link"]
            item_model["icon"] = icon["icon"]
            sortedEquipment[slot_name] = item_model

        return sortedEquipment

    def get_talents(self):
        specializations = requests.get(
            self.get_base_url("specializations"),
            headers=self.headers,
        ).json()
        specs = []

        for specialization in specializations.get("specializations", []):
            current_spec = SpecializationModel().model_dump()
            current_spec["name"] = specialization["specialization_name"]
            current_spec["talents"] = []
            for talent in specialization.get("talents", []):
                if not talents.get(
                    talent["spell_tooltip"]["spell"]["id"]
                ) or not talents.get(talent["spell_tooltip"]["spell"]["id"], {}).get(
                    "icon"
                ):
                    print(f"Talent {talent['spell_tooltip']['spell']} is missing")
                    save_talent(talent["spell_tooltip"]["spell"])
                current_spec["talents"].append(talent["spell_tooltip"]["spell"]["id"])
            specs.append(current_spec)

        for index, specialization in enumerate(specs):
            for glyph in specializations["specialization_groups"][index].get(
                "glyphs", []
            ):
                if not glyphs.get(glyph["id"]) or not glyphs.get(glyph["id"], {}).get(
                    "icon"
                ):
                    print(f"Glyph {glyph} is missing")
                    find_glyph(glyph)
                specialization["glyphs"].append(glyphs[glyph["id"]]["id"])
            specialization["active"] = specializations["specialization_groups"][index][
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


class IconParser(BlizzardParser):
    def __init__(
        self,
        id: str,
        media_type: str,
        token=None,
    ):
        super().__init__(token)
        self.id = str(id)
        self.media_type = media_type
        self.base_url = "https://eu.api.blizzard.com/data/wow/media/MEDIATYPE/MEDIAID?namespace=static-classic-eu&locale=en_GB&access_token="

    def get_base_url(self, url_type=""):
        return (
            super()
            .get_base_url(url_type)
            .replace("MEDIATYPE", self.media_type.lower())
            .replace("MEDIAID", self.id)
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
        except KeyError:
            icon_template["icon"] = None

        return icon_template


def find_glyph(glyph):
    wowhead_url = "https://www.wowhead.com/mop-classic/"

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
                if obj["type"] == 6 and obj["lvjson"]["cat"] == -13:
                    print(obj)
                    glyphs[glyph["id"]] = {
                        "name": glyph["name"],
                        "id": obj["typeId"],
                        "icon": None,
                    }
                    response = requests.get(f'{wowhead_url}spell={obj["typeId"]}')
                    found = re.search(r"Icon\.create\((.*?)\)", response.text)
                    if found:
                        icon_text = found.group(1)
                        icon_text = (
                            icon_text.replace(" ", "").replace('"', "").split(",")
                        )
                        glyphs[glyph["id"]]["icon"] = icon_text[0]

        except json.JSONDecodeError as e:
            print("JSON parsing error:", e)

    new_dict = dict(sorted(glyphs.items()))
    with open("src/helper/glyphs.py", "w") as f:
        f.write(f"glyphs = {str(new_dict)}")


def save_talent(talent):
    wowhead_url = "https://www.wowhead.com/mop-classic/"

    import re

    talents[talent["id"]] = {
        "id": talent["id"],
        "name": talent["name"],
        "icon": None,
    }

    response = requests.get(f'{wowhead_url}spell={talent["id"]}')
    found = re.search(r"Icon\.create\((.*?)\)", response.text)
    if found:
        icon_text = found.group(1)
        icon_text = icon_text.replace(" ", "").replace('"', "").split(",")
        talents[talent["id"]]["icon"] = icon_text[0]

    new_dict = dict(sorted(talents.items()))
    with open("src/helper/talents.py", "w") as f:
        f.write(f"talents = {str(new_dict)}")


if __name__ == "__main__":
    load_dotenv(".env")
    load_dotenv(".env.local", override=True)
    test = CharacterParser("Heavenstamp", "Everlook")
    output = test.get_sorted_equipment()
    print(output)
