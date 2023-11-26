import traceback
from models.effect import Effect, Mtg, HealBonus, Hot, maxHpShield
from models.player import Player, allPlayer
from models.record import Record
from models.event import Event, EventType


class PhysicDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def createRecord(
        self,
        target: Player,
        value: float = 0,
        effect: list[Effect] | Effect = [],
    ) -> Record:
        return Record(
            Event(EventType.Heal, traceback.extract_stack()[-2][2], value, effect),
            self,
            target,
        )
    def Tactician(self) -> Record:
        return self.createRecord(allPlayer, effect=Mtg("Tactician", 15, 0.9))


class Bard(PhysicDPS):
    def __init__(self, hp: int, potency: float = 0) -> None:
        super().__init__("Bard", hp, potency)

    def NaturesMinne(self) -> Record:
        return self.createRecord(allPlayer, effect=HealBonus("NaturesMinne", 15, 1.15))


class Dancer(PhysicDPS):
    def __init__(self, hp: int, potency: float = 0) -> None:
        super().__init__("Dancer", hp, potency)

    def Improvisation(self, stack: int = 0) -> Record:
        stackList = [5, 6, 7, 8, 10]
        return self.createRecord(
            allPlayer,
            effect=[
                maxHpShield("ImprovisationShield", 30, stackList[stack]),
                Hot("ImprovisationHot", 15, 100),
            ],
        )

    def CuringWaltz(self) -> Record:
        return self.createRecord(allPlayer, value=300)


class Machinist(PhysicDPS):
    def __init__(self, hp: int, potency: float = 0) -> None:
        super().__init__("Machinist", hp, potency)

    def Dismantle(self) -> Record:
        return self.createRecord(allPlayer, effect=Mtg("Dismantle", 10, 0.9))
