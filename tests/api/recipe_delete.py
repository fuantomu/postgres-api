from tests.api.base_test import BaseAPITest
import json

class TestRecipeDelete(BaseAPITest):
    def __init__(self, methodName="runTest", client=None):
        super().__init__(methodName, client)
        self.endpoint = "Recipe"
        with open(f"src/database/structure/testdata/recipes.json","r") as f:
            self.recipes = json.load(f)

    def test_delete_by_id_positive(self):
        recipe = self.recipes[3]
        response = self.client.delete(f"/api/{self.endpoint}/?id={recipe['id']}")
        if response.status_code == self.base_success_code:
            response_delete = response.json()["Result"]
            self.assertEqual(f"Deleted recipe with id '{recipe['id']}'", response_delete)
            response_recipes = self.client.get(f"/api/Recipe/?id={recipe['id']}")
            if response_recipes.status_code == self.bad_request_error_code:
                result_recipes = response_recipes.json()["Result"]
                self.assertEqual(f"No recipe found for id '{recipe['id']}'", result_recipes)
            else:
                self.fail(f"Did not get status code {self.bad_request_error_code} - {response_recipes.status_code}")
        else:
            self.fail(f"Did not get status code {self.base_success_code} - {response.status_code}")

    def test_delete_by_id_negative_incorrect_id(self):
        test_id = '12412414'
        response = self.client.delete(f"/api/{self.endpoint}/?id={test_id}")
        if response.status_code == self.bad_request_error_code:
            response_recipe = response.json()["Result"]
            self.assertEqual(f"Value '{test_id}' does not match type of 'uuid'", response_recipe)
        else:
            self.fail(f"Did not get status code {self.bad_request_error_code} - {response.status_code}")
    
    def test_delete_by_id_negative_unknown_id(self):
        test_id = '02000000-1111-11f0-909f-0242ac120007'
        response = self.client.delete(f"/api/{self.endpoint}/?id={test_id}")
        if response.status_code == self.bad_request_error_code:
            response_recipe = response.json()["Result"]
            self.assertEqual(f"No recipe found for id '{test_id}'", response_recipe)
        else:
            self.fail(f"Did not get status code {self.bad_request_error_code} - {response.status_code}")

    def test_delete_by_name_positive(self):
        recipe = self.recipes[2]
        response = self.client.delete(f"/api/{self.endpoint}/?name={recipe['name']}")
        if response.status_code == self.base_success_code:
            response_delete = response.json()["Result"]
            self.assertEqual(f"Deleted recipe with name '{recipe['name']}'", response_delete)
            response_recipes = self.client.get(f"/api/Recipe/?name={recipe['name']}")
            if response_recipes.status_code == self.bad_request_error_code:
                result_recipes = response_recipes.json()["Result"]
                self.assertEqual(f"No recipe found for name '{recipe['name']}'", result_recipes)
            else:
                self.fail(f"Did not get status code {self.bad_request_error_code} - {response_recipes.status_code}")
        else:
            self.fail(f"Did not get status code {self.base_success_code} - {response.status_code}")

    def test_delete_by_id_negative_unknown_name(self):
        test_name = 'recipe1000'
        response = self.client.delete(f"/api/{self.endpoint}/?name={test_name}")
        if response.status_code == self.bad_request_error_code:
            response_recipe = response.json()["Result"]
            self.assertEqual(f"No recipe found for name '{test_name}'", response_recipe)
        else:
            self.fail(f"Did not get status code {self.bad_request_error_code} - {response.status_code}")
