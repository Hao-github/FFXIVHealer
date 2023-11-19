from models.effect import Mitigation
from models.event import Event, EventType
from models.player import Player
class Tank(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)
        self.RampartRemainTime = 0
        self.HugeDefenseRemainTime = 0
        
    
    def Reprisal(self) -> Event:
        return Event(
            EventType.Other, "Reprisal", effectList=Mitigation("Reprisal", 10, 0.1)
        )