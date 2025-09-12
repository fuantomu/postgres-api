from pydantic import BaseModel, Field
from typing import List
from models.recipe_ingredients_model import RecipeIngredientModel

class RecipeModel(BaseModel):
    id: str | None = None
    name: str | None = None
    description: str | None = None
    ingredients: List[RecipeIngredientModel] = Field(default_factory=list)