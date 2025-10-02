from pydantic import BaseModel


class SpecializationModel(BaseModel):
    name: str = "Unknown"
    talents: list[int] = []
    glyphs: list[int] = []
    active: bool = True
