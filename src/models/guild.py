from typing import Literal
from pydantic import BaseModel


class GuildModel(BaseModel):
    id: int | None = None
    name: str = "Unknown"
    realm: str = "Dev"
    faction: Literal["Alliance", "Horde"] = "Alliance"
    achievement_points: int = 0
    member_count: int = 0
    created_timestamp: int = 0
    region: Literal["eu", "us", "kr", "tw", "cn"] = "eu"
    version: str = "mop"
