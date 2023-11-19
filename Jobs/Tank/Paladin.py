from Jobs.Tank.Tank import Tank
from models.effect import Mitigation, Shield
from models.event import Event, EventType


class Paladin(Tank):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def DivineVeil(self) -> Event:
        return Event(
            EventType.Heal,
            "DivineVeil",
            int(400 * self.potency),
            effectList=Shield("DivineVeil", 30, self.maxHp // 10),
        )

    def PassageOfArms(self) -> Event:
        return Event(
            EventType.Other,
            "PassageOfArms",
            effectList=Mitigation("PassageOfArms", 5, 0.15),
        )
