from typing import Literal
from pydantic import BaseModel


class ItemModel(BaseModel):
    character_id: int = 0
    id: int = 0
    name: str = "Test"
    slot: Literal[
        "Head",
        "Neck",
        "Shoulder",
        "Back",
        "Chest",
        "Shirt",
        "Tabard",
        "Wrist",
        "Hands",
        "Waist",
        "Legs",
        "Feet",
        "Ring 1",
        "Ring 2",
        "Trinket 1",
        "Trinket 2",
        "Main Hand",
        "Off Hand",
        "Ranged",
    ] = "Head"
    quality: Literal[
        "Poor",
        "Common",
        "Uncommon",
        "Rare",
        "Epic",
        "Legendary",
        "Artifact",
        "Heirloom",
    ] = "Common"
    wowhead_link: str | None = None
