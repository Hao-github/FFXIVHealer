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
    get_snapshot: bool = field(compare=False, default=False)
    display: bool = True

    def __post_init__(self):
        self.remain_time = self.duration

    def update(self, timeInterval: float, **kwargs) -> StatusRtn | None:
        self.remain_time -= timeInterval

    def __str__(self) -> str:
        return f"{self.name}: {round(self.remain_time, 2)}s"

    def __lt__(self, __value: BaseStatus) -> bool:
        return self.value < __value.value

    def apply_buff(self, percentage: float) -> BaseStatus:
        if self.get_snapshot:
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
    get_snapshot: bool = True


class MaxHpShield(BaseStatus):
    def to_shield(self, max_hp: int) -> Shield:
        return Shield(self.name, self.duration, max_hp * self.value // 100)


@dataclass
class Dot(BaseStatus):
    get_snapshot: bool = True

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
    get_snapshot: bool = True
    until: float = 999999

    def __post_init__(self):
        super().__post_init__()
        self.isGround = False
        self.timer: Timer = Timer(self.interval)

    def update(self, timeInterval: float, **kwargs) -> StatusRtn | None:
        super().update(timeInterval)
        if kwargs.get("hp", 0) > self.until:
            self.remain_time = 0
        if self.timer.update(timeInterval):
            return StatusRtn(
                EventType.GroundHeal if self.isGround else EventType.TrueHeal,
                self.name,
                self.value,
            )


@dataclass
class DelayHeal(BaseStatus):
    trigger: float = 0.5
    get_snapshot: bool = True
    # 专为不死鸟帽写的属性
    isRekindle: bool = False

    def update(self, timeInterval: float, hpPercentage: float) -> StatusRtn | None:
        super().update(timeInterval)
        if self.remain_time <= 0 or hpPercentage < self.trigger:
            self.remain_time = 0
            ret = StatusRtn(EventType.TrueHeal, self.name, self.value)
            if self.isRekindle:
                ret.status = Hot("Rekindle", 15, self.value / 2)
            return ret


@dataclass
class IncreaseMaxHp(HealBonus):
    increase_hp_num: int = 0

    def update(self, timeInterval: float, **kwargs) -> StatusRtn | None:
        super().update(timeInterval)
        if self.remain_time <= 0:
            return StatusRtn(EventType.MaxHpChange, self.name, self.increase_hp_num)


@dataclass
class HaimaShield(Shield):
    def __post_init__(self):
        super().__post_init__()
        self.stack: int = 5
        self.stackTime: float = 15
        self.originValue: float = self.value

    def apply_buff(self, percentage: float) -> BaseStatus:
        self.originValue *= percentage
        return super().apply_buff(percentage)

    def update(self, timeInterval: float, **kwargs) -> StatusRtn | None:
        super().update(timeInterval)
        self.stackTime -= timeInterval
        # 检测到海马时间已过
        if self.stackTime <= 0:
            ret = StatusRtn(
                EventType.TrueHeal,
                self.name,
                self.originValue * self.stack / 2,
                status=Shield(self.name, self.remain_time, self.value),
            )
            return ret
        # 检测到海马盾已破
        if self.value <= 0 and self.stack > 0:
            self.stack -= 1
            self.remain_time = self.duration
            self.value = self.originValue


@dataclass
class Bell(BaseStatus):
    get_snapshot: bool = False

    def __post_init__(self):
        super().__post_init__()
        self.bellCD: float = 0

    def update(self, timeInterval: float, **kwargs) -> StatusRtn | None:
        super().update(timeInterval)
        self.bellCD -= timeInterval
        if self.remain_time <= 0 and self.value > 0:
            return StatusRtn(EventType.Heal, "BellEnd", self.value * 200)

    def get_heal(self) -> StatusRtn | None:
        if self.bellCD > 0:
            return
        self.bellCD = 1
        self.value -= 1
        if self.value == 0:
            self.remain_time = 0
        return StatusRtn(EventType.Heal, "BellHeal", 400)
