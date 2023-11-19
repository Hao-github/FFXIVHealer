from models.effect import Mitigation
from models.player import Player
from models.event import Event, EventType


class PhysicDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def Tactician(self) -> Event:
        return Event(EventType.Other, "Feint", effectList=Mitigation("Tactician", 15, 0.1))
