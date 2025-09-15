import psycopg
import src.database.tables as tables
from src.logger.log import get_logger
from uuid import UUID
import json

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
    with open(f"src/database/structure/testdata/ingredients.json","r") as f:
        ingredients = json.load(f)
    for ingredient in ingredients:
        ingredient_table.insert(ingredient)

def add_recipes(connection: psycopg.Connection):
    recipes_table = tables.RecipeTable(connection, "Recipe")
    with open(f"src/database/structure/testdata/recipes.json","r") as f:
        recipes = json.load(f)
    for recipe in recipes:
        recipes_table.insert(recipe)