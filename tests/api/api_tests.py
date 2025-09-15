import unittest
from fastapi.testclient import TestClient
from src.server import Server
from tests.api.ingredient_delete import TestIngredientDelete
from tests.api.ingredient_get import TestIngredientGet
from tests.api.ingredient_post import TestIngredientPost
from tests.api.recipe_delete import TestRecipeDelete
from tests.api.recipe_delete_ingredients import TestRecipeIngredientsDelete
from tests.api.recipe_get import TestRecipeGet
from tests.api.recipe_get_recipes_by_ingredient import TestRecipesRecipesByIngredient
from tests.api.recipe_post import TestRecipePost

def get_test_suite(client):
    suite = unittest.TestSuite()
    # for method_name in unittest.defaultTestLoader.getTestCaseNames(TestRecipeGet):
    #    suite.addTest(TestRecipeGet(methodName=method_name, client=client))
    # for method_name in unittest.defaultTestLoader.getTestCaseNames(TestIngredientGet):
    #    suite.addTest(TestIngredientGet(methodName=method_name, client=client))
    # for method_name in unittest.defaultTestLoader.getTestCaseNames(TestRecipesRecipesByIngredient):
    #     suite.addTest(TestRecipesRecipesByIngredient(methodName=method_name, client=client))
    # for method_name in unittest.defaultTestLoader.getTestCaseNames(TestIngredientPost):
    #      suite.addTest(TestIngredientPost(methodName=method_name, client=client))
    # for method_name in unittest.defaultTestLoader.getTestCaseNames(TestRecipePost):
    #      suite.addTest(TestRecipePost(methodName=method_name, client=client))
    # for method_name in unittest.defaultTestLoader.getTestCaseNames(TestIngredientDelete):
    #      suite.addTest(TestIngredientDelete(methodName=method_name, client=client))
    # for method_name in unittest.defaultTestLoader.getTestCaseNames(TestRecipeDelete):
    #      suite.addTest(TestRecipeDelete(methodName=method_name, client=client))
    for method_name in unittest.defaultTestLoader.getTestCaseNames(TestRecipeIngredientsDelete):
         suite.addTest(TestRecipeIngredientsDelete(methodName=method_name, client=client))
    return suite

def init_server():
    server = Server(port=1441, database="cookbook_test")
    server.initialize_endpoints()
    server.initialize_logging()
    server.clean_database()
    server.initialize_database()
    server.test_data()
    return server

if __name__ == "__main__":
    server = init_server()
    client = TestClient(server.app)

    suite = get_test_suite(client)
    runner = unittest.TextTestRunner()
    runner.run(suite)
    
    