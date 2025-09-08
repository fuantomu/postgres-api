from pydantic import BaseModel, Field
from typing import List
from models.recipe_ingredients_model import RecipeIngredient, RecipeIngredientModel
from uuid import UUID, uuid4

class Recipe:
    def __init__(self, name: str, description: str, ingredients: List[RecipeIngredient]):
        self.name = name
        self.description = description
        self.ingredients = ingredients

class RecipeModel(BaseModel):
    id: UUID | None = None
    name: str
    description: str
    ingredients: List[RecipeIngredientModel] = Field(default_factory=list)