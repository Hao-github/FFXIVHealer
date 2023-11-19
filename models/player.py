from .effect import Dot, Effect, HealBonus, HealingSpellBonus, Hot, Mitigation, Shield
from functools import reduce


class Player:
    def __init__(self, name: str, hp: int, potency: float) -> None:
        self.name: str = name
        self.maxHp: int = hp
        self.hp: int = hp
        self.effectList: list[Effect] = []
        self.isSurvival: bool = True
        self.potency: float = potency

    def getDamage(self, damage: int, fromEffect: bool = False) -> None:
        realDamage: int = int(damage if fromEffect else damage * self.totalMitigation)
        for effect in self.effectList:
            if type(effect) == Shield:
                if effect.shieldHp > realDamage:
                    effect.shieldHp -= realDamage
                    return
                realDamage -= effect.shieldHp
                effect.shieldHp = 0
                effect.remainTime = 0
        self.hp -= realDamage

    def getHeal(self, heal: int, fromEffect: bool = False) -> None:
        realHeal: int = int(heal if fromEffect else heal * self.totalHealBonus)
        self.hp = min(self.maxHp, self.hp + realHeal)

    def getEffect(self, effect: Effect) -> None:
        if type(effect) == Dot:
            effect.damage = int(effect.damage * self.totalMitigation)
        elif type(effect) == Hot:
            effect.healing = int(effect.healing * self.totalHealBonus)
        self.effectList.append(effect)

    def update(self, timeInterval: float) -> None:
        # 如果已经死了就不用update了
        if not self.isSurvival:
            return

        # 根据计时器变更数据
        for effect in self.effectList:
            if effect.update(timeInterval):
                if type(effect) == Hot:
                    self.getHeal(effect.healing, fromEffect=True)
                elif type(effect) == Dot:
                    self.getDamage(effect.damage, fromEffect=True)

        # 删除到时的buff
        self.effectList = list(filter(lambda x: x.remainTime > 0, self.effectList))
        if self.hp <= 0:  # 判断是否死亡
            self.isSurvival = False

    @property
    def totalMitigation(self) -> float:
        return reduce(
            lambda x, y: x * (1 - (y.percentage if type(y) == Mitigation else 0)),
            self.effectList,
            1,
        )

    @property
    def totalHealBonus(self) -> float:
        return reduce(
            lambda x, y: x * (1 + (y.percentage if type(y) == HealBonus else 0)),
            self.effectList,
            1,
        )

    @property
    def totalHealingSpellBonus(self) -> float:
        return reduce(
            lambda x, y: x
            * (1 + (y.percentage if type(y) == HealingSpellBonus else 0)),
            self.effectList,
            1,
        )
