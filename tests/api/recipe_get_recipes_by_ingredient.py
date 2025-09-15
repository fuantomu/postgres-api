from tests.api.base_test import BaseAPITest
import json

class TestRecipesGetRecipesByIngredient(BaseAPITest):
    def __init__(self, methodName="runTest", client=None):
        super().__init__(methodName, client)
        self.endpoint = "Recipe/GetRecipesByIngredient"
        self.ingredient_recipes = {}
        with open(f"src/database/structure/testdata/recipes.json","r") as f:
            self.recipes = json.load(f)
        with open(f"src/database/structure/testdata/ingredients.json","r") as f:
            self.ingredients = json.load(f)
        for recipe in self.recipes:
            for ingredient in recipe["ingredients"]:
                if not self.ingredient_recipes.get(ingredient["name"]):
                    self.ingredient_recipes[ingredient['name']] = []
                self.ingredient_recipes[ingredient['name']].extend([recipe['name']])
                self.ingredient_recipes[ingredient['name']] = list(set(self.ingredient_recipes[ingredient['name']]))

    def test_get_negative_missing_id_name(self):
        response = self.client.get(f"/api/{self.endpoint}/")
        if response.status_code == self.bad_request_error_code:
            self.assertEqual("Missing one or more required parameters in: 'ingredient_id,ingredient'", response.text)
        else:
            self.fail(f"Did not get status code {self.bad_request_error_code} - {response.status_code}")

    def test_get_by_name_positive(self):
        for recipe in self.recipes:
            for ingredient in recipe["ingredients"]:
                response = self.client.get(f"/api/{self.endpoint}/?ingredient={ingredient['name']}")
                if response.status_code == self.get_success_code:
                    response_recipes = response.json()["Result"]

                    self.assertEqual(len(response_recipes), len(self.ingredient_recipes[ingredient["name"]]))
                    self.assertIn(recipe["name"],[_item["name"] for _item in response_recipes])
                    for response_recipe in response_recipes:
                        response_ingredient_names = [_item["name"] for _item in response_recipe["ingredients"]]
                        self.assertIn(ingredient["name"],response_ingredient_names)     
                else:
                    self.fail(f"Did not get status code {self.get_success_code} - {response.status_code}")
    
    def test_get_by_id_positive(self):
        for recipe in self.recipes:
            for ingredient in recipe["ingredients"]:
                ingredient_id = [_ingredient["id"] for _ingredient in self.ingredients if _ingredient["name"] == ingredient["name"]][0]
                response = self.client.get(f"/api/{self.endpoint}/?ingredient_id={ingredient_id}")
                if response.status_code == self.get_success_code:
                    response_recipes = response.json()["Result"]

                    self.assertEqual(len(response_recipes), len(self.ingredient_recipes[ingredient["name"]]))
                    self.assertIn(recipe["name"],[_item["name"] for _item in response_recipes])
                    for response_recipe in response_recipes:
                        response_ingredient_names = [_item["name"] for _item in response_recipe["ingredients"]]
                        self.assertIn(ingredient["name"],response_ingredient_names)     
                else:
                    self.fail(f"Did not get status code {self.get_success_code} - {response.status_code}")

    def test_get_by_name_negative_unknown_name(self):
        test_name = "Ingredient1000"
        response = self.client.get(f"/api/{self.endpoint}/?ingredient={test_name}")
        if response.status_code == self.bad_request_error_code:
            self.assertEqual(f"No ingredient found for name '{test_name}'", response.json()["Result"])
        else:
            self.fail(f"Did not get status code {self.bad_request_error_code} - {response.status_code}")

    def test_get_by_id_negative_unknown_id(self):
        test_id = '02000000-1111-11f0-909f-0242ac120007'
        response = self.client.get(f"/api/{self.endpoint}/?ingredient_id={test_id}")
        if response.status_code == self.bad_request_error_code:
            self.assertEqual(f"No ingredient found for id '{test_id}'", response.json()["Result"])
        else:
            self.fail(f"Did not get status code {self.bad_request_error_code} - {response.status_code}")
    
    def test_get_by_id_negative_incorrect_id(self):
        test_id = '124235'
        response = self.client.get(f"/api/{self.endpoint}/?ingredient_id={test_id}")
        if response.status_code == self.bad_request_error_code:
            response_recipe = response.json()["Result"]
            self.assertEqual(f"Value '{test_id}' does not match type of 'uuid'", response_recipe)
        else:
            self.fail(f"Did not get status code {self.bad_request_error_code} - {response.status_code}")

    def test_get_by_name_positive_include_alias(self):
        ingredient = self.ingredients[1]
        for alias_name in ingredient["alias"]:
            response = self.client.get(f"/api/{self.endpoint}/?ingredient={alias_name}&include_alias=true")
            if response.status_code == self.get_success_code:
                response_recipes = response.json()["Result"]

                self.assertEqual(len(response_recipes), len(self.ingredient_recipes[ingredient["name"]]))
                self.assertIn(self.recipes[1]["name"],[_item["name"] for _item in response_recipes])
                for response_recipe in response_recipes:
                    response_ingredient_names = [_item["name"] for _item in response_recipe["ingredients"]]
                    self.assertIn(ingredient["name"],response_ingredient_names)     
            else:
                self.fail(f"Did not get status code {self.get_success_code} - {response.status_code}")
    
    def test_get_by_name_negative_include_alias(self):
        alias_name = "Alias1000"
        response = self.client.get(f"/api/{self.endpoint}/?ingredient={alias_name}&include_alias=true")
        if response.status_code == self.bad_request_error_code:
            response_recipe = response.json()["Result"]
            self.assertEqual(f"No ingredient found for alias '{alias_name}'", response_recipe)
        else:
            self.fail(f"Did not get status code {self.bad_request_error_code} - {response.status_code}")