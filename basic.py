from random import random
from enum import Enum

class Timer:
    def __init__(self, initialTime: float = 0):
        self.__time = initialTime

    def update(self, time: float) -> bool:
        self.__time += time
        if self.__time >= 3:
            self.__time -= 3
            return True
        return False


class Effect:
    def __init__(self, name: str, duration: int) -> None:
        self.name: str = name
        self.duration: int = duration
        self.remainTime: float = duration

    def update(self, timeInterval: float) -> None:
        self.remainTime -= timeInterval


class Mitigation(Effect):
    def __init__(self, name: str, duration: int, percentage: float) -> None:
        super().__init__(name, duration)
        self.percentage: float = percentage

class Shield(Effect):
    def __init__(self, name: str, duration: int, value: int) -> None:
        super().__init__(name, duration)
        self.shieldHp: int = value

class HealBonus(Effect):
    def __init__(self, name: str, duration: int, percentage: float) -> None:
        super().__init__(name, duration)
        self.percentage: float = percentage


class Dot(Effect):
    def __init__(self, name: str, duration: int, damage: float) -> None:
        super().__init__(name, duration)
        self.damage: float = damage
        self.timer: Timer = Timer(random() * 3)

    def update(self, timeInterval: float) -> bool:
        super().update(timeInterval)
        return self.timer.update(timeInterval)


class Hot(Effect):
    def __init__(self, name: str, duration: int, healing: float) -> None:
        super().__init__(name, duration)
        self.healing: float = healing
        self.timer: Timer = Timer(random() * 3)
        self.type = "Hot"

    def update(self, timeInterval: float) -> bool:
        super().update(timeInterval)
        return self.timer.update(timeInterval)

class EventType(Enum):
    Nothing = 0
    Heal = 1
    Mitigation = 2
    PhysicsDamage = 3
    MagicDamage = 4


class Event:
    def __init__(
        self, eventType: EventType, value: int = 0, effectList: list[Effect] = []
    ) -> None:
        self.eventType: EventType = eventType
        self.value = value
        self.effectList: list[Effect] = effectList

