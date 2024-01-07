from functools import reduce
from models.baseStatus import BaseStatus
from models.status import (
    DelayHeal,
    IncreaseMaxHp,
    MagicMtg,
    Mtg,
    Shield,
    Hot,
    maxHpShield,
)
from models.event import Event
from models.player import Player, allPlayer
from models.record import Record


class Tank(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency, 0.48, 0.48)

    def Reprisal(self) -> Record:
        return self.buildRecord(self, status=Mtg("Reprisal", 10, 0.9))

    def Vengeance(self) -> Record:
        return self.buildRecord(self, status=Mtg("Vengeance", 15, 0.7))

    def Rampart(self) -> Record:
        return self.buildRecord(self, status=Mtg("Rampart", 20, 0.8))


class Paladin(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Paladin", hp, potency)

    def asEventUser(self, event: Event) -> Event:
        if event.name == "Intervention":
            if self.searchStatus("Rampart") or self.searchStatus("Vengeance"):
                event.append(Mtg("Intervention", 8, 0.8))
            else:
                event.append(Mtg("Intervention", 8, 0.9))
        return super().asEventUser(event)

    def DivineVeil(self) -> Record:
        return self.buildRecord(
            allPlayer, 400, status=Shield("DivineVeil", 30, self.maxHp // 10)
        )

    def PassageOfArms(self) -> Record:
        return self.buildRecord(allPlayer, status=Mtg("PassageOfArms", 5, 0.85))

    def Bulwark(self) -> Record:
        return self.buildRecord(self, status=Mtg("Bulwark", 10, 0.8))

    def HolySheltron(self) -> Record:
        return self.buildRecord(
            self,
            status=[
                Mtg("HolySheltron", 8, 0.85),
                Mtg("Knight'sResolve", 4, 0.85),
                Hot("Knight'sResolve", 12, 250),
            ],
        )

    def Intervention(self, target: Player) -> Record:
        return self.buildRecord(
            target,
            status=[Mtg("Knight'sResolve", 4, 0.9), Hot("Knight'sResolve", 12, 250)],
        )

    def HallowedGround(self) -> Record:
        return self.buildRecord(self, status=Shield("HallowedGround", 10, 1000000))


class Warrior(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Warrior", hp, potency)

    def asEventUser(self, event: Event) -> Event:
        if event.name == "ShakeItOff":
            event.append(maxHpShield("ShakeItOffShield", 30, self.__checkDefense()))
        return super().asEventUser(event)

    def dealWithReadyEvent(self, event: Event) -> None:
        super().dealWithReadyEvent(event)
        if not self.isSurvival and self.searchStatus("Holmgang"):
            self.isSurvival = True
            self.hp = 1

    def __checkDefense(self) -> int:
        return reduce(
            lambda x, y: x + 2 if self.removeStatus(y) else x,
            ["Bloodwhetting", "Vengeance", "TrillOfBattleHB"],
            15,
        )

    def ShakeItOff(self) -> Record:
        return self.buildRecord(
            allPlayer, value=300, status=Hot("ShakeItOffHot", 15, 100)
        )

    def Bloodwhetting(self) -> Record:
        return self.buildRecord(
            self,
            status=[
                Mtg("Bloodwhetting", 8, 0.9),
                Mtg("StemTheFlow", 4, 0.9),
                Hot("BloodwhettingHot", 7.5, 400, interval=2.5),
                Shield("StemTheTide", 20, 400),
            ],
        )

    def NascentFlash(self, target: Player) -> list[Record]:
        return [
            self.buildRecord(
                self, status=Hot("NascentFlashHot", 7.5, 400, interval=2.5)
            ),
            self.buildRecord(
                target,
                status=[
                    Mtg("NascentFlash", 8, 0.9),
                    Mtg("StemTheFlow", 4, 0.9),
                    Hot("NascentFlashHot", 7.5, 400, interval=2.5),
                    Shield("StemTheTide", 20, 400),
                ],
            ),
        ]

    def Equilibrium(self) -> Record:
        return self.buildRecord(self, value=1200, status=Hot("Equilibrium", 15, 200))

    def TrillOfBattle(self) -> Record:
        return self.buildRecord(self, status=IncreaseMaxHp("TrillOfBattle", 10, 1.2))

    def Holmgang(self) -> Record:
        return self.buildRecord(self, status=BaseStatus("Holmgang", 10))


class GunBreaker(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("GunBreaker", hp, potency)

    def asEventUser(self, event: Event) -> Event:
        if event.name == "HeartOfCorundum" and event.target != self:
            event.append(Shield("Brutal", 30, 200))
        elif event.name == "Superbolide":
            self.hp = 1
        return super().asEventUser(event)

    def HeartOfLight(self) -> Record:
        return self.buildRecord(allPlayer, status=MagicMtg("HeartOfLight", 15, 0.9))

    def Aurora(self, target: Player) -> Record:
        return self.buildRecord(target, status=Hot("Aurora", 18, 200))

    def Camouflage(self) -> Record:
        return self.buildRecord(self, status=Mtg("Camouflage", 20, 0.9))

    def HeartOfCorundum(self, target: Player) -> Record:
        return self.buildRecord(
            target,
            status=[
                Mtg("HeartOfCorundum", 8, 0.85),
                Mtg("ClarityOfCorundum", 4, 0.85),
                DelayHeal("CatharsisOfCorundum", 20, 900),
            ],
        )

    def Superbolide(self) -> Record:
        return self.buildRecord(self, status=Shield("Superbolide", 10, 1000000))


class DarkKnight(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("DarkKnight", hp, potency)

    def dealWithReadyEvent(self, event: Event) -> None:
        super().dealWithReadyEvent(event)
        if not self.isSurvival and self.searchStatus("LivingDead"):
            self.isSurvival = True
            self.hp = 1

    def DarkMissionary(self) -> Record:
        return self.buildRecord(self, status=MagicMtg("DarkMissionary", 15, 0.9))

    def DarkMind(self) -> Record:
        return self.buildRecord(self, status=MagicMtg("DarkMind", 10, 0.8))

    def TheBlackestNight(self, target: Player) -> Record:
        return self.buildRecord(target, status=maxHpShield("TheBlackestNight", 7, 25))

    def Oblation(self, target: Player) -> Record:
        return self.buildRecord(target, status=Mtg("Oblation", 10, 0.9))

    def LivingDead(self) -> Record:
        return self.buildRecord(self, status=BaseStatus("LivingDead", 10))
