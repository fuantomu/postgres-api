from typing import List
from pydantic import BaseModel

from models.ingredient_model import IngredientModel
from models.recipe_model import RecipeModel

class BaseResponseModel(BaseModel):
    Result: str

class IngredientResponseModel(BaseModel):
    Result: IngredientModel|List[IngredientModel]

class RecipeResponseModel(BaseModel):
    Result: RecipeModel|List[RecipeModel]