from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field

import pandas as pd
from models.status import BaseStatus, EventType, StatusRtn, Dot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.player import Player


@dataclass
class Event:
    eventType: EventType
    name: str
    user: Player
    target: Player
    value: float = 0
    statusList: list[BaseStatus] = field(default_factory=list)

    def copy(self, target: "Player") -> Event:
        return Event(
            self.eventType,
            self.name,
            self.user,
            target,
            self.value,
            deepcopy(self.statusList),
        )

    def getBuff(self, percentage: float) -> Event:
        self.value *= percentage
        self.statusList = list(map(lambda x: x.getBuff(percentage), self.statusList))
        return self

    def __str__(self) -> str:
        return (
            f"{self.user.name} do {self.name}({self.eventType.name}) on {self.target.name}"
            f", value: {str(self.value)}"
            f", statusList:[{5}{', '.join((str(i) for i in self.statusList))}]"
        )

    def append(self, status: BaseStatus) -> None:
        self.statusList.append(status)

    def nameIs(self, name: str) -> bool:
        return self.name == name

    @staticmethod
    def fromRow(row: pd.Series, user: "Player", target: "Player") -> Event:
        return Event(
            EventType.MagicDmg if row["type"] == "magic" else EventType.PhysicDmg,
            name=row["name"],
            value=row["damage"],
            user=user,
            target=target,
            statusList=[Dot(row["name"], row["dotTime"], row["dotDamage"])]
            if row["hasDot"]
            else [],
        )

    @staticmethod
    def fromStatusRtn(s: StatusRtn, user: "Player", target: "Player") -> Event:
        return Event(
            s.eventType, s.name, user, target, s.value, [s.status] if s.status else []
        )
