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
    realm_version: Literal["classic", "vanilla", "fresh", "sod", "retail"] = "classic"


class GuildRosterModel(BaseModel):
    id: int = 0
    name: str = "Unknown"
    rank: int = 9
    level: int = 1
    race: Literal[
        "Human",
        "Nightelf",
        "Dwarf",
        "Gnome",
        "Draenei",
        "Worgen",
        "Orc",
        "Troll",
        "Tauren",
        "Undead",
        "Bloodelf",
        "Goblin",
        "Pandaren",
        "Alien",
    ] = "Alien"
    character_class: Literal[
        "Adventurer",
        "Paladin",
        "Warrior",
        "Hunter",
        "Mage",
        "Warlock",
        "Priest",
        "Rogue",
        "Druid",
        "Shaman",
        "Deathknight",
        "Monk",
    ] = "Adventurer"
