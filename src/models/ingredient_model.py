from pydantic import BaseModel

class Ingredient:
    def __init__(self, name: str, description: str, alias: list[str] | None = None):
        self.name = name
        self.description = description
        self.alias = alias

class IngredientModel(BaseModel):
    name: str
    description: str
    alias: list[str] | None = None