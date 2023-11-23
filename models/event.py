from models.effect import Effect
from enum import Enum


class EventType(Enum):
    Heal = 1
    PhysicsDamage = 2
    MagicDamage = 3
    TrueDamage = 4


class Event:
    def __init__(
        self,
        eventType: EventType,
        name: str,
        value: float = 0,
        effect: list[Effect] | Effect = [],
    ) -> None:
        self.name: str = name
        self.eventType: EventType = eventType
        self.value: float = value
        self.effectList: list[Effect] = []
        if isinstance(effect, list):
            self.effectList.extend(effect)
        else:
            self.append(effect)
        self.prepared: bool = False

    def getPercentage(self, percentage: float) -> None:
        self.value = self.value * percentage
        for effect in self.effectList:
            if effect.getSnapshot:
                effect.value = effect.value * percentage

    def __str__(self) -> str:
        return self.name + ": " + str(self.value)

    def append(self, effect: Effect) -> None:
        self.effectList.append(effect)


def petSkill(func):
    def wrapper(self, *args, **kwargs):
        ret: Event = func(self, *args, **kwargs)
        ret.getPercentage(self.petCoefficient)
        return ret

    return wrapper
