from pydantic import BaseModel

class IngredientModel(BaseModel):
    id: str | None = None
    name: str
    description: str
    alias: list[str] | None = None

class IngredientAliasModel(BaseModel):
    name: str
