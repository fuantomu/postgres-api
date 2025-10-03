from datetime import datetime
from src.database.tables.table import Table


class GuildTable(Table):
    columns = {
        "id": {
            "value": "INTEGER UNIQUE NOT NULL",
        },
        "name": {"value": "varchar(80) UNIQUE NOT NULL", "default": "'Unknown'"},
        "faction": {"value": "TEXT NOT NULL", "default": "'Alliance'"},
        "realm": {"value": "TEXT NOT NULL", "default": "'Dev'"},
        "achievement_points": {"value": "INTEGER NOT NULL", "default": 0},
        "member_count": {"value": "SMALLINT NOT NULL", "default": 0},
        "created_timestamp": {"value": "BIGINT NOT NULL", "default": 0},
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
        found_guild = self.select("id", [(request["key"], "=", request["value"])])
        if len(found_guild) == 0:
            raise Exception(f"No guild found for {request['key']} '{request['value']}'")

        return super().delete_entry(request)

    def add_or_update(self, request):
        if not request.get("id"):
            request["id"] = self.select("MAX(id)", [], "guild")[0][0] + 1

        found_item = self.select(
            "id",
            [("name", "=", request["name"]), ("realm", "=", request["realm"]), "AND"],
            "guild",
        )
        if found_item:
            self.update(
                request,
                [
                    ("name", "=", request["name"]),
                    ("realm", "=", request["realm"]),
                    "AND",
                ],
                "guild",
            )
        else:
            if request["created_timestamp"] == 0:
                request["created_timestamp"] = datetime.now().timestamp() * 1000
            self.insert(request, "guild")
            return f"{request['id']}"
        return "Success"

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Get", self.get)
        self.set_function("Post", self.add_or_update)
        self.set_function("Delete", self.delete_entry)
