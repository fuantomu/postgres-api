from typing import List
from pydantic import BaseModel
from src.models.character import (
    CharacterEquipmentModel,
    CharacterModel,
    CharacterStatisticModel,
)
from src.models.guild import GuildModel
from src.models.specialization import SpecializationModel


class BaseResponseModel(BaseModel):
    Result: str


class CharacterResponseModel(BaseModel):
    Result: CharacterModel | List[CharacterModel]


class CharacterEquipmentResponseModel(BaseModel):
    Result: CharacterEquipmentModel


class CharacterSpecializationResponseModel(BaseModel):
    Result: List[SpecializationModel]


class CharacterStatisticResponseModel(BaseModel):
    Result: CharacterStatisticModel


class GuildResponseModel(BaseModel):
    Result: GuildModel | List[GuildModel]
