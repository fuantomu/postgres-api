from src.database.tables.table import Table


class AccountCharacterTable(Table):
    columns = {
        "account_id": {"value": "INTEGER NOT NULL REFERENCES account(id)"},
        "character_id": {"value": "INTEGER NOT NULL REFERENCES character(id)"},
        "PRIMARY KEY": {"value": "(account_id,character_id)", "default": ""},
    }

    def delete_entry(self, request):
        found_character = self.select(
            "account_id",
            [
                ("account_id", "=", request["account_id"]),
                ("character_id", "=", request["character_id"]),
                "AND",
            ],
            "accountcharacter",
        )
        if len(found_character) == 0:
            raise Exception(
                f"No character found for account_id '{request['account_id']}' and character_id '{request['character_id']}'"
            )

        return self.delete(
            [
                ("account_id", "=", request["account_id"]),
                ("character_id", "=", request["character_id"]),
                "AND",
            ],
            "accountcharacter",
        )

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Delete", self.delete_entry)
