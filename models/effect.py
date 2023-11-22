"""
模拟buff和debuff的模型的文件
"""
from random import random


class Timer:
    def __init__(self, timeInterval: float):
        self.__time = random() * timeInterval
        self.__timeInterval = timeInterval

    def update(self, time: float) -> bool:
        self.__time += time
        if self.__time >= self.__timeInterval:
            self.__time -= self.__timeInterval
            return True
        return False


class Effect:
    def __init__(self, name: str, duration: float, value: float) -> None:
        self.name: str = name
        self.duration: float = duration
        self.remainTime: float = duration
        self.getSnapshot: bool = False
        self.value = value

    def update(self, timeInterval: float) -> None:
        self.remainTime -= timeInterval

    def __str__(self) -> str:
        return self.name + ": " + str(round(self.remainTime, 2)) + "s"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Effect):
            return False
        return type(self) == type(__value) and self.name == __value.name


class Mitigation(Effect):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)


class MagicMitigation(Effect):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)


class Shield(Effect):
    def __init__(self, name: str, duration: float, value: int) -> None:
        super().__init__(name, duration, value)
        self.getSnapshot = True


class maxHpShield(Effect):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)


class HealBonus(Effect):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)


class SpellBonus(Effect):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)


class Dot(Effect):
    def __init__(self, name: str, duration: float, value: int) -> None:
        super().__init__(name, duration, value)
        self.timer: Timer = Timer(3)
        self.getSnapshot = True

    def update(self, timeInterval: float) -> bool:
        super().update(timeInterval)
        return self.timer.update(timeInterval)


class Hot(Effect):
    def __init__(
        self, name: str, duration: float, value: int, timeInterval: float = 3
    ) -> None:
        super().__init__(name, duration, value)
        self.timer: Timer = Timer(timeInterval)
        self.getSnapshot = True

    def update(self, timeInterval: float) -> bool:
        super().update(timeInterval)
        return self.timer.update(timeInterval)


class DelayHealing(Effect):
    def __init__(self, name: str, duration: float, value: int) -> None:
        super().__init__(name, duration, value)
        self.getSnapshot = True

    def update(self, timeInterval: float) -> bool:
        super().update(timeInterval)
        if self.remainTime > 0:
            return False
        return True


class IncreaseMaxHp(Effect):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)

    def update(self, timeInterval: float) -> bool:
        super().update(timeInterval)
        if self.remainTime > 0:
            return False
        return True
