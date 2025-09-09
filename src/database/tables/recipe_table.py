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
    
    def get_recipes_by_ingredient(self, request: str|dict):
        output : list[RecipeModel|None] = []
        try:
            ingredient_id = self.format_result(self.select("ALL", [(request["key"],"=",request["value"])], "ingredient"))[0]["id"]
        except IndexError:
            raise Exception(f"No ingredient found for '{request['value']}'")
        recipe_ids = self.select("recipe_id", [("ingredient_id","=",ingredient_id)],"recipeingredient")
        for recipe_id in recipe_ids:
            output.extend(self.get({"key": "id", "value": str(recipe_id[0])}))

        return output

    def add_ingredient(self, request: dict):
        try:
            recipe_id = self.format_result(self.select("ALL", [(request["key"],"=",request["value"])], "recipe"))[0]["id"]
        except IndexError:
            raise Exception(f"No recipe found for '{request['value']}'")

        for ingredient in request["ingredients"].copy() :
            result = self.select("id", [("name","=",ingredient["name"])],"ingredient")
            if result:
                ingredient["id"] = result[0][0]
            else:
                request["ingredients"].remove(ingredient)
                self.logger.error(f"No ingredient found for '{ingredient['name']}'")

        if len(request["ingredients"]) == 0:
            raise Exception("No ingredients found for given request") 
        
        existing_ingredients = self.select("ingredient_id", [("recipe_id","=",recipe_id)],"recipeingredient")
        for new_ingredient in request["ingredients"].copy():
            for existing_ingredient in existing_ingredients:
                if new_ingredient["id"] == existing_ingredient[0]:
                    request["ingredients"].remove(new_ingredient)
                    self.logger.debug(f"Removing duplicate ingredient '{new_ingredient['id']}'")
                    
        if len(request["ingredients"]) == 0:
            raise Exception("Cannot add any of the given ingredients (duplicate or non-existing)") 

        recipe_ingredient_request = {
            "recipe_id": recipe_id,
            "ingredients": request["ingredients"]
        }
        return RecipeIngredientTable.insert(self, recipe_ingredient_request)
        

        
    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Add", self.insert)
        self.set_function("Get", self.get)
        self.set_function("GetRecipesByIngredient", self.get_recipes_by_ingredient)
        self.set_function("AddIngredient", self.add_ingredient)

    

    