from models.effect import (
    DelayHealing,
    HealBonus,
    IncreaseMaxHp,
    MagicMitigation,
    Mitigation,
    Shield,
    Hot,
    maxHpShield,
)
from models.event import Event, EventType
from models.player import Player


class Tank(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def Reprisal(self) -> Event:
        return Event(
            EventType.Other, "Reprisal", effect=Mitigation("Reprisal", 10, 0.9)
        )

    def Vengeance(self) -> Event:
        return Event(
            EventType.Other, "Vengeance", effect=Mitigation("Vengeance", 15, 0.7)
        )

    def Rampart(self) -> Event:
        return Event(EventType.Other, "Rampart", effect=Mitigation("Rampart", 20, 0.8))


class Paladin(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Paladin", hp, potency)

    def asEventUser(self, event: Event) -> Event:
        if event.name == "Intervention":
            event.effectList.append(
                Mitigation("Intervention", 8, 0.2 if self.__checkDefense() else 0.1)
            )
        return event

    def __checkDefense(self) -> bool:
        if self._searchEffect("Rampart") or self._searchEffect("Vengeance"):
            return True
        return False

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

    def Bulwark(self) -> Event:
        return Event(EventType.Other, "Bulwark", effect=Mitigation("Bulwark", 10, 0.2))

    def HolySheltron(self) -> Event:
        return Event(
            EventType.Other,
            "HolySheltron",
            effect=[
                Mitigation("HolySheltron", 8, 0.15),
                Mitigation("Knight'sResolve", 4, 0.15),
                Hot("Knight'sResolve", 12, int(250 * self.potency)),
            ],
        )

    def Intervention(self) -> Event:
        return Event(
            EventType.Other,
            "Intervention",
            effect=[
                # Mitigation("Intervention", 8, 0.1),
                Mitigation("Knight'sResolve", 4, 0.1),
                Hot("Knight'sResolve", 12, int(250 * self.potency)),
            ],
        )


class Warrior(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Warrior", hp, potency)

    def updateEvent(self, event: Event) -> Event:
        if event.name == "ShakeItOff":
            event.effectList.append(
                maxHpShield("ShakeItOffShield", 30, self.__checkDefense())
            )
        return event

    def __checkDefense(self) -> int:
        origin = 15
        for effect in self.effectList:
            if effect.name in ["Bloodwhetting", "Vengeance", "TrillOfBattle"]:
                effect.remainTime = 0
                origin += 2
        return origin

    def ShakeItOff(self) -> Event:
        return Event(
            EventType.Heal,
            "ShakeItOff",
            value=int(300 * self.potency),
            effect=Hot("ShakeItOffHot", 15, int(100 * self.potency)),
        )

    def Bloodwhetting(self) -> Event:
        return Event(
            EventType.Other,
            "Bloodwhetting",
            effect=[
                Mitigation("Bloodwhetting", 8, 0.1),
                Mitigation("StemTheFlow", 4, 0.1),
                Hot("BloodwhettingHot", 9, int(400 * self.potency)),
                Shield("StemTheTide", 20, int(400 * self.potency)),
            ],
        )

    def NascentFlash(self) -> list[Event]:
        return [
            Event(
                EventType.Other,
                "NascentFlash",
                effect=Hot("NascentFlashHot", 9, int(400 * self.potency)),
            ),
            Event(
                EventType.Other,
                "NascentFlash",
                effect=[
                    Mitigation("NascentFlash", 8, 0.9),
                    Mitigation("StemTheFlow", 4, 0.9),
                    Hot(
                        "NascentFlashHot", 7.5, int(400 * self.potency), timeInterval=3
                    ),
                    Shield("StemTheTide", 20, int(400 * self.potency)),
                ],
            ),
        ]

    def Equilibrium(self) -> Event:
        return Event(
            EventType.Heal,
            "Equilibrium",
            value=int(1200 * self.potency),
            effect=Hot("Equilibrium", 15, int(200 * self.potency)),
        )

    def TrillOfBattle(self) -> Event:
        return Event(
            EventType.Other,
            "TrillOfBattle",
            effect=[
                HealBonus("TrillOfBattleHB", 10, 1.2),
                IncreaseMaxHp("TrillOfBattleIMH", 10, 1.2),
            ],
        )


class GunBreaker(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("GunBreaker", hp, potency)

    def asEventUser(self, event: Event, target: Player) -> Event:
        event = super().asEventUser(event, target)
        if target != self:
            event.effectList.append(Shield("Brutal", 30, int(200 * self.potency)))
        return event

    def HeartOfLight(self) -> Event:
        return Event(
            EventType.Other,
            "HeartOfLight",
            effect=MagicMitigation("HeartOfLight", 15, 0.9),
        )

    def Aurora(self) -> Event:
        return Event(
            EventType.Other, "Aurora", effect=Hot("Aurora", 18, int(200 * self.potency))
        )

    def Camouflage(self) -> Event:
        return Event(
            EventType.Other,
            "Camouflage",
            effect=Mitigation("Camouflage", 20, 0.9),
        )

    def HeartOfCorundum(self) -> Event:
        return Event(
            EventType.Other,
            "HeartOfCorundum",
            effect=[
                Mitigation("HeartOfCorundum", 8, 0.85),
                Mitigation("ClarityOfCorundum", 4, 0.85),
                DelayHealing("CatharsisOfCorundum", 20, int(900 * self.potency)),
            ],
        )


class DarkKnight(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("DarkKnight", hp, potency)

    def DarkMissionary(self) -> Event:
        return Event(
            EventType.Other,
            "DarkMissionary",
            effect=MagicMitigation("DarkMissionary", 15, 0.9),
        )

    def DarkMind(self) -> Event:
        return Event(
            EventType.Other,
            "DarkMind",
            effect=MagicMitigation("DarkMind", 10, 0.8),
        )

    def TheBlackestKnight(self) -> Event:
        return Event(
            EventType.Other,
            "TheBlackestKnight",
            effect=maxHpShield("TheBlackestKnight", 7, 25),
        )

    def Oblation(self) -> Event:
        return Event(
            EventType.Other,
            "Oblation",
            effect=MagicMitigation("Oblation", 10, 0.9),
        )
