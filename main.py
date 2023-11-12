from random import random
from basic import Timer
from effect import Effect, Dot, Mitigation





class Player:
    def __init__(self, name: str, hp: int) -> None:
        self.name: str = name
        self.maxHp: int = hp
        self.natureHealingTimer = Timer(random() * 3)
        self.hp: int = hp
        self.dotList: list[Dot] = []
        self.buffList: list[Effect] = []
        self.totalMitigation: float = 1
        self.isSurvival: bool = True

    def getDirectHurt(self, damage: float) -> None:
        self.hp -= damage * self.totalMitigation

    def getDotHurt(self, duration: float, damage: float) -> None:
        self.dotList.append(Dot(duration, damage * self.totalMitigation))

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
        
        for debuff in self.dotList: # dot扣血
            if debuff.update(timeInterval):
                self.hp -= debuff.dotDamage
        
        if self.hp <= 0: # 判断是否死亡
            self.isSurvival = False
            return
        
        
        totalMitation = 1
        for buff in self.buffList:
            if type(buff) == Mitigation:
                totalMitation = totalMitation * buff.percentage
        self.totalMitigation = totalMitation
        
        # 更新buff和debuff的时间，以及总减伤百分比
        self.updateEffectTime(self.buffList, timeInterval)
        self.updateEffectTime(self.dotList, timeInterval)
        
        if self.naturalHealTimer.update(timeInterval): # 自然回血
            self.hp = min(self.maxHp, self.hp + self.maxHp // 100)
        


    def ifSurvival(self):
        pass


class Aoe:
    def __init__(self, damage: int, dot: Dot | None = None) -> None:
        self.damage = damage
        self.dot = dot


class PlayerList:
    playerList: list[Player] = []

    def addPlayer(self, player: Player) -> None:
        self.playerList.append(player)

    def getAOEHurt(self, aoe: Aoe):
        for player in self.playerList:
            player.getDirectHurt(aoe.damage)
            if aoe.dot is not None:
                player.dotList.append(aoe.dot)


class TimeLine:
    damageList: list[tuple(Aoe, float)] = []

    def addAoe(self, aoe: Aoe, time: float) -> None:
        self.damageList.append((aoe, time))


if __name__ == "__main__":
    pass
