import psycopg
import database.tables as tables
from logger.log import get_logger

logger = get_logger("database")

def initialize_tables(connection: psycopg.Connection):
    logger.info("Initializing tables")

    for table in tables.__all__:
        if table == "table":
            continue

        table_class = find_table(f"{table}table")

        if table_class:
            new_table = table_class(connection, table)
        else:
            new_table = tables.Table(connection, table)
        
        new_table.create()

def find_table(table_name: str):
    for _class in tables.Table.__subclasses__():
        if _class.__name__.lower() == table_name.lower():
            return _class
    return None

def add_ingredients(connection: psycopg.Connection):
    ingredient_table = tables.IngredientTable(connection, "Ingredient")
    ingredients = [{
        "name": "Ingredient1",
        "description": "TestIngredient1"
    },{
        "name": "Ingredient2",
        "description": "TestIngredient2"
    },{
        "name": "Ingredient3",
        "description": "TestIngredient3"
    },{
        "name": "Ingredient4",
        "description": "TestIngredient4"
    }]
    for ingredient in ingredients:
        ingredient_table.insert(ingredient)

def add_recipes(connection: psycopg.Connection):
    recipes_table = tables.RecipeTable(connection, "Recipe")
    recipes = [{
        "name": "Recipe1",
        "description": "TestRecipe1",
        "ingredients": [{
            "name": "Ingredient1",
            "quantity": "5"
        },{
            "name": "Ingredient4",
            "quantity": "3"
        }]
    },{
        "name": "Recipe2",
        "description": "TestRecipe2",
        "ingredients": [{
            "name": "Ingredient2",
            "quantity": "2g"
        },{
            "name": "Ingredient3",
            "quantity": "6g"
        },{
            "name": "Ingredient4",
            "quantity": "34g"
        }]
    },{
        "name": "Recipe3",
        "description": "TestRecipe3",
        "ingredients": [{
            "name": "Ingredient1",
            "quantity": "20g"
        },{
            "name": "Ingredient3",
            "quantity": "12g"
        }]
    }]
    recipe_ids = []
    for recipe in recipes:
        recipe_ids.append(recipes_table.insert(recipe))