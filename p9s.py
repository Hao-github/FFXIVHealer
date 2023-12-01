from models.boss import Boss
from models.event import EventType
from models.record import Record
from models.player import allPlayer, Player


class P9S(Boss):
    timeLine: list[tuple[float, Record]] = []

    def createMagicAoe(self, name: str, damage: int) -> Record:
        return self.createDamage(name, damage, EventType.MagicDamage, target=allPlayer)

    def createPhysicsAoe(self, name: str, damage: int) -> Record:
        return self.createDamage(
            name, damage, EventType.PhysicsDamage, target=allPlayer
        )

    def a(self) -> Record:
        return self.createMagicAoe("暴食预兆", 102000)

    def attack(self, target: Player) -> Record:
        return self.createDamage(
            "攻击", 53000, eventType=EventType.PhysicsDamage, target=target
        )

    def bcc(self) -> Record:
        return self.createMagicAoe("烈火桩", 88000)

    def atqwe(self) -> Record:
        return self.createMagicAoe("灵魂涌动", 88000)

    def atqwqwe(self) -> Record:
        return self.createMagicAoe("暴雷", 88000)

    def atqwqewe(self) -> Record:
        return self.createMagicAoe("古式地裂劲", 77000)

    def atqzwe(self) -> Record:
        return self.createMagicAoe("古式地裂拳", 97000)

    def atqwezcx(self) -> Record:
        return self.createMagicAoe("星屑冲击", 93000)

    def atqzcxwe(self) -> Record:
        return self.createMagicAoe("霹雳", 60000)

    def atqwcvxve(self) -> Record:
        return self.createMagicAoe("野兽胆汁", 60000)

    def atqwcvxsadve(self) -> Record:
        return self.createPhysicsAoe("冲击波", 18000)
