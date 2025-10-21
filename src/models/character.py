from typing import Literal
from pydantic import BaseModel

from src.models.item import ItemModel


class CharacterModel(BaseModel):
    id: int | None = None
    name: str = "Unknown"
    gender: Literal["Female", "Male"] = "Male"
    faction: Literal["Alliance", "Horde"] = "Alliance"
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
    active_spec: str = "Adventurer"
    realm: str = "Dev"
    guild: int | None = None
    level: int = 1
    achievement_points: int = 0
    last_login_timestamp: int | None = None
    equipped_item_level: int = 0
    active_title: str | None = None
    region: Literal["eu", "us", "kr", "tw", "cn"] = "eu"
    version: str = "mop"
    realm_version: Literal["classic", "vanilla", "fresh", "sod", "retail"] = "classic"


class CharacterEquipmentModel(BaseModel):
    head: ItemModel | None = None
    neck: ItemModel | None = None
    shoulders: ItemModel | None = None
    shirt: ItemModel | None = None
    chest: ItemModel | None = None
    waist: ItemModel | None = None
    legs: ItemModel | None = None
    feet: ItemModel | None = None
    wrist: ItemModel | None = None
    hands: ItemModel | None = None
    ring_1: ItemModel | None = None
    ring_2: ItemModel | None = None
    trinket_1: ItemModel | None = None
    trinket_2: ItemModel | None = None
    back: ItemModel | None = None
    main_hand: ItemModel | None = None
    off_hand: ItemModel | None = None
    ranged: ItemModel | None = None
    tabard: ItemModel | None = None


class RatingModel(BaseModel):
    value: float = 0.0
    rating: int = 0


class CharacterStatisticModel(BaseModel):
    health: int = 0
    power: int | None = None
    power_type: Literal[
        "Mana", "Rage", "Energy", "Focus", "Runic Power", "Maelstrom"
    ] = "Mana"
    strength: int = 0
    agility: int = 0
    intellect: int = 0
    stamina: int = 0
    spirit: int | None = None
    melee_crit: RatingModel | None = None
    ranged_crit: RatingModel | None = None
    spell_crit: RatingModel | None = None
    melee_haste: RatingModel | None = None
    ranged_haste: RatingModel | None = None
    spell_haste: RatingModel | None = None
    mastery: RatingModel | None = None
    attack_power: int = 0
    spell_power: int = 0
    armor: int = 0
    dodge: RatingModel | None = None
    parry: RatingModel | None = None
    block: RatingModel | None = None
    defense: int = 0
    mana_regen: float = 0.0
    holy_resistance: int | None = None
    fire_resistance: int | None = None
    shadow_resistance: int | None = None
    nature_resistance: int | None = None
    arcane_resistance: int | None = None
    frost_resistance: int | None = None


class CharacterParseModel(BaseModel):
    players: list[list] = [[]]
    region: Literal["eu", "us", "kr", "tw", "cn"] = "eu"
    version: str = "mop"
