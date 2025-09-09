from pydantic import BaseModel

class RecipeIngredientModel(BaseModel):
    name: str
    quantity: str
