from pydantic import BaseModel
from typing import List
from src.models.recipe_ingredients_model import RecipeIngredientModel


class RecipeModel(BaseModel):
    id: str | None = None
    name: str | None = None
    description: str | None = None
    ingredients: List[RecipeIngredientModel] | None = None


class DeleteIngredientsModel(BaseModel):
    id: str | None = None
    name: str | None = None
