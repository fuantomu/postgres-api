from src.database.tables.table import Table


class RecipeIngredientTable(Table):
    columns = {
        "recipe_id": {
            "value": "UUID NOT NULL REFERENCES recipe(id)",
            "default": "uuid_generate_v1()",
        },
        "ingredient_id": {
            "value": "UUID NOT NULL REFERENCES ingredient(id)",
            "default": "uuid_generate_v1()",
        },
        "quantity": {"value": "TEXT", "default": ""},
        "PRIMARY KEY": {"value": "(recipe_id,ingredient_id)", "default": ""},
    }

    def insert_recipe_ingredient(self, request: dict) -> None:
        ingredients = []
        for ingredient in request["ingredients"]:
            if ingredient.get("id"):
                ingredients.extend([("id", "=", ingredient["id"])])
                ingredient["key"] = "id"
            else:
                ingredients.extend([("name", "=", ingredient["name"])])
                ingredient["key"] = "name"
        ingredients.append("OR")
        ingredients = self.select(["id", "name"], ingredients, "ingredient")

        recipe_ingredient_requests = []
        for ingredient in ingredients:
            recipe_ingredient_requests.append(
                {
                    "recipe_id": request["recipe_id"],
                    "ingredient_id": ingredient[0],
                    "quantity": [
                        _ingredient["quantity"]
                        for _ingredient in request["ingredients"]
                        if _ingredient[_ingredient["key"]]
                        == (
                            ingredient[0]
                            if _ingredient["key"] == "id"
                            else ingredient[1]
                        )
                    ][0],
                }
            )

        for _request in recipe_ingredient_requests:
            Table.insert(self, _request, "recipeingredient", "recipe_id")

    def update(self, request: dict) -> None:
        if len(request["ingredients"]) == 0:
            return RecipeIngredientTable.delete(
                self, [("recipe_id", "=", request["recipe_id"])], "recipeingredient"
            )
        for idx, ingredient in enumerate(request["ingredients"].copy()):
            result = self.select(
                "id", [("name", "=", ingredient["name"])], "ingredient"
            )
            if result:
                request["ingredients"][idx]["id"] = result[0][0]
            else:
                request["ingredients"].remove(ingredient)
                self.logger.warning(f"No recipe found for '{ingredient['name']}'")

        if request["overwrite_ingredients"]:
            self.delete([("recipe_id", "=", request["recipe_id"])], "recipeingredient")

        existing_ingredients = self.select(
            ["ingredient_id", "quantity"],
            [("recipe_id", "=", request["recipe_id"])],
            "recipeingredient",
        )

        for new_ingredient in request["ingredients"].copy():
            for existing_ingredient in existing_ingredients:
                if new_ingredient["id"] == existing_ingredient[0]:
                    request["ingredients"].remove(new_ingredient)
                    if new_ingredient["quantity"] != existing_ingredient[1]:
                        Table.update(
                            self,
                            {"quantity": new_ingredient["quantity"]},
                            [
                                ("recipe_id", "=", request["recipe_id"]),
                                ("ingredient_id", "=", new_ingredient["id"]),
                                "AND",
                            ],
                            "recipeingredient",
                            "recipe_id",
                        )

        if len(request["ingredients"]) > 0:
            recipe_ingredient_request = {
                "recipe_id": request["recipe_id"],
                "ingredients": request["ingredients"],
            }
            return RecipeIngredientTable.insert_recipe_ingredient(
                self, recipe_ingredient_request
            )
