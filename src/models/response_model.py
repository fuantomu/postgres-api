from typing import List
from pydantic import BaseModel
from src.models.ingredient_model import IngredientModel
from src.models.recipe_model import RecipeModel


class BaseResponseModel(BaseModel):
    Result: str


class IngredientResponseModel(BaseModel):
    Result: IngredientModel | List[IngredientModel]


class RecipeResponseModel(BaseModel):
    Result: RecipeModel | List[RecipeModel]
