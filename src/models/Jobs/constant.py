from typing import Type

from .Tank import DarkKnight, Paladin, Warrior, GunBreaker
from .Healer import Sage, WhiteMage, Scholar
from .MagicDPS import Summoner, BlackMage, RedMage
from .RangedDPS import Bard, Dancer, Machinist
from .MeleeDPS import Samurai, Monk, Dragoon, Reaper, Ninja


STR2JOB_CLASSES: dict[str, Type] = {
    "DarkKnight": DarkKnight,
    "GunBreaker": GunBreaker,
    "Paladin": Paladin,
    "Warrior": Warrior,
    "Sage": Sage,
    "WhiteMage": WhiteMage,
    "Scholar": Scholar,
    "Summoner": Summoner,
    "BlackMage": BlackMage,
    "RedMage": RedMage,
    "Bard": Bard,
    "Dancer": Dancer,
    "Machinist": Machinist,
    "Samurai": Samurai,
    "Monk": Monk,
    "Dragoon": Dragoon,
    "Reaper": Reaper,
    "Ninja": Ninja,
}
