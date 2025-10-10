import json
from src.database.helper.blizzard_parser import CharacterParser, GuildParser
from src.database.tables.characteritem_table import CharacterItemTable
from src.database.tables.characterspec_table import CharacterSpecTable
from src.database.tables.characterstat_table import CharacterStatTable
from src.database.tables.guild_table import GuildTable
from src.database.tables.table import Table
from src.models.character import (
    CharacterEquipmentModel,
    CharacterParseModel,
    CharacterStatisticModel,
)
from src.models.item import ItemModel
from src.models.specialization import GlyphModel, SpecializationModel, TalentModel


class CharacterTable(Table):
    columns = {
        "id": {
            "value": "INTEGER UNIQUE NOT NULL",
        },
        "name": {"value": "varchar(16) NOT NULL", "default": "'Unknown'"},
        "region": {"value": "varchar(2)", "default": "'eu'"},
        "realm": {"value": "varchar(32)", "default": "'Dev'"},
        "version": {"value": "varchar(8)", "default": "'mop'"},
        "gender": {"value": "varchar(8)", "default": "'Male'"},
        "faction": {"value": "varchar(8)", "default": "'Alliance'"},
        "race": {"value": "varchar(16)", "default": "'Human'"},
        "character_class": {"value": "varchar(16)", "default": "'Adventurer'"},
        "active_spec": {"value": "varchar(16)", "default": "'Adventurer'"},
        "guild": {"value": "INTEGER REFERENCES guild(id)"},
        "level": {"value": "SMALLINT NOT NULL", "default": 1},
        "achievement_points": {"value": "INTEGER NOT NULL", "default": 0},
        "last_login_timestamp": {"value": "BIGINT NOT NULL", "default": 0},
        "average_item_level": {"value": "SMALLINT NOT NULL", "default": 0},
        "equipped_item_level": {"value": "SMALLINT NOT NULL", "default": 0},
        "active_title": {"value": "varchar(64)"},
        "PRIMARY KEY": {"value": "(id,version)", "default": ""},
    }

    def get(self, request: str | dict):
        self.logger.debug(f"Get {self.name}: {request}")
        if not request["value"]:
            if not request["version"]:
                return self.format_result(self.select("ALL"))
            return self.format_result(
                self.select("ALL", [("version", "=", request["version"])])
            )

        results = []
        selection = [
            (
                request["key"],
                "=",
                request["value"],
            ),
            ("version", "=", request["version"]),
        ]
        if request["key"] == "name":
            if request.get("realm"):
                selection.append(("realm", "=", request["realm"]))
            if request.get("region"):
                selection.append(("region", "=", request["region"]))
        selection.append("AND")
        results = self.format_result(self.select("ALL", selection))
        return results

    def delete_entry(self, request):
        self.logger.debug(f"DeleteEntry {self.name}: {request}")
        found_character = self.select(
            "id",
            [
                (request["key"], "=", request["value"]),
                ("version", "=", request["version"]),
                "AND",
            ],
        )
        if len(found_character) == 0:
            raise Exception(
                f"No character found for {request['key']} '{request['value']}' in '{request['version']}'"
            )

        CharacterItemTable.delete(
            self,
            [
                ("character_id", "=", request["value"]),
                ("version", "=", request["version"]),
                "AND",
            ],
            "characteritem",
        )
        CharacterSpecTable.delete(
            self,
            [
                ("id", "=", request["value"]),
                ("version", "=", request["version"]),
                "AND",
            ],
            "characterspec",
        )
        CharacterStatTable.delete(
            self,
            [
                ("id", "=", request["value"]),
                ("version", "=", request["version"]),
                "AND",
            ],
            "characterstat",
        )
        return super().delete_entry(request)

    def parse(self, request: CharacterParseModel):
        self.logger.debug(f"Parse {self.name}: {request}")
        guild_updated = []
        for player in request.players:
            character_parser = CharacterParser(
                player[0],
                player[1],
                region=request.region,
                version=request.version,
            )
            existing_player = character_parser.get_character()
            if existing_player.get("error"):
                return existing_player["error"]
            guild = existing_player.pop("guild_name")

            if guild:
                guild_parser = GuildParser(
                    guild,
                    player[1],
                    region=request.region,
                    version=request.version,
                )
                guild = guild_parser.get_guild()
                guild["version"] = request.version
                if guild["id"] not in guild_updated:
                    GuildTable.add_or_update(self, guild)
                    guild_updated.append(guild["id"])

            self.add_or_update(existing_player)

            equipment = character_parser.get_sorted_equipment()
            for slot in equipment:
                if equipment[slot]:
                    equipment[slot]["character_id"] = existing_player["id"]
                    equipment[slot]["version"] = request.version
                    CharacterItemTable.add_or_update(self, equipment[slot])
                else:
                    CharacterItemTable.delete_entry(
                        self,
                        {
                            "character_id": existing_player["id"],
                            "slot": slot,
                            "version": request.version,
                        },
                    )

            talents = character_parser.get_talents()
            for talent in talents:
                talent["id"] = existing_player["id"]
                talent["version"] = request.version
                talent["talents"] = str(talent["talents"])
                CharacterSpecTable.add_or_update(self, talent)

            stats = character_parser.get_statistics()
            for stat in stats:
                temp_stat = {
                    "id": existing_player["id"],
                    "name": stat,
                    "type": type(stats[stat]).__name__,
                    "value": str(stats[stat]),
                    "version": request.version,
                }
                CharacterStatTable.add_or_update(self, temp_stat)

        return f"{existing_player['id']}"

    def add_or_update(self, request):
        self.logger.debug(f"AddOrUpdate {self.name}: {request}")
        new_character = False
        if not request.get("id"):
            request["id"] = (self.select("MAX(id)", [], "character")[0][0] or 0) + 1
            new_character = True
            found_item = self.select(
                "id",
                [
                    ("name", "=", request["name"]),
                    ("realm", "=", request["realm"]),
                    ("region", "=", request["region"]),
                    ("version", "=", request["version"]),
                    "AND",
                ],
                "character",
            )
        else:
            found_item = self.select(
                "id",
                [
                    ("id", "=", request["id"]),
                    ("realm", "=", request["realm"]),
                    ("region", "=", request["region"]),
                    ("version", "=", request["version"]),
                    "AND",
                ],
                "character",
            )
            if not found_item:
                found_item = self.select(
                    "id",
                    [
                        ("name", "=", request["name"]),
                        ("realm", "=", request["realm"]),
                        ("region", "=", request["region"]),
                        ("version", "=", request["version"]),
                        "AND",
                    ],
                    "character",
                )
        if found_item:
            if request["guild"] == -1:
                request["guild"] = None
            self.update(
                request,
                [
                    ("id", "=", found_item[0][0]),
                    ("realm", "=", request["realm"]),
                    ("region", "=", request["region"]),
                    ("version", "=", request["version"]),
                    "AND",
                ],
                "character",
            )
        else:
            if request["guild"] == -1:
                request["guild"] = None
            if new_character:
                id = self.updateCharacter(
                    request["name"],
                    request["realm"],
                    region=request["region"],
                    version=request["version"],
                    new_character=new_character,
                )
                if id != "Not Found":
                    return f"{id}"
            self.insert(request, "character")
            return f"{request['id']}"
        return "Success"

    def get_equipment(self, request: str | dict):
        self.logger.debug(f"GetEquipment {self.name}: {request}")
        selection = [(request["key"], "=", request["value"])]
        if request["key"] == "name":
            if not request.get("realm"):
                raise Exception("No realm set in request")
            if not request.get("region"):
                raise Exception("No region set in request")
            selection.extend(
                [
                    ("realm", "=", request["realm"]),
                    ("region", "=", request["region"]),
                    ("version", "=", request["version"]),
                    "AND",
                ]
            )

        found_character = self.select("id", selection)
        if len(found_character) == 0:
            raise Exception(
                f"No character found for {request['key']} '{request['value']}'"
            )

        items = CharacterEquipmentModel().model_dump()
        found_items = self.select(
            "ALL",
            [
                ("character_id", "=", found_character[0][0]),
                ("version", "=", request["version"]),
                "AND",
            ],
            "characteritem",
        )
        for item in found_items:
            items[item[3].lower().replace(" ", "_")] = ItemModel().model_dump()
            items[item[3].lower().replace(" ", "_")]["character_id"] = item[0]
            items[item[3].lower().replace(" ", "_")]["id"] = item[1]
            items[item[3].lower().replace(" ", "_")]["name"] = item[2]
            items[item[3].lower().replace(" ", "_")]["slot"] = item[3]
            items[item[3].lower().replace(" ", "_")]["quality"] = item[4]
            items[item[3].lower().replace(" ", "_")]["wowhead_link"] = item[5]
            items[item[3].lower().replace(" ", "_")]["icon"] = item[6]
            items[item[3].lower().replace(" ", "_")]["inventory_type"] = item[7]
            items[item[3].lower().replace(" ", "_")]["enchantment"] = item[8]
            items[item[3].lower().replace(" ", "_")]["version"] = item[9]
        return items

    def get_specialization(self, request: str | dict):
        from src.helper.glyphs import glyphs
        from src.helper.talents import talents

        self.logger.debug(f"GetSpecialization {self.name}: {request}")

        selection = [(request["key"], "=", request["value"])]
        if request["key"] == "name":
            if not request.get("realm"):
                raise Exception("No realm set in request")
            if not request.get("region"):
                raise Exception("No region set in request")
            if not request.get("version"):
                raise Exception("No version set in request")
            selection.extend(
                [
                    ("realm", "=", request["realm"]),
                    ("region", "=", request["region"]),
                    ("version", "=", request["version"]),
                    "AND",
                ]
            )

        found_character = self.select("id", selection)
        if len(found_character) == 0:
            raise Exception(
                f"No character found for {request['key']} '{request['value']}'"
            )

        specialization = []
        found_specialization = self.select(
            "ALL",
            [
                ("id", "=", found_character[0][0]),
                ("version", "=", request["version"]),
                "AND",
            ],
            "characterspec",
        )
        for spec in found_specialization:
            current_spec = SpecializationModel().model_dump()
            current_spec["id"] = spec[0]
            current_spec["name"] = spec[1]
            current_spec["talents"] = []
            for talent in json.loads(spec[2].replace("'", '"')):
                try:
                    temp_talent = TalentModel().model_dump()
                    temp_talent["id"] = talent["id"]
                    temp_talent["name"] = talents[talent["id"]]["name"]
                    temp_talent["icon"] = talents[talent["id"]]["icon"]
                    temp_talent["rank"] = talent.get("rank", 0)
                    current_spec["talents"].append(temp_talent)
                except KeyError:
                    continue
            current_spec["glyphs"] = []
            for glyph in spec[3]:
                try:
                    temp_glyph = GlyphModel().model_dump()
                    temp_glyph["id"] = glyph
                    found_glyph = [
                        found_glyph.get(request["version"])
                        for found_glyph in glyphs.values()
                        if found_glyph[request["version"]]["id"] == glyph
                    ][0]
                    temp_glyph["name"] = found_glyph["name"]
                    temp_glyph["icon"] = found_glyph.get("icon")
                    temp_glyph["type"] = found_glyph.get("type")

                    current_spec["glyphs"].append(temp_glyph)
                except KeyError:
                    continue
            current_spec["active"] = spec[4]
            current_spec["spent_points"] = spec[6]
            specialization.append(current_spec)
        return specialization

    def get_stats(self, request: str | dict):
        self.logger.debug(f"GetStats {self.name}: {request}")
        selection = [(request["key"], "=", request["value"])]
        if request["key"] == "name":
            if not request.get("realm"):
                raise Exception("No realm set in request")
            if not request.get("region"):
                raise Exception("No region set in request")
            if not request.get("version"):
                raise Exception("No version set in request")
            selection.extend(
                [
                    ("realm", "=", request["realm"]),
                    ("region", "=", request["region"]),
                    ("version", "=", request["version"]),
                    "AND",
                ]
            )

        found_character = self.select("id", selection)
        if len(found_character) == 0:
            raise Exception(
                f"No character found for {request['key']} '{request['value']}'"
            )

        found_stats = self.select(
            "ALL",
            [
                ("id", "=", found_character[0][0]),
                ("version", "=", request["version"]),
                "AND",
            ],
            "characterstat",
        )

        stat_template = CharacterStatisticModel().model_dump()
        for stat in found_stats:
            match stat[2]:
                case "int" | "float" | "str":
                    stat_template[stat[1]] = stat[3]
                case "dict":
                    try:
                        stat_template[stat[1]] = json.loads(stat[3].replace("'", '"'))
                    except json.decoder.JSONDecodeError:
                        self.logger.warning(f"Failed to decode {stat[3]}")

        return stat_template

    def updateCharacter(self, character, realm, region, version, new_character=False):
        self.logger.debug(
            f"Updating {self.name}: {character},{realm},{region},{version},{new_character}"
        )
        character_parser = CharacterParser(
            character, realm, region=region, version=version
        )

        existing_player = character_parser.get_character()
        if existing_player.get("error"):
            return existing_player["error"]
        guild = existing_player.pop("guild_name")

        if guild:
            guild_parser = GuildParser(
                guild,
                realm,
                region=region,
                version=version,
            )
            guild = guild_parser.get_guild()
            guild["version"] = version

            GuildTable.add_or_update(self, guild)

        if new_character:
            self.insert(existing_player, "character")
        else:
            self.add_or_update(existing_player)

        equipment = character_parser.get_sorted_equipment()
        for slot in equipment:
            if equipment[slot]:
                equipment[slot]["character_id"] = existing_player["id"]
                equipment[slot]["version"] = version
                CharacterItemTable.add_or_update(self, equipment[slot])
            else:
                CharacterItemTable.delete_entry(
                    self,
                    {
                        "character_id": existing_player["id"],
                        "slot": slot,
                        "version": version,
                    },
                )

        talents = character_parser.get_talents()
        for talent in talents:
            talent["id"] = existing_player["id"]
            talent["version"] = version
            talent["talents"] = str(talent["talents"])
            CharacterSpecTable.add_or_update(self, talent)

        stats = character_parser.get_statistics()
        for stat in stats:
            temp_stat = {
                "id": existing_player["id"],
                "name": stat,
                "type": type(stats[stat]).__name__,
                "value": str(stats[stat]),
                "version": version,
            }
            CharacterStatTable.add_or_update(self, temp_stat)

        return existing_player["id"]

    def post(self, request):
        self.logger.debug(f"Post {self.name}: {request}")
        character_parser = CharacterParser(
            request["name"],
            request["realm"],
            region=request["region"],
            version=request["version"],
        )
        existing_player = character_parser.get_character()

        if not existing_player.get("error"):
            existing_player.pop("guild_name")
            self.delete(
                [
                    ("id", "=", request["id"]),
                    ("version", "=", request["version"]),
                    "AND",
                ]
            )
            request = existing_player
        return self.add_or_update(request)

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Get", self.get)
        self.set_function("Parse", self.parse)
        self.set_function("Delete", self.delete_entry)
        self.set_function("GetEquipment", self.get_equipment)
        self.set_function("GetSpecialization", self.get_specialization)
        self.set_function("GetStatistic", self.get_stats)
        self.set_function("Post", self.post)
