from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING
import pandas as pd

from .Status import BaseStatus, EventType, StatusRtn, Dot

if TYPE_CHECKING:
    from .player import Player


@dataclass
class Event:
    eventType: EventType
    name: str
    user: Player
    target: Player
    value: float = 0
    status_list: list[BaseStatus] = field(default_factory=list)

    def copy(self, target: "Player") -> Event:
        return replace(self, target=target, status_list=deepcopy(self.status_list))

    def apply_buff(self, percentage: float) -> Event:
        self.value *= percentage
        self.status_list = [x.apply_buff(percentage) for x in self.status_list]
        return self

    def __str__(self) -> str:
        return (
            f"{self.user.name} do {self.name}({self.eventType.name}) on {self.target.name}"
            f", value: {str(self.value)}"
            f", statusList:[{5}{', '.join((str(i) for i in self.status_list))}]"
        )

    def append(self, status: BaseStatus) -> None:
        self.status_list.append(status)

    def name_is(self, name: str) -> bool:
        return self.name == name

    @staticmethod
    def from_row(row: pd.Series, user: "Player", target: "Player") -> Event:
        return Event(
            EventType.MagicDmg if row["type"] == "magic" else EventType.PhysicDmg,
            name=row["name"],
            value=row["damage"],
            user=user,
            target=target,
            status_list=[Dot(row["name"], row["dotTime"], row["dotDamage"])]
            if row["hasDot"]
            else [],
        )

    @staticmethod
    def from_StatusRtn(s: StatusRtn, user: "Player", target: "Player") -> Event:
        return Event(
            s.eventType, s.name, user, target, s.value, [s.status] if s.status else []
        )

