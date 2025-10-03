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
        "Night Elf",
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
    ] = "Human"
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
        "Death Knight",
        "Monk",
    ] = "Adventurer"
    active_spec: str = "Adventurer"
    realm: str = "Dev"
    guild: int | None = None
    level: int = 1
    achievement_points: int = 0
    last_login_timestamp: int | None = None
    average_item_level: int = 0
    equipped_item_level: int = 0
    active_title: str | None = None


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
