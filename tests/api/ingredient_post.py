from tests.api.base_test import BaseAPITest
import json
import re

class TestIngredientPost(BaseAPITest):
    def __init__(self, methodName="runTest", client=None):
        super().__init__(methodName, client)
        self.endpoint = "Ingredient"
        with open(f"src/database/structure/testdata/ingredients.json","r") as f:
            self.ingredients = json.load(f)

    def test_post_positive_missing_optional_parameters(self):
        request = {
            "name": "TestMissingOptionalParameters"
        }
        response = self.client.post(f"/api/{self.endpoint}/", json=request)
        if response.status_code == self.post_success_code:
            response_ingredient = response.json()["Result"]
            ingredient_id = re.search(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", response_ingredient).group()
            self.assertEqual(f"Created 'ingredient' with id '{ingredient_id}'", response_ingredient)
            get_response = self.client.get(f"/api/{self.endpoint}/?id={ingredient_id}")
            if get_response.status_code == self.get_success_code:
                get_ingredient = get_response.json()["Result"][0]
                self.assertEqual(get_ingredient["name"],request["name"])
                self.assertEqual(get_ingredient["description"],None)
                self.assertEqual(get_ingredient["alias"],None)
                self.assertEqual(get_ingredient["id"],ingredient_id)
            else:
                self.fail(f"Did not get status code {self.post_success_code} - {get_response.status_code}")
        else:
            self.fail(f"Did not get status code {self.post_success_code} - {response.status_code}")

    def test_post_positive(self):
        request = {
            "name": "TestIngredientAllParameters",
            "description": "TestIngredientAllParameters",
            "alias": ["TestIngredientAllParametersAlias1","TestIngredientAllParametersAlias2"]
        }
        response = self.client.post(f"/api/{self.endpoint}/", json=request)
        if response.status_code == self.post_success_code:
            response_ingredient = response.json()["Result"]
            ingredient_id = re.search(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", response_ingredient).group()
            self.assertEqual(f"Created 'ingredient' with id '{ingredient_id}'", response_ingredient)
            get_response = self.client.get(f"/api/{self.endpoint}/?id={ingredient_id}")
            if get_response.status_code == self.get_success_code:
                get_ingredient = get_response.json()["Result"][0]
                self.assertEqual(get_ingredient["name"],request["name"])
                self.assertEqual(get_ingredient["description"],request["description"])
                self.assertEqual(get_ingredient["alias"],request["alias"])
                self.assertEqual(get_ingredient["id"],ingredient_id)
            else:
                self.fail(f"Did not get status code {self.post_success_code} - {get_response.status_code}")
        else:
            self.fail(f"Did not get status code {self.post_success_code} - {response.status_code}")
    
    def test_post_negative_missing_name(self):
        request = {
            "description": "TestDescription",
            "alias": []
        }
        response = self.client.post(f"/api/{self.endpoint}/", json=request)
        if response.status_code == self.bad_request_error_code:
            response_ingredient = response.json()["Result"]
            self.assertEqual(f"No name found in request", response_ingredient)
        else:
            self.fail(f"Did not get status code {self.bad_request_error_code} - {response.status_code}")
    
    def test_post_positive_update_single_parameters(self):
        ingredient = self.ingredients[1].copy()
        new_alias = ["ChangedAlias1","ChangedAlias2"]
        ingredient["alias"] = new_alias

        response = self.client.post(f"/api/{self.endpoint}/", json=ingredient)
        if response.status_code == self.post_success_code:
            response_ingredient = response.json()["Result"]
            self.assertEqual(f"Updated 'ingredient' with id '{ingredient['id']}'", response_ingredient)
            response_changed = self.client.get(f"/api/{self.endpoint}/?id={ingredient['id']}")
            if response_changed.status_code == self.get_success_code:
                response_changed_ingredient = response_changed.json()["Result"][0]
                self.assertNotEqual(ingredient['alias'], response_changed_ingredient['alias'])
                self.assertEqual(ingredient['description'], response_changed_ingredient['description'])
                for alias in ingredient['alias']:
                    self.assertIn(alias, response_changed_ingredient['alias'])
            else:
                self.fail(f"Did not get status code {self.get_success_code} - {response_changed.status_code}")
        else:
            self.fail(f"Did not get status code {self.post_success_code} - {response.status_code}")
            
    def test_post_positive_update_all_parameters(self):
        ingredient = self.ingredients[0].copy()
        new_description = "Changed Description"
        ingredient["description"] = new_description
        new_alias = ["ChangedAlias1","ChangedAlias2"]
        ingredient["alias"] = new_alias

        response = self.client.post(f"/api/{self.endpoint}/", json=ingredient)
        if response.status_code == self.post_success_code:
            response_ingredient = response.json()["Result"]
            self.assertEqual(f"Updated 'ingredient' with id '{ingredient['id']}'", response_ingredient)
            response_changed = self.client.get(f"/api/{self.endpoint}/?id={ingredient['id']}")
            if response_changed.status_code == self.get_success_code:
                response_changed_ingredient = response_changed.json()["Result"][0]
                self.assertDictEqual(ingredient, response_changed_ingredient)
            else:
                self.fail(f"Did not get status code {self.get_success_code} - {response_changed.status_code}")
        else:
            self.fail(f"Did not get status code {self.post_success_code} - {response.status_code}")
            
    def test_post_positive_update_alias_overwrite_alias(self):
        ingredient = self.ingredients[1].copy()
        new_alias = ["ChangedAlias1","ChangedAlias2"]
        ingredient["alias"] = new_alias

        response = self.client.post(f"/api/{self.endpoint}/?overwrite_alias=true", json=ingredient)
        if response.status_code == self.post_success_code:
            response_ingredient = response.json()["Result"]
            self.assertEqual(f"Updated 'ingredient' with id '{ingredient['id']}'", response_ingredient)
            response_changed = self.client.get(f"/api/{self.endpoint}/?id={ingredient['id']}")
            if response_changed.status_code == self.get_success_code:
                response_changed_ingredient = response_changed.json()["Result"][0]
                self.assertEqual(ingredient['alias'], response_changed_ingredient['alias'])
            else:
                self.fail(f"Did not get status code {self.get_success_code} - {response_changed.status_code}")
        else:
            self.fail(f"Did not get status code {self.post_success_code} - {response.status_code}")