"""
模拟buff和debuff的模型的文件
"""
from random import random

from models.baseStatus import BaseStatus
from models.event import Event, EventType


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


class MagicMtg(BaseStatus):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)


class PhysicsMtg(BaseStatus):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)


class Mtg(MagicMtg, PhysicsMtg):
    #     """Mitigation 减伤"""
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)


class Shield(BaseStatus):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)
        self.getSnapshot = True


class maxHpShield(BaseStatus):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)


class HealBonus(BaseStatus):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)


class SpellBonus(BaseStatus):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)


class Dot(BaseStatus):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)
        self.timer: Timer = Timer(3)
        self.getSnapshot = True

    def update(self, timeInterval: float, **kwargs) -> Event | None:
        super().update(timeInterval)
        if self.timer.update(timeInterval):
            return Event(EventType.TrueDamage, self.name, self.value)


class Hot(BaseStatus):
    def __init__(
        self,
        name: str,
        duration: float,
        value: float,
        interval: float = 3,
        isGround: bool = False,
    ) -> None:
        super().__init__(name, duration, value)
        self.timer: Timer = Timer(interval)
        self.getSnapshot: bool = True
        self.isGround: bool = isGround

    def update(self, timeInterval: float, **kwargs) -> Event | None:
        super().update(timeInterval)
        if self.timer.update(timeInterval):
            if self.isGround:
                return Event(EventType.GroundHeal, self.name, self.value)
            return Event(EventType.TrueHeal, self.name, self.value)


class DelayHeal(BaseStatus):
    """Delay Heal, 指延迟治疗"""

    def __init__(
        self, name: str, duration: float, value: float, snapshot: bool = True
    ) -> None:
        super().__init__(name, duration, value)
        self.getSnapshot = snapshot
        self.trigger: float = 0.5

    def update(self, timeInterval: float, hpPercentage: float) -> Event | None:
        super().update(timeInterval)
        if self.remainTime <= 0 or hpPercentage < self.trigger:
            return Event(EventType.TrueHeal, self.name, self.value)


class IncreaseMaxHp(HealBonus):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)

    def update(self, timeInterval: float, **kwargs) -> Event | None:
        super().update(timeInterval)
        if self.remainTime <= 0:
            return Event(EventType.TrueHeal, self.name, 0)


class HaimaShield(Shield):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)
        self.stack = 5
        self.stackTime = 15

    def update(self, timeInterval: float, **kwargs) -> Event | None:
        super().update(timeInterval)
        self.stackTime -= timeInterval
        # 检测到海马时间已过
        if self.stackTime <= 0:
            ret = Event(
                EventType.TrueHeal,
                self.name,
                self.originValue * self.stack / 2,
                status=Shield(self.name, self.remainTime, self.value),
            )
            self.setZero()
            return ret
        # 检测到海马盾已破
        if self.value <= 0 and self.stack > 0:
            self.stack -= 1
            self.remainTime = self.duration
            self.value = self.originValue
