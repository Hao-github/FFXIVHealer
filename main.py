from enum import Enum
from playerPart import Player, PlayerList


class DamageType(Enum):
    PhysicsAoe = 0
    MagicAoe = 1
    PhysicsAA = 2
    MagicAA = 3


class HealingType(Enum):
    Hot = 0
    Mitigation = 1
    DirectHeal = 2
    Shield = 3

class DamageTimeLine:
    # 格式为(伤害类型[aoe还是死刑还是aa], 数值, 伤害判定时间)
    damageList: list[tuple[DamageType, int, float]] = []

    def addMagicAoe(self, damage: int, time: float) -> None:
        self.damageList.append((DamageType.MagicAoe, damage, time))

    def addPhysicsAoe(self, damage: int, time: float) -> None:
        self.damageList.append((DamageType.PhysicsAoe, damage, time))

    def addMagicAA(self, damage: int, time: float) -> None:
        self.damageList.append((DamageType.MagicAA, damage, time))

    def addPhysicsAA(self, damage: int, time: float) -> None:
        self.damageList.append((DamageType.PhysicsAA, damage, time))


# class HealingTimeLine:
#     healingList: list[tuple(DamageType, int, float)] = []

    # def  add


if __name__ == "__main__":
    PlayerList.addPlayer(Player("mt", 120000))
    PlayerList.addPlayer(Player("st", 120000))
    PlayerList.addPlayer(Player("h1", 80000))
    PlayerList.addPlayer(Player("h2", 80000))
    PlayerList.addPlayer(Player("d1", 80000))
    PlayerList.addPlayer(Player("d2", 80000))
    PlayerList.addPlayer(Player("d3", 80000))
    PlayerList.addPlayer(Player("d4", 80000))

    pass
