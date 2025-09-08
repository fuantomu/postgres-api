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