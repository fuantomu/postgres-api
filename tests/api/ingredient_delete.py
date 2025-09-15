from tests.api.base_test import BaseAPITest
import json


class TestIngredientDelete(BaseAPITest):
    def __init__(self, methodName="runTest", client=None):
        super().__init__(methodName, client)
        self.endpoint = "Ingredient"
        with open("src/database/structure/testdata/ingredients.json", "r") as f:
            self.ingredients = json.load(f)

    def test_delete_by_id_positive(self):
        ingredient = self.ingredients[3]
        response = self.client.delete(f"/api/{self.endpoint}/?id={ingredient['id']}")
        if response.status_code == self.base_success_code:
            response_delete = response.json()["Result"]
            self.assertEqual(
                f"Deleted ingredient with id '{ingredient['id']}'", response_delete
            )
            response_recipes = self.client.get(
                f"/api/Recipe/ByIngredient/?ingredient_id={ingredient['id']}"
            )
            if response_recipes.status_code == self.bad_request_error_code:
                result_recipes = response_recipes.json()["Result"]
                self.assertEqual(
                    f"No ingredient found for id '{ingredient['id']}'", result_recipes
                )
            else:
                self.fail(
                    f"Did not get status code {self.bad_request_error_code} - {response_recipes.status_code}"
                )
        else:
            self.fail(
                f"Did not get status code {self.base_success_code} - {response.status_code}"
            )

    def test_delete_by_id_negative_incorrect_id(self):
        test_id = "12412414"
        response = self.client.delete(f"/api/{self.endpoint}/?id={test_id}")
        if response.status_code == self.bad_request_error_code:
            response_ingredient = response.json()["Result"]
            self.assertEqual(
                f"Value '{test_id}' does not match type of 'uuid'", response_ingredient
            )
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )

    def test_delete_by_id_negative_unknown_id(self):
        test_id = "02000000-0000-11f0-909f-0242ac120007"
        response = self.client.delete(f"/api/{self.endpoint}/?id={test_id}")
        if response.status_code == self.bad_request_error_code:
            response_ingredient = response.json()["Result"]
            self.assertEqual(
                f"No ingredient found for id '{test_id}'", response_ingredient
            )
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )

    def test_delete_by_name_positive(self):
        ingredient = self.ingredients[2]
        response = self.client.delete(
            f"/api/{self.endpoint}/?name={ingredient['name']}"
        )
        if response.status_code == self.base_success_code:
            response_delete = response.json()["Result"]
            self.assertEqual(
                f"Deleted ingredient with name '{ingredient['name']}'", response_delete
            )
            response_recipes = self.client.get(
                f"/api/Recipe/ByIngredient/?ingredient={ingredient['name']}"
            )
            if response_recipes.status_code == self.bad_request_error_code:
                result_recipes = response_recipes.json()["Result"]
                self.assertEqual(
                    f"No ingredient found for name '{ingredient['name']}'",
                    result_recipes,
                )
            else:
                self.fail(
                    f"Did not get status code {self.bad_request_error_code} - {response_recipes.status_code}"
                )
        else:
            self.fail(
                f"Did not get status code {self.base_success_code} - {response.status_code}"
            )

    def test_delete_by_id_negative_unknown_name(self):
        test_name = "Ingredient1000"
        response = self.client.delete(f"/api/{self.endpoint}/?name={test_name}")
        if response.status_code == self.bad_request_error_code:
            response_ingredient = response.json()["Result"]
            self.assertEqual(
                f"No ingredient found for name '{test_name}'", response_ingredient
            )
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )
