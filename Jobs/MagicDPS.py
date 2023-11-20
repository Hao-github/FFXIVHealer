from models.effect import Mitigation
from models.player import Player
from models.event import Event, EventType


class MagicDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def Addle(self) -> Event:
        return Event(EventType.Other, "Addle", effect=Mitigation("Addle", 10, 0.1))
