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
        request.pop("overwrite_ingredients", None)
        ingredients = request.pop("ingredients", None)
        recipe_id = super().insert(request)
        recipe_ingredient_request = {
            "recipe_id": recipe_id,
            "ingredients": ingredients
        }
        RecipeIngredientTable.insert_recipe_ingredient(self, recipe_ingredient_request)
        return recipe_id
    
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
    
    def update(self, request: dict, where = None, table_name = None, return_key = "id"):
        ingredients = request.pop("ingredients", None)
        recipe_ingredient_request = {
            "recipe_id" : request["id"],
            "ingredients" : ingredients,
            "overwrite_ingredients": request.pop("overwrite_ingredients", None)
        }
        RecipeIngredientTable.update(self, recipe_ingredient_request)
        return super().update(request, where, "recipe")
    
    def get_recipes_by_ingredient(self, request: str|dict):
        output : list[RecipeModel|None] = []
        recipe_ids = []
        if request["include_alias"] and request['key'] == "name":
            ingredients = self.format_result(self.select("ALL", [('alias',"@>",[request["value"]])], "ingredient"))
            for ingredient in ingredients:
                recipe_ids.extend(self.select("recipe_id", [("ingredient_id","=",ingredient["id"])],"recipeingredient"))            

        try:
            ingredient = self.format_result(self.select("ALL", [(request["key"],"=",request["value"])], "ingredient"))[0]
        except IndexError:
            if len(recipe_ids) == 0:
                raise Exception(f"No ingredient found for '{request['value']}'")
        
        recipe_ids.extend(self.select("recipe_id", [("ingredient_id","=",ingredient["id"])],"recipeingredient"))
        recipe_ids = list(set(recipe_ids))
        
        for recipe_id in recipe_ids:
            output.extend(self.get({"key": "id", "value": str(recipe_id[0])}))

        return output       

        
    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Post", self.add_or_update)
        self.set_function("Get", self.get)
        self.set_function("GetRecipesByIngredient", self.get_recipes_by_ingredient)

    

    