from basic import Dot, Effect, HealBonus, Hot, Mitigation, Shield
from functools import reduce


class Player:
    def __init__(self, name: str, hp: int) -> None:
        self.name: str = name
        self.maxHp: int = hp
        self.hp: int = hp
        self.effectList: list[Effect] = []
        self.isSurvival: bool = True

    def getDamage(self, damage: int, fromEffect: bool = False) -> None:
        shieldList: list[Shield] = list(filter(lambda x: type(x) == Shield, self.effectList))
        realDamage: float = damage if fromEffect else damage * self.totalMitigation
        if not shieldList:
            self.hp -= realDamage
            return
        for shield in shieldList:
            if shield.shieldHp > realDamage:
                shield.shieldHp -= realDamage
                return
            realDamage -= shield.shieldHp
            shield.shieldHp = 0
            shield.remainTime = 0
        self.hp -= realDamage

    def getHeal(self, heal: int, fromEffect: bool = False) -> None:
        realHeal = heal if fromEffect else heal * self.totalHealBonus
        self.hp = min(self.maxHp, self.hp + realHeal)

    def getEffect(self, effect: Effect) -> None:
        if type(effect) == Dot:
            effect.damage = effect.damage * self.totalMitigation
        elif type(effect) == Hot:
            effect.healing = effect.healing * self.totalHealBonus
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
