from __future__ import annotations
import json
from copy import deepcopy
from dataclasses import dataclass, field, replace

import pandas as pd

from ..utils import STR2STATUS
from .Status import BaseStatus, EventType, StatusRtn

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player


@dataclass
class Event:
    """表示一个事件的类。

    Attributes:
        eventType (EventType): 事件类型，例如魔法伤害或物理伤害。
        name (str): 事件的名称。
        user (Player): 事件的释放者。
        target (Player): 事件的目标。
        value (float): 事件的值或强度。
        status_list (List[BaseStatus]): 事件中可能附加的状态列表。
        reduced_pct (float): 被减伤百分比。
        reduced_value (int): 被盾值抵消数值。
    """

    eventType: EventType
    name: str
    user: Player
    target: Player
    value: float = 0.0
    status_list: list[BaseStatus] = field(default_factory=list)
    reduced_pct: float = 1
    reduced_value: int = 0

    def copy(self, target: Player) -> Event:
        """创建事件的副本，指定新的目标玩家。

        Args:
            target (Player): 新的目标玩家。

        Returns:
            Event: 事件的副本，目标为指定的玩家。
        """
        return replace(self, target=target, status_list=deepcopy(self.status_list))

    def apply_buff(self, percentage: float) -> Event:
        """应用百分比加成到事件的值和状态列表。

        Args:
            percentage (float): 要应用的加成百分比。

        Returns:
            Event: 应用了加成后的事件。
        """
        self.value *= percentage
        self.status_list = [x.apply_buff(percentage) for x in self.status_list]
        return self

    def append(self, status: BaseStatus) -> None:
        """将状态附加到事件的状态列表。

        Args:
            status (BaseStatus): 要附加的状态。
        """
        self.status_list.append(status)

    def name_is(self, name: str) -> bool:
        """检查事件名称是否与给定的名称匹配。

        Args:
            name (str): 要检查的名称。

        Returns:
            bool: 如果名称匹配，则为 True，否则为 False。
        """
        return self.name == name

    @staticmethod
    def from_row(row: pd.Series, user: Player, target: Player) -> Event:
        """从 pandas 系列对象创建一个事件对象。

        Args:
            row (pd.Series): 包含事件数据的 pandas 系列对象。
            user (Player): 执行事件的用户。
            target (Player): 事件的目标。

        Returns:
            Event: 创建的事件对象。
        """
        # 设置事件类型
        event_type = (
            EventType.MagicDmg if row["type"] == "magic" else EventType.PhysicDmg
        )

        # 初始化状态列表
        status_list: list[BaseStatus] = []

        # 检查额外状态信息
        extra_status = row.get("extra_info")
        if extra_status and not pd.isna(extra_status):
            status_data = json.loads(extra_status)
            status_type = status_data.pop("type", None)
            if status_type and status_type in STR2STATUS:
                status_list.append(STR2STATUS[status_type](**status_data))

        # 返回新的事件对象
        return Event(
            eventType=event_type,
            name=row["name"],
            value=row["damage"],
            user=user,
            target=target,
            status_list=status_list,
        )

    @staticmethod
    def from_StatusRtn(s: StatusRtn, user: Player, target: Player) -> Event:
        """从 StatusRtn 对象创建一个事件对象。

        Args:
            s (StatusRtn): 包含状态返回数据的 StatusRtn 对象。
            user (Player): 事件的释放者。
            target (Player): 事件的目标。

        Returns:
            Event: 创建的事件对象。
        """
        return Event(
            eventType=s.eventType,
            name=s.name,
            user=user,
            target=target,
            value=s.value,
            status_list=[s.status] if s.status else [],
        )
