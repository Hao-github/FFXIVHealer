from __future__ import annotations
import traceback

from models.record import Record
from .baseStatus import BaseStatus
from models.event import Event, EventType
from .status import (
    HealBonus,
    Hot,
    IncreaseMaxHp,
    MagicMtg,
    PhysicsMtg,
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
        physicsDefense: float,
    ) -> None:
        self.name: str = name
        self.maxHp: int = hp
        self.hp: int = hp
        self.statusList: list[BaseStatus] = [
            Hot("naturalHeal", 10000, hp / 100, isGround=True),
            MagicMtg("magicDefense", 10000, magicDefense),
            PhysicsMtg("physicsDefense", 10000, physicsDefense),
        ]
        self.potency: float = potency
        self.isSurvival: bool = True

    def asEventUser(self, event: Event, target: Player) -> tuple[Event, Player]:
        """作为事件的使用者, 如果是治疗事件, 计算自身身上的威力"""
        if event.eventType == EventType.Heal:
            event.getBuff(self.potency)
        return event, target

    def asEventTarget(self, event: Event) -> Event:
        """作为事件的对象, 计算受疗或者减伤等"""
        if event.eventType == EventType.TrueHeal:
            # 从普通hot获得的治疗, 直接返回
            return event
        elif event.eventType == EventType.MaxHpChange:
            self.__maxHpChange(int(event.value))
            return event
        elif event.eventType in [EventType.Heal, EventType.GroundHeal]:
            # 从普通治疗或者地面治疗获得的治疗, 计算实时增益
            return event.getBuff(self.calPct(HealBonus))
        elif event.eventType == EventType.MagicDamage:
            event.getBuff(self.calPct(MagicMtg))
        elif event.eventType == EventType.PhysicsDamage:
            event.getBuff(self.calPct(PhysicsMtg))
        event.value = self.calDamageAfterShield(int(event.value))
        return event

    def createRecord(
        self,
        target: Player,
        value: float = 0,
        status: list[BaseStatus] | BaseStatus = [],
        delay: float = 0,
    ) -> Record:
        return Record(
            Event(EventType.Heal, traceback.extract_stack()[-2][2], value, status),
            self,
            target,
            delay,
        )

    def calDamageAfterShield(self, damage: int) -> int:
        for status in self.statusList:
            if isinstance(status, Shield):
                if status.value > damage:
                    status.value -= damage
                    return 0
                damage -= int(status.value)
                status.setZero()  # TODO: haima盾逻辑不对
        return damage

    def __maxHpChange(self, hpChange: int) -> None:
        if hpChange > 0:
            self.maxHp += hpChange
            self.hp += hpChange
        else:
            self.maxHp -= hpChange
            self.hp = max(self.maxHp, self.hp)

    def getStatus(self, status: BaseStatus) -> None:
        """获取buff, 如果是基于自身最大生命值的盾, 则转化为对应数值"""

        # 对基于目标最大生命值百分比的盾而非自己的进行特殊处理
        if isinstance(status, maxHpShield):
            status = status.toShield(self.maxHp)
        elif isinstance(status, IncreaseMaxHp):
            status.value = int(self.maxHp * status.value)
            self.__maxHpChange(status.value)

        # 如果状态列表里已经有盾且新盾小于旧盾值,则不刷新
        if oldStatus := self.removeStatus(status.name):
            if isinstance(status, Shield) and status < oldStatus:
                status = oldStatus

        # 贤学群盾互顶
        if status.name in BaseStatus.conflict:
            self.dealWithH2Shield(status)
        self.statusList.append(status)

    def dealWithH2Shield(self, status: BaseStatus):
        if status.name != BaseStatus.conflict[0]:
            self.removeStatus(BaseStatus.conflict[0])
        if status.name != BaseStatus.conflict[1]:
            self.removeStatus(BaseStatus.conflict[1])
        if status.name != BaseStatus.conflict[2]:
            if self.searchStatus(BaseStatus.conflict[2]):
                status.setZero()

    def dealWithPepsis(self, event: Event) -> Event:
        if self.removeStatus("EkurasianDignosis"):
            event.getBuff(1.4)
        elif not self.removeStatus("EkurasianPrognosis"):
            event.getBuff(0)
        return event

    def dealWithReadyEvent(self, event: Event) -> None:
        if not self.isSurvival:
            return
        map(lambda status: self.getStatus(status), event.statusList)

        # 对于治疗事件
        if event.eventType.value < 3:
            if event.name == "Pepsis":
                event = self.dealWithPepsis(event)
            self.hp = min(self.maxHp, self.hp + int(event.value))
            return

        self.hp -= int(event.value)
        self.isSurvival = self.hp > 0

    def update(self, timeInterval: float) -> list[Record]:
        """更新所有的status, 如果status, 并返回所有status产生的event"""
        if not self.isSurvival:
            return []
        ret: list[Record] = []
        for status in self.statusList:
            if event := status.update(timeInterval, hpPercentage=self.hp / self.maxHp):
                ret.append(Record(event, self, self))

        # 删除到时的buff
        self.statusList = [e for e in self.statusList if e.remainTime > 0]
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


allPlayer = Player("totalPlayer", 0, 0, 0, 0)
