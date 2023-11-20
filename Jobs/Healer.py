from models.effect import Effect, HealBonus, HealingSpellBonus, Hot, Mitigation, Shield
from models.event import Event, EventType
from models.player import Player


class Scholar(Player):
    def __init__(self, hp: int, potency: int, criticalNum: float) -> None:
        super().__init__("Scholar", hp, potency)
        self.petCoefficient: float = 0.95
        self.criticalNum: float = criticalNum

    def Recitation(self) -> Event:
        return Event(EventType.Other, "Recitation", effect=Effect("Recitation", 15))

    def updateEvent(self, event: Event) -> Event:
        if event.name in ["Succor"]:
            self._bonusHealingSpell(event, self.totalHealingSpellBonus)
        if event.name in ["Succor", "Indomitability"]:
            for effect in self.effectList:
                if effect.name == "Recitation":
                    effect.remainTime = 0
                    self._bonusHealingSpell(event, self.criticalNum)
                    break
        return event

    def WhisperingDawn(self) -> Event:
        return Event(
            EventType.Heal,
            "WhisperingDawn",
            0,
            Hot("WhisperingDawn", 21, int(80 * self.potency * self.petCoefficient)),
        )

    def Succor(self) -> Event:
        return Event(
            EventType.Heal,
            "Succor",
            int(200 * self.potency),
            Shield("Succor", 30, int(320 * self.potency)),
        )

    def FeyIllumination(self) -> Event:
        return Event(
            EventType.Other,
            "FeyIllumination",
            effect=[
                Mitigation("FeyIlluminationMtg", 20, 0.05),
                HealingSpellBonus("FeyIlluminationHSB", 20, 0.1),
            ],
        )

    def SacredSoil(self) -> Event:
        return Event(
            EventType.Heal,
            "SacredSoil",
            value=int(100 * self.potency),
            effect=[
                Mitigation("SacredSoilMtg", 18, 0.1),
                Hot("SacredSoilHB", 15, int(100 * self.potency)),
            ],
        )

    def Indomitability(self) -> Event:
        return Event(EventType.Heal, "Indomitability", int(400 * self.potency))

    def Dissipation(self) -> Event:
        return Event(
            EventType.Other,
            "Dissipation",
            effect=HealingSpellBonus("Dissipation", 30, 0.2),
            target=self,
        )

    def FeyBlessing(self) -> Event:
        return Event(
            EventType.Heal, "FeyBlessing", int(320 * self.petCoefficient * self.potency)
        )

    def Consolation(self) -> Event:
        return Event(
            EventType.Heal,
            "Consolation",
            int(250 * self.petCoefficient * self.potency),
            Shield("Consolation", 30, int(250 * self.petCoefficient * self.potency)),
        )

    def Expedient(self) -> Event:
        return Event(
            EventType.Other,
            "Expedient",
            effect=[Mitigation("Expedient", 20, 0.1)],
        )

    def _bonusHealingSpell(self, event: Event, percentage: float) -> Event:
        if event.name in ["Succor"]:
            event.value = int(event.value * percentage)
            for effect in event.effectList:
                if type(effect) == Shield:
                    effect.shieldHp = int(effect.shieldHp * percentage)
        return event


class WhiteMage(Player):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("WhiteMage", hp, potency)

    def updateEvent(self, event: Event) -> Event:
        if event.name in ["Medica", "MedicaII", "CureIII", "AfflatusRapture"]:
            event.value = int(event.value * self.totalHealingSpellBonus)
            for effect in event.effectList:
                if type(effect) == Hot:
                    effect.healing *= int(self.totalHealingSpellBonus)
            for effect in self.effectList:
                if effect.name == "PlenaryIndulgence":
                    event.value += 200
                    break
        return event

    def PlenaryIndulgence(self) -> Event:
        """
        全大赦
        """
        return Event(
            EventType.Other,
            "PlenaryIndulgence",
            effect=Effect("PlenaryIndulgence", 10),
            target=self,
        )

    def Medica(self) -> Event:
        """医治"""
        basicPotency = 400 * self.totalHealingSpellBonus
        return Event(EventType.Heal, "Medica", value=int(basicPotency * self.potency))

    def AfflatusRapture(self) -> Event:
        """狂喜之心"""
        basicPotency = 400 * self.totalHealingSpellBonus
        return Event(
            EventType.Heal, "AfflatusRapture", value=int(basicPotency * self.potency)
        )

    def CureIII(self) -> Event:
        """愈疗"""
        basicPotency = 600 * self.totalHealingSpellBonus
        return Event(EventType.Heal, "CureIII", value=int(basicPotency * self.potency))

    def MedicaII(self) -> Event:
        """医济"""
        basicPotency = 250 * self.totalHealingSpellBonus
        basicHotPotency = 150 * self.totalHealingSpellBonus
        return Event(
            EventType.Heal,
            "MedicaII",
            value=int(basicPotency * self.potency),
            effect=Hot("MedicaII", 15, int(basicHotPotency * self.potency)),
        )

    def Asylum(self) -> Event:
        """庇护所"""
        return Event(
            EventType.Heal,
            "Asylum",
            value=int(100 * self.potency),
            effect=[
                Hot("AsylumHot", 24, int(100 * self.potency)),
                HealBonus("AsylumHB", 27, 0.1),
            ],
        )

    def Assize(self) -> Event:
        """法令"""
        return Event(
            EventType.Heal,
            "Assize",
            value=int(400 * self.potency),
        )

    def Temperance(self) -> Event:
        """节制"""
        self.TemperanceRemainTime = 20
        return Event(
            EventType.Other,
            "Temperance",
            effect=[
                Mitigation("Temperance", 22, 0.1),
                # HealingSpellBonus("TemperanceHSB", 22, 0.2),
            ],
        )


# from basic import Event, EventType, Hot, Mitigation, Shield


# class Astrologian:
#     def __init__(self, potency: int) -> None:
#         self.potency: int = potency
#         self.EarthlyStarRemainTime: float = -1
#         self.NeutralSectRemainTime: float = 0
#         self.HoroscopeRemainTime: float = -1
#         self.MacrocosmosRemainTime: float = -1
#         self.BigHoroscopeRemainTime: float = -1
#         self.HealingSpellBonus: float = 1

#     def update(self) -> None:
#         pass

#     def Helios(self) -> Event:
#         basicPotency: float = 400 * self.HealingSpellBonus
#         if self.HoroscopeRemainTime > 0:
#             self.HoroscopeRemainTime = -1
#             self.BigHoroscopeRemainTime = 30
#         return Event(EventType.Heal, "Helios",value=basicPotency * self.potency)

#     def AspectedHelios(self) -> Event:
#         basicPotency: int = 250 * self.HealingSpellBonus
#         basicHotPotency: int = 150 * self.HealingSpellBonus
#         if self.HoroscopeRemainTime > 0:
#             self.HoroscopeRemainTime = -1
#             self.BigHoroscopeRemainTime = 30
#         ret: Event = Event(
#             EventType.Heal,
#             value=basicPotency * self.potency,
#             effectList=[Hot("AspectedHeliosHot", 15, basicHotPotency * self.potency)],
#         )
#         if self.NeutralSectRemainTime > 0:
#             ret.effectList.append(
#                 Shield("AspectedHeliosShield", 30, basicPotency * 1.25 * self.potency)
#             )
#         return ret

#     def CollectiveUnconscious(self) -> Event:
#         return Event(
#             EventType.Heal,
#             effectList=[
#                 Mitigation("CUMtg", 5, 0.1),
#                 Hot("CUHot", 15, 100),
#             ],
#         )

#     def CelestialOpposition(self) -> Event:
#         return Event(EventType.Heal, value=200, effectList=[Hot("COHot", 15, 100)])

#     def SetEarthlyStar(self) -> None:
#         self.EarthlyStarRemainTime = 20

#     def EarthlyStar(self) -> Event | None:
#         if self.EarthlyStarRemainTime > 10:
#             return Event(EventType.Heal, value=540 * self.potency)
#         elif self.EarthlyStarRemainTime >= 0:
#             return Event(EventType.Heal, value=720 * self.potency)
#         else:
#             return None

#     def SetHoroscope(self) -> None:
#         self.HoroscopeRemainTime = 10

#     def Horoscope(self) -> Event | None:
#         if self.HoroscopeRemainTime > 0:
#             self.HoroscopeRemainTime = -1
#             return Event(EventType.Heal, 200 * self.potency)
#         if self.BigHoroscopeRemainTime > 0:
#             self.HoroscopeRemainTime = -1
#             return Event(EventType.Heal, 400 * self.potency)
#         return None

#     def NeutralSect(self) -> Event | None:
#         self.NeutralSectRemainTime = 20
