from functools import reduce
from models.Jobs.decorator import selfSkill, targetSkill
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

# class ComboHealingStack:


class Tank(Player):
    def __init__(self, name: str, hp: int, damagePerPotency: float) -> None:
        super().__init__(name, hp, damagePerPotency, 0.48, 0.48)
        self.comboHealingStack: int = 0

    def Reprisal(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Reprisal", 10, 0.9))

    @selfSkill
    def Vengeance(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Vengeance", 15, 0.7))

    @selfSkill
    def Rampart(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Rampart", 20, 0.8))


class Paladin(Tank):
    def __init__(self, hp: int, damagePerPotency: float) -> None:
        super().__init__("Paladin", hp, damagePerPotency)

    def asEventUser(self, event: Event) -> Event:
        if event.nameIs("Intervention"):
            if self.searchStatus("Rampart") or self.searchStatus("Vengeance"):
                event.append(Mtg("Intervention", 8, 0.8))
            else:
                event.append(Mtg("Intervention", 8, 0.9))
        return super().asEventUser(event)

    def DivineVeil(self, **kwargs) -> Record:
        return self._buildRecord(
            value=400,
            status=Shield("DivineVeil", 30, self.maxHp // 10, False),
        )

    def PassageOfArms(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("PassageOfArms", 5, 0.85))

    @selfSkill
    def Bulwark(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Bulwark", 10, 0.8))

    @selfSkill
    def HolySheltron(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[
                Mtg("HolySheltron", 8, 0.85),
                Mtg("Knight'sResolve", 4, 0.85),
                Hot("Knight'sResolve", 12, 250),
            ]
        )

    @targetSkill
    def Intervention(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[Mtg("Knight'sResolve", 4, 0.9), Hot("Knight'sResolve", 12, 250)]
        )

    @selfSkill
    def HallowedGround(self, **kwargs) -> Record:
        return self._buildRecord(status=Shield("HallowedGround", 10, 1000000))


class Warrior(Tank):
    def __init__(self, hp: int, damagePerPotency: float) -> None:
        super().__init__("Warrior", hp, damagePerPotency)

    def asEventUser(self, event: Event) -> Event:
        if event.nameIs("ShakeItOff"):
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

    @selfSkill
    def Bloodwhetting(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[
                Mtg("Bloodwhetting", 8, 0.9),
                Mtg("StemTheFlow", 4, 0.9),
                Hot("Bloodwhetting", 7.5, 400, interval=2.5, display=False),
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
                        Hot("NascentFlash", 7.5, 400, interval=2.5, display=False),
                        Shield("StemTheTide", 20, 400),
                    ]
                ),
                self._buildEvent(
                    True, status=Hot("NascentFlash", 7.5, 400, interval=2.5)
                ),
            ]
        )

    @selfSkill
    def Equilibrium(self, **kwargs) -> Record:
        return self._buildRecord(value=1200, status=Hot("Equilibrium", 15, 200))

    @selfSkill
    def TrillOfBattle(self, **kwargs) -> Record:
        return self._buildRecord(status=IncreaseMaxHp("TrillOfBattle", 10, 1.2))

    @selfSkill
    def Holmgang(self, **kwargs) -> Record:
        return self._buildRecord(status=BaseStatus("Holmgang", 10))

    def dealWithReadyEvent(self, event: Event) -> Event | bool:
        ret = super().dealWithReadyEvent(event)
        if ret is False and self.searchStatus("Holmgang"):
            self.hp = 1
            self.isSurvival = True
            return True
        return ret


class GunBreaker(Tank):
    def __init__(self, hp: int, damagePerPotency: float) -> None:
        super().__init__("GunBreaker", hp, damagePerPotency)

    def asEventUser(self, event: Event) -> Event:
        if event.nameIs("HeartOfCorundum") and event.target != self:
            event.append(Shield("Brutal", 30, 200))
        elif event.nameIs("Superbolide"):
            self.hp = 1
        return super().asEventUser(event)

    def HeartOfLight(self, **kwargs) -> Record:
        return self._buildRecord(status=MagicMtg("HeartOfLight", 15, 0.9))

    @targetSkill
    def Aurora(self, **kwargs) -> Record:
        return self._buildRecord(status=Hot("Aurora", 18, 200))

    @selfSkill
    def Camouflage(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Camouflage", 20, 0.9))

    @targetSkill
    def HeartOfCorundum(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[
                Mtg("HeartOfCorundum", 8, 0.85),
                Mtg("ClarityOfCorundum", 4, 0.85),
                DelayHeal("CatharsisOfCorundum", 20, 900),
            ]
        )

    @selfSkill
    def Superbolide(self, **kwargs) -> Record:
        return self._buildRecord(status=Shield("Superbolide", 10, 1000000))


class DarkKnight(Tank):
    def __init__(self, hp: int, damagePerPotency: float) -> None:
        super().__init__("DarkKnight", hp, damagePerPotency)

    def DarkMissionary(self, **kwargs) -> Record:
        return self._buildRecord(status=MagicMtg("DarkMissionary", 15, 0.9))

    @selfSkill
    def DarkMind(self, **kwargs) -> Record:
        return self._buildRecord(status=MagicMtg("DarkMind", 10, 0.8))

    @targetSkill
    def TheBlackestNight(self, **kwargs) -> Record:
        return self._buildRecord(status=maxHpShield("TheBlackestNight", 7, 25))

    @targetSkill
    def Oblation(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Oblation", 10, 0.9))

    @selfSkill
    def LivingDead(self, **kwargs) -> Record:
        return self._buildRecord(status=BaseStatus("LivingDead", 10))
    
    def dealWithReadyEvent(self, event: Event) -> Event | bool:
        ret = super().dealWithReadyEvent(event)
        if ret is False and self.searchStatus("LivingDead"):
                self.hp = 1
                self.isSurvival = True
                return True
        return ret
