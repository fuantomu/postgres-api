import json
from src.database.helper.blizzard_parser import CharacterParser, GuildParser, slotNames
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
                talent["name"] = f"{existing_player['character_class']}{talent['name']}"
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
        if not request.get("id"):
            request["id"] = self.select("MAX(id)", [], "character")[0][0] + 1
        query = f"select id,version from character where (id = '{request['id']}' or name = '{request['name']}') and region = '{request["region"]}' and realm = '{request['realm']}'"
        found_item = self.select_query(query)

        if found_item:
            character_same_version = [
                character_same_version
                for character_same_version in found_item
                if character_same_version[1] == request["version"]
            ]

            if character_same_version:
                if request.get("guild") == -1:
                    request.pop("guild")
                self.update(
                    request,
                    [
                        ("id", "=", character_same_version[0][0]),
                        ("realm", "=", request["realm"]),
                        ("region", "=", request["region"]),
                        ("version", "=", request["version"]),
                        "AND",
                    ],
                    "character",
                )
                return "Success"
        if request["guild"] == -1:
            request.pop("guild", None)
        request.pop("guild_name", None)

        self.insert(request, "character")
        result = self.updateCharacter(
            request["name"], request["realm"], request["region"], request["version"]
        )
        if result == "Not Found":
            return f"{request['id']}"
        return f"{result}"

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
            current_spec["version"] = request["version"]
            current_spec["talents"] = []
            for talent in json.loads(spec[2].replace("'", '"')):
                try:
                    temp_talent = TalentModel().model_dump()
                    temp_talent["id"] = talent["id"]
                    found_talent = [
                        found_talent[request["version"]]
                        for found_talent in talents.values()
                        if found_talent.get(request["version"], {}).get("id", {})
                        == talent["id"]
                    ]
                    if found_talent:
                        temp_talent["name"] = found_talent[0].get("name")
                        temp_talent["icon"] = found_talent[0].get("icon")
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
                        if found_glyph.get(request["version"]).get("id") == glyph
                    ]
                    if found_glyph:
                        temp_glyph["name"] = found_glyph[0]["name"]
                        temp_glyph["icon"] = found_glyph[0].get("icon")
                        temp_glyph["type"] = found_glyph[0].get("type")
                        temp_glyph["character_class"] = found_glyph[0].get(
                            "character_class"
                        )

                    current_spec["glyphs"].append(temp_glyph)
                except KeyError:
                    continue
            current_spec["spec_id"] = spec[4]
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

    def updateCharacter(self, character, realm, region, version):
        self.logger.debug(
            f"Updating {self.name}: {character},{realm},{region},{version}"
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
        query = f"select id from character where (id = '{request['id']}' and name != '{request['name']}') and region = '{request["region"]}' and realm = '{request['realm']}'"
        result = self.select_query(query)

        # Character name was changed
        if len(result) > 0:
            character_parser = CharacterParser(
                request["name"],
                request["realm"],
                region=request["region"],
                version=request["version"],
            )
            existing_player = character_parser.get_character()
            if (
                not existing_player.get("error")
                and existing_player.get("id") != result[0]
            ):
                CharacterItemTable.delete(
                    self,
                    [
                        ("character_id", "=", request["id"]),
                        ("version", "=", request["version"]),
                        "AND",
                    ],
                    "characteritem",
                )
                CharacterSpecTable.delete(
                    self,
                    [
                        ("id", "=", request["id"]),
                        ("version", "=", request["version"]),
                        "AND",
                    ],
                    "characterspec",
                )
                CharacterStatTable.delete(
                    self,
                    [
                        ("id", "=", request["id"]),
                        ("version", "=", request["version"]),
                        "AND",
                    ],
                    "characterstat",
                )
                self.delete(
                    [
                        ("id", "=", request["id"]),
                        ("version", "=", request["version"]),
                        ("realm", "=", request["realm"]),
                        ("region", "=", request["region"]),
                        "AND",
                    ]
                )
                return self.add_or_update(existing_player)

        return self.add_or_update(request)

    def post_equipment(self, request):
        self.logger.debug(f"PostEquipment {self.name}: {request}")
        found_character = self.select(
            "id",
            [
                ("id", "=", request["id"]),
                ("version", "=", request["version"]),
                "AND",
            ],
        )
        if len(found_character) == 0:
            raise Exception(
                f"No character found for id '{request['id']}' in '{request['version']}'"
            )

        for slot in slotNames:
            if not request[slot]:
                CharacterItemTable.delete_entry(
                    self,
                    {
                        "character_id": request["id"],
                        "slot": slot.capitalize(),
                        "version": request["version"],
                    },
                )
            else:
                CharacterItemTable.add_or_update(self, request[slot])
        return "Success"

    def post_specialization(self, request):
        self.logger.debug(f"PostSpecialization {self.name}: {request}")
        found_character = self.select(
            "id",
            [
                ("id", "=", request["id"]),
                ("version", "=", request["version"]),
                "AND",
            ],
        )
        if len(found_character) == 0:
            raise Exception(
                f"No character found for id '{request['id']}' in '{request['version']}'"
            )

        request["talents"] = str(
            [
                {"id": talent["id"], "rank": talent["rank"]}
                for talent in request["talents"]
            ]
        )
        request["glyphs"] = [glyph["id"] for glyph in request["glyphs"]]

        return CharacterSpecTable.add_or_update(self, request)

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Get", self.get)
        self.set_function("Parse", self.parse)
        self.set_function("Delete", self.delete_entry)
        self.set_function("GetEquipment", self.get_equipment)
        self.set_function("GetSpecialization", self.get_specialization)
        self.set_function("GetStatistic", self.get_stats)
        self.set_function("Post", self.post)
        self.set_function("PostEquipment", self.post_equipment)
        self.set_function("PostSpecialization", self.post_specialization)
