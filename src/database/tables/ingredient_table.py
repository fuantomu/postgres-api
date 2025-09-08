from database.tables.table import Table

class IngredientTable(Table):
    columns = {
        "id": {
            "value": "UUID NOT NULL PRIMARY KEY",
            "default": "uuid_generate_v1()"
        },
        "name": {
            "value": "TEXT UNIQUE NOT NULL",
            "default": ""
        },
        "description": {
            "value": "TEXT",
            "default": ""
        },
        "alias": {
            "value": "TEXT",
            "default": ""
        }
    }

    def get(self, request : str|dict):
        return self.format_result(super().select("ALL", [("id","=",request)]))

    def find(self, request : str|dict):
        return self.format_result(super().select("ALL", [("name","=",request)]))

    def get_recipes_by_ingredient(self, request : str|dict):
        return self.format_result(super().select(request))

    def get_all(self, request : str|dict):
        return self.format_result(super().select(request))

    functions = {
        "GetAll" : get_all,
        "Get": get,
        "GetRecipesByIngredient": get_recipes_by_ingredient,
        "Find": find,
        "Add": Table.insert
    }

    