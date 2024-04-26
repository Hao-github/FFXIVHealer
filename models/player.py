from __future__ import annotations
import traceback
from models.status import EventType, StatusRtn

from models.record import Record
from models.event import Event
from models.status import (
    BaseStatus,
    HealBonus,
    Hot,
    IncreaseMaxHp,
    MagicMtg,
    PhysicMtg,
    maxHpShield,
)

from models.statusList import StatusList


class Player:
    def __init__(
        self,
        name: str,
        hp: int,
        damagePerPotency: float,
        magicDefense: float,
        physicDefense: float,
        gcdPotency: int = 0,
    ) -> None:
        self.name: str = name
        self.maxHp: int = hp
        self.hp: int = hp
        self.statusList: StatusList = StatusList(
            [
                Hot("naturalHeal", 10000, hp / 100, getSnapshot=False, display=False),
                MagicMtg("magicDefense", 10000, magicDefense, display=False),
                PhysicMtg("physicDefense", 10000, physicDefense, display=False),
            ]
        )

        self.damagePerPotency: float = damagePerPotency
        self.isSurvival: bool = True
        self.gcdPotency: int = gcdPotency

    def asEventUser(self, event: Event) -> Event:
        """作为事件的使用者, 如果是治疗事件, 计算自身身上的威力"""
        match event.eventType:
            case EventType.Heal | EventType.GroundInit:
                return event.getBuff(self.damagePerPotency)
            case _:
                return event

    def asEventTarget(self, event: Event) -> Event:
        """作为事件的对象, 计算受疗或者减伤等"""
        match event.eventType:
            case EventType.GroundInit:
                event.value *= self.calPct(HealBonus)
            case EventType.MaxHpChange:
                self.__maxHpChange(-int(event.value))
            case EventType.Heal | EventType.GroundHeal:
                event.getBuff(self.calPct(HealBonus))
            case EventType.MagicDmg:
                event.getBuff(self.calPct(MagicMtg))
                event.value = self.calDamageAfterShield(int(event.value))
            case EventType.PhysicDmg:
                event.getBuff(self.calPct(PhysicMtg))
                event.value = self.calDamageAfterShield(int(event.value))
            case EventType.TrueDamage:
                event.value = self.calDamageAfterShield(int(event.value))
        return event

    def calDamageAfterShield(self, damage: int) -> int:
        for status in self.statusList.sheildList:
            if status.value > damage:
                status.value -= damage
                return 0
            damage -= int(status.value)
            status.remainTime = 0
        return damage

    def dealWithReadyEvent(self, event: Event) -> Event | bool:
        if not self.isSurvival:
            return True
        list(map(lambda status: self.__getStatus(status), event.statusList))
        # 对于治疗事件
        if event.eventType.value < 4:
            if event.nameIs("Pepsis"):
                if self.removeShield("EkurasianDignosis"):
                    event.getBuff(1.4)
                elif not self.removeShield("EkurasianPrognosis"):
                    event.getBuff(0)
            self.hp = min(self.maxHp, self.hp + int(event.value))
            return True

        self.hp -= int(event.value)
        if self.hp > 0:
            return self.statusList.calHotTick() < self.hp
        self.isSurvival = False
        return False

    def update(self, timeInterval: float) -> list[Event]:
        """更新所有的status, 并返回所有status产生的event"""
        if not self.isSurvival:
            return []
        rtn: list[StatusRtn] = self.statusList.update(
            timeInterval, hpPercentage=self.hp / self.maxHp, hp=self.hp
        )
        return list(map(lambda x: Event.fromStatusRtn(x, self, self), rtn))

    def calPct(self, myType: type) -> float:
        return self.statusList.calPct(myType)

    def searchStatus(self, name: str) -> BaseStatus | None:
        """检查自身有无对应的status"""
        return self.statusList.searchStatus(name)

    def removeStatus(self, name: str) -> BaseStatus | None:
        return self.statusList.searchStatus(name, True)
    
    def removeShield(self, name: str) -> BaseStatus | None:
        return self.statusList.searchStatus(name, True, True)

    def __str__(self) -> str:
        return (
            f"{self.name:<13}: {str(self.hp):>6}/{str(self.maxHp):<6},"
            f"statusList: [{str(self.statusList)}]\n"
        )

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

    def __maxHpChange(self, hpChange: int) -> None:
        self.maxHp += hpChange
        self.hp = self.hp + hpChange if hpChange > 0 else max(self.maxHp, self.hp)

    def __getStatus(self, status: BaseStatus) -> None:
        """获取buff, 如果是基于自身最大生命值的盾, 则转化为对应数值"""

        # 对基于目标最大生命值百分比的盾而非自己的进行特殊处理
        if isinstance(status, maxHpShield):
            status = status.toShield(self.maxHp)
        elif isinstance(status, IncreaseMaxHp):
            status.increaseHpNum = int(self.maxHp * (status.value - 1))
            self.__maxHpChange(status.increaseHpNum)

        self.statusList.append(status)


allPlayer = Player("totalPlayer", 0, 0, 0, 0)
