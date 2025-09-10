from database.tables.table import Table

class IngredientTable(Table):
    columns = {
        "id": {
            "value": "UUID NOT NULL",
            "default": "uuid_generate_v1()"
        },
        "name": {
            "value": "varchar(80) UNIQUE NOT NULL",
            "default": ""
        },
        "description": {
            "value": "TEXT",
            "default": ""
        },
        "alias": {
            "value": "TEXT[]",
            "default": ""
        },
        "PRIMARY KEY": {
            "value": "(id)",
            "default": ""
        }
    }

    def add_alias(self, request: dict):
        try:
            ingredient = request["value"] if request["key"] == "id" else self.format_result(self.select("ALL", [(request["key"],"=",request["value"])], "ingredient"))[0]
        except IndexError:
            raise Exception(f"No ingredient found for '{request['value']}'")

        update_request = {
            "id": ingredient["id"],
            "alias": [alias['name'] for alias in request['alias']]
        }

        if ingredient.get("alias"):
            list(set(update_request["alias"].extend(ingredient['alias'])))

        return self.update(update_request, [("id","=",ingredient["id"])], "ingredient")

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Alias", self.add_alias)

    