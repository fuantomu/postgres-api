from database.tables.table import Table

class RecipeIngredientTable(Table):
    columns = {
        "recipe_id": {
            "value": "UUID NOT NULL REFERENCES recipe(id)",
            "default": "uuid_generate_v1()"
        },
        "ingredient_id": {
            "value": "UUID NOT NULL REFERENCES ingredient(id)",
            "default": "uuid_generate_v1()"
        },
        "quantity": {
            "value": "TEXT",
            "default": ""
        },
        "PRIMARY KEY": {
            "value": "(recipe_id,ingredient_id)",
            "default": ""
        }
    }

    def insert_recipe_ingredient(self, request: dict) -> None:
        recipe_ingredient_requests = []
        for ingredient in request["ingredients"]:
            temp_request = {
                "recipe_id" : request["recipe_id"],
                "quantity" : ingredient["quantity"]
            }
            try:
                if ingredient["name"]:
                    temp_request["ingredient_id"] = self.select("id", [("name","=",ingredient["name"])], "ingredient")[0][0]
                else:
                    temp_request["ingredient_id"] = self.select("id", [("id","=",ingredient["id"])], "ingredient")[0][0]
            except IndexError:
                self.logger.error(f"Ingredient '{ingredient['name'] or ingredient['id']}' does not exist")
            
            if temp_request.get("ingredient_id"):
                recipe_ingredient_requests.append(temp_request)

        for _request in recipe_ingredient_requests:
            Table.insert(self,_request, "recipeingredient", "recipe_id")

    def update(self, request: dict) -> None:
        
        for ingredient in request["ingredients"].copy():
            result = self.select("id", [("name","=",ingredient["name"])],"ingredient")
            if result:
                ingredient["id"] = result[0][0]
            else:
                request["ingredients"].remove(ingredient)
                self.logger.warning(f"No ingredient found for '{ingredient['name']}'")
        
        if request["overwrite_ingredients"]:
            self.delete("ALL", [("recipe_id","=",request["recipe_id"])], "recipeingredient")

        existing_ingredients = self.select("ingredient_id", [("recipe_id","=",request["recipe_id"])],"recipeingredient")
        for new_ingredient in request["ingredients"].copy():
            for existing_ingredient in existing_ingredients:
                if new_ingredient["id"] == existing_ingredient[0]:
                    request["ingredients"].remove(new_ingredient)
        
        recipe_ingredient_request = {
            "recipe_id": request["recipe_id"],
            "ingredients": request["ingredients"]
        }
        return RecipeIngredientTable.insert_recipe_ingredient(self,recipe_ingredient_request)

        

    