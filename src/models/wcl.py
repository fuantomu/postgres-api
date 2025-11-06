from pydantic import BaseModel
from typing import Literal


class AllStarsRanking(BaseModel):
    partition: int
    spec: str | None = None
    points: float | str
    possiblePoints: int
    rank: int | str
    regionRank: int | str
    serverRank: int | str = None
    rankPercent: float | None | str = None
    total: int
    rankTooltip: str | None = None


class NameModel(BaseModel):
    id: int
    name: str
    journalID: int | None = None


class SlugModel(BaseModel):
    slug: str
    name: str | None = None


class ServerModel(SlugModel):
    region: SlugModel


class GuildModel(BaseModel):
    id: int
    name: str
    server: ServerModel


class RankModel(BaseModel):
    rank_id: int
    _class: int
    spec: int
    per_second_amount: float
    ilvl: int
    fight_metadata: int


class EncounterRanking(BaseModel):
    encounter: NameModel
    rankPercent: float | None = None
    medianPercent: float | None = None
    lockedIn: bool
    totalKills: int
    fastestKill: int
    allStars: AllStarsRanking | None = None
    spec: str | None = None
    bestSpec: str | None = None
    bestAmount: float
    rankTooltip: str | None = None
    bestRank: RankModel | None = None


class ZoneRanking(BaseModel):
    bestPerformanceAverage: float | None = None
    medianPerformanceAverage: float | None = None
    difficulty: int
    metric: Literal["dps", "hps"]
    partition: int
    zone: int
    size: int
    allStars: list[AllStarsRanking] = []
    rankings: list[EncounterRanking]


class RankingModel(BaseModel):
    name: str
    id: int
    classID: int
    gameData: dict
    faction: NameModel
    level: int
    hidden: str | bool
    guilds: list[GuildModel]
    guildRank: int
    zoneRankings: ZoneRanking


class BracketModel(BaseModel):
    min: int
    max: int
    bucket: int
    type: str


class DifficultyModel(BaseModel):
    id: int
    name: str
    sizes: list[int]


class ZoneModel(BaseModel):
    brackets: BracketModel | None = None
    difficulties: list[DifficultyModel]
    encounters: list[NameModel]
    expansion: NameModel
    frozen: bool
    name: str


class SimpleRankingModel(BaseModel):
    number: int
    color: str | None = None


class GuildZoneRankTypeModel(BaseModel):
    worldRank: SimpleRankingModel | None
    regionRank: SimpleRankingModel | None
    serverRank: SimpleRankingModel | None


class GuildZoneRankingModel(BaseModel):
    progress: GuildZoneRankTypeModel | None
    speed: GuildZoneRankTypeModel | None
    completeRaidSpeed: GuildZoneRankTypeModel | None


class GuildRankingModel(BaseModel):
    name: str
    id: int
    zoneRanking: GuildZoneRankingModel
