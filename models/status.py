"""
模拟buff和debuff的模型的文件
"""
from __future__ import annotations
from enum import Enum
from random import random


class EventType(Enum):
    TrueHeal = 0  # 快照后的治疗
    Heal = 1  # 普通治疗
    GroundHeal = 2  # 特殊治疗, 吃施法者快照但目标身上实时判定
    PhysicsDmg = 3  # 物理伤害
    MagicDmg = 4  # 魔法伤害
    TrueDamage = 5  # dot伤害
    MaxHpChange = 6  # 关于最大生命值的变动事件


class StatusRtn:
    def __init__(self, eventType: EventType, name: str, value: float) -> None:
        self.eventType: EventType = eventType
        self.name: str = name
        self.value: float = value


class BaseStatus:
    def __init__(self, name: str, duration: float, value: float = 0) -> None:
        self.name: str = name
        self.duration: float = duration
        self.remainTime: float = duration
        self.value: float = value
        self.getSnapshot: bool = False

    def update(self, timeInterval: float, **kwargs) -> StatusRtn | None:
        self.remainTime -= timeInterval

    def __str__(self) -> str:
        return "{0}: {1}s".format(self.name, str(round(self.remainTime, 2)))

    def __eq__(self, __value: BaseStatus) -> bool:
        return type(self) == type(__value) and self.name == __value.name

    def __lt__(self, __value: BaseStatus) -> bool:
        return self.value < __value.value

    def getBuff(self, percentage: float) -> BaseStatus:
        if self.getSnapshot:
            self.value *= percentage
        return self


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
    pass


class PhysicsMtg(BaseStatus):
    pass


class Mtg(MagicMtg, PhysicsMtg):
    pass


class HealBonus(BaseStatus):
    pass


class SpellBonus(BaseStatus):
    pass


class Shield(BaseStatus):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)
        self.getSnapshot = True


class maxHpShield(BaseStatus):
    def toShield(self, maxHp: int) -> Shield:
        return Shield(self.name, self.duration, maxHp * self.value // 100)


class Dot(BaseStatus):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)
        self.timer: Timer = Timer(3)
        self.getSnapshot = True

    def update(self, timeInterval: float, **kwargs) -> StatusRtn | None:
        super().update(timeInterval)
        if self.timer.update(timeInterval):
            return StatusRtn(EventType.TrueDamage, self.name, self.value)


class Hot(BaseStatus):
    def __init__(
        self,
        name: str,
        duration: float,
        value: float,
        interval: float = 3,
        ground: bool = False,
    ) -> None:
        super().__init__(name, duration, value)
        self.timer: Timer = Timer(interval)
        self.getSnapshot: bool = not ground

    def update(self, timeInterval: float, **kwargs) -> StatusRtn | None:
        super().update(timeInterval)
        if self.timer.update(timeInterval):
            return StatusRtn(
                EventType.TrueHeal if self.getSnapshot else EventType.GroundHeal,
                self.name,
                self.value,
            )


class DelayHeal(BaseStatus):
    """Delay Heal, 指延迟治疗"""

    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)
        self.trigger: float = 0.5

    def update(self, timeInterval: float, hpPercentage: float) -> StatusRtn | None:
        super().update(timeInterval)
        if self.remainTime <= 0 or hpPercentage < self.trigger:
            self.remainTime = 0
            return StatusRtn(EventType.TrueHeal, self.name, self.value)


class IncreaseMaxHp(HealBonus):
    def update(self, timeInterval: float, **kwargs) -> StatusRtn | None:
        super().update(timeInterval)
        if self.remainTime <= 0:
            return StatusRtn(EventType.MaxHpChange, self.name, self.value)


class HaimaShield(Shield):
    def __init__(self, name: str, duration: float, value: float) -> None:
        super().__init__(name, duration, value)
        self.stack = 5
        self.stackTime = 15
        self.originValue = value

    def getBuff(self, percentage: float) -> BaseStatus:
        self.originValue *= percentage
        return super().getBuff(percentage)

    # def update(self, timeInterval: float, **kwargs) -> Event | None:
    #     super().update(timeInterval)
    #     self.stackTime -= timeInterval
    #     # 检测到海马时间已过
    #     if self.stackTime <= 0:
    #         ret = Event(
    #             EventType.TrueHeal,
    #             self.name,
    #             self.originValue * self.stack / 2,
    #             status=Shield(self.name, self.remainTime, self.value),
    #         )
    #         return ret
    #     # 检测到海马盾已破
    #     if self.value <= 0 and self.stack > 0:
    #         self.stack -= 1
    #         self.remainTime = self.duration
    #         self.value = self.originValue
