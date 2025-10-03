from pydantic import BaseModel


class TalentModel(BaseModel):
    id: int = 0
    name: str = "Unknown"


class GlyphModel(BaseModel):
    id: int = 0
    name: str = "Unknown"


class SpecializationModel(BaseModel):
    id: int = 0
    name: str = "Unknown"
    talents: list[TalentModel] = []
    glyphs: list[GlyphModel] = []
    active: bool = True
