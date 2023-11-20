from models.effect import Mitigation, HealBonus, Shield, Hot
from models.player import Player
from models.event import Event, EventType


class PhysicDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def Tactician(self) -> Event:
        return Event(EventType.Other, "Feint", effect=Mitigation("Tactician", 15, 0.1))


class Bard(PhysicDPS):
    def __init__(self, hp: int, potency: float = 0) -> None:
        super().__init__("Bard", hp, potency)

    def NaturesMinne(self) -> Event:
        return Event(
            EventType.Other,
            "NaturesMinne",
            effect=HealBonus("NaturesMinne", 15, 0.15),
        )


class Dancer(PhysicDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Dancer", hp, potency)

    def Improvisation(self, stack: int = 0) -> Event:
        stackList = [0.05, 0.06, 0.07, 0.08, 0.1]
        return Event(
            EventType.Other,
            "Improvisation",
            effect=[
                Shield("ImprovisationShield", 30, int(self.maxHp * stackList[stack])),
                Hot("ImprovisationHot", 15, int(100 * self.potency)),
            ],
        )

    def CuringWaltz(self) -> Event:
        return Event(EventType.Heal, "CuringWaltz", value=int(300 * self.potency))


class Machinist(Player):
    def __init__(self, hp: int, potency: float = 0) -> None:
        super().__init__("Machinist", hp, potency)

    def Dismantle(self) -> Event:
        return Event(
            EventType.Other, "Dismantle", effect=Mitigation("Dismantle", 10, 0.1)
        )