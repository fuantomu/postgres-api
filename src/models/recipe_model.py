from pydantic import BaseModel, Field
from typing import List
from models.recipe_ingredients_model import RecipeIngredient, RecipeIngredientModel

class Recipe:
    def __init__(self, name: str, description: str, ingredients: List[RecipeIngredient]):
        self.name = name
        self.description = description
        self.ingredients = ingredients

class RecipeModel(BaseModel):
    name: str
    description: str
    ingredients: List[RecipeIngredientModel] = Field(default_factory=list)