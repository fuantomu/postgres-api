from database.tables.recipe_ingredient_table import RecipeIngredientTable
from database.tables.table import Table
from models.recipe_model import RecipeModel

class RecipeTable(Table):
    columns = {
        "id": {
            "value": "UUID NOT NULL",
            "default": "uuid_generate_v1()"
        },
        "name": {
            "value": "varchar(80) NOT NULL",
            "default": ""
        },
        "description": {
            "value": "TEXT",
            "default": ""
        },
        "PRIMARY KEY": {
            "value": "(id)",
            "default": ""
        }
    }

    def insert(self, request: dict) -> None:
        recipe_request = {}
        for column in self.columns.keys():
            if request.get(column):
                recipe_request[column] = request[column]
        recipe_id = super().insert(recipe_request)
        recipe_ingredient_request = {
            "recipe_id": recipe_id,
            "ingredients": request["ingredients"]
        }
        return RecipeIngredientTable.insert(self, recipe_ingredient_request)
    
    def get(self, request : str|dict):
        output : list[RecipeModel] = super().get(request)
        for recipe in output:
            ingredients = self.select("ALL",[("recipe_id","=",recipe["id"])],"recipeingredient")
            recipe["ingredients"] = []
            for ingredient in ingredients:
                result = self.select("ALL", [("id","=",ingredient[1])],"ingredient")[0]
                recipe["ingredients"].append({
                    "id": str(ingredient[1]),
                    "name": result[1],
                    "quantity": ingredient[2]
                })

        return output

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Add", self.insert)
        self.set_function("Get", self.get)

    

    