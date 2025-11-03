from datetime import datetime, timezone
from src.database.tables.table import Table


class GuildTable(Table):
    columns = {
        "id": {
            "value": "INTEGER UNIQUE NOT NULL",
        },
        "name": {"value": "varchar(32) NOT NULL", "default": "'Unknown'"},
        "faction": {"value": "varchar(8) NOT NULL", "default": "'Alliance'"},
        "realm": {"value": "varchar(32) NOT NULL", "default": "'Dev'"},
        "achievement_points": {"value": "INTEGER NOT NULL", "default": 0},
        "member_count": {"value": "SMALLINT NOT NULL", "default": 0},
        "created_timestamp": {"value": "BIGINT NOT NULL", "default": 0},
        "region": {"value": "varchar(2)", "default": "'eu'"},
        "version": {"value": "varchar(8)", "default": "'mop'"},
        "realm_version": {"value": "varchar(32)"},
        "PRIMARY KEY": {"value": "(id,version)", "default": ""},
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
            if request.get("realm"):
                selection.append(("realm", "=", request["realm"]))
            if request.get("region"):
                selection.append(("region", "=", request["region"]))
            if request.get("version"):
                selection.append(("version", "=", request["version"]))
            selection.append("AND")
        results = self.format_result(self.select("ALL", selection))

        return results

    def delete_entry(self, request):
        found_guild = self.select(
            "id",
            [
                (request["key"], "=", request["value"]),
                ("version", "=", request["version"]),
            ],
        )
        if len(found_guild) == 0:
            raise Exception(
                f"No guild found for {request['key']} '{request['value']}' in '{request['version']}'"
            )

        return super().delete_entry(request)

    def add_or_update(self, request):
        query = f"select id,version from guild where (id = '{request['id']}' or name = '{request['name']}') and region = '{request['region']}' and realm = '{request['realm']}'"
        found_item = self.select_query(query)

        if found_item:
            guild_same_version = [
                guild for guild in found_item if guild[1] == request["version"]
            ]

            if guild_same_version:
                self.update(
                    request,
                    [
                        ("name", "=", request["name"]),
                        ("realm", "=", request["realm"]),
                        ("version", "=", request["version"]),
                        "AND",
                    ],
                    "guild",
                )
                return "Success"
        request["id"] = self.select("MAX(id)", [], "guild")[0][0] + 1
        if request["created_timestamp"] == 0:
            request["created_timestamp"] = datetime.now(timezone.utc).timestamp()
        self.insert(request, "guild")
        return f"{request['id']}"

        # found_item = self.select(
        #     ["id", "version"],
        #     [
        #         ("name", "=", request["name"]),
        #         ("realm", "=", request["realm"]),
        #         "AND",
        #     ],
        #     "guild",
        # )
        if found_item:
            if found_item[0][1] == request["version"]:
                self.update(
                    request,
                    [
                        ("name", "=", request["name"]),
                        ("realm", "=", request["realm"]),
                        ("version", "=", request["version"]),
                        "AND",
                    ],
                    "guild",
                )
            else:
                request["id"] = self.select("MAX(id)", [], "guild")[0][0] + 1
                if request["created_timestamp"] == 0:
                    request["created_timestamp"] = datetime.now(
                        timezone.utc
                    ).timestamp()
                self.insert(request, "guild")
                return f"{request['id']}"
        else:
            if request["created_timestamp"] == 0:
                request["created_timestamp"] = datetime.now(timezone.utc).timestamp()
            self.insert(request, "guild")
            return f"{request['id']}"
        return "Success"

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Get", self.get)
        self.set_function("Post", self.add_or_update)
        self.set_function("Delete", self.delete_entry)
