from models.effect import Mtg
from models.player import Player
from models.event import Event, EventType


class MeleeDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def Feint(self) -> Event:
        return Event(EventType.Other, "Feint", effect=Mtg("Feint", 10, 0.95))
