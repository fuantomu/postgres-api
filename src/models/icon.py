from pydantic import BaseModel


class IconModel(BaseModel):
    id: int | None = None
    icon: str = "Unknown"
