from __future__ import annotations
from models.baseStatus import BaseStatus
from enum import Enum


class EventType(Enum):
    TrueHeal = 0  # 快照后的治疗
    Heal = 1  # 普通治疗
    GroundHeal = 2  # 特殊治疗, 吃施法者快照但目标身上实时判定
    PhysicsDamage = 3  # 物理伤害
    MagicDamage = 4  # 魔法伤害
    TrueDamage = 5  # dot伤害


class Event:
    def __init__(
        self,
        eventType: EventType,
        name: str,
        value: float = 0,
        status: list[BaseStatus] | BaseStatus = [],
    ) -> None:
        self.name: str = name
        self.eventType: EventType = eventType
        self.value: float = value
        self.statusList: list[BaseStatus] = []
        if isinstance(status, list):
            self.statusList.extend(status)
        else:
            self.append(status)
        self.prepared: bool = False

    def getBuff(self, percentage: float) -> Event:
        self.value *= percentage
        self.statusList = [status.getBuff(percentage) for status in self.statusList]
        return self

    def __str__(self) -> str:
        return self.name + ": " + str(self.value)

    def append(self, status: BaseStatus) -> None:
        self.statusList.append(status)


def petSkill(func):
    def wrapper(self, *args, **kwargs):
        ret: Event = func(self, *args, **kwargs)
        ret.getBuff(self.petCoefficient)
        return ret

    return wrapper
