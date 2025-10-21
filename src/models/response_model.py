from typing import List
from pydantic import BaseModel
from src.models.character import (
    CharacterEquipmentModel,
    CharacterModel,
    CharacterStatisticModel,
    RankingModel,
)
from src.models.guild import GuildModel
from src.models.item import EnchantmentModel, ItemModel
from src.models.specialization import GlyphModel, SpecializationModel


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


class ItemResponseModel(BaseModel):
    Result: ItemModel


class GlyphResponseModel(BaseModel):
    Result: List[GlyphModel]


class EnchantmentResponseModel(BaseModel):
    Result: List[EnchantmentModel]


class RankingResponseModel(BaseModel):
    Result: RankingModel
