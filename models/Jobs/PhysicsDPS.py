from models.status import Mtg, HealBonus, Hot, maxHpShield
from models.player import Player
from models.record import Record


class PhysicsDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency, 0.78, 0.78)

    def Tactician(self, **kwargs) -> Record:
        return self.buildRecord(status=Mtg("Tactician", 15, 0.9))

    def SecondWind(self, **kwargs) -> Record:
        return self.buildRecord(True, value=500)


class Bard(PhysicsDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Bard", hp, potency)

    def NaturesMinne(self, **kwargs) -> Record:
        return self.buildRecord(status=HealBonus("NaturesMinne", 15, 1.15))


class Dancer(PhysicsDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Dancer", hp, potency)

    def Improvisation(self, **kwargs) -> Record:
        stackList = [5, 6, 7, 8, 10]
        return self.buildRecord(
            status=[
                maxHpShield("Improvisation", 30, stackList[kwargs.get("stack", 0)]),
                Hot("Improvisation", 15, 100),
            ],
        )

    def CuringWaltz(self, **kwargs) -> Record:
        return self.buildRecord(value=300)


class Machinist(PhysicsDPS):
    def __init__(self, hp: int, potency: float = 0) -> None:
        super().__init__("Machinist", hp, potency)

    def Dismantle(self, **kwargs) -> Record:
        return self.buildRecord(status=Mtg("Dismantle", 10, 0.9))
