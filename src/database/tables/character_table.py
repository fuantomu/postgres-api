from src.database.helper.blizzard_parser import CharacterParser, GuildParser
from src.database.tables.characteritem_table import CharacterItemTable
from src.database.tables.characterspec_table import CharacterSpecTable
from src.database.tables.guild_table import GuildTable
from src.database.tables.table import Table
from src.models.character import CharacterEquipmentModel
from src.models.item import ItemModel
from src.models.specialization import GlyphModel, SpecializationModel, TalentModel


class CharacterTable(Table):
    columns = {
        "id": {
            "value": "INTEGER UNIQUE NOT NULL",
        },
        "name": {"value": "varchar(80) UNIQUE NOT NULL", "default": "'Unknown'"},
        "gender": {"value": "TEXT NOT NULL", "default": "'Male'"},
        "faction": {"value": "TEXT NOT NULL", "default": "'Alliance'"},
        "race": {"value": "TEXT NOT NULL", "default": "'Human'"},
        "character_class": {"value": "TEXT NOT NULL", "default": "'Adventurer'"},
        "active_spec": {"value": "TEXT NOT NULL", "default": "'Adventurer'"},
        "realm": {"value": "TEXT NOT NULL", "default": "'Dev'"},
        "guild": {"value": "INTEGER REFERENCES guild(id)"},
        "level": {"value": "SMALLINT NOT NULL", "default": 1},
        "achievement_points": {"value": "INTEGER NOT NULL", "default": 0},
        "last_login_timestamp": {"value": "BIGINT NOT NULL", "default": 0},
        "average_item_level": {"value": "SMALLINT NOT NULL", "default": 0},
        "equipped_item_level": {"value": "SMALLINT NOT NULL", "default": 0},
        "active_title": {"value": "TEXT"},
        "PRIMARY KEY": {"value": "(id)", "default": ""},
    }

    def get(self, request: str | dict):
        if not request["value"]:
            return Table.get(self, request)

        results = []
        selection = [(request["key"], "=", request["value"])]
        if request["key"] == "name":
            if not request.get("realm"):
                raise Exception("No realm set in request")
            selection.append(("realm", "=", request["realm"]))
        results = self.format_result(self.select("ALL", selection))

        return results

    def delete_entry(self, request):
        found_character = self.select("id", [(request["key"], "=", request["value"])])
        if len(found_character) == 0:
            raise Exception(
                f"No character found for {request['key']} '{request['value']}'"
            )

        CharacterItemTable.delete(
            self, [("character_id", "=", request["value"])], "characteritem"
        )
        CharacterSpecTable.delete(
            self, [("id", "=", request["value"])], "characterspec"
        )
        return super().delete_entry(request)

    def parse(self, request: str | dict):
        guild_updated = []
        for player in request["players"]:
            character_parser = CharacterParser(player[0], player[1])
            existing_player = character_parser.get_character()
            if existing_player.get("error"):
                return existing_player["error"]
            guild = existing_player.pop("guild_name")

            if guild:
                guild_parser = GuildParser(guild, player[1])
                guild = guild_parser.get_guild()

                if guild["id"] not in guild_updated:
                    GuildTable.add_or_update(self, guild)
                    guild_updated.append(guild["id"])

            self.add_or_update(existing_player)

            equipment = character_parser.get_sorted_equipment()
            for slot in equipment:
                if equipment[slot]:
                    equipment[slot]["character_id"] = existing_player["id"]
                    CharacterItemTable.add_or_update(self, equipment[slot])
                else:
                    CharacterItemTable.delete_entry(
                        self, {"character_id": existing_player["id"], "slot": slot}
                    )

            talents = character_parser.get_talents()
            for talent in talents:
                talent["id"] = existing_player["id"]
                CharacterSpecTable.add_or_update(self, talent)
        return "Success"

    def add_or_update(self, request):
        new_character = False
        if not request.get("id"):
            request["id"] = self.select("MAX(id)", [], "character")[0][0] + 1
            new_character = True

        found_item = self.select(
            "id",
            [("name", "=", request["name"]), ("realm", "=", request["realm"]), "AND"],
            "character",
        )
        if found_item:
            if request["guild"] == -1:
                request["guild"] = None
            self.update(
                request,
                [
                    ("name", "=", request["name"]),
                    ("realm", "=", request["realm"]),
                    "AND",
                ],
                "character",
            )
        else:
            if request["guild"] == -1:
                request["guild"] = None
            if new_character:
                id = self.updateCharacter(
                    request["name"], request["realm"], new_character
                )
                if id != "Not Found":
                    return f"{id}"
            self.insert(request, "character")
            return f"{request['id']}"
        return "Success"

    def get_equipment(self, request: str | dict):
        selection = [(request["key"], "=", request["value"])]
        if request["key"] == "name":
            if not request.get("realm"):
                raise Exception("No realm set in request")
            selection.append(("realm", "=", request["realm"]))
            selection.append("AND")

        found_character = self.select("id", selection)
        if len(found_character) == 0:
            raise Exception(
                f"No character found for {request['key']} '{request['value']}'"
            )

        items = CharacterEquipmentModel().model_dump()
        found_items = self.select(
            "ALL", [("character_id", "=", found_character[0][0])], "characteritem"
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
        return items

    def get_specialization(self, request: str | dict):
        from src.helper.glyphs import glyphs
        from src.helper.talents import talents

        selection = [(request["key"], "=", request["value"])]
        if request["key"] == "name":
            if not request.get("realm"):
                raise Exception("No realm set in request")
            selection.append(("realm", "=", request["realm"]))
            selection.append("AND")

        found_character = self.select("id", selection)
        if len(found_character) == 0:
            raise Exception(
                f"No character found for {request['key']} '{request['value']}'"
            )

        specialization = []
        found_specialization = self.select(
            "ALL", [("id", "=", found_character[0][0])], "characterspec"
        )
        for spec in found_specialization:
            current_spec = SpecializationModel().model_dump()
            current_spec["id"] = spec[0]
            current_spec["name"] = spec[1]
            current_spec["talents"] = []
            for talent in spec[2]:
                try:
                    temp_talent = TalentModel().model_dump()
                    temp_talent["id"] = talent
                    temp_talent["name"] = talents[talent]["name"]
                    temp_talent["icon"] = talents[talent]["icon"]
                    current_spec["talents"].append(temp_talent)
                except KeyError:
                    continue
            current_spec["glyphs"] = []
            for glyph in spec[3]:
                try:
                    temp_glyph = GlyphModel().model_dump()
                    temp_glyph["id"] = glyph
                    found_glyph = [
                        found_glyph
                        for found_glyph in glyphs.values()
                        if found_glyph["id"] == glyph
                    ][0]
                    temp_glyph["name"] = found_glyph["name"]
                    temp_glyph["icon"] = found_glyph.get("icon")

                    current_spec["glyphs"].append(temp_glyph)
                except KeyError:
                    continue
            current_spec["active"] = spec[4]
            specialization.append(current_spec)
        return specialization

    def updateCharacter(self, character, realm, new_character=False):
        character_parser = CharacterParser(character, realm)
        existing_player = character_parser.get_character()
        if existing_player.get("error"):
            return existing_player["error"]
        guild = existing_player.pop("guild_name")

        if guild:
            guild_parser = GuildParser(guild, realm)
            guild = guild_parser.get_guild()

            GuildTable.add_or_update(self, guild)

        if new_character:
            self.insert(existing_player, "character")
        else:
            self.add_or_update(existing_player)

        equipment = character_parser.get_sorted_equipment()
        for slot in equipment:
            if equipment[slot]:
                equipment[slot]["character_id"] = existing_player["id"]
                CharacterItemTable.add_or_update(self, equipment[slot])
            else:
                CharacterItemTable.delete_entry(
                    self, {"character_id": existing_player["id"], "slot": slot}
                )

        talents = character_parser.get_talents()
        for talent in talents:
            talent["id"] = existing_player["id"]
            CharacterSpecTable.add_or_update(self, talent)

        return existing_player["id"]

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Get", self.get)
        self.set_function("Parse", self.parse)
        self.set_function("Delete", self.delete_entry)
        self.set_function("GetEquipment", self.get_equipment)
        self.set_function("GetSpecialization", self.get_specialization)
