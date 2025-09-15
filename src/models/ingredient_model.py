from pydantic import BaseModel

class IngredientModel(BaseModel):
    id: str | None = None
    name: str | None = None
    description: str | None = None
    alias: list[str] | None = None