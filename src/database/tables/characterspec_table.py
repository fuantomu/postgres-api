from src.database.tables.table import Table


class CharacterSpecTable(Table):
    columns = {
        "id": {
            "value": "INTEGER NOT NULL REFERENCES character(id)",
        },
        "name": {"value": "varchar(64) NOT NULL", "default": "'Unknown'"},
        "talents": {"value": "TEXT NOT NULL", "default": ""},
        "glyphs": {"value": "INTEGER[] NOT NULL", "default": ""},
        "spec_id": {"value": "SMALLINT", "default": ""},
        "version": {"value": "varchar(8)", "default": "'mop'"},
        "PRIMARY KEY": {"value": "(id,spec_id,version)", "default": ""},
    }

    def get(self, request: str | dict):
        if not request["value"]:
            if not request["version"]:
                return self.format_result(self.select("ALL"))
            return self.format_result(
                self.select("ALL", [("version", "=", request["version"])])
            )

        results = []
        selection = [(request["key"], "=", request["value"])]
        if request["key"] == "name":
            if request.get("version"):
                selection.append(("version", "=", request["version"]))
            selection.append("AND")
        results = self.format_result(self.select("ALL", selection))

        return results

    def delete_entry(self, request):
        found_character = self.select(
            "id",
            [
                (request["key"], "=", request["value"]),
                ("version", "=", request["version"]),
                "AND",
            ],
        )
        if len(found_character) == 0:
            raise Exception(f"No spec found for {request['key']} '{request['value']}'")

        return super().delete_entry(request)

    def add_or_update(self, request):
        found_item = self.select(
            ["id", "name"],
            [
                ("id", "=", request["id"]),
                ("spec_id", "=", request["spec_id"]),
                ("version", "=", request["version"]),
                "AND",
            ],
            "characterspec",
        )
        if found_item:
            self.update(
                request,
                [
                    ("id", "=", request["id"]),
                    ("spec_id", "=", request["spec_id"]),
                    ("version", "=", request["version"]),
                    "AND",
                ],
                "characterspec",
            )
        else:
            self.insert(request, "characterspec")
        return "Success"

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Get", self.get)
        self.set_function("Delete", self.delete_entry)
        self.set_function("Insert", self.add_or_update)
