from src.database.tables.table import Table


class CharacterItemTable(Table):
    columns = {
        "character_id": {
            "value": "INTEGER NOT NULL REFERENCES character(id)",
        },
        "id": {
            "value": "INTEGER NOT NULL",
        },
        "name": {"value": "varchar(80) NOT NULL", "default": "'Unknown'"},
        "slot": {"value": "TEXT NOT NULL", "default": "'Head'"},
        "quality": {"value": "TEXT NOT NULL", "default": "'Common'"},
        "wowhead_link": {"value": "TEXT", "default": "''"},
        "icon": {"value": "TEXT", "default": "''"},
        "inventory_type": {"value": "TEXT", "default": "''"},
        "enchantment": {"value": "TEXT", "default": "''"},
        "PRIMARY KEY": {"value": "(character_id,slot)", "default": ""},
    }

    def get(self, request: str | dict):
        if not request["value"]:
            return Table.get(self, request)

        results = []
        selection = [(request["key"], "=", request["value"])]
        results = self.format_result(self.select("ALL", selection))

        return results

    def delete_entry(self, request):
        slot = " ".join([entry.capitalize() for entry in request["slot"].split("_")])
        found_item = self.select(
            "id",
            [
                ("character_id", "=", request["character_id"]),
                ("slot", "=", slot),
                "AND",
            ],
            "characteritem",
        )
        if len(found_item) > 0:
            return self.delete(
                [
                    ("character_id", "=", request["character_id"]),
                    ("slot", "=", slot),
                    "AND",
                ],
                "characteritem",
            )
        return (
            f"No item found in slot '{slot}' for character '{request['character_id']}'"
        )

    def add_or_update(self, request):
        found_item = self.select(
            ["character_id", "slot"],
            [
                ("character_id", "=", request["character_id"]),
                ("slot", "=", request["slot"]),
                "AND",
            ],
            "characteritem",
        )
        if found_item:
            self.update(
                request,
                [
                    ("character_id", "=", request["character_id"]),
                    ("slot", "=", request["slot"]),
                    "AND",
                ],
                "characteritem",
            )
        else:
            self.insert(request, "characteritem")
        return "Success"

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Get", self.get)
        self.set_function("Delete", self.delete_entry)
        self.set_function("Insert", self.add_or_update)
