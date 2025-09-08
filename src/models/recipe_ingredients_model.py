from pydantic import BaseModel

class RecipeIngredient:
    def __init__(self, name: str, quantity: str):
        self.name = name
        self.quantity = quantity

class RecipeIngredientModel(BaseModel):
    name: str
    quantity: str
