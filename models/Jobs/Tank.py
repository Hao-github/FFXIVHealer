from functools import reduce
from models.decorator import targetSkill
from models.status import (
    BaseStatus,
    DelayHeal,
    IncreaseMaxHp,
    MagicMtg,
    Mtg,
    Shield,
    Hot,
    maxHpShield,
)
from models.event import Event
from models.player import Player
from models.record import Record


class Tank(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency, 0.48, 0.48)

    def Reprisal(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Reprisal", 10, 0.9))

    def Vengeance(self, **kwargs) -> Record:
        return self._buildRecord(True, status=Mtg("Vengeance", 15, 0.7))

    def Rampart(self, **kwargs) -> Record:
        return self._buildRecord(True, status=Mtg("Rampart", 20, 0.8))


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

    def DivineVeil(self, **kwargs) -> Record:
        return self._buildRecord(
            value=400,
            status=Shield("DivineVeil", 30, self.maxHp // (self.potency * 10)),
        )

    def PassageOfArms(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("PassageOfArms", 5, 0.85))

    def Bulwark(self, **kwargs) -> Record:
        return self._buildRecord(True, status=Mtg("Bulwark", 10, 0.8))

    def HolySheltron(self, **kwargs) -> Record:
        return self._buildRecord(
            True,
            status=[
                Mtg("HolySheltron", 8, 0.85),
                Mtg("Knight'sResolve", 4, 0.85),
                Hot("Knight'sResolve", 12, 250),
            ],
        )

    @targetSkill
    def Intervention(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[Mtg("Knight'sResolve", 4, 0.9), Hot("Knight'sResolve", 12, 250)]
        )

    def HallowedGround(self, **kwargs) -> Record:
        return self._buildRecord(True, status=Shield("HallowedGround", 10, 1000000))


class Warrior(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Warrior", hp, potency)

    def asEventUser(self, event: Event) -> Event:
        if event.name == "ShakeItOff":
            event.append(maxHpShield("ShakeItOffShield", 30, self.__checkDefense()))
        return super().asEventUser(event)

    def __checkDefense(self) -> int:
        return reduce(
            lambda x, y: x + 2 if self.removeStatus(y) else x,
            ["Bloodwhetting", "Vengeance", "TrillOfBattleHB"],
            15,
        )

    def ShakeItOff(self, **kwargs) -> Record:
        return self._buildRecord(value=300, status=Hot("ShakeItOffHot", 15, 100))

    def Bloodwhetting(self, **kwargs) -> Record:
        return self._buildRecord(
            True,
            status=[
                Mtg("Bloodwhetting", 8, 0.9),
                Mtg("StemTheFlow", 4, 0.9),
                Hot("BloodwhettingHot", 7.5, 400, interval=2.5),
                Shield("StemTheTide", 20, 400),
            ],
        )

    @targetSkill
    def NascentFlash(self, **kwargs) -> Record:
        return Record(
            [
                self._buildEvent(
                    status=[
                        Mtg("NascentFlash", 8, 0.9),
                        Mtg("StemTheFlow", 4, 0.9),
                        Hot("NascentFlashHot", 7.5, 400, interval=2.5),
                        Shield("StemTheTide", 20, 400),
                    ]
                ),
                self._buildEvent(
                    True, status=Hot("NascentFlashHot", 7.5, 400, interval=2.5)
                ),
            ]
        )

    def Equilibrium(self, **kwargs) -> Record:
        return self._buildRecord(True, value=1200, status=Hot("Equilibrium", 15, 200))

    def TrillOfBattle(self, **kwargs) -> Record:
        return self._buildRecord(True, status=IncreaseMaxHp("TrillOfBattle", 10, 1.2))

    def Holmgang(self, **kwargs) -> Record:
        return self._buildRecord(True, status=BaseStatus("Holmgang", 10))


class GunBreaker(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("GunBreaker", hp, potency)

    def asEventUser(self, event: Event) -> Event:
        if event.name == "HeartOfCorundum" and event.target != self:
            event.append(Shield("Brutal", 30, 200))
        elif event.name == "Superbolide":
            self.hp = 1
        return super().asEventUser(event)

    def HeartOfLight(self, **kwargs) -> Record:
        return self._buildRecord(status=MagicMtg("HeartOfLight", 15, 0.9))

    @targetSkill
    def Aurora(self, **kwargs) -> Record:
        return self._buildRecord(status=Hot("Aurora", 18, 200))

    def Camouflage(self, **kwargs) -> Record:
        return self._buildRecord(True, status=Mtg("Camouflage", 20, 0.9))

    @targetSkill
    def HeartOfCorundum(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[
                Mtg("HeartOfCorundum", 8, 0.85),
                Mtg("ClarityOfCorundum", 4, 0.85),
                DelayHeal("CatharsisOfCorundum", 20, 900),
            ]
        )

    def Superbolide(self, **kwargs) -> Record:
        return self._buildRecord(True, status=Shield("Superbolide", 10, 1000000))


class DarkKnight(Tank):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("DarkKnight", hp, potency)

    def DarkMissionary(self, **kwargs) -> Record:
        return self._buildRecord(status=MagicMtg("DarkMissionary", 15, 0.9))

    def DarkMind(self, **kwargs) -> Record:
        return self._buildRecord(True, status=MagicMtg("DarkMind", 10, 0.8))

    @targetSkill
    def TheBlackestNight(self, **kwargs) -> Record:
        return self._buildRecord(status=maxHpShield("TheBlackestNight", 7, 25))

    @targetSkill
    def Oblation(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Oblation", 10, 0.9))

    def LivingDead(self, **kwargs) -> Record:
        return self._buildRecord(True, status=BaseStatus("LivingDead", 10))
