from src.database.helper.blizzard_parser import CharacterParser, GuildParser
from src.database.tables.characteritem_table import CharacterItemTable
from src.database.tables.characterspec_table import CharacterSpecTable
from src.database.tables.guild_table import GuildTable
from src.database.tables.table import Table


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
        results = self.format_result(self.select("ALL", selection))

        return results

    def delete_entry(self, request):
        found_character = self.select("id", [(request["key"], "=", request["value"])])
        if len(found_character) == 0:
            raise Exception(
                f"No character found for {request['key']} '{request['value']}'"
            )

        return super().delete_entry(request)

    def parse(self, request: str | dict):
        guild_updated = []
        for player in request["players"]:
            character_parser = CharacterParser(player[0], player[1])
            existing_player = character_parser.get_character()
            guild = existing_player.pop("guild_name")

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

            talents = character_parser.get_talents()
            for talent in talents:
                talent["id"] = existing_player["id"]
                CharacterSpecTable.add_or_update(self, talent)
        return "Success"

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Get", self.get)
        self.set_function("Parse", self.parse)
        self.set_function("Delete", self.delete_entry)
