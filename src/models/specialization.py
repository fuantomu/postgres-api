from pydantic import BaseModel


class SpecializationModel(BaseModel):
    id: int = 0
    name: str = "Unknown"
    talents: list[int] = []
    glyphs: list[int] = []
    active: bool = True
