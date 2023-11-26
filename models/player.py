from __future__ import annotations
from models.event import Event, EventType
from .effect import (
    DelayHeal,
    Dot,
    Effect,
    HaimaShield,
    HealBonus,
    Hot,
    IncreaseMaxHp,
    MagicMtg,
    Mtg,
    Shield,
    maxHpShield,
)
from functools import reduce


class Player:
    def __init__(self, name: str, hp: int, potency: float) -> None:
        self.name: str = name
        self.maxHp: int = hp
        self.hp: int = hp
        self.effectList: list[Effect] = [Hot("naturalHeal", 10000, hp // 100)]
        self.potency: float = potency
        self.isSurvival: bool = True

    def asEventUser(self, event: Event, target: Player) -> tuple[Event, Player]:
        """作为事件的使用者, 计算自身身上的威力"""
        if event.name == "naturalHeal" or event.eventType != EventType.Heal:
            return event, target
        event.getBuff(self.potency)
        return event, target

    def asEventTarget(self, event: Event, user: Player) -> tuple[Event, Player]:
        """作为事件的对象, 计算受疗或者减伤等"""
        if event.eventType == EventType.TrueHeal:
            return event, user
        elif event.eventType == EventType.Heal:
            event.getBuff(self.calPct(HealBonus))
            return event, user
        elif event.eventType == EventType.MagicDamage:
            event.getBuff(self.calPct(MagicMtg) * self.calPct(Mtg))
        elif event.eventType == EventType.PhysicsDamage:
            event.getBuff(self.calPct(Mtg))
        event.value = self.calDamageAfterShield(int(event.value))
        return event, user

    def calDamageAfterShield(self, damage: int) -> int:
        for effect in self.effectList:
            if isinstance(effect, Shield):
                if effect.value > damage:
                    effect.value -= damage
                    return 0
                damage -= int(effect.value)
                # 对海马类技能特殊处理
                if isinstance(effect, HaimaShield):
                    effect.resetShield()
                else:
                    effect.setZero()
        return damage

    def getEffect(self, effect: Effect) -> None:
        """获取buff, 如果是基于自身最大生命值的盾, 则转化为对应数值"""

        # 对基于目标最大生命值百分比的盾而非自己的进行特殊处理
        if isinstance(effect, maxHpShield):
            effect = Shield(
                effect.name, effect.duration, int(self.maxHp * effect.value / 100)
            )
        elif isinstance(effect, IncreaseMaxHp):
            effect.value = int(self.maxHp * effect.value)
            self.maxHp += effect.value
            self.hp += effect.value

        # 如果状态列表里已经有盾且新盾小于旧盾值,则不刷新
        if oldEffect := self.searchEffect(effect.name):
            if (
                type(effect) == Shield
                and type(oldEffect) == Shield
                and effect.value < oldEffect.value
            ):
                return
            self.effectList.remove(oldEffect)
        self.effectList.append(effect)

    def dealWithReadyEvent(self, event: Event) -> None:
        if event.eventType == EventType.Heal:
            self.hp = min(self.maxHp, self.hp + int(event.value))
        else:
            if e := self.searchEffect("Macrocosmos"):
                # 如果有大宇宙, 记录大宇宙时自身所受的伤害
                e.value += int(event.value) / 2
            self.hp -= int(event.value)
        for effect in event.effectList:
            self.getEffect(effect)
        if self.hp <= 0:
            self.isSurvival = False

    def update(self, timeInterval: float) -> list[Event]:
        if not self.isSurvival:
            return []
        ret: list[Event] = []
        for e in self.effectList:
            if e.update(timeInterval):
                if isinstance(e, (Hot, DelayHeal)):
                    # hot类型为TrueHot以防止重复计算受疗和威力
                    ret.append(Event(EventType.TrueHeal, e.name, e.value))
                elif isinstance(e, Dot):
                    # dot类型为TrueDamage以防止重复计算减伤, 但是仍能判定在盾上
                    ret.append(Event(EventType.TrueDamage, e.name, e.value))
                elif isinstance(e, IncreaseMaxHp):
                    # 增加生命值上限的技能到时间了, 减少对应的上限
                    self.maxHp = self.maxHp - int(e.value)
                    self.hp = max(self.maxHp, self.hp)
                elif isinstance(e, HaimaShield) and e.stack > 0:
                    # 海马盾到期了, 转化为对应的血量
                    ret.append(
                        Event(
                            EventType.TrueHeal,
                            e.name,
                            e.originValue * e.stack / 2,
                            effect=Shield(e.name, e.remainTime, e.value),
                        )
                    )

        # 删除到时的buff
        self.effectList = [e for e in self.effectList if e.remainTime > 0]
        return ret

    def calPct(self, myType: type) -> float:
        return reduce(
            lambda x, y: x * (y.value if (type(y) == myType) else 1),  # type: ignore
            self.effectList,
            1,
        )

    def searchEffect(self, name: str, remove: bool = False) -> Effect | None:
        for effect in self.effectList:
            if effect.name == name:
                if remove:
                    effect.setZero()
                return effect
        return None


allPlayer = Player("totalPlayer", 0, 0)
