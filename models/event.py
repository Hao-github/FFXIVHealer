from enum import Enum

from models.player import Player
from .effect import Effect


class EventType(Enum):
    Other = 0
    Heal = 1
    PhysicsDamage = 2
    MagicDamage = 3


class Event:
    def __init__(
        self,
        eventType: EventType,
        name: str,
        value: int = 0,
        effectList: list[Effect] | Effect = [],
        target: Player | None = None,
    ) -> None:
        self.name: str = name
        self.eventType: EventType = eventType
        self.value: int = value
        self.effectList: list[Effect] | Effect = effectList
        self.target: Player | None = target
