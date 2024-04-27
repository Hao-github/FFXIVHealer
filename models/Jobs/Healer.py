from functools import reduce
from models.status import Bell, EventType
from models.Jobs.decorator import (
    cost,
    ground_skill,
    pet_skill,
    self_skill,
    target_skill,
)
from models.status import (
    BaseStatus,
    DelayHeal,
    HaimaShield,
    HealBonus,
    SpellBonus,
    Hot,
    IncreaseMaxHp,
    MagicMtg,
    Mtg,
    Shield,
)
from models.event import Event
from models.player import Player, allPlayer
from models.record import Record


class Healer(Player):
    def __init__(
        self,
        name: str,
        hp: int,
        damage_per_potency: float,
        spellList: list[str],
        gcd_potency: int,
    ) -> None:
        super().__init__(name, hp, damage_per_potency, 0.73, 0.84, gcd_potency)
        self.spellList: list[str] = spellList

    def as_event_user(self, event: Event) -> Event:
        if event.name in self.spellList:
            event.apply_buff(self.calPct(SpellBonus))
        return super().as_event_user(event)


class Scholar(Healer):
    def __init__(self, hp: int, damage_per_potency: float) -> None:
        super().__init__(
            "Scholar", hp, damage_per_potency, ["Adloquium", "Succor", "Physick"], 295
        )
        self.pet_coefficient: float = 0.95
        self.critNum: float = 1.6
        self.ether_potency: int = 100

    def as_event_user(self, event: Event) -> Event:
        if event.name_is("DeploymentTactics"):
            if s := event.target.remove_shield("Galvanize"):
                e = Event(EventType.TrueHeal, event.name, event.user, allPlayer, 0, [s])
                return super().as_event_user(e)
        event = self.__dealWithRct(event)
        event = self.__dealWithET(event)
        return super().as_event_user(event)

    @self_skill
    def Recitation(self, **kwargs) -> Record:
        return self._buildRecord(status=BaseStatus("Recitation", 15))

    def __dealWithRct(self, e: Event) -> Event:
        if e.name not in ["Adloquium", "Succor", "Indomitability", "Excogitation"]:
            return e
        if not self.remove_status("Recitation"):
            return e
        if e.name == "Adloquium":
            e.append(Shield("Catalyze", 30, 540))
        return e.apply_buff(self.critNum)

    @self_skill
    def Dissipation(self, **kwargs) -> Record:
        return self._buildRecord(status=SpellBonus("Dissipation", 30, 1.2))

    @target_skill
    def DeploymentTactics(self, **kwargs) -> Record:
        return self._buildRecord()

    @self_skill
    def EmergencyTactics(self, **kwargs) -> Record:
        return self._buildRecord(status=BaseStatus("EmergencyTactics", 15))

    def __dealWithET(self, e: Event) -> Event:
        if e.name in ["Adloquium", "Succor"] and self.remove_status("EmergencyTactics"):
            e.value = reduce(lambda x, y: x + y.value, e.status_list, e.value)
            e.status_list.clear()
        return e

    # 单奶

    @cost("gcd")
    @target_skill
    def Physick(self, **kwargs) -> Record:
        return self._buildRecord(value=450)

    @cost("gcd")
    @target_skill
    def Adloquium(self, **kwargs) -> Record:
        return self._buildRecord(value=300, status=Shield("Galvanize", 30, 540))

    @cost("ether")
    @target_skill
    def Lustrate(self, **kwargs) -> Record:
        return self._buildRecord(value=600)

    @cost("ether")
    @target_skill
    def Excogitation(self, **kwargs) -> Record:
        return self._buildRecord(status=DelayHeal("Excogitation", 45, 800))

    @pet_skill
    @target_skill
    def Aetherpact(self, **kwargs) -> Record:
        time = kwargs.get("duration", 0)
        return self._buildRecord(status=Hot("Aetherpact", time, 300))

    @target_skill
    def Protraction(self, **kwargs) -> Record:
        return self._buildRecord(status=IncreaseMaxHp("Protraction", 10, 1.1))

    # 群奶
    @pet_skill
    def WhisperingDawn(self, **kwargs) -> Record:
        return self._buildRecord(status=Hot("WhisperingDawn", 21, 80))

    @cost("gcd")
    def Succor(self, **kwargs) -> Record:
        return self._buildRecord(value=200, status=Shield("Galvanize", 30, 320))

    @pet_skill
    def FeyIllumination(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[
                MagicMtg("FeyIllumination", 20, 0.95),
                SpellBonus("FeyIllumination", 20, 1.1, display=False),
            ]
        )

    @cost("ether")
    @ground_skill
    def SacredSoil(self, **kwargs) -> Record:
        return self._buildRecord(
            value=100,
            status=[Mtg("SacredSoil", 17, 0.9), Hot("SacredSoil", 15, 100)],
        )

    @cost("ether")
    def Indomitability(self, **kwargs) -> Record:
        return self._buildRecord(value=400)

    @pet_skill
    def FeyBlessing(self, **kwargs) -> Record:
        return self._buildRecord(value=320)

    @pet_skill
    def Consolation(self, **kwargs) -> Record:
        return self._buildRecord(value=250, status=Shield("Consolation", 30, 250))

    def Expedient(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Expedient", 20, 0.9))


class WhiteMage(Healer):
    aoeSpell: list[str] = ["Medica", "MedicaII", "CureIII", "AfflatusRapture"]
    singleSpell: list[str] = ["Cure", "CureII", "Regen", "AfflatusSolace"]

    def __init__(self, hp: int, damage_per_potency: float) -> None:
        super().__init__(
            "WhiteMage", hp, damage_per_potency, self.singleSpell + self.aoeSpell, 310
        )

    def as_event_user(self, event: Event) -> Event:
        if event.name in self.aoeSpell and self.has_status("PlenaryIndulgence"):
            event.value += 200
        elif event.name_is("closeTheBell"):
            if e := self.has_status("LiturgyOfTheBell"):
                e.remain_time = 0
        elif event.name_is("BellEnd"):
            event.target = allPlayer
        return super().as_event_user(event)

    @self_skill
    def PlenaryIndulgence(self, **kwargs) -> Record:
        """全大赦"""
        return self._buildRecord(status=BaseStatus("PlenaryIndulgence", 10))

    def deal_with_ready_event(self, event: Event) -> Event | bool:
        ret = super().deal_with_ready_event(event)
        if event.eventType.value < 4:
            return ret
        if bell := self.has_status("LiturgyOfTheBell"):
            return self.__process_LiturgyOfTheBell(bell)
        return True

    def __process_LiturgyOfTheBell(self, bell: BaseStatus) -> Event | bool:
        if isinstance(bell, Bell):
            if heal_StatusRtn := bell.get_heal():
                return Event.from_StatusRtn(heal_StatusRtn, self, allPlayer)
        return True

    # 单奶

    @cost("gcd")
    @target_skill
    def Cure(self, **kwargs) -> Record:
        return self._buildRecord(value=500)

    @cost("gcd")
    @target_skill
    def CureII(self, **kwargs) -> Record:
        return self._buildRecord(value=800)

    @cost("gcd")
    @target_skill
    def Regen(self, **kwargs) -> Record:
        return self._buildRecord(status=Hot("Regen", 18, 250))

    @target_skill
    def Benediction(self, **kwargs) -> Record:
        return self._buildRecord(value=1000000)

    @target_skill
    def AfflatusSolace(self, **kwargs) -> Record:
        return self._buildRecord(value=800)

    @target_skill
    def Tetragrammaton(self, **kwargs) -> Record:
        return self._buildRecord(value=700)

    @target_skill
    def DivineBenison(self, **kwargs) -> Record:
        return self._buildRecord(status=Shield("DivineBenison", 15, 500))

    @target_skill
    def Aquaveil(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Aquaveil", 8, 0.85))

    @cost("gcd")
    def Medica(self, **kwargs) -> Record:
        """医治"""
        return self._buildRecord(value=400)

    def AfflatusRapture(self, **kwargs) -> Record:
        """狂喜之心"""
        return self._buildRecord(value=400)

    @cost("gcd")
    def CureIII(self, **kwargs) -> Record:
        """愈疗"""
        return self._buildRecord(value=600)

    @cost("gcd")
    def MedicaII(self, **kwargs) -> Record:
        """医济"""
        return self._buildRecord(value=250, status=Hot("MedicaII", 15, 150))

    @ground_skill
    def Asylum(self, **kwargs) -> Record:
        """庇护所"""
        return self._buildRecord(
            value=100,
            status=[Hot("AsylumHot", 24, 100), HealBonus("Asylum", 26, 1.1)],
        )

    def Assize(self, **kwargs) -> Record:
        """法令"""
        return self._buildRecord(value=400)

    def Temperance(self, **kwargs) -> Record:
        """节制"""
        return Record(
            eventList=[
                self._buildEvent(status=Mtg("TemperanceMtg", 22, 0.9)),
                self._buildEvent(True, status=SpellBonus("Temperance", 20, 1.2)),
            ]
        )

    @self_skill
    def LiturgyOfTheBell(self, **kwargs) -> Record:
        return self._buildRecord(status=Bell("LiturgyOfTheBell", 20, 5))


class Sage(Healer):
    spellList = [
        "Dignosis",
        "Prognosis",
        "EkurasianDignosis",
        "EkurasianPrognosis",
        "Pneuma",
    ]

    def __init__(self, hp: int, damage_per_potency: float) -> None:
        super().__init__("Sage", hp, damage_per_potency, self.spellList, 330)

    def as_event_user(self, event: Event) -> Event:
        if self.remove_status("Zoe"):
            event.apply_buff(1.5)
        return super().as_event_user(event)

    @cost("gcd")
    @target_skill
    def Dignosis(self, **kwargs) -> Record:
        return self._buildRecord(value=450)

    @cost("gcd")
    def Prognosis(self, **kwargs) -> Record:
        return self._buildRecord(value=300)

    def PhysisII(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[Hot("PhysisIIHot", 15, 130), HealBonus("PhysisII", 10, 1.1)]
        )

    @cost("gcd")
    @target_skill
    def EkurasianDignosis(self, **kwargs) -> Record:
        return self._buildRecord(value=300, status=Shield("EkurasianDignosis", 30, 540))

    @cost("gcd")
    def EkurasianPrognosis(self, **kwargs) -> Record:
        return self._buildRecord(
            value=100, status=Shield("EkurasianPrognosis", 30, 320)
        )

    @target_skill
    def Druochole(self, **kwargs) -> Record:
        return self._buildRecord(value=600)

    def Kerachole(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[Mtg("Kerachole", 15, 0.9), Hot("KeracholeHot", 15, 100)]
        )

    def Ixochole(self, **kwargs) -> Record:
        return self._buildRecord(value=400)

    @self_skill
    def Zoe(self, **kwargs) -> Record:
        return self._buildRecord(status=BaseStatus("Zoe", 30))

    @target_skill
    def Taurochole(self, **kwargs) -> Record:
        return self._buildRecord(value=700, status=Mtg("Kerachole", 15, 0.9))

    def Holos(self, **kwargs) -> Record:
        return self._buildRecord(
            value=300, status=[Mtg("Holos", 20, 0.9), Shield("HolosShield", 30, 300)]
        )

    @target_skill
    def Krasis(self, **kwargs) -> Record:
        return self._buildRecord(status=HealBonus("Krasis", 10, 1.2))

    def Pneuma(self, **kwargs) -> Record:
        return self._buildRecord(value=600)

    @target_skill
    def Haima(self, **kwargs) -> Record:
        return self._buildRecord(status=HaimaShield("Haima", 15, 300))

    def Panhaima(self, **kwargs) -> Record:
        return self._buildRecord(status=HaimaShield("Panhaima", 15, 200))

    def Pepsis(self, **kwargs) -> Record:
        return self._buildRecord(value=350)


# class Astrologian(Healer):
#     aoeSpell: list[str] = ["AspectedHelios", "Helios"]
#     singleSpell: list[str] = ["Benefic", "BeneficII", "AspectedBenefic"]

#     def __init__(self, hp: int, damage_per_potency: float) -> None:
#         super().__init__(
#             "Astrologian", hp, damage_per_potency, self.aoeSpell + self.singleSpell, 250
#         )

#     def asEventUser(self, event: Event) -> Event:
#         if event.name in self.aoeSpell:
#             if self.searchStatus("NeutralSect"):
#                 if event.name == "AspectedHelios":
#                     event.append(Shield("AspectedHeliosShield", 30, 312.5))
#                 else:
#                     event.append(Shield("AspectedBeneficShield", 30, 625))
#         #     if self.searchStatus("Horoscope", remove=True):
#         #         self.getStatus(BaseStatus("HugeMoroscope", 30, 400))
#         # elif event.name == "closeHoroscope":
#         #     self.__setStatusZero("Horoscope")
#         # elif event.name == "Horoscope" and event.eventType == EventType.TrueHeal:
#         #     # 表示天宫图时间归0, 将天宫图事件转为群奶
#         #     event.value *= self.damage_per_potency
#         #     target = allPlayer
#         return super().asEventUser(event)

#     @targetSkill
#     def Benefic(self) -> Record:
#         return self._buildRecord(value=500)

#     @targetSkill
#     def BeneficII(self) -> Record:
#         return self._buildRecord(value=800)

#     @targetSkill
#     def AspectedBenefic(self) -> Record:
#         return self._buildRecord(value=250, status=Hot("AspectedBenefic", 15, 250))

#     @targetSkill
#     def CelestialIntersection(self) -> Record:
#         return self._buildRecord(
#             value=200, status=Shield("CelestialIntersection", 30, 400)
#         )

#     @targetSkill
#     def Exaltation(self) -> Record:
#         return self._buildRecord(
#             status=[Mtg("Exaltation", 8, 0.9), DelayHeal("Exaltation", 8, 500)],
#         )

#     # 群奶

#     def Helios(self) -> Record:
#         return self._buildRecord(value=400)

#     def AspectedHelios(self) -> Record:
#         return self._buildRecord(value=250, status=Hot("AspectedHelios", 15, 150))

#     def CollectiveUnconscious(self) -> Record:
#         return self._buildRecord(status=[Mtg("CU", 5, 0.9), Hot("CU", 15, 100)])

#     def CelestialOpposition(self) -> Record:
#         return self._buildRecord(value=200, status=Hot("CO", 15, 100))

#     def EarthlyStar(self) -> Record:
#         return self._buildRecord(value=720)

#     @selfSkill
#     def NeutralSect(self) -> Record:
#         return self._buildRecord(status=HealBonus("NeutralSect", 20, 1.2))

#     def Horoscope(self) -> Record:
#         return self._buildRecord(status=DelayHeal("Horoscope", 10, 200))

#     def Macrocosmos(self) -> Record:
#         return self._buildRecord(status=DelayHeal("Macrocosmos", 15, 200))

#     # def Microcosmos(self) -> Record:
#     #     return self._buildRecord(status=DelayHeal("Horoscope", 10, 250, trigger=-1))
