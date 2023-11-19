from models.effect import Mitigation
from models.player import Player
from models.event import Event, EventType


class Machinist(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def Dismantle(self) -> Event:
        return Event(
            EventType.Other, "Dismantle", effectList=Mitigation("Dismantle", 10, 0.1)
        )
