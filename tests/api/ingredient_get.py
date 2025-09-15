from tests.api.base_test import BaseAPITest
import json


class TestIngredientGet(BaseAPITest):
    def __init__(self, methodName="runTest", client=None):
        super().__init__(methodName, client)
        self.endpoint = "Ingredient"
        with open("src/database/structure/testdata/ingredients.json", "r") as f:
            self.ingredients = json.load(f)

    def test_get_by_id_positive(self):
        for ingredient in self.ingredients:
            response = self.client.get(f"/api/{self.endpoint}/?id={ingredient['id']}")
            if response.status_code == self.get_success_code:
                response_ingredient = response.json()["Result"][0]
                for key in ingredient.keys():
                    self.assertEqual(
                        response_ingredient[key],
                        ingredient[key],
                        f"{key} is not equal: {response_ingredient[key]} - {ingredient[key]}",
                    )
            else:
                self.fail(
                    f"Did not get status code {self.get_success_code} - {response.status_code}"
                )

    def test_get_by_id_negative_incorrect_id(self):
        test_id = "12412414"
        response = self.client.get(f"/api/{self.endpoint}/?id={test_id}")
        if response.status_code == self.bad_request_error_code:
            response_ingredient = response.json()["Result"]
            self.assertEqual(
                f"Value '{test_id}' does not match type of 'uuid'", response_ingredient
            )
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )

    def test_get_by_id_negative_unknown_id(self):
        test_id = "02000000-0000-11f0-909f-0242ac120007"
        response = self.client.get(f"/api/{self.endpoint}/?id={test_id}")
        if response.status_code == self.bad_request_error_code:
            response_ingredient = response.json()["Result"]
            self.assertEqual(
                f"No ingredient found for id '{test_id}'", response_ingredient
            )
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )

    def test_get_by_name_positive(self):
        for ingredient in self.ingredients:
            response = self.client.get(
                f"/api/{self.endpoint}/?name={ingredient['name']}"
            )
            if response.status_code == self.get_success_code:
                response_ingredient = response.json()["Result"][0]
                for key in ingredient.keys():
                    self.assertEqual(
                        response_ingredient[key],
                        ingredient[key],
                        f"{key} is not equal: {response_ingredient[key]} - {ingredient[key]}",
                    )
            else:
                self.fail(
                    f"Did not get status code {self.get_success_code} - {response.status_code}"
                )

    def test_get_by_name_negative_unknown_name(self):
        test_name = "Ingredient1000"
        response = self.client.get(f"/api/{self.endpoint}/?name={test_name}")
        if response.status_code == self.bad_request_error_code:
            response_ingredient = response.json()["Result"]
            self.assertEqual(
                f"No ingredient found for name '{test_name}'", response_ingredient
            )
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )

    def test_get_all(self):
        response = self.client.get(f"/api/{self.endpoint}/")
        if response.status_code == self.get_success_code:
            self.assertEqual(
                len(self.ingredients),
                len(response.json()["Result"]),
                f"Did not return same length of result: {len(self.ingredients)} - {len(response.json()['Result'])}",
            )
        else:
            self.fail(
                f"Did not get status code {self.get_success_code} - {response.status_code}"
            )

    def test_get_by_name_search_alias_positive(self):
        ingredient = self.ingredients[2]
        for alias in ingredient["alias"]:
            response = self.client.get(
                f"/api/{self.endpoint}/?name={alias}&search_alias=true"
            )
            if response.status_code == self.get_success_code:
                response_ingredient = response.json()["Result"][0]
                for key in ingredient.keys():
                    self.assertEqual(
                        response_ingredient[key],
                        ingredient[key],
                        f"{key} is not equal: {response_ingredient[key]} - {ingredient[key]}",
                    )
            else:
                self.fail(
                    f"Did not get status code {self.get_success_code} - {response.status_code}"
                )

    def test_get_by_id_search_alias_negative_unknown_name(self):
        test_name = "Alias1000"
        response = self.client.get(
            f"/api/{self.endpoint}/?name={test_name}&search_alias=true"
        )
        if response.status_code == self.get_success_code:
            response_ingredient = response.json()["Result"]
            self.assertEqual([], response_ingredient)
        else:
            self.fail(
                f"Did not get status code {self.get_success_code} - {response.status_code}"
            )

    def test_get_by_id_search_alias_positive(self):
        ingredient = self.ingredients[2]
        response = self.client.get(
            f"/api/{self.endpoint}/?id={ingredient['id']}&search_alias=true"
        )
        if response.status_code == self.get_success_code:
            response_ingredient = response.json()["Result"][0]
            for key in ingredient.keys():
                self.assertEqual(
                    response_ingredient[key],
                    ingredient[key],
                    f"{key} is not equal: {response_ingredient[key]} - {ingredient[key]}",
                )
        else:
            self.fail(
                f"Did not get status code {self.get_success_code} - {response.status_code}"
            )

    def test_get_by_id_search_alias_negative_incorrect_id(self):
        test_id = "12412414"
        response = self.client.get(
            f"/api/{self.endpoint}/?id={test_id}&search_alias=true"
        )
        if response.status_code == self.bad_request_error_code:
            response_ingredient = response.json()["Result"]
            self.assertEqual(
                f"Value '{test_id}' does not match type of 'uuid'", response_ingredient
            )
        else:
            self.fail(
                f"Did not get status code {self.bad_request_error_code} - {response.status_code}"
            )

    def test_get_by_id_search_alias_negative_unknown_id(self):
        test_id = "02000000-0000-11f0-909f-0242ac120007"
        response = self.client.get(
            f"/api/{self.endpoint}/?id={test_id}&search_alias=true"
        )
        if response.status_code == self.get_success_code:
            response_ingredient = response.json()["Result"]
            self.assertEqual([], response_ingredient)
        else:
            self.fail(
                f"Did not get status code {self.get_success_code} - {response.status_code}"
            )
