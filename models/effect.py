"""
模拟buff和debuff的模型的文件
"""
from enum import Enum
from random import random


class DataType(Enum):
    Physics = 0
    Magic = 1
    Real = 2


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


class MagicMitigation(Effect):
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


class HealingSpellBonus(Effect):
    def __init__(self, name: str, duration: int, percentage: float) -> None:
        super().__init__(name, duration)
        self.percentage: float = percentage


class Dot(Effect):
    def __init__(self, name: str, duration: int, damage: int) -> None:
        super().__init__(name, duration)
        self.damage: int = damage
        self.timer: Timer = Timer(random() * 3)

    def update(self, timeInterval: float) -> bool:
        super().update(timeInterval)
        return self.timer.update(timeInterval)


class Hot(Effect):
    def __init__(self, name: str, duration: int, healing: int) -> None:
        super().__init__(name, duration)
        self.healing: int = healing
        self.timer: Timer = Timer(random() * 3)

    def update(self, timeInterval: float) -> bool:
        super().update(timeInterval)
        return self.timer.update(timeInterval)
