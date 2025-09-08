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

    def insert(self, request: dict) -> None:
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
            except:
                self.logger.error(f"Ingredient {ingredient} does not exist")
            
            if temp_request.get("ingredient_id"):
                recipe_ingredient_requests.append(temp_request)
        

        for _request in recipe_ingredient_requests:
            Table.insert(self, _request, "recipeingredient", "recipe_id")
        return str(request["recipe_id"])

    