"""
模拟buff和debuff的模型的文件
"""
from random import random


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

    def __str__(self) -> str:
        return self.name + ": " + str(round(self.remainTime, 2)) + "s"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Effect):
            return False
        return type(self) == type(__value) and self.name == __value.name


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
        self.value: int = value


class HealBonus(Effect):
    def __init__(self, name: str, duration: int, percentage: float) -> None:
        super().__init__(name, duration)
        self.percentage: float = percentage


class HealingSpellBonus(Effect):
    def __init__(self, name: str, duration: int, percentage: float) -> None:
        super().__init__(name, duration)
        self.percentage: float = percentage


class Dot(Effect):
    def __init__(
        self,
        name: str,
        duration: int,
        value: int,
    ) -> None:
        super().__init__(name, duration)
        self.value: int = value
        self.timer: Timer = Timer(random() * 3)

    def update(self, timeInterval: float) -> bool:
        super().update(timeInterval)
        return self.timer.update(timeInterval)


class Hot(Effect):
    def __init__(self, name: str, duration: int, value: int) -> None:
        super().__init__(name, duration)
        self.value: int = value
        self.timer: Timer = Timer(random() * 3)

    def update(self, timeInterval: float) -> bool:
        super().update(timeInterval)
        return self.timer.update(timeInterval)


class DelayHealing(Effect):
    def __init__(self, name: str, duration: int, value: int) -> None:
        super().__init__(name, duration)
        self.value: int = value

    def update(self, timeInterval: float) -> bool:
        super().update(timeInterval)
        if self.remainTime > 0:
            return False
        return True


class IncreaseMaxHp(Effect):
    def __init__(self, name: str, duration: int, percentage: float) -> None:
        super().__init__(name, duration)
        self.percentage = percentage

    def update(self, timeInterval: float) -> bool:
        super().update(timeInterval)
        if self.remainTime > 0:
            return False
        return True
