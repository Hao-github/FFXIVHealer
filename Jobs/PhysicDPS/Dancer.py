from Jobs.PhysicDPS.PhysicDPS import PhysicDPS
from models.effect import Hot, Shield
from models.event import Event, EventType


class Dancer(PhysicDPS):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def Improvisation(self, stack: int = 0) -> Event:
        stackList = [0.05, 0.06, 0.07, 0.08, 0.1]
        return Event(
            EventType.Other,
            "Improvisation",
            effectList=[
                Shield("ImprovisationShield", 30, int(self.maxHp * stackList[stack])),
                Hot("ImprovisationHot", 15, int(100 * self.potency)),
            ],
        )

    def CuringWaltz(self) -> Event:
        return Event(EventType.Heal, "CuringWaltz", value=int(300 * self.potency))
