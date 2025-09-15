from src.database.tables.recipe_ingredient_table import RecipeIngredientTable
from src.database.tables.table import Table
from src.models.recipe_model import RecipeModel


class RecipeTable(Table):
    columns = {
        "id": {"value": "UUID NOT NULL", "default": "uuid_generate_v1()"},
        "name": {"value": "varchar(80) NOT NULL", "default": ""},
        "description": {"value": "TEXT", "default": ""},
        "PRIMARY KEY": {"value": "(id)", "default": ""},
    }

    def insert(self, request: dict) -> None:
        request.pop("overwrite_ingredients", None)
        ingredients = request.pop("ingredients", None)
        recipe_id = super().insert(request)

        if ingredients is not None and len(ingredients) > 0:
            recipe_ingredient_request = {
                "recipe_id": recipe_id,
                "ingredients": ingredients,
            }
            RecipeIngredientTable.insert_recipe_ingredient(
                self, recipe_ingredient_request
            )

        return recipe_id

    def get(self, request: str | dict):
        output: list[RecipeModel] = super().get(request)
        if len(output) == 0:
            raise Exception(
                f"No recipe found for {request['key']} '{request['value']}'"
            )
        recipe_ingredients = self.select(
            ["recipe_id", "ingredient_id", "name", "quantity"],
            [("recipe_id", "=", x) for x in output].extend(["OR"]),
            "recipeingredient",
            "ingredient ON id = ingredient_id",
        )
        for recipe in output:
            current_recipe_ingredients = [
                ingredient
                for ingredient in recipe_ingredients
                if str(ingredient[0]) == recipe["id"]
            ]
            recipe["ingredients"] = [
                {
                    "id": str(ingredient[1]),
                    "name": ingredient[2],
                    "quantity": ingredient[3],
                }
                for ingredient in current_recipe_ingredients
            ]

        return output

    def update(self, request: dict, where=None, table_name=None, return_key="id"):
        ingredients = request.pop("ingredients", None)
        overwrite_ingredients = request.pop("overwrite_ingredients", None)
        if ingredients is not None and len(ingredients):
            recipe_ingredient_request = {
                "recipe_id": request["id"],
                "ingredients": ingredients,
                "overwrite_ingredients": overwrite_ingredients,
            }
            RecipeIngredientTable.update(self, recipe_ingredient_request)
        if list(request.keys()) == ["name", "id"]:
            return str(request["id"])
        return super().update(request, where, "recipe")

    def get_recipes_by_ingredient(self, request: str | dict):
        output: list[RecipeModel | None] = []
        recipe_ids = []
        if request["include_alias"] and request["key"] == "name":
            ingredients = self.format_result(
                self.select(
                    "ALL",
                    [
                        ("alias", "@>", [request["value"]]),
                        (request["key"], "=", request["value"]),
                        "OR",
                    ],
                    "ingredient",
                )
            )
            recipe_ids.extend(
                [("ingredient_id", "=", ingredient["id"]) for ingredient in ingredients]
            )
            if len(recipe_ids) == 0:
                raise Exception(f"No ingredient found for alias '{request['value']}'")
        else:
            try:
                ingredient = self.format_result(
                    self.select(
                        "ALL", [(request["key"], "=", request["value"])], "ingredient"
                    )
                )[0]
            except IndexError:
                if len(recipe_ids) == 0:
                    raise Exception(
                        f"No ingredient found for {request['key']} '{request['value']}'"
                    )

            recipe_ids.extend([("ingredient_id", "=", ingredient["id"])])

        recipe_ids.append("OR")
        recipe_ids = self.select("recipe_id", recipe_ids, "recipeingredient")
        recipe_ids = list(set(recipe_ids))

        for recipe_id in recipe_ids:
            output.extend(self.get({"key": "id", "value": str(recipe_id[0])}))

        return output

    def delete_entry(self, request):
        found_recipe = self.select("id", [(request["key"], "=", request["value"])])
        if len(found_recipe) == 0:
            raise Exception(
                f"No recipe found for {request['key']} '{request['value']}'"
            )

        recipe_id = found_recipe[0][0]

        self.delete([("recipe_id", "=", recipe_id)], "recipeingredient")
        return super().delete_entry(request)

    def delete_ingredients(self, request):
        found_recipe = self.select("id", [(request["key"], "=", request["value"])])
        if len(found_recipe) == 0:
            raise Exception(
                f"No recipe found for {request['key']} '{request['value']}'"
            )
        if len(request["ingredients"]) == 0:
            raise Exception("No ingredients found in request")
        errors = []
        for ingredient in request["ingredients"]:
            found_ingredient = self.select(
                "id",
                [
                    (
                        "id" if ingredient["id"] else "name",
                        "=",
                        ingredient["id"] if ingredient["id"] else ingredient["name"],
                    )
                ],
                "ingredient",
            )
            if found_ingredient:
                ingredient["id"] = found_ingredient[0][0]
                where = [
                    ("recipe_id", "=", found_recipe[0][0]),
                    ("ingredient_id", "=", ingredient["id"]),
                    "AND",
                ]
                self.delete(where, "recipeingredient")
            else:
                errors.append(ingredient["id" if ingredient["id"] else "name"])
        if len(errors) == len(request["ingredients"]):
            raise Exception(
                f"No ingredients found for {"id" if ingredient['id'] else "name"} '{','.join(errors)}'"
            )
        else:
            return f"Deleted ingredients '{','.join([ingredient['name'] for ingredient in request['ingredients'] if ingredient['id'] not in errors])}' for recipe with {request['key']} '{request['value']}'"

    def update_functions(self):
        self.logger.debug(f"Updating function calls for {self.name}")
        self.set_function("Post", self.add_or_update)
        self.set_function("Get", self.get)
        self.set_function("ByIngredient", self.get_recipes_by_ingredient)
        self.set_function("Delete", self.delete_entry)
        self.set_function("DeleteIngredients", self.delete_ingredients)
