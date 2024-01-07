from __future__ import annotations

import pandas as pd
from Settings.baseConfig import EventType
from models.status import BaseStatus, StatusRtn, Dot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.player import Player


class Event:
    def __init__(
        self,
        eventType: EventType,
        name: str,
        user: "Player",
        target: "Player",
        value: float = 0,
        status: list[BaseStatus] | BaseStatus = [],
    ) -> None:
        self.name: str = name
        self.eventType: EventType = eventType
        self.value: float = value
        self.statusList: list[BaseStatus] = (
            status if isinstance(status, list) else [status]
        )
        self.user: Player = user
        self.target: Player = target

    def getBuff(self, percentage: float) -> Event:
        self.value *= percentage
        map(lambda x: x.getBuff(percentage), self.statusList)
        return self

    def __str__(self) -> str:
        return "{0}: {1}, EventType: {2}".format(
            self.name,
            str(self.value),
            ("magic" if self.eventType == EventType.MagicDmg else "physics"),
        )

    def append(self, status: BaseStatus) -> None:
        self.statusList.append(status)

    @staticmethod
    def fromRow(row: pd.Series, user: "Player", target: "Player") -> Event:
        return Event(
            EventType.MagicDmg if row["type"] == "magic" else EventType.PhysicsDmg,
            name=row["name"],
            value=row["damage"],
            user=user,
            target=target,
            status=Dot(row["name"], row["dotTime"], row["dotDamage"])
            if row["hasDot"]
            else [],
        )

    @staticmethod
    def fromStatusRtn(s: StatusRtn, user: "Player", target: "Player") -> Event:
        return Event(s.eventType, s.name, user, target, s.value)


def petSkill(func):
    def wrapper(self, *args, **kwargs):
        ret: Event = func(self, *args, **kwargs)
        ret.getBuff(self.petCoefficient)
        return ret

    return wrapper
