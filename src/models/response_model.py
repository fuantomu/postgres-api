from typing import List
from pydantic import BaseModel
from src.models.character import CharacterModel
from src.models.guild import GuildModel


class BaseResponseModel(BaseModel):
    Result: str


class CharacterResponseModel(BaseModel):
    Result: CharacterModel | List[CharacterModel]


class GuildResponseModel(BaseModel):
    Result: GuildModel | List[GuildModel]
