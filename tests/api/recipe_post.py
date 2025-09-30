from tests.api.base_test import BaseAPITest
import json
import re


class TestRecipePost(BaseAPITest):
    def __init__(self, methodName="runTest", client=None):
        super().__init__(methodName, client)
        self.endpoint = "Recipe"
        with open("src/database/structure/testdata/recipes.json", "r") as f:
            self.recipes = json.load(f)
        with open("src/database/structure/testdata/ingredients.json", "r") as f:
            self.ingredients = json.load(f)

    def test_post_positive_missing_optional_parameters(self):
        request = {"name": "TestRecipeMissingOptionalParameters"}
        response = self.client.post(f"/api/{self.endpoint}/", json=request)
        if response.status_code == self.post_success_code:
            response_recipe = response.json()["Result"]
            recipe_id = re.search(
                r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
                response_recipe,
            ).group()
            self.assertEqual(f"Created 'recipe' with id '{recipe_id}'", response_recipe)
            get_response = self.client.get(f"/api/{self.endpoint}/?id={recipe_id}")
            if get_response.status_code == self.get_success_code:
                get_recipe = get_response.json()["Result"][0]
                self.assertEqual(get_recipe["name"], request["name"])
                self.assertEqual(get_recipe["description"], None)
                self.assertEqual(get_recipe["ingredients"], [])
                self.assertEqual(get_recipe["id"], recipe_id)
            else:
                self.fail(
                    f"Did not get status code {self.post_success_code} - {get_response.status_code}"
                )
        else:
            self.fail(
                f"Did not get status code {self.post_success_code} - {response.status_code}"
            )

    def test_post_positive(self):
        request = {
            "name": "TestRecipeAllParameters",
            "description": "TestRecipeAllParameters",
            "ingredients": [
                {"name": self.ingredients[0]["name"], "quantity": "100"},
                {"name": self.ingredients[1]["name"], "quantity": "200"},
            ],
        }
        response = self.client.post(f"/api/{self.endpoint}/", json=request)
        if response.status_code == self.post_success_code:
            response_recipe = response.json()["Result"]
            recipe_id = re.search(
                r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
                response_recipe,
            ).group()
            self.assertEqual(f"Created 'recipe' with id '{recipe_id}'", response_recipe)
            get_response = self.client.get(f"/api/{self.endpoint}/?id={recipe_id}")
            if get_response.status_code == self.get_success_code:
                get_recipe = get_response.json()["Result"][0]
                self.assertEqual(get_recipe["name"], request["name"])
                self.assertEqual(get_recipe["description"], request["description"])
                self.assertEqual(get_recipe["ingredients"], request["ingredients"])
                self.assertEqual(get_recipe["id"], recipe_id)
            else:
                self.fail(
                    f"Did not get status code {self.post_success_code} - {get_response.status_code}"
                )
        else:
            self.fail(
                f"Did not get status code {self.post_success_code} - {response.status_code}"
            )

    def test_post_positive_unknown_ingredient(self):
        request = {
            "name": "TestRecipeUnknownIngredients",
            "description": "TestRecipeUnknownIngredients",
            "ingredients": [
                {"name": "IncorrectIngredient1", "quantity": "100"},
                {"name": "IncorrectIngredient2", "quantity": "200"},
            ],
        }
        response = self.client.post(f"/api/{self.endpoint}/", json=request)
        if response.status_code == self.post_success_code:
            response_recipe = response.json()["Result"]
            recipe_id = re.search(
                r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
                response_recipe,
            ).group()
            self.assertEqual(f"Created 'recipe' with id '{recipe_id}'", response_recipe)
            get_response = self.client.get(f"/api/{self.endpoint}/?id={recipe_id}")
            if get_response.status_code == self.get_success_code:
                get_recipe = get_response.json()["Result"][0]
                self.assertEqual(get_recipe["name"], request["name"])
                self.assertEqual(get_recipe["description"], request["description"])
                self.assertEqual(get_recipe["ingredients"], [])
                self.assertEqual(get_recipe["id"], recipe_id)
            else:
                self.fail(
                    f"Did not get status code {self.post_success_code} - {get_response.status_code}"
                )
        else:
            self.fail(
                f"Did not get status code {self.post_success_code} - {response.status_code}"
            )

    def test_post_negative_missing_name(self):
        request = {"description": "TestRecipeMissingName"}
        response = self.client.post(f"/api/{self.endpoint}/", json=request)
        if response.status_code == self.bad_request_error_code:
            response_recipe = response.json()["Result"]
            self.assertEqual("No name found in request", response_recipe)
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )

    def test_post_positive_update_single_parameter(self):
        request = {
            "name": self.recipes[0]["name"],
            "ingredients": [{"name": self.ingredients[1]["name"], "quantity": "100"}],
        }
        response = self.client.post(f"/api/{self.endpoint}/", json=request)
        if response.status_code == self.post_success_code:
            response_recipe = response.json()["Result"]
            recipe_id = re.search(
                r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
                response_recipe,
            ).group()
            self.assertEqual(f"Updated 'recipe' with id '{recipe_id}'", response_recipe)
            get_response = self.client.get(f"/api/{self.endpoint}/?id={recipe_id}")
            if get_response.status_code == self.get_success_code:
                get_recipe = get_response.json()["Result"][0]
                self.assertEqual(get_recipe["name"], request["name"])
                self.recipes[0]["ingredients"].extend(request["ingredients"])
                self.assertEqual(
                    get_recipe["ingredients"], self.recipes[0]["ingredients"]
                )
                self.assertEqual(get_recipe["id"], recipe_id)
            else:
                self.fail(
                    f"Did not get status code {self.post_success_code} - {get_response.status_code}"
                )
        else:
            self.fail(
                f"Did not get status code {self.post_success_code} - {response.status_code}"
            )

    def test_post_positive_update_all_parameters(self):
        request = {
            "name": self.recipes[1]["name"],
            "description": "TestRecipeUpdateAllParameters",
            "ingredients": [
                {"name": self.recipes[1]["ingredients"][0]["name"], "quantity": "100"},
                {"name": "Ingredient1", "quantity": "200"},
            ],
        }
        response = self.client.post(f"/api/{self.endpoint}/", json=request)
        if response.status_code == self.post_success_code:
            response_recipe = response.json()["Result"]
            recipe_id = re.search(
                r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
                response_recipe,
            ).group()
            self.assertEqual(f"Updated 'recipe' with id '{recipe_id}'", response_recipe)
            get_response = self.client.get(f"/api/{self.endpoint}/?id={recipe_id}")
            if get_response.status_code == self.get_success_code:
                get_recipe = get_response.json()["Result"][0]
                self.recipes[1]["ingredients"].append(request["ingredients"][1])
                self.assertEqual(get_recipe["name"], request["name"])
                self.assertEqual(get_recipe["description"], request["description"])
                self.assertEqual(
                    get_recipe["ingredients"][2], request["ingredients"][0]
                )
                self.assertEqual(
                    get_recipe["ingredients"][3], request["ingredients"][1]
                )
                self.assertEqual(
                    len(get_recipe["ingredients"]), len(self.recipes[1]["ingredients"])
                )
                self.assertEqual(get_recipe["id"], recipe_id)
            else:
                self.fail(
                    f"Did not get status code {self.post_success_code} - {get_response.status_code}"
                )
        else:
            self.fail(
                f"Did not get status code {self.post_success_code} - {response.status_code}"
            )

    def test_post_positive_update_incorrect_ingredient(self):
        request = {
            "name": self.recipes[2]["name"],
            "ingredients": [{"name": "IncorrectIngredient1", "quantity": "200"}],
        }
        response = self.client.post(f"/api/{self.endpoint}/", json=request)
        if response.status_code == self.post_success_code:
            response_recipe = response.json()["Result"]
            recipe_id = re.search(
                r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
                response_recipe,
            ).group()
            self.assertEqual(f"Updated 'recipe' with id '{recipe_id}'", response_recipe)
            get_response = self.client.get(f"/api/{self.endpoint}/?id={recipe_id}")
            if get_response.status_code == self.get_success_code:
                get_recipe = get_response.json()["Result"][0]
                self.assertEqual(get_recipe["name"], request["name"])
                self.assertEqual(
                    get_recipe["description"], self.recipes[2]["description"]
                )
                self.assertEqual(
                    get_recipe["ingredients"], self.recipes[2]["ingredients"]
                )
                self.assertEqual(get_recipe["id"], recipe_id)
            else:
                self.fail(
                    f"Did not get status code {self.post_success_code} - {get_response.status_code}"
                )
        else:
            self.fail(
                f"Did not get status code {self.post_success_code} - {response.status_code}"
            )

    def test_post_positive_update_overwrite_alias_incorrect_ingredient(self):
        request = {
            "name": self.recipes[2]["name"],
            "ingredients": [{"name": "IncorrectIngredient1", "quantity": "200"}],
        }
        response = self.client.post(
            f"/api/{self.endpoint}/?overwrite_alias=true", json=request
        )
        if response.status_code == self.post_success_code:
            response_recipe = response.json()["Result"]
            recipe_id = re.search(
                r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
                response_recipe,
            ).group()
            self.assertEqual(f"Updated 'recipe' with id '{recipe_id}'", response_recipe)
            get_response = self.client.get(f"/api/{self.endpoint}/?id={recipe_id}")
            if get_response.status_code == self.get_success_code:
                get_recipe = get_response.json()["Result"][0]
                self.assertEqual(get_recipe["name"], request["name"])
                self.assertEqual(
                    get_recipe["description"], self.recipes[2]["description"]
                )
                self.assertEqual(
                    get_recipe["ingredients"], self.recipes[2]["ingredients"]
                )
                self.assertEqual(get_recipe["id"], recipe_id)
            else:
                self.fail(
                    f"Did not get status code {self.post_success_code} - {get_response.status_code}"
                )
        else:
            self.fail(
                f"Did not get status code {self.post_success_code} - {response.status_code}"
            )

    def test_post_positive_update_overwrite_ingredients(self):
        request = {
            "name": self.recipes[2]["name"],
            "ingredients": [{"name": "Ingredient1", "quantity": "200"}],
        }
        response = self.client.post(
            f"/api/{self.endpoint}/?overwrite_ingredients=true", json=request
        )
        if response.status_code == self.post_success_code:
            response_recipe = response.json()["Result"]
            recipe_id = re.search(
                r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
                response_recipe,
            ).group()
            self.assertEqual(f"Updated 'recipe' with id '{recipe_id}'", response_recipe)
            get_response = self.client.get(f"/api/{self.endpoint}/?id={recipe_id}")
            if get_response.status_code == self.get_success_code:
                get_recipe = get_response.json()["Result"][0]
                self.assertEqual(get_recipe["name"], request["name"])
                self.assertEqual(
                    get_recipe["description"], self.recipes[2]["description"]
                )
                self.assertEqual(get_recipe["ingredients"], request["ingredients"])
                self.assertEqual(get_recipe["id"], recipe_id)
            else:
                self.fail(
                    f"Did not get status code {self.post_success_code} - {get_response.status_code}"
                )
        else:
            self.fail(
                f"Did not get status code {self.post_success_code} - {response.status_code}"
            )

    def test_post_positive_update_overwrite_ingredients_no_ingredients(self):
        request = {
            "name": self.recipes[3]["name"],
        }
        response = self.client.post(
            f"/api/{self.endpoint}/?overwrite_ingredients=true", json=request
        )
        if response.status_code == self.post_success_code:
            response_recipe = response.json()["Result"]
            recipe_id = re.search(
                r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
                response_recipe,
            ).group()
            self.assertEqual(f"Updated 'recipe' with id '{recipe_id}'", response_recipe)
            get_response = self.client.get(f"/api/{self.endpoint}/?id={recipe_id}")
            if get_response.status_code == self.get_success_code:
                get_recipe = get_response.json()["Result"][0]
                self.assertEqual(get_recipe["name"], request["name"])
                self.assertEqual(
                    get_recipe["description"], self.recipes[3]["description"]
                )
                self.assertEqual(get_recipe["ingredients"], [])
                self.assertEqual(get_recipe["id"], recipe_id)
            else:
                self.fail(
                    f"Did not get status code {self.post_success_code} - {get_response.status_code}"
                )
        else:
            self.fail(
                f"Did not get status code {self.post_success_code} - {response.status_code}"
            )
