from pydantic import BaseModel
from uuid import UUID, uuid4

class Ingredient:
    def __init__(self, name: str, description: str, alias: list[str] | None = None):
        self.name = name
        self.description = description
        self.alias = alias

class IngredientModel(BaseModel):
    id: UUID = uuid4()
    name: str
    description: str
    alias: list[str] | None = None