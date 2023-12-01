from __future__ import annotations
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

    def asEventTarget(self, event: Event, user: Player) -> tuple[Event, Player]:
        """作为事件的对象, 计算受疗或者减伤等"""
        if event.eventType == EventType.TrueHeal:
            # 从普通hot获得的治疗, 直接返回
            return event, user
        elif event.eventType.value < 3:
            # 从普通治疗或者地面治疗获得的治疗, 计算实时增益
            return event.getBuff(self.calPct(HealBonus)), user
        elif event.eventType == EventType.MagicDamage:
            event.getBuff(self.calPct(MagicMtg))
        elif event.eventType == EventType.PhysicsDamage:
            event.getBuff(self.calPct(PhysicsMtg))
        event.value = self.calDamageAfterShield(int(event.value))
        return event, user

    def calDamageAfterShield(self, damage: int) -> int:
        for status in self.statusList:
            if isinstance(status, Shield):
                if status.value > damage:
                    status.value -= damage
                    return 0
                damage -= int(status.value)
                status.setZero()
        return damage

    def getStatus(self, status: BaseStatus) -> None:
        """获取buff, 如果是基于自身最大生命值的盾, 则转化为对应数值"""

        # 对基于目标最大生命值百分比的盾而非自己的进行特殊处理
        if isinstance(status, maxHpShield):
            status = Shield(
                status.name, status.duration, int(self.maxHp * status.value / 100)
            )
        elif isinstance(status, IncreaseMaxHp):
            status.value = int(self.maxHp * status.value)
            self.maxHp += status.value
            self.hp += status.value

        # 如果状态列表里已经有盾且新盾小于旧盾值,则不刷新
        if oldStatus := self.searchStatus(status.name, type(status)):
            if isinstance(status, Shield) and status < oldStatus:
                return
            self.statusList.remove(oldStatus)

        # 贤学群盾互顶
        if status.name in BaseStatus.conflict:
            self.dealWithH2Shield(status)
        self.statusList.append(status)

    def dealWithH2Shield(self, status: BaseStatus):
        if status.name != BaseStatus.conflict[0]:
            self.searchStatus(BaseStatus.conflict[0], remove=True)
        if status.name != BaseStatus.conflict[1]:
            self.searchStatus(BaseStatus.conflict[1], remove=True)
        if status.name != BaseStatus.conflict[2]:
            if self.searchStatus(BaseStatus.conflict[2]):
                status.setZero()

    def dealWithReadyEvent(self, event: Event) -> None:
        if not self.isSurvival:
            return
        for status in event.statusList:
            self.getStatus(status)

        # 对于治疗事件
        if event.eventType.value < 3:
            if event.name == "Pepsis":
                if self.searchStatus("EkurasianDignosis", Shield, remove=True):
                    event.value *= 1.4
                elif not self.searchStatus("EkurasianPrognosis", Shield, remove=True):
                    return
            elif event.name == "Microcosmos":
                if e := self.searchStatus("Macrocosmos"):
                    e.remainTime = 0
            self.hp = min(self.maxHp, self.hp + int(event.value))
            return

        # 对于伤害事件
        if e := self.searchStatus("Macrocosmos"):
            # 如果有大宇宙, 记录大宇宙时自身所受的伤害
            e.value += int(event.value) / 2
        self.hp -= int(event.value)
        self.isSurvival = self.hp > 0

    def update(self, timeInterval: float) -> list[Event]:
        """更新所有的status, 如果status, 并返回所有status产生的event"""
        if not self.isSurvival:
            return []
        ret: list[Event] = []
        for status in self.statusList:
            if event := status.update(timeInterval, hpPercentage=self.hp / self.maxHp):
                if isinstance(status, IncreaseMaxHp):
                    # 增加生命值上限的技能到时间了, 减少对应的上限
                    self.maxHp -= int(status.value)
                    self.hp = max(self.maxHp, self.hp)
                else:
                    ret.append(event)

        # 删除到时的buff
        self.statusList = [e for e in self.statusList if e.remainTime > 0]
        return ret

    def calPct(self, myType: type) -> float:
        return reduce(
            lambda x, y: x * (y.value if isinstance(y, myType) else 1),
            self.statusList,
            1,
        )

    def searchStatus(
        self, name: str, myType: type = BaseStatus, remove: bool = False
    ) -> BaseStatus | None:
        """检查自身有无对应的status, 并且当remove=True时, 移除该status"""
        for status in self.statusList:
            if status.name == name and isinstance(status, myType):
                return status.setZero() if remove else status
        return None


allPlayer = Player("totalPlayer", 0, 0, 0, 0)
