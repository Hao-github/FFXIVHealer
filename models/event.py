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
        return "{0} do {1}({2}) on {3}, value: {4}{5}".format(
            self.user.name,
            self.name,
            self.eventType.name,
            self.target.name,
            str(self.value),
            ", statusList:[{0}]".format(", ".join((str(i) for i in self.statusList)))
            if self.statusList
            else "",
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
            statusList=[Dot(row["name"], row["dotTime"], row["dotDamage"])]
            if row["hasDot"]
            else [],
        )

    @staticmethod
    def fromStatusRtn(s: StatusRtn, user: "Player", target: "Player") -> Event:
        return Event(s.eventType, s.name, user, target, s.value)
