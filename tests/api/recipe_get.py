from tests.api.base_test import BaseAPITest
import json


class TestRecipeGet(BaseAPITest):
    def __init__(self, methodName="runTest", client=None):
        super().__init__(methodName, client)
        self.endpoint = "Recipe"
        with open("src/database/structure/testdata/recipes.json", "r") as f:
            self.recipes = json.load(f)

    def test_get_by_id_positive(self):
        for recipe in self.recipes:
            response = self.client.get(f"/api/{self.endpoint}/?id={recipe['id']}")
            if response.status_code == self.get_success_code:
                response_recipe = response.json()["Result"][0]
                for key in recipe.keys():
                    self.assertEqual(
                        response_recipe[key],
                        recipe[key],
                        f"{key} is not equal: {response_recipe[key]} - {recipe[key]}",
                    )
            else:
                self.fail(
                    f"Did not get status code {self.get_success_code} - {response.status_code}"
                )

    def test_get_by_id_negative_unknown_id(self):
        test_id = "02000000-1111-11f0-909f-0242ac120007"
        response = self.client.get(f"/api/{self.endpoint}/?id={test_id}")
        if response.status_code == self.bad_request_error_code:
            response_recipe = response.json()["Result"]
            self.assertEqual(f"No recipe found for id '{test_id}'", response_recipe)
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )

    def test_get_by_id_negative_incorrect_id(self):
        test_id = "124235"
        response = self.client.get(f"/api/{self.endpoint}/?id={test_id}")
        if response.status_code == self.bad_request_error_code:
            response_recipe = response.json()["Result"]
            self.assertEqual(
                f"Value '{test_id}' does not match type of 'uuid'", response_recipe
            )
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )

    def test_get_by_name_positive(self):
        for recipe in self.recipes:
            response = self.client.get(f"/api/{self.endpoint}/?name={recipe['name']}")
            if response.status_code == self.get_success_code:
                response_recipe = response.json()["Result"][0]
                for key in recipe.keys():
                    self.assertEqual(
                        response_recipe[key],
                        recipe[key],
                        f"{key} is not equal: {response_recipe[key]} - {recipe[key]}",
                    )
            else:
                self.fail(
                    f"Did not get status code {self.get_success_code} - {response.status_code}"
                )

    def test_get_by_name_negative_unknown_name(self):
        test_name = "Recipe1000"
        response = self.client.get(f"/api/{self.endpoint}/?name={test_name}")
        if response.status_code == self.bad_request_error_code:
            response_recipe = response.json()["Result"]
            self.assertEqual(f"No recipe found for name '{test_name}'", response_recipe)
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )

    def test_get_all(self):
        response = self.client.get(f"/api/{self.endpoint}/")
        if response.status_code == self.get_success_code:
            self.assertEqual(
                len(self.recipes),
                len(response.json()["Result"]),
                f"Did not return same length of result: {len(self.recipes)} - {len(response.json()['Result'])}",
            )
        else:
            self.fail(
                f"Did not get status code {self.get_success_code} - {response.status_code}"
            )
