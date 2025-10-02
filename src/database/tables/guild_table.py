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

    # def update_alias(self, request: dict):
    #     ingredient = self.format_result(
    #         self.select("ALL", [("id", "=", request["id"])], "ingredient")
    #     )[0]
    #     alias_list = [alias for alias in request["alias"]]

    #     for alias in alias_list:
    #         if alias == ingredient["name"]:
    #             alias_list.remove(alias)
    #             self.logger.warning(
    #                 f"'{alias}' is the same name as the Ingredient. Removing from request"
    #             )

    #     if ingredient.get("alias"):
    #         alias_list.extend(ingredient["alias"])
    #         alias_list = list(set(alias_list))

    #     return alias_list

    def get(self, request: str | dict):
        if not request["value"]:
            return Table.get(self, request)

        results = []
        selection = [(request["key"], "=", request["value"])]
        results = self.format_result(self.select("ALL", selection))

        return results

    # def insert(self, request: dict) -> str:
    #     request.pop("overwrite_alias", None)
    #     if request.get("alias"):
    #         for alias in request.get("alias", []):
    #             if alias == request["name"]:
    #                 request["alias"].remove(alias)
    #                 self.logger.warning(
    #                     f"'{alias}' is the same name as the Ingredient. Removing from request"
    #                 )

    #     return super().insert(request)

    # def update(self, request: dict, where=None, table_name=None, return_key="id"):
    #     if not request["overwrite_alias"]:
    #         request["alias"] = self.update_alias(request)
    #     request.pop("overwrite_alias")
    #     if list(request.keys()) == ["name", "id"]:
    #         return str(request["id"])
    #     return super().update(request, where, "ingredient")

    # def delete_entry(self, request):
    #     found_ingredient = self.select("id", [(request["key"], "=", request["value"])])
    #     if len(found_ingredient) == 0:
    #         raise Exception(
    #             f"No ingredient found for {request['key']} '{request['value']}'"
    #         )

    #     ingredient_id = found_ingredient[0][0]

    #     self.delete([("ingredient_id", "=", ingredient_id)], "recipeingredient")
    #     return super().delete_entry(request)

    def add_or_update(self, request):
        found_item = self.select(
            "id",
            [
                ("id", "=", request["id"]),
            ],
            "guild",
        )
        if found_item:
            self.update(
                request,
                [
                    ("id", "=", request["id"]),
                ],
                "guild",
            )
        else:
            self.insert(request, "guild")
        return "Success"

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Get", self.get)
        self.set_function("Post", self.add_or_update)
        # self.set_function("Delete", self.delete_entry)
