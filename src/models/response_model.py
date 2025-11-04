from typing import List
from pydantic import BaseModel
from src.models.account import AccountLoginSessionModel, AccountModel, SessionModel
from src.models.character import (
    CharacterEquipmentModel,
    CharacterModel,
    CharacterSearchModel,
    CharacterStatisticModel,
)
from src.models.guild import GuildModel
from src.models.item import EnchantmentModel, ItemModel
from src.models.specialization import GlyphModel, SpecializationModel
from src.models.wcl import RankingModel, ZoneModel


class BaseResponseModel(BaseModel):
    Result: str
    status_code: int | None = None


class CharacterResponseModel(BaseModel):
    Result: CharacterModel | List[CharacterModel]


class CharacterEquipmentResponseModel(BaseModel):
    Result: CharacterEquipmentModel


class CharacterSpecializationResponseModel(BaseModel):
    Result: List[SpecializationModel]


class CharacterStatisticResponseModel(BaseModel):
    Result: CharacterStatisticModel


class CharacterSearchResponseModel(BaseModel):
    Result: CharacterSearchModel


class GuildResponseModel(BaseModel):
    Result: GuildModel | List[GuildModel]


class ItemResponseModel(BaseModel):
    Result: List[ItemModel]


class GlyphResponseModel(BaseModel):
    Result: List[GlyphModel]


class EnchantmentResponseModel(BaseModel):
    Result: List[EnchantmentModel]


class RankingResponseModel(BaseModel):
    Result: RankingModel


class ZoneResponseModel(BaseModel):
    Result: ZoneModel


class AccountResponseModel(BaseModel):
    Result: AccountModel | List[AccountModel]


class AccountLoginResponseModel(BaseModel):
    Result: AccountLoginSessionModel


class SessionResponseModel(BaseModel):
    Result: SessionModel


class AccountCharactersResponseModel(BaseModel):
    Result: List[int]
