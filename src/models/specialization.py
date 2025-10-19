from pydantic import BaseModel


class TalentModel(BaseModel):
    id: int = 0
    name: str = "Unknown"
    icon: str | None = None
    rank: int = 0


class GlyphModel(BaseModel):
    id: int = 0
    name: str = "Unknown"
    icon: str | None = None
    type: str | None = None
    character_class: str | None = None


class SpecializationModel(BaseModel):
    id: int = 0
    name: str = "Unknown"
    talents: list[TalentModel] = []
    glyphs: list[GlyphModel] = []
    spec_id: int = 0
    version: str = "mop"
