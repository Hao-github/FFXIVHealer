from models.effect import Effect, Mtg, HealBonus, Hot, maxHpShield
from models.player import Player, allPlayer
from models.event import Event, EventType
from models.record import Record


class PhysicDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def createRecord(
        self,
        name: str,
        target: Player,
        value: int = 0,
        effect: list[Effect] | Effect = [],
    ) -> Record:
        return Record(Event(EventType.Heal, name, value, effect), self, target)

    def Tactician(self) -> Record:
        return self.createRecord(
            "Tactician", allPlayer, effect=Mtg("Tactician", 15, 0.9)
        )


class Bard(PhysicDPS):
    def __init__(self, hp: int, potency: float = 0) -> None:
        super().__init__("Bard", hp, potency)

    def NaturesMinne(self) -> Record:
        return self.createRecord(
            "NaturesMinne",
            allPlayer,
            effect=HealBonus("NaturesMinne", 15, 1.15),
        )


class Dancer(PhysicDPS):
    def __init__(self, hp: int, potency: float = 0) -> None:
        super().__init__("Dancer", hp, potency)

    def Improvisation(self, stack: int = 0) -> Record:
        stackList = [5, 6, 7, 8, 10]
        return self.createRecord(
            "Improvisation",
            allPlayer,
            effect=[
                maxHpShield("ImprovisationShield", 30, stackList[stack]),
                Hot("ImprovisationHot", 15, 100),
            ],
        )

    def CuringWaltz(self) -> Record:
        return self.createRecord("CuringWaltz", allPlayer, value=300)


class Machinist(PhysicDPS):
    def __init__(self, hp: int, potency: float = 0) -> None:
        super().__init__("Machinist", hp, potency)

    def Dismantle(self) -> Record:
        return self.createRecord(
            "Dismantle", allPlayer, effect=Mtg("Dismantle", 10, 0.9)
        )
