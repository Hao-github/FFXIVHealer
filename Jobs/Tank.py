import traceback
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
        target: Player,
        value: int = 0,
        effect: list[Effect] | Effect = [],
    ) -> Record:
        return Record(
            Event(EventType.Heal, traceback.extract_stack()[-2][2], value, effect),
            self,
            target,
        )

    def Reprisal(self) -> Record:
        return self.createRecord(self, effect=Mtg("Reprisal", 10, 0.9))

    def Vengeance(self) -> Record:
        return self.createRecord(self, effect=Mtg("Vengeance", 15, 0.7))

    def Rampart(self) -> Record:
        return self.createRecord(self, effect=Mtg("Rampart", 20, 0.8))


class Paladin(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Paladin", hp, potency)

    def asEventUser(self, event: Event, target: Player) -> tuple[Event, Player]:
        if event.name == "Intervention":
            event.append(Mtg("Intervention", 8, 0.8 if self.__check() else 0.9))
        return super().asEventUser(event, target)

    def __check(self) -> bool:
        if self.searchEffect("Rampart") or self.searchEffect("Vengeance"):
            return True
        return False

    def DivineVeil(self) -> Record:
        return self.createRecord(
            allPlayer, 400, effect=Shield("DivineVeil", 30, self.maxHp // 10)
        )

    def PassageOfArms(self) -> Record:
        return self.createRecord(allPlayer, effect=Mtg("PassageOfArms", 5, 0.85))

    def Bulwark(self) -> Record:
        return self.createRecord(self, effect=Mtg("Bulwark", 10, 0.8))

    def HolySheltron(self) -> Record:
        return self.createRecord(
            self,
            effect=[
                Mtg("HolySheltron", 8, 0.85),
                Mtg("Knight'sResolve", 4, 0.85),
                Hot("Knight'sResolve", 12, 250),
            ],
        )

    def Intervention(self, target: Player) -> Record:
        return self.createRecord(
            target,
            effect=[Mtg("Knight'sResolve", 4, 0.9), Hot("Knight'sResolve", 12, 250)],
        )


class Warrior(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Warrior", hp, potency)

    def asEventUser(self, event: Event, target: Player) -> tuple[Event, Player]:
        if event.name == "ShakeItOff":
            event.append(maxHpShield("ShakeItOffShield", 30, self.__checkDefense()))
        return super().asEventUser(event, target)

    def __checkDefense(self) -> int:
        origin = 15
        for effect in self.effectList:
            if effect.name in ["Bloodwhetting", "Vengeance", "TrillOfBattle"]:
                effect.remainTime = 0
                origin += 2
        return origin

    def ShakeItOff(self) -> Record:
        return self.createRecord(
            allPlayer, value=300, effect=Hot("ShakeItOffHot", 15, 100)
        )

    def Bloodwhetting(self) -> Record:
        return self.createRecord(
            self,
            effect=[
                Mtg("Bloodwhetting", 8, 0.9),
                Mtg("StemTheFlow", 4, 0.9),
                Hot("BloodwhettingHot", 7.5, 400, interval=2.5),
                Shield("StemTheTide", 20, 400),
            ],
        )

    def NascentFlash(self, target: Player) -> list[Record]:
        return [
            self.createRecord(
                self, effect=Hot("NascentFlashHot", 7.5, 400, interval=2.5)
            ),
            self.createRecord(
                target,
                effect=[
                    Mtg("NascentFlash", 8, 0.9),
                    Mtg("StemTheFlow", 4, 0.9),
                    Hot("NascentFlashHot", 7.5, 400, interval=2.5),
                    Shield("StemTheTide", 20, 400),
                ],
            ),
        ]

    def Equilibrium(self) -> Record:
        return self.createRecord(self, value=1200, effect=Hot("Equilibrium", 15, 200))

    def TrillOfBattle(self) -> Record:
        return self.createRecord(
            self,
            effect=[
                HealBonus("TrillOfBattleHB", 10, 1.2),
                IncreaseMaxHp("TrillOfBattleIMH", 10, 1.2),
            ],
        )


class GunBreaker(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("GunBreaker", hp, potency)

    def asEventUser(self, event: Event, target: Player) -> tuple[Event, Player]:
        if event.name == "HeartOfCorundum" and target != self:
            event.append(Shield("Brutal", 30, 200))
        return super().asEventUser(event, target)

    def HeartOfLight(self) -> Record:
        return self.createRecord(allPlayer, effect=MagicMtg("HeartOfLight", 15, 0.9))

    def Aurora(self, target: Player) -> Record:
        return self.createRecord(target, effect=Hot("Aurora", 18, 200))

    def Camouflage(self) -> Record:
        return self.createRecord(self, effect=Mtg("Camouflage", 20, 0.9))

    def HeartOfCorundum(self, target: Player) -> Record:
        return self.createRecord(
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
        return self.createRecord(self, effect=MagicMtg("DarkMissionary", 15, 0.9))

    def DarkMind(self) -> Record:
        return self.createRecord(self, effect=MagicMtg("DarkMind", 10, 0.8))

    def TheBlackestNight(self, target: Player) -> Record:
        return self.createRecord(target, effect=maxHpShield("TheBlackestNight", 7, 25))

    def Oblation(self, target: Player) -> Record:
        return self.createRecord(target, effect=Mtg("Oblation", 10, 0.9))
