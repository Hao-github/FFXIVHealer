from Jobs.PhysicDPS.PhysicDPS import PhysicDPS
from models.effect import HealBonus
from models.event import Event, EventType


class Bard(PhysicDPS):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def NaturesMinne(self) -> Event:
        return Event(
            EventType.Other,
            "NaturesMinne",
            effectList=HealBonus("NaturesMinne", 15, 0.15),
        )
