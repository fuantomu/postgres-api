from pydantic import BaseModel
from uuid import UUID, uuid4

class RecipeIngredient:
    def __init__(self, id:str, name: str, quantity: str):
        self.id = id
        self.name = name
        self.quantity = quantity

class RecipeIngredientModel(BaseModel):
    id: UUID = uuid4()
    name: str
    quantity: str
