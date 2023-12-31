import traceback
from models.baseStatus import BaseStatus
from models.status import Mtg, HealBonus, Hot, maxHpShield
from models.player import Player, allPlayer
from models.record import Record
from models.event import Event, EventType


class PhysicsDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency, 0.78, 0.78)

    def createRecord(
        self,
        target: Player,
        value: float = 0,
        status: list[BaseStatus] | BaseStatus = [],
    ) -> Record:
        return Record(
            Event(EventType.Heal, traceback.extract_stack()[-2][2], value, status),
            self,
            target,
        )

    def Tactician(self) -> Record:
        return self.createRecord(allPlayer, status=Mtg("Tactician", 15, 0.9))

    def SecondWind(self) -> Record:
        return self.createRecord(self, value=500)


class Bard(PhysicsDPS):
    def __init__(self, hp: int, potency: float = 0) -> None:
        super().__init__("Bard", hp, potency)

    def NaturesMinne(self) -> Record:
        return self.createRecord(allPlayer, status=HealBonus("NaturesMinne", 15, 1.15))


class Dancer(PhysicsDPS):
    def __init__(self, hp: int, potency: float = 0) -> None:
        super().__init__("Dancer", hp, potency)

    def Improvisation(self, stack: int = 0) -> Record:
        stackList = [5, 6, 7, 8, 10]
        return self.createRecord(
            allPlayer,
            status=[
                maxHpShield("Improvisation", 30, stackList[stack]),
                Hot("Improvisation", 15, 100),
            ],
        )

    def CuringWaltz(self) -> Record:
        return self.createRecord(allPlayer, value=300)


class Machinist(PhysicsDPS):
    def __init__(self, hp: int, potency: float = 0) -> None:
        super().__init__("Machinist", hp, potency)

    def Dismantle(self) -> Record:
        return self.createRecord(allPlayer, status=Mtg("Dismantle", 10, 0.9))
