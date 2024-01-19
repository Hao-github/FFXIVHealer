"""
模拟buff和debuff的模型的文件
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from random import random


class EventType(Enum):
    TrueHeal = 0  # 快照后的治疗
    Heal = 1  # 普通治疗
    GroundHeal = 2  # 从罩子每一跳中获得的治疗，需计算目标身上buff
    GroundInit = 3  # 罩子放下时的事件，需计算施法者身上的快照
    PhysicDmg = 4  # 物理伤害
    MagicDmg = 5  # 魔法伤害
    TrueDamage = 6  # dot伤害
    MaxHpChange = 7  # 关于最大生命值的变动事件


@dataclass
class StatusRtn:
    eventType: EventType
    name: str
    value: float
    status: BaseStatus | None = None


@dataclass
class BaseStatus:
    name: str
    duration: float = field(compare=False)
    value: float = field(compare=False, default=0)
    getSnapshot: bool = field(compare=False, default=False)
    display: bool = True

    def __post_init__(self):
        self.remainTime = self.duration

    def update(self, timeInterval: float, **kwargs) -> StatusRtn | None:
        self.remainTime -= timeInterval

    def __str__(self) -> str:
        return "{0}: {1}s".format(self.name, str(round(self.remainTime, 2)))

    def __lt__(self, __value: BaseStatus) -> bool:
        return self.value < __value.value

    def getBuff(self, percentage: float) -> BaseStatus:
        self.value *= percentage if self.getSnapshot else 1
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


class PhysicMtg(BaseStatus):
    pass


class Mtg(MagicMtg, PhysicMtg):
    pass


class HealBonus(BaseStatus):
    pass


class SpellBonus(BaseStatus):
    pass


@dataclass
class Shield(BaseStatus):
    getSnapshot: bool = True


class maxHpShield(BaseStatus):
    def toShield(self, maxHp: int) -> Shield:
        return Shield(self.name, self.duration, maxHp * self.value // 100)


@dataclass
class Dot(BaseStatus):
    getSnapshot: bool = True

    def __post_init__(self):
        super().__post_init__()
        self.timer: Timer = Timer(3)

    def update(self, timeInterval: float, **kwargs) -> StatusRtn | None:
        super().update(timeInterval)
        if self.timer.update(timeInterval):
            return StatusRtn(EventType.TrueDamage, self.name, self.value)


@dataclass
class Hot(BaseStatus):
    interval: float = 3
    getSnapshot: bool = True

    def __post_init__(self):
        super().__post_init__()
        self.isGround = False
        self.timer: Timer = Timer(self.interval)

    def update(self, timeInterval: float, **kwargs) -> StatusRtn | None:
        super().update(timeInterval)
        if self.timer.update(timeInterval):
            return StatusRtn(
                EventType.GroundHeal if self.isGround else EventType.TrueHeal,
                self.name,
                self.value,
            )


@dataclass
class DelayHeal(BaseStatus):
    trigger: float = 0.5
    getSnapshot: bool = True
    # 专为不死鸟帽写的属性
    isRekindle: bool = False

    def update(self, timeInterval: float, hpPercentage: float) -> StatusRtn | None:
        super().update(timeInterval)
        if self.remainTime <= 0 or hpPercentage < self.trigger:
            self.remainTime = 0
            ret = StatusRtn(EventType.TrueHeal, self.name, self.value)
            if self.isRekindle:
                ret.status = Hot("Rekindle", 15, self.value / 2)
            return ret


@dataclass
class IncreaseMaxHp(HealBonus):
    increaseHpNum: int = 0

    def update(self, timeInterval: float, **kwargs) -> StatusRtn | None:
        super().update(timeInterval)
        if self.remainTime <= 0:
            return StatusRtn(EventType.MaxHpChange, self.name, self.increaseHpNum)


@dataclass
class HaimaShield(Shield):
    def __post_init__(self):
        super().__post_init__()
        self.stack: int = 5
        self.stackTime: float = 15
        self.originValue: float = self.value

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


@dataclass
class Bell(BaseStatus):
    getSnapshot: bool = False

    def __post_init__(self):
        super().__post_init__()
        self.bellCD: float = 0

    def update(self, timeInterval: float, **kwargs) -> StatusRtn | None:
        super().update(timeInterval)
        self.bellCD -= timeInterval
        if self.remainTime <= 0 and self.value > 0:
            return StatusRtn(EventType.Heal, "BellEnd", self.value * 200)

    def getHeal(self) -> StatusRtn | None:
        if self.bellCD > 0:
            return
        self.bellCD = 1
        self.value -= 1
        if self.value == 0:
            self.remainTime = 0
        return StatusRtn(EventType.Heal, "BellHeal", 400)
