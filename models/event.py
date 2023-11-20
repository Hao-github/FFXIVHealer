from enum import Enum

from models.player import Player
from models.effect import Effect


class EventType(Enum):
    Other = 0
    Heal = 1
    PhysicsDamage = 2
    MagicDamage = 3
    TrueDamage = 4

class Event:
    def __init__(
        self,
        eventType: EventType,
        name: str,
        value: int = 0,
        effect: list[Effect] | Effect = [],
        user: Player | None = None,
        target: Player | None = None,
    ) -> None:
        self.name: str = name
        self.eventType: EventType = eventType
        self.value: int = value
        self.effectList: list[Effect] = []
        if isinstance(effect, list):
            for e in effect:
                self.effectList.append(e)
        else:
            self.effectList.append(effect)
        self.user: Player | None = user
        self.target: Player | None = target
