from functools import reduce
from models.status import EventType
from models.decorator import groundSkill, petSkill, targetSkill
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
        self, name: str, hp: int, potency: float, spellList: list[str]
    ) -> None:
        super().__init__(name, hp, potency, 0.73, 0.84)
        self.spellList: list[str] = spellList

    def asEventUser(self, event: Event) -> Event:
        if event.name in self.spellList:
            event.getBuff(self.calPct(SpellBonus))
        return super().asEventUser(event)


class Scholar(Healer):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Scholar", hp, potency, ["Adloquium", "Succor", "Physics"])
        self.petCoefficient: float = 0.95
        self.critNum: float = 1.6

    def asEventUser(self, event: Event) -> Event:
        if event.name == "Deployment" and (s := event.target.removeStatus("Galvanize")):
            event.target = allPlayer
            event.statusList.append(s)
            return super().asEventUser(event)
        event = self.__dealWithRct(event)
        event = self.__dealWithET(event)
        return super().asEventUser(event)

    def Recitation(self, **kwargs) -> Record:
        return self._buildRecord(True, status=BaseStatus("Recitation", 15))

    def __dealWithRct(self, e: Event) -> Event:
        if e.name not in ["Adloquium", "Succor", "Indomitability", "Excogitation"]:
            return e
        if not self.removeStatus("Recitation"):
            return e
        if e.name == "Adloquium":
            e.append(Shield("Catalyze", 30, 540))
        return e.getBuff(self.critNum)

    def Dissipation(self, **kwargs) -> Record:
        return self._buildRecord(True, status=SpellBonus("Dissipation", 30, 1.2))

    @targetSkill
    def Deployment(self, **kwargs) -> Record:
        return self._buildRecord()

    def EmergencyTactics(self, **kwargs) -> Record:
        return self._buildRecord(True, status=BaseStatus("EmergencyTactics", 15))

    def __dealWithET(self, e: Event) -> Event:
        if e.name in ["Adloquium", "Succor"] and self.removeStatus("EmergencyTactics"):
            e.value = reduce(lambda x, y: x + y.value, e.statusList, e.value)
            e.statusList.clear()
        return e

    # 单奶

    @targetSkill
    def Physick(self, **kwargs) -> Record:
        return self._buildRecord(value=450)

    @targetSkill
    def Adloquium(self, **kwargs) -> Record:
        return self._buildRecord(value=300, status=Shield("Galvanize", 30, 540))

    @targetSkill
    def Lustrate(self, **kwargs) -> Record:
        return self._buildRecord(value=600)

    @targetSkill
    def Excogitation(self, **kwargs) -> Record:
        return self._buildRecord(status=DelayHeal("Excogitation", 45, 800))

    @petSkill
    @targetSkill
    def Aetherpact(self, **kwargs) -> Record:
        time = kwargs.get("duration", 0)
        return self._buildRecord(status=Hot("Aetherpact", time, 300))

    @targetSkill
    def Protraction(self, **kwargs) -> Record:
        return self._buildRecord(status=IncreaseMaxHp("Protraction", 10, 1.1))

    # 群奶
    @petSkill
    def WhisperingDawn(self, **kwargs) -> Record:
        return self._buildRecord(status=Hot("WhisperingDawn", 21, 80))

    def Succor(self, **kwargs) -> Record:
        return self._buildRecord(value=200, status=Shield("Galvanize", 30, 320))

    @petSkill
    def FeyIllumination(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[
                MagicMtg("FeyIllumination", 20, 0.95),
                SpellBonus("FeyIllumination", 20, 1.1),
            ]
        )

    @groundSkill
    def SacredSoil(self, **kwargs) -> Record:
        return self._buildRecord(
            value=100,
            status=[Mtg("SacredSoil", 17, 0.9), Hot("SacredSoil", 15, 100)],
        )

    def Indomitability(self, **kwargs) -> Record:
        return self._buildRecord(value=400)

    @petSkill
    def FeyBlessing(self, **kwargs) -> Record:
        return self._buildRecord(value=320)

    @petSkill
    def Consolation(self, **kwargs) -> Record:
        return self._buildRecord(value=250, status=Shield("Consolation", 30, 250))

    def Expedient(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Expedient", 20, 0.9))


class WhiteMage(Healer):
    aoeSpell: list[str] = ["Medica", "MedicaII", "CureIII", "AfflatusRapture"]

    def __init__(self, hp: int, potency: float) -> None:
        super().__init__(
            "WhiteMage",
            hp,
            potency,
            ["Cure", "CureII", "Regen", "AfflatusSolace"] + self.aoeSpell,
        )
        self.bellCD = 0

    def asEventUser(self, event: Event) -> Event:
        if event.name in self.aoeSpell and self.searchStatus("PlenaryIndulgence"):
            event.value += 200
        elif event.name == "closeTheBell":
            if e := self.removeStatus("LiturgyOfTheBell"):
                event = Event(
                    EventType.Heal, "LiturgyHeal", self, allPlayer, e.value * 200
                )
        return super().asEventUser(event)

    def PlenaryIndulgence(self, **kwargs) -> Record:
        """全大赦"""
        return self._buildRecord(True, status=BaseStatus("PlenaryIndulgence", 10))

    def update(self, timeInterval: float) -> list[Event]:
        self.bellCD -= timeInterval
        return super().update(timeInterval)

    def dealWithReadyEvent(self, event: Event) -> Event | None:
        super().dealWithReadyEvent(event)
        if event.eventType.value > 2:
            return
        if (bell := self.searchStatus("LiturgyOfTheBell")) and self.bellCD <= 0:
            bell.value -= 1
            self.bellCD = 1
            if bell.value == 0:
                bell.remainTime = 0
            return Event(EventType.Heal, "LiturgyHeal", self, allPlayer, 400)

    # 单奶

    @targetSkill
    def Cure(self, **kwargs) -> Record:
        return self._buildRecord(value=500)

    @targetSkill
    def CureII(self, **kwargs) -> Record:
        return self._buildRecord(value=800)

    @targetSkill
    def Regen(self, **kwargs) -> Record:
        return self._buildRecord(status=Hot("Regen", 18, 250))

    @targetSkill
    def Benediction(self, **kwargs) -> Record:
        return self._buildRecord(value=1000000)

    @targetSkill
    def AfflatusSolace(self, **kwargs) -> Record:
        return self._buildRecord(value=800)

    @targetSkill
    def Tetragrammaton(self, **kwargs) -> Record:
        return self._buildRecord(value=700)

    @targetSkill
    def DivineBenison(self, **kwargs) -> Record:
        return self._buildRecord(status=Shield("DivineBenison", 15, 500))

    @targetSkill
    def Aquaveil(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Aquaveil", 8, 0.85))

    def Medica(self, **kwargs) -> Record:
        """医治"""
        return self._buildRecord(value=400)

    def AfflatusRapture(self, **kwargs) -> Record:
        """狂喜之心"""
        return self._buildRecord(value=400)

    def CureIII(self, **kwargs) -> Record:
        """愈疗"""
        return self._buildRecord(value=600)

    def MedicaII(self, **kwargs) -> Record:
        """医济"""
        return self._buildRecord(value=250, status=Hot("MedicaII", 15, 150))

    @groundSkill
    def Asylum(self, **kwargs) -> Record:
        """庇护所"""
        return self._buildRecord(
            value=100,
            status=[Hot("Asylum", 24, 100), HealBonus("Asylum", 26, 1.1)],
        )

    def Assize(self, **kwargs) -> Record:
        """法令"""
        return self._buildRecord(value=400)

    def Temperance(self, **kwargs) -> Record:
        """节制"""
        return Record(
            eventList=[
                self._buildEvent(status=Mtg("Temperance", 22, 0.9)),
                self._buildEvent(True, status=SpellBonus("Temperance", 20, 1.2)),
            ]
        )

    def LiturgyOfTheBell(self, **kwargs) -> Record:
        return self._buildRecord(True, status=BaseStatus("LiturgyOfTheBell", 20, 5))


class Sage(Healer):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__(
            "Sage",
            hp,
            potency,
            [
                "Dignosis",
                "Prognosis",
                "EkurasianDignosis",
                "EkurasianPrognosis",
                "Pneuma",
            ],
        )

    def asEventUser(self, event: Event) -> Event:
        if self.removeStatus("Zoe"):
            event.getBuff(1.5)
        return super().asEventUser(event)

    @targetSkill
    def Dignosis(self, **kwargs) -> Record:
        return self._buildRecord(value=450)

    def Prognosis(self, **kwargs) -> Record:
        return self._buildRecord(value=300)

    def PhysisII(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[Hot("PhysisII", 15, 130), HealBonus("PhysisII", 10, 1.1)]
        )

    @targetSkill
    def EkurasianDignosis(self, **kwargs) -> Record:
        return self._buildRecord(value=300, status=Shield("EkurasianDignosis", 30, 540))

    def EkurasianPrognosis(self, **kwargs) -> Record:
        return self._buildRecord(
            value=100, status=Shield("EkurasianPrognosis", 30, 320)
        )

    @targetSkill
    def Druochole(self, **kwargs) -> Record:
        return self._buildRecord(value=600)

    def Kerachole(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[Mtg("Kerachole", 15, 0.9), Hot("Kerachole", 15, 100)]
        )

    def Ixochole(self, **kwargs) -> Record:
        return self._buildRecord(value=400)

    def Zoe(self, **kwargs) -> Record:
        return self._buildRecord(True, status=BaseStatus("Zoe", 30))

    @targetSkill
    def Taurochole(self, **kwargs) -> Record:
        return self._buildRecord(value=700, status=Mtg("Kerachole", 15, 0.9))

    def Holos(self, **kwargs) -> Record:
        return self._buildRecord(
            value=300, status=[Mtg("Holos", 20, 0.9), Shield("Holos", 30, 300)]
        )

    @targetSkill
    def Krasis(self, **kwargs) -> Record:
        return self._buildRecord(status=HealBonus("Krasis", 10, 1.2))

    def Pneuma(self, **kwargs) -> Record:
        return self._buildRecord(value=600)

    @targetSkill
    def Haima(self, **kwargs) -> Record:
        return self._buildRecord(status=HaimaShield("haima", 15, 300))

    def Panhaima(self, **kwargs) -> Record:
        return self._buildRecord(status=HaimaShield("Panhaima", 15, 200))

    def Pepsis(self, **kwargs) -> Record:
        return self._buildRecord(value=350)


# class Astrologian(Healer):
#     aoeSpell: list[str] = ["AspectedHelios", "Helios"]
#     singleSpell: list[str] = ["Benefic", "BeneficII", "AspectedBenefic"]

#     def __init__(self, hp: int, potency: float) -> None:
#         super().__init__("Astrologian", hp, potency, self.aoeSpell + self.singleSpell)
#         self.SynastryTarget: Player = self

#     def asEventUser(self, event: Event) -> tuple[Event, Player]:
#         # if event.name == "Synastry":
#         #     self.SynastryTarget = target
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
#         #     event.value *= self.potency
#         #     target = allPlayer
#         return super().asEventUser(event, target)

#     # def dealWithReadyEvent(self, event: Event) -> Record | None:
#     #     super().dealWithReadyEvent(event)
#     #     if event.name not in self.singleSpell:
#     #         return
#     #     if self.searchStatus("Synastry") and self.SynastryTarget != self:
#     #         return Record(
#     #             Event(EventType.TrueHeal, "SynastryHeal", event.value * 0.4),
#     #             self,
#     #             self.SynastryTarget,
#     #         )

#     # def Synastry(self) -> Record:
#     #     return self.createRecord(target)

#     def Benefic(self) -> Record:
#         return self.createRecord(target, value=500)

#     def BeneficII(self) -> Record:
#         return self.createRecord(target, value=800)

#     def AspectedBenefic(self) -> Record:
#         return self.createRecord(
#             target, value=250, status=Hot("AspectedBenefic", 15, 250)
#         )

#     def CelestialIntersection(self) -> Record:
#         return self.createRecord(
#             target, value=200, status=Shield("CelestialIntersection", 30, 400)
#         )

#     def Exaltation(self) -> Record:
#         return self.createRecord(
#             target,
#             status=[Mtg("Exaltation", 8, 0.9), DelayHeal("Exaltation", 8, 500)],
#         )

#     # 群奶

#     def Helios(self) -> Record:
#         return self.createRecord(allPlayer, value=400)

#     def AspectedHelios(self) -> Record:
#         return self.createRecord(
#             allPlayer, value=250, status=Hot("AspectedHelios", 15, 150)
#         )

#     def CollectiveUnconscious(self) -> Record:
#         return self.createRecord(
#             allPlayer, status=[Mtg("CU", 5, 0.9), Hot("CU", 15, 100)]
#         )

#     def CelestialOpposition(self) -> Record:
#         return self.createRecord(allPlayer, value=200, status=Hot("CO", 15, 100))

#     def EarthlyStar(self) -> Record:
#         return self.createRecord(allPlayer, value=720)

#     def NeutralSect(self) -> Record:
#         return self.createRecord(self, status=HealBonus("NeutralSect", 20, 1.2))

#     def Horoscope(self) -> Record:
#         return self.createRecord(self, status=BaseStatus("Horoscope", 10, 200))

#     # def closeHoroscope(self) -> Record:
#     #     return self.createRecord(self)

#     def Macrocosmos(self) -> Record:
#         return self.createRecord(allPlayer, status=DelayHeal("Macrocosmos", 15, 200))

#     def Microcosmos(self) -> Record:
#         return self.createRecord(allPlayer)
