from .effect import (
    DataType,
    Dot,
    Effect,
    HealBonus,
    HealingSpellBonus,
    Hot,
    MagicMitigation,
    Mitigation,
    Shield,
)
from functools import reduce


class Player:
    def __init__(self, name: str, hp: int, potency: float) -> None:
        self.name: str = name
        self.maxHp: int = hp
        self.hp: int = hp
        self.effectList: list[Effect] = []
        self.isSurvival: bool = True
        self.potency: float = potency

    def __getRealDamage(self, damage: int, damageType: DataType) -> int:
        if damageType == DataType.Real:
            return damage
        if damageType == DataType.Magic:
            return int(damage * self.totalMagicMitigation)
        return int(damage * self.totalPhysicsMitigation)

    def __getRealHeal(self, heal: int, healingType: DataType) -> int:
        if healingType == DataType.Real:
            return heal
        return int(heal * self.totalHealBonus)

    def getDamage(
        self,
        damage: int,
        dataType: DataType = DataType.Magic,
    ) -> None:
        damage = self.__getRealDamage(damage, dataType)
        for effect in self.effectList:
            if type(effect) == Shield:
                if effect.shieldHp > damage:
                    effect.shieldHp -= damage
                    return
                damage -= effect.shieldHp
                effect.shieldHp = 0
                effect.remainTime = 0
        self.hp -= damage

    def getHeal(self, heal: int, dataType: DataType = DataType.Magic) -> None:
        self.hp = min(self.maxHp, self.hp + self.__getRealHeal(heal, dataType))

    def getEffect(self, effect: Effect, dataType: DataType = DataType.Magic) -> None:
        if type(effect) == Dot:
            effect.damage = self.__getRealDamage(effect.damage, dataType)
        elif type(effect) == Hot:
            effect.healing = self.__getRealHeal(effect.healing, dataType)
        self.effectList.append(effect)

    def update(self, timeInterval: float) -> None:
        # 如果已经死了就不用update了
        if not self.isSurvival:
            return

        # 根据计时器变更数据
        for effect in self.effectList:
            if effect.update(timeInterval):
                if type(effect) == Hot:
                    self.getHeal(effect.healing, dataType=DataType.Real)
                elif type(effect) == Dot:
                    self.getDamage(effect.damage, dataType=DataType.Real)

        # 删除到时的buff
        self.effectList = list(filter(lambda x: x.remainTime > 0, self.effectList))
        if self.hp <= 0:  # 判断是否死亡
            self.isSurvival = False

    @property
    def totalMagicMitigation(self) -> float:
        return reduce(
            lambda x, y: x
            * (
                1
                - (
                    y.percentage
                    if (type(y) == Mitigation or type(y) == MagicMitigation)
                    else 0
                )
            ),
            self.effectList,
            1,
        )

    @property
    def totalPhysicsMitigation(self) -> float:
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
        ret = reduce(
            lambda x, y: x
            * (1 + (y.percentage if type(y) == HealingSpellBonus else 0)),
            self.effectList,
            1,
        )
        print(self.effectList)
        print(ret)
        return ret
