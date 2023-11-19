from Jobs.Tank.tank import Tank
from models.effect import Hot, Shield
from models.event import Event, EventType


class Warrior(Tank):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def ShakeItOff(self) -> Event:
        return Event(
            EventType.Heal,
            "ShakeItOff",
            value=int(300 * self.potency),
            effectList=[
                Hot("ShakeItOffHot", 15, int(100 * self.potency)),
                Shield("ShakeItOffShield", 30, int(self.maxHp * 0.15)),
            ],
        )

