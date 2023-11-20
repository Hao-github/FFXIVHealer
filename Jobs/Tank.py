from models.effect import MagicMitigation, Mitigation, Shield, Hot
from models.event import Event, EventType
from models.player import Player


class Tank(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)
        self.RampartRemainTime = 0
        self.HugeDefenseRemainTime = 0

    def Reprisal(self) -> Event:
        return Event(
            EventType.Other, "Reprisal", effect=Mitigation("Reprisal", 10, 0.1)
        )


class Paladin(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Paladin", hp, potency)

    def DivineVeil(self) -> Event:
        return Event(
            EventType.Heal,
            "DivineVeil",
            int(400 * self.potency),
            effect=Shield("DivineVeil", 30, self.maxHp // 10),
        )

    def PassageOfArms(self) -> Event:
        return Event(
            EventType.Other,
            "PassageOfArms",
            effect=Mitigation("PassageOfArms", 5, 0.15),
        )


class Warrior(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Warrior", hp, potency)

    def ShakeItOff(self) -> Event:
        return Event(
            EventType.Heal,
            "ShakeItOff",
            value=int(300 * self.potency),
            effect=[
                Hot("ShakeItOffHot", 15, int(100 * self.potency)),
                Shield("ShakeItOffShield", 30, int(self.maxHp * 0.15)),
            ],
        )


class GunBreaker(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("GunBreaker", hp, potency)

    def HeartOfLight(self) -> Event:
        return Event(
            EventType.Other,
            "HeartOfLight",
            effect=MagicMitigation("HeartOfLight", 15, 0.1),
        )


class DarkKnight(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("GunBreaker", hp, potency)

    def DarkMissionary(self) -> Event:
        return Event(
            EventType.Other,
            "DarkMissionary",
            effect=MagicMitigation("DarkMissionary", 15, 0.1),
        )
