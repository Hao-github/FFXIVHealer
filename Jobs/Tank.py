from models.effect import (
    DelayHeal,
    Effect,
    HealBonus,
    IncreaseMaxHp,
    MagicMtg,
    Mtg,
    Shield,
    Hot,
    maxHpShield,
)
from models.event import Event, EventType
from models.player import Player, allPlayer
from models.record import Record


class Tank(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def createRecord(
        self,
        name: str,
        target: Player,
        value: int = 0,
        effect: list[Effect] | Effect = [],
    ) -> Record:
        return Record(Event(EventType.Heal, name, value, effect), self, target)

    def Reprisal(self) -> Record:
        return self.createRecord("Reprisal", self, effect=Mtg("Reprisal", 10, 0.9))

    def Vengeance(self) -> Record:
        return self.createRecord("Vengeance", self, effect=Mtg("Vengeance", 15, 0.7))

    def Rampart(self) -> Record:
        return self.createRecord("Rampart", self, effect=Mtg("Rampart", 20, 0.8))


class Paladin(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Paladin", hp, potency)

    def asEventUser(self, event: Event, target: Player) -> Event:
        super().asEventUser(event, target)
        if event.name == "Intervention":
            event.append(Mtg("Intervention", 8, 0.8 if self.__check() else 0.9))
        return event

    def __check(self) -> bool:
        if self._searchEffect("Rampart") or self._searchEffect("Vengeance"):
            return True
        return False

    def DivineVeil(self) -> Record:
        return self.createRecord(
            "DivineVeil",
            allPlayer,
            400,
            effect=Shield("DivineVeil", 30, self.maxHp // 10),
        )

    def PassageOfArms(self) -> Record:
        return self.createRecord(
            "PassageOfArms", allPlayer, effect=Mtg("PassageOfArms", 5, 0.85)
        )

    def Bulwark(self) -> Record:
        return self.createRecord("Bulwark", self, effect=Mtg("Bulwark", 10, 0.8))

    def HolySheltron(self) -> Record:
        return self.createRecord(
            "HolySheltron",
            self,
            effect=[
                Mtg("HolySheltron", 8, 0.85),
                Mtg("Knight'sResolve", 4, 0.85),
                Hot("Knight'sResolve", 12, 250),
            ],
        )

    def Intervention(self, target: Player) -> Record:
        return self.createRecord(
            "Intervention",
            target,
            effect=[Mtg("Knight'sResolve", 4, 0.9), Hot("Knight'sResolve", 12, 250)],
        )


class Warrior(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Warrior", hp, potency)

    def asEventUser(self, event: Event, target: Player) -> Event:
        super().asEventUser(event, target)
        if event.name == "ShakeItOff":
            event.append(maxHpShield("ShakeItOffShield", 30, self.__checkDefense()))
        return event

    def __checkDefense(self) -> int:
        origin = 15
        for effect in self.effectList:
            if effect.name in ["Bloodwhetting", "Vengeance", "TrillOfBattle"]:
                effect.remainTime = 0
                origin += 2
        return origin

    def ShakeItOff(self) -> Record:
        return self.createRecord(
            "ShakeItOff", allPlayer, value=300, effect=Hot("ShakeItOffHot", 15, 100)
        )

    def Bloodwhetting(self) -> Record:
        return self.createRecord(
            "Bloodwhetting",
            self,
            effect=[
                Mtg("Bloodwhetting", 8, 0.9),
                Mtg("StemTheFlow", 4, 0.9),
                Hot("BloodwhettingHot", 9, 400),
                Shield("StemTheTide", 20, 400),
            ],
        )

    def NascentFlash(self, target: Player) -> list[Record]:
        return [
            self.createRecord(
                "NascentFlash", self, effect=Hot("NascentFlashHot", 9, 400)
            ),
            self.createRecord(
                "NascentFlash",
                target,
                effect=[
                    Mtg("NascentFlash", 8, 0.9),
                    Mtg("StemTheFlow", 4, 0.9),
                    Hot("NascentFlashHot", 7.5, 400, timeInterval=3),
                    Shield("StemTheTide", 20, 400),
                ],
            ),
        ]

    def Equilibrium(self) -> Record:
        return self.createRecord(
            "Equilibrium", self, value=1200, effect=Hot("Equilibrium", 15, 200)
        )

    def TrillOfBattle(self) -> Record:
        return self.createRecord(
            "TrillOfBattle",
            self,
            effect=[
                HealBonus("TrillOfBattleHB", 10, 1.2),
                IncreaseMaxHp("TrillOfBattleIMH", 10, 1.2),
            ],
        )


class GunBreaker(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("GunBreaker", hp, potency)

    def asEventUser(self, event: Event, target: Player) -> Event:
        if target != self:
            event.append(Shield("Brutal", 30, 200))
        event = super().asEventUser(event, target)
        return event

    def HeartOfLight(self) -> Record:
        return self.createRecord(
            "HeartOfLight", allPlayer, effect=MagicMtg("HeartOfLight", 15, 0.9)
        )

    def Aurora(self, target: Player) -> Record:
        return self.createRecord("Aurora", target, effect=Hot("Aurora", 18, 200))

    def Camouflage(self) -> Record:
        return self.createRecord("Camouflage", self, effect=Mtg("Camouflage", 20, 0.9))

    def HeartOfCorundum(self, target: Player) -> Record:
        return self.createRecord(
            "HeartOfCorundum",
            target,
            effect=[
                Mtg("HeartOfCorundum", 8, 0.85),
                Mtg("ClarityOfCorundum", 4, 0.85),
                DelayHeal("CatharsisOfCorundum", 20, 900),
            ],
        )


class DarkKnight(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("DarkKnight", hp, potency)

    def DarkMissionary(self) -> Record:
        return self.createRecord(
            "DarkMissionary", self, effect=MagicMtg("DarkMissionary", 15, 0.9)
        )

    def DarkMind(self) -> Record:
        return self.createRecord("DarkMind", self, effect=MagicMtg("DarkMind", 10, 0.8))

    def TheBlackestKnight(self, target: Player) -> Record:
        return self.createRecord(
            "TheBlackestKnight", target, effect=maxHpShield("TheBlackestKnight", 7, 25)
        )

    def Oblation(self, target: Player) -> Record:
        return self.createRecord("Oblation", target, effect=Mtg("Oblation", 10, 0.9))
