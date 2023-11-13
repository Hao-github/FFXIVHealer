from effect import Effect, Hot, Mitigation, Dot, HealBonus


class Player:
    def __init__(self, name: str, hp: int) -> None:
        self.name: str = name
        self.maxHp: int = hp
        self.hp: int = hp
        self.shieldHp: int = 0
        self.effectList: list[Effect] = []
        self.totalMitigation: float = 1
        self.totalHealBonus: float = 1
        self.isSurvival: bool = True

    def getDamage(self, damage: int) -> None:
        realDamage = damage * self.totalMitigation - self.shieldHp
        if realDamage > 0:
            self.hp -= realDamage
        else:
            self.shieldHp = -realDamage

    def getHeal(self, heal: int) -> None:
        self.hp = min(self.maxHp, self.hp + heal * self.totalHealBonus)

    def getEffect(self, effect: Effect) -> None:
        if type(effect) == Hot:
            self.effectList.append(
                Hot(effect.name, effect.duration, effect.damage * self.totalMitigation)
            )
        elif type(effect) == Mitigation:
            self.effectList.append(effect)

    def getShield(self, shield: int) -> None:
        self.shieldHp += shield * self.totalHealBonus

    def updateEffectTime(
        self, EffectList: list[Effect], timeInterval: float
    ) -> list[Effect]:
        for effect in EffectList:
            effect.remainTime -= timeInterval
        return filter(lambda x: x.remainTime > 0, EffectList)

    def update(self, timeInterval: float) -> None:
        # 如果已经死了就不用update了
        if not self.isSurvival:
            return

        # 更新所有状态的时间，并根据计时器变更数据
        self.resettotalPercentage()
        for effect in self.effectList:
            result = effect.update(timeInterval)
            if type(effect) == Hot and result:  # hot回血或dot扣血
                self.getHeal(effect.healing)
            elif type(effect) == Dot and result:
                self.getDamage(effect.damage)
            elif type(effect) == Mitigation:
                self.totalMitation = self.totalMitation * effect.percentage
            elif type(effect) == HealBonus:
                self.totalHealBonus = self.totalHealBonus * effect.percentage

        if self.hp <= 0:  # 判断是否死亡
            self.isSurvival = False

    def resettotalPercentage(self) -> None:
        self.totalHealBonus = 1
        self.totalMitigation = 1


class Aoe:
    def __init__(self, damage: int, dot: Dot | None = None) -> None:
        self.damage = damage
        self.dot = dot


class PlayerList:
    playerList: list[Player] = []

    def addPlayer(self, player: Player) -> None:
        self.playerList.append(player)
        player.getEffect(Hot("naturalHeal", float("inf"), player.maxHp // 100))

    def getAOEHurt(self, aoe: Aoe):
        for player in self.playerList:
            player.getDamage(aoe.damage)
            if aoe.dot is not None:
                player.getEffect(aoe.dot)


class DamageTimeLine:
    damageList: list[tuple(Aoe, float)] = []

    def addAoe(self, aoe: Aoe, time: float) -> None:
        self.damageList.append((aoe, time))

## TODO: 添加平a，添加死刑，如何标记双t？


if __name__ == "__main__":
    pass
