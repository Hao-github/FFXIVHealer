from .effect import (
    DataType,
    DelayHealing,
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
        self.effectList: list[Effect] = [Hot("naturalHeal", 10000, hp // 100)]
        self.isSurvival: bool = True
        self.potency: float = potency

    def __getRealDamage(self, damage: int, damageType: DataType) -> int:
        """根据伤害类型计算承受伤害"""
        if damageType == DataType.Real:
            return damage
        if damageType == DataType.Magic:
            return int(damage * self.totalMagicMitigation)
        return int(damage * self.totalPhysicsMitigation)

    def __getRealHeal(self, heal: int, healingType: DataType) -> int:
        """根据治疗类型判断是否吃受疗加成"""
        if healingType == DataType.Real:
            return heal
        return int(heal * self.totalHealBonus)

    def getDamage(
        self,
        damage: int,
        dataType: DataType = DataType.Magic,
    ) -> None:
        """计算承受伤害,并从盾值中抵消"""
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
        """计算治疗数值, 并防止角色血量超上限"""
        self.hp = min(self.maxHp, self.hp + self.__getRealHeal(heal, dataType))

    def getEffect(self, effect: Effect, dataType: DataType = DataType.Magic) -> None:
        """获取buff或者debuff,如果是hot或者dot就要计算快照"""
        if type(effect) == Dot:
            effect.damage = self.__getRealDamage(effect.damage, dataType)
        elif type(effect) == Hot or type(effect) == DelayHealing:
            effect.healing = self.__getRealHeal(effect.healing, dataType)
        elif type(effect) == Shield and effect.name in [
            "ShakeItOffShield",
            "ImprovisationShield",
        ]: # 对基于目标最大生命值百分比的盾而非自己的进行特殊处理
            effect.shieldHp = self.maxHp * effect.shieldHp // 100
        self.effectList.append(effect)

    def update(self, timeInterval: float) -> None:
        # 如果已经死了就不用update了
        if not self.isSurvival:
            return

        # 根据计时器变更数据
        for effect in self.effectList:
            if effect.update(timeInterval):
                if type(effect) == Hot or type(effect) == DelayHealing:
                    self.getHeal(effect.healing, dataType=DataType.Real)
                elif type(effect) == Dot:
                    self.getDamage(effect.damage, dataType=DataType.Real)

        # 删除到时的buff
        self.effectList = list(filter(lambda x: x.remainTime > 0, self.effectList))
        if self.hp <= 0:  # 判断是否死亡
            self.isSurvival = False

    @property
    def totalMagicMitigation(self) -> float:
        """计算魔法减伤"""
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
        """计算物理减伤"""
        return reduce(
            lambda x, y: x * (1 - (y.percentage if type(y) == Mitigation else 0)),
            self.effectList,
            1,
        )

    @property
    def totalHealBonus(self) -> float:
        """计算受疗增益"""
        return reduce(
            lambda x, y: x * (1 + (y.percentage if type(y) == HealBonus else 0)),
            self.effectList,
            1,
        )

    @property
    def totalHealingSpellBonus(self) -> float:
        """计算治疗魔法增益"""
        ret = reduce(
            lambda x, y: x
            * (1 + (y.percentage if type(y) == HealingSpellBonus else 0)),
            self.effectList,
            1,
        )
        return ret
