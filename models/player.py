from __future__ import annotations
import traceback
from models.status import EventType

from models.record import Record
from models.event import Event
from models.status import (
    BaseStatus,
    HealBonus,
    Hot,
    IncreaseMaxHp,
    MagicMtg,
    PhysicMtg,
    Shield,
    maxHpShield,
)
from functools import reduce


class Player:
    def __init__(
        self,
        name: str,
        hp: int,
        potency: float,
        magicDefense: float,
        physicDefense: float,
    ) -> None:
        self.name: str = name
        self.maxHp: int = hp
        self.hp: int = hp
        self.statusList: list[BaseStatus] = [
            Hot("naturalHeal", 10000, hp / 100, getSnapshot=False),
            MagicMtg("magicDefense", 10000, magicDefense),
            PhysicMtg("physicDefense", 10000, physicDefense),
        ]
        self.potency: float = potency
        self.isSurvival: bool = True

    def asEventUser(self, event: Event) -> Event:
        """作为事件的使用者, 如果是治疗事件, 计算自身身上的威力"""
        return (
            event.getBuff(self.potency) if event.eventType == EventType.Heal else event
        )

    def asEventTarget(self, event: Event) -> Event:
        """作为事件的对象, 计算受疗或者减伤等"""
        if event.eventType == EventType.TrueHeal:
            # 从普通hot获得的治疗, 直接返回
            return event
        elif event.eventType == EventType.MaxHpChange:
            self.__maxHpChange(-int(event.value))
            return event
        elif event.eventType in [EventType.Heal, EventType.GroundHeal]:
            # 从普通治疗或者地面治疗获得的治疗, 计算实时增益
            return event.getBuff(self.calPct(HealBonus))  # TODO: 地面治疗吃了两次增益
        elif event.eventType == EventType.MagicDmg:
            event.getBuff(self.calPct(MagicMtg))
        elif event.eventType == EventType.PhysicDmg:
            event.getBuff(self.calPct(PhysicMtg))
        event.value = self.calDamageAfterShield(int(event.value))
        return event

    def _buildRecord(
        self,
        value: float = 0,
        status: list[BaseStatus] | BaseStatus = [],
        delay: float = 0,
    ) -> Record:
        return Record([self._buildEvent(value=value, status=status)], delay)

    def _buildEvent(
        self,
        selfTarget: bool = False,
        value: float = 0,
        status: list[BaseStatus] | BaseStatus = [],
    ):
        return Event(
            EventType.Heal,
            traceback.extract_stack()[-3][2],
            self,
            self if selfTarget else allPlayer,
            value,
            status if isinstance(status, list) else [status],
        )

    def calDamageAfterShield(self, damage: int) -> int:
        for status in self.statusList:
            if isinstance(status, Shield):
                if status.value > damage:
                    status.value -= damage
                    return 0
                damage -= int(status.value)
                status.remainTime = 0  # TODO: haima盾逻辑不对
        return damage

    def __maxHpChange(self, hpChange: int) -> None:
        self.maxHp += hpChange
        if hpChange > 0:
            self.hp += hpChange
        else:
            self.hp = max(self.maxHp, self.hp)

    def getStatus(self, status: BaseStatus) -> None:
        """获取buff, 如果是基于自身最大生命值的盾, 则转化为对应数值"""

        # 对基于目标最大生命值百分比的盾而非自己的进行特殊处理
        if isinstance(status, maxHpShield):
            status = status.toShield(self.maxHp)
        elif isinstance(status, IncreaseMaxHp):
            status.increaseHpNum = int(self.maxHp * (status.value - 1))
            self.__maxHpChange(status.increaseHpNum)

        for s in self.statusList:
            if s == status:
                s = status if (not isinstance(status, Shield) or status > s) else s
                return

        # 贤学群盾互顶
        conflict = ["Galvanize", "EkurasianPrognosis", "EkurasianDignosis"]
        if status.name not in conflict:
            return self.statusList.append(status)
        if status.name != conflict[0]:
            self.removeStatus(conflict[0])
        if status.name != conflict[1]:
            self.removeStatus(conflict[1])
        if status.name != conflict[2] and self.searchStatus(conflict[2]):
            return
        self.statusList.append(status)

    def dealWithReadyEvent(self, event: Event) -> Event | None:
        if not self.isSurvival:
            return
        list(map(lambda status: self.getStatus(status), event.statusList))
        # 对于治疗事件
        if event.eventType.value < 3:
            if event.name == "Pepsis":
                if self.removeStatus("EkurasianDignosis"):
                    event.getBuff(1.4)
                elif not self.removeStatus("EkurasianPrognosis"):
                    event.getBuff(0)
            self.hp = min(self.maxHp, self.hp + int(event.value))
            return

        self.hp -= int(event.value)
        if self.hp > 0:
            return
        if self.searchStatus("LivingDead") or self.searchStatus("Holmgang"):
            self.hp = 1
            return
        self.isSurvival = False

    def update(self, timeInterval: float) -> list[Event]:
        """更新所有的status, 如果status, 并返回所有status产生的event"""
        if not self.isSurvival:
            return []
        ret: list[Event] = []
        for status in self.statusList:
            if s := status.update(timeInterval, hpPercentage=self.hp / self.maxHp):
                ret.append(Event.fromStatusRtn(s, self, self))

        # 删除到时的buff
        self.statusList = list(filter(lambda x: x.remainTime > 0, self.statusList))
        return ret

    def calPct(self, myType: type) -> float:
        return reduce(
            lambda x, y: x * (y.value if isinstance(y, myType) else 1),
            self.statusList,
            1,
        )

    def searchStatus(self, name: str, remove: bool = False) -> BaseStatus | None:
        """检查自身有无对应的status"""
        for status in self.statusList:
            if status.name == name:
                if remove:
                    self.statusList.remove(status)
                return status
        return None

    def removeStatus(self, name: str) -> BaseStatus | None:
        return self.searchStatus(name, True)

    def __str__(self) -> str:
        return "{0:<13}: {1:>6}/{2:<6}, statusList: [{3}]\n".format(
            self.name,
            str(self.hp),
            str(self.maxHp),
            ", ".join(
                str(i)
                for i in self.statusList
                if i.name not in ["naturalHeal", "magicDefense", "physicDefense"]
            ),
        )


allPlayer = Player("totalPlayer", 0, 0, 0, 0)
