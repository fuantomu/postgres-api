from tests.api.base_test import BaseAPITest
import json


class TestRecipeIngredientDelete(BaseAPITest):
    def __init__(self, methodName="runTest", client=None):
        super().__init__(methodName, client)
        self.endpoint = "Recipe/Ingredient"
        with open("src/database/structure/testdata/recipes.json", "r") as f:
            self.recipes = json.load(f)
        with open("src/database/structure/testdata/ingredients.json", "r") as f:
            self.ingredients = json.load(f)

    def test_delete_ingredient_by_name_positive(self):
        recipe = self.recipes[9]
        request = [
            {"name": recipe["ingredients"][0]["name"]},
            {"name": recipe["ingredients"][1]["name"]},
        ]
        response = self.client.request(
            "DELETE", f"/api/{self.endpoint}/?name={recipe['name']}", json=request
        )
        if response.status_code == self.base_success_code:
            response_delete = response.json()["Result"]
            self.assertEqual(
                f"Deleted ingredients '{','.join(ingredient['name'] for ingredient in request)}' for recipe with name '{recipe['name']}'",
                response_delete,
            )
            response_recipes = self.client.get(f"/api/Recipe/?name={recipe['name']}")
            if response_recipes.status_code == self.get_success_code:
                result_recipes = response_recipes.json()["Result"][0]
                self.assertEqual(
                    recipe["ingredients"][2:], result_recipes["ingredients"]
                )
            else:
                self.fail(
                    f"Did not get status code {self.get_success_code} - {response_recipes.status_code}"
                )
        else:
            self.fail(
                f"Did not get status code {self.base_success_code} - {response.status_code}"
            )

    def test_delete_ingredient_by_name_negative_unknown_name(self):
        recipe_name = "TestRecipe1000"
        request = [
            {"name": self.recipes[4]["ingredients"][0]["name"]},
            {"name": self.recipes[4]["ingredients"][1]["name"]},
        ]
        response = self.client.request(
            "DELETE", f"/api/{self.endpoint}/?name={recipe_name}", json=request
        )
        if response.status_code == self.bad_request_error_code:
            response_delete = response.json()["Result"]
            self.assertEqual(
                f"No recipe found for name '{recipe_name}'", response_delete
            )
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )

    def test_delete_ingredient_by_id_positive(self):
        recipe = self.recipes[7]
        request = [{"name": recipe["ingredients"][0]["name"]}]
        response = self.client.request(
            "DELETE", f"/api/{self.endpoint}/?id={recipe['id']}", json=request
        )
        if response.status_code == self.base_success_code:
            response_delete = response.json()["Result"]
            self.assertEqual(
                f"Deleted ingredients '{','.join(ingredient['name'] for ingredient in request)}' for recipe with id '{recipe['id']}'",
                response_delete,
            )
            response_recipes = self.client.get(f"/api/Recipe/?id={recipe['id']}")
            if response_recipes.status_code == self.get_success_code:
                result_recipes = response_recipes.json()["Result"][0]
                self.assertEqual(
                    recipe["ingredients"][1:], result_recipes["ingredients"]
                )
            else:
                self.fail(
                    f"Did not get status code {self.get_success_code} - {response_recipes.status_code}"
                )
        else:
            self.fail(
                f"Did not get status code {self.base_success_code} - {response.status_code}"
            )

    def test_delete_ingredient_by_id_negative_unknown_id(self):
        recipe_id = "07000000-1111-11f0-909f-0242ac120007"
        request = [{"name": self.recipes[8]["ingredients"][0]["name"]}]
        response = self.client.request(
            "DELETE", f"/api/{self.endpoint}/?id={recipe_id}", json=request
        )
        if response.status_code == self.bad_request_error_code:
            response_delete = response.json()["Result"]
            self.assertEqual(f"No recipe found for id '{recipe_id}'", response_delete)
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )

    def test_delete_ingredient_by_id_negative_incorrect_id(self):
        recipe_id = "12345"
        request = [{"name": self.recipes[8]["ingredients"][0]["name"]}]
        response = self.client.request(
            "DELETE", f"/api/{self.endpoint}/?id={recipe_id}", json=request
        )
        if response.status_code == self.bad_request_error_code:
            response_delete = response.json()["Result"]
            self.assertEqual(
                f"Value '{recipe_id}' does not match type of 'uuid'", response_delete
            )
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )

    def test_delete_ingredient_negative_empty_request(self):
        recipe = self.recipes[8]
        request = []
        response = self.client.request(
            "DELETE", f"/api/{self.endpoint}/?name={recipe['name']}", json=request
        )
        if response.status_code == self.bad_request_error_code:
            response_delete = response.json()["Result"]
            self.assertEqual("No ingredients found in request", response_delete)
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )

    def test_delete_ingredient_negative_bad_ingredient_id(self):
        recipe = self.recipes[8]
        request = [{"id": "07000000-1111-11f0-909f-0242ac120007"}]
        response = self.client.request(
            "DELETE", f"/api/{self.endpoint}/?name={recipe['name']}", json=request
        )
        if response.status_code == self.bad_request_error_code:
            response_delete = response.json()["Result"]
            self.assertEqual(
                f"No ingredients found for id '{request[0]['id']}'", response_delete
            )
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )

    def test_delete_ingredient_positive_bad_ingredient_id(self):
        recipe = self.recipes[8]
        request = [
            {"id": "07000000-1111-11f0-909f-0242ac120007"},
            {"name": "Ingredient5"},
        ]
        response = self.client.request(
            "DELETE", f"/api/{self.endpoint}/?name={recipe['name']}", json=request
        )
        if response.status_code == self.base_success_code:
            response_delete = response.json()["Result"]
            self.assertEqual(
                f"Deleted ingredients '{request[1]['name']}' for recipe with name '{recipe['name']}'",
                response_delete,
            )
            response_recipes = self.client.get(f"/api/Recipe/?id={recipe['id']}")
            if response_recipes.status_code == self.get_success_code:
                result_recipes = response_recipes.json()["Result"][0]
                self.assertEqual(
                    [recipe["ingredients"][0]], result_recipes["ingredients"]
                )
            else:
                self.fail(
                    f"Did not get status code {self.get_success_code} - {response_recipes.status_code}"
                )
        else:
            self.fail(
                f"Did not get status code {self.base_success_code} - {response.status_code}"
            )
