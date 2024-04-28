from .decorator import self_skill, target_skill
from ..Status import (
    BaseStatus,
    DelayHeal,
    IncreaseMaxHp,
    MagicMtg,
    Mtg,
    Shield,
    Hot,
    MaxHpShield,
)
from ..Event import Event
from ..player import Player
from ..Record import Record

# class ComboHealingStack:


class Tank(Player):
    def __init__(self, name: str, hp: int, damage_per_potency: float) -> None:
        super().__init__(name, hp, damage_per_potency, 0.48, 0.48)
        self.combo_healing_stack: int = 0

    def Reprisal(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Reprisal", 10, 0.9))

    @self_skill
    def Vengeance(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Vengeance", 15, 0.7))

    @self_skill
    def Rampart(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Rampart", 20, 0.8))


class Paladin(Tank):
    def __init__(self, hp: int, damage_per_potency: float) -> None:
        super().__init__("Paladin", hp, damage_per_potency)

    def as_event_user(self, event: Event) -> Event:
        """处理作为事件使用者的逻辑"""
        event.append(self.__get_intervention_status())
        return super().as_event_user(event)

    def __get_intervention_status(self) -> Mtg:
        """根据角色状态获取Intervention状态"""
        reduction = (
            0.8 if self.has_status("Rampart") or self.has_status("Vengeance") else 0.9
        )
        return Mtg("Intervention", 8, reduction)

    def DivineVeil(self, **kwargs) -> Record:
        return self._buildRecord(
            value=400,
            status=Shield("DivineVeil", 30, self.max_hp // 10, False),
        )

    def PassageOfArms(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("PassageOfArms", 5, 0.85))

    @self_skill
    def Bulwark(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Bulwark", 10, 0.8))

    @self_skill
    def HolySheltron(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[
                Mtg("HolySheltron", 8, 0.85),
                Mtg("Knight'sResolve", 4, 0.85),
                Hot("Knight'sResolveHot", 12, 250),
            ]
        )

    @target_skill
    def Intervention(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[Mtg("Knight'sResolve", 4, 0.9), Hot("Knight'sResolveHot", 12, 250)]
        )

    @self_skill
    def HallowedGround(self, **kwargs) -> Record:
        return self._buildRecord(status=Shield("HallowedGround", 10, 1000000))


class Warrior(Tank):
    status_to_check = ["Bloodwhetting", "Vengeance", "TrillOfBattleHB"]

    def __init__(self, hp: int, damage_per_potency: float) -> None:
        super().__init__("Warrior", hp, damage_per_potency)

    def as_event_user(self, event: Event) -> Event:
        if event.name_is("ShakeItOff"):
            defense_bonus = self.__calculate_defense_bonus()
            event.append(MaxHpShield("ShakeItOffShield", 30, defense_bonus))
        return super().as_event_user(event)

    def __calculate_defense_bonus(self) -> int:
        return 15 + sum(
            2 for status in self.status_to_check if self.remove_status(status)
        )

    def ShakeItOff(self, **kwargs) -> Record:
        return self._buildRecord(value=300, status=Hot("ShakeItOffHot", 15, 100))

    @self_skill
    def Bloodwhetting(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[
                Mtg("Bloodwhetting", 8, 0.9),
                Mtg("StemTheFlow", 4, 0.9),
                Hot("Bloodwhetting", 7.5, 400, interval=2.5, display=False),
                Shield("StemTheTide", 20, 400),
            ],
        )

    @target_skill
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
                    True,
                    status=Hot("NascentFlash", 7.5, 400, interval=2.5, display=False),
                ),
            ]
        )

    @self_skill
    def Equilibrium(self, **kwargs) -> Record:
        return self._buildRecord(value=1200, status=Hot("Equilibrium", 15, 200))

    @self_skill
    def TrillOfBattle(self, **kwargs) -> Record:
        return self._buildRecord(status=IncreaseMaxHp("TrillOfBattle", 10, 1.2))

    @self_skill
    def Holmgang(self, **kwargs) -> Record:
        return self._buildRecord(status=BaseStatus("Holmgang", 10))

    def deal_with_ready_event(self, event: Event) -> Event | bool:
        ret = super().deal_with_ready_event(event)
        if not ret and self.has_status("Holmgang"):
            self.hp = 1
            self.is_survival = True
            return True
        return ret


class GunBreaker(Tank):
    def __init__(self, hp: int, damage_per_potency: float) -> None:
        super().__init__("GunBreaker", hp, damage_per_potency)

    def as_event_user(self, event: Event) -> Event:
        if event.name_is("HeartOfCorundum") and event.target != self:
            event.append(Shield("Brutal", 30, 200))
        elif event.name_is("Superbolide"):
            self.hp = 1
        return super().as_event_user(event)

    def HeartOfLight(self, **kwargs) -> Record:
        return self._buildRecord(status=MagicMtg("HeartOfLight", 15, 0.9))

    @target_skill
    def Aurora(self, **kwargs) -> Record:
        return self._buildRecord(status=Hot("Aurora", 18, 200))

    @self_skill
    def Camouflage(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Camouflage", 20, 0.9))

    @target_skill
    def HeartOfCorundum(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[
                Mtg("HeartOfCorundum", 8, 0.85),
                Mtg("ClarityOfCorundum", 4, 0.85),
                DelayHeal("CatharsisOfCorundum", 20, 900),
            ]
        )

    @self_skill
    def Superbolide(self, **kwargs) -> Record:
        return self._buildRecord(status=Shield("Superbolide", 10, 1000000))


class DarkKnight(Tank):
    def __init__(self, hp: int, damage_per_potency: float) -> None:
        super().__init__("DarkKnight", hp, damage_per_potency)

    def DarkMissionary(self, **kwargs) -> Record:
        return self._buildRecord(status=MagicMtg("DarkMissionary", 15, 0.9))

    @self_skill
    def DarkMind(self, **kwargs) -> Record:
        return self._buildRecord(status=MagicMtg("DarkMind", 10, 0.8))

    @target_skill
    def TheBlackestNight(self, **kwargs) -> Record:
        return self._buildRecord(status=MaxHpShield("TheBlackestNight", 7, 25))

    @target_skill
    def Oblation(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Oblation", 10, 0.9))

    @self_skill
    def LivingDead(self, **kwargs) -> Record:
        return self._buildRecord(status=BaseStatus("LivingDead", 10))

    def deal_with_ready_event(self, event: Event) -> Event | bool:
        ret = super().deal_with_ready_event(event)
        if ret is False and self.has_status("LivingDead"):
            self.hp = 1
            self.is_survival = True
            return True
        return ret
