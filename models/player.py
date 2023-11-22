from models.event import Event
from .effect import (
    DelayHealing,
    Dot,
    Effect,
    HealBonus,
    HealingSpellBonus,
    Hot,
    IncreaseMaxHp,
    MagicMitigation,
    Mitigation,
    Shield,
)
from .basicEnum import EventType
from functools import reduce


class Player:
    def __init__(self, name: str, hp: int, potency: float) -> None:
        self.name: str = name
        self.originalMaxHp: int = hp
        self.maxHp: int = hp
        self.hp: int = hp
        self.effectList: list[Effect] = [Hot("naturalHeal", 10000, hp // 100)]
        self.isSurvival: bool = True
        self.potency: float = potency

    def asEventUser(self, event: Event) -> Event:
        return event

    def asEventTarget(self, event: Event) -> Event:
        if event.eventType == EventType.Heal:
            return self.updateHealEvent(event, self.totalHealBonus)
        elif event.eventType == EventType.Other:
            return event
        elif event.eventType == EventType.MagicDamage:
            event = self.calDamageAfterMtg(event, self.totalMagicMitigation)
        elif event.eventType == EventType.PhysicsDamage:
            event = self.calDamageAfterMtg(event, self.totalPhysicsMitigation)
        event.value = self.calDamageAfterShield(event.value)
        return event

    def calDamageAfterMtg(self, event: Event, percentage: float) -> Event:
        """对伤害进行快照计算"""
        event.value = int(event.value * percentage)
        for effect in event.effectList:
            if type(effect) == Dot:
                effect.value = int(effect.value * percentage)
        return event

    def calDamageAfterShield(self, damage: int) -> int:
        for effect in self.effectList:
            if type(effect) == Shield:
                if effect.value > damage:
                    effect.value -= damage
                    return 0
                damage -= effect.value
                effect.value = 0
                effect.remainTime = 0
        return damage

    def updateHealEvent(self, event: Event, percentage: float) -> Event:
        event.value = int(event.value * percentage)
        for effect in event.effectList:
            if (
                type(effect) == Shield
                or type(effect) == Hot
                or type(effect) == DelayHealing
            ):
                effect.value = int(effect.value * percentage)
        return event

    def getEffect(self, effect: Effect) -> None:
        """获取buff, 如果是基于自身最大生命值的盾, 则转化为对应数值"""
        if type(effect) == Shield:
            if effect.name in [
                "ShakeItOffShield",
                "ImprovisationShield",
            ]:  # 对基于目标最大生命值百分比的盾而非自己的进行特殊处理
                effect.value = self.maxHp * effect.value // 100
        elif type(effect) == IncreaseMaxHp:
            self.maxHp = int(self.maxHp * (1 + effect.percentage))

        # 如果状态列表里已经有盾且新盾小于旧盾值,则不刷新
        if oldEffect := self.findEffect(effect.name):
            if (
                type(effect) == Shield
                and type(oldEffect) == Shield
                and effect.value < oldEffect.value
            ):
                return
            self.effectList.remove(oldEffect)
        self.effectList.append(effect)

    def findEffect(self, effectName: str) -> Effect | None:
        for effect in self.effectList:
            if effect.name == effectName:
                return effect
        return None

    def dealWithReadyEvent(self, event: Event) -> None:
        if event.eventType == EventType.Heal:
            self.hp = min(self.maxHp, self.hp + event.value)
        elif event.eventType != EventType.Other:
            self.hp -= event.value
        for effect in event.effectList:
            self.getEffect(effect)

    def update(self, timeInterval: float) -> list[Event]:
        ret: list[Event] = []
        for effect in self.effectList:
            if effect.update(timeInterval):
                if type(effect) == Hot or type(effect) == DelayHealing:
                    ret.append(Event(EventType.Heal, effect.name, effect.value))
                elif type(effect) == Dot:
                    ret.append(Event(EventType.TrueDamage, effect.name, effect.value))
                elif type(effect) == IncreaseMaxHp:
                    # 增加生命值上限的技能到时间了, 减少对应的上限
                    self.maxHp = int(self.maxHp / (1 + effect.percentage))
                    if self.maxHp < self.originalMaxHp + 10:  # 防止误差
                        self.maxHp = self.originalMaxHp
                    self.hp = max(self.maxHp, self.hp)

        # 删除到时的buff
        self.effectList = list(filter(lambda x: x.remainTime > 0, self.effectList))
        return ret

    def totalPercentage(self, myType: type) -> float:
        if myType not in [Mitigation, MagicMitigation, HealBonus, HealingSpellBonus]:
            return 1
        return reduce(
            lambda x, y: x * (y.percentage if (type(y) == myType) else 1),  # type: ignore
            self.effectList,
            1,
        )

    @property
    def totalMagicMitigation(self) -> float:
        """计算魔法减伤"""
        return self.totalPercentage(MagicMitigation) * self.totalPercentage(Mitigation)

    @property
    def totalPhysicsMitigation(self) -> float:
        """计算物理减伤"""
        return self.totalPercentage(Mitigation)

    @property
    def totalHealBonus(self) -> float:
        """计算受疗增益"""
        return self.totalPercentage(HealBonus)

    @property
    def totalHealingSpellBonus(self) -> float:
        """计算治疗魔法增益"""
        return self.totalPercentage(HealingSpellBonus)
