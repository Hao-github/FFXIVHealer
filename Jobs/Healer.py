from models.effect import (
    Effect,
    HealBonus,
    HealingSpellBonus,
    Hot,
    MagicMitigation,
    Mitigation,
    Shield,
)
from models.event import Event, EventType
from models.player import Player


class Healer(Player):
    def __init__(
        self, name: str, hp: int, potency: float, spellList: list[str]
    ) -> None:
        super().__init__(name, hp, potency)
        self.HealingSpellList: list[str] = spellList

    def updateEvent(self, event: Event) -> Event:
        if event.name in self.HealingSpellList:
            self._bonusHealingSpell(event, self.totalHealingSpellBonus)
        return event

    def _bonusHealingSpell(self, event: Event, percentage: float) -> Event:
        event.value = int(event.value * percentage)
        for effect in event.effectList:
            if type(effect) == Shield:
                effect.shieldHp = int(effect.shieldHp * percentage)
            elif type(effect) == Hot:
                effect.healing = int(effect.healing * percentage)
        return event


class Scholar(Healer):
    def __init__(self, hp: int, potency: int, criticalNum: float) -> None:
        super().__init__("Scholar", hp, potency, ["Succor"])
        self.petCoefficient: float = 0.95
        self.criticalNum: float = criticalNum

    def Recitation(self) -> Event:
        return Event(EventType.Other, "Recitation", effect=Effect("Recitation", 15))

    def updateEvent(self, event: Event) -> Event:
        event = super().updateEvent(event)
        if event.name in ["Succor", "Indomitability"]:
            for effect in self.effectList:
                if effect.name == "Recitation":
                    effect.remainTime = 0
                    return self._bonusHealingSpell(event, self.criticalNum)
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
                MagicMitigation("FeyIlluminationMtg", 20, 0.05),
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


class WhiteMage(Healer):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__(
            "WhiteMage",
            hp,
            potency,
            ["Medica", "MedicaII", "CureIII", "AfflatusRapture"],
        )

    def updateEvent(self, event: Event) -> Event:
        event = super().updateEvent(event)
        for effect in self.effectList:
            if (
                effect.name == "PlenaryIndulgence"
                and event.name in self.HealingSpellList
            ):
                event.value += 200
                return event
        return event

    def PlenaryIndulgence(self) -> Event:
        """全大赦"""
        return Event(
            EventType.Other,
            "PlenaryIndulgence",
            effect=Effect("PlenaryIndulgence", 10),
            target=self,
        )

    def Medica(self) -> Event:
        """医治"""
        return Event(EventType.Heal, "Medica", value=int(400 * self.potency))

    def AfflatusRapture(self) -> Event:
        """狂喜之心"""
        return Event(EventType.Heal, "AfflatusRapture", value=int(400 * self.potency))

    def CureIII(self) -> Event:
        """愈疗"""
        return Event(EventType.Heal, "CureIII", value=int(600 * self.potency))

    def MedicaII(self) -> Event:
        """医济"""
        return Event(
            EventType.Heal,
            "MedicaII",
            value=int(250 * self.potency),
            effect=Hot("MedicaII", 15, int(150 * self.potency)),
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
        return Event(
            EventType.Other,
            "Temperance",
            effect=[
                Mitigation("Temperance", 22, 0.1),
                # HealingSpellBonus("TemperanceHSB", 22, 0.2),
            ],
        )


class Astrologian(Healer):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency, ["Helios", "AspectedHelios"])

    def updateEvent(self, event: Event) -> Event:
        event = super().updateEvent(event)
        for effect in self.effectList:
            if effect.name == "NeutralSect" and event.name in ["AspectedHelios"]:
                event.effectList.append(
                    Shield("NeutralSectShield", 30, int(event.value * 1.25))
                )
                break
        return event

    def Helios(self) -> Event:
        return Event(EventType.Heal, "Helios", value=int(400 * self.potency))

    def AspectedHelios(self) -> Event:
        return Event(
            EventType.Heal,
            "AspectedHelios",
            value=int(250 * self.potency),
            effect=Hot("AspectedHeliosHot", 15, int(150 * self.potency)),
        )

    def CollectiveUnconscious(self) -> Event:
        return Event(
            EventType.Heal,
            "CollectiveUnconscious",
            effect=[
                Mitigation("CUMtg", 5, 0.1),
                Hot("CUHot", 15, int(100 * self.potency)),
            ],
        )

    def CelestialOpposition(self) -> Event:
        return Event(
            EventType.Heal,
            "CelestialOpposition",
            value=int(200 * self.potency),
            effect=Hot("COHot", 15, int(100 * self.potency)),
        )

    def EarthlyStar(self) -> Event:
        return Event(EventType.Heal, "EarthlyStar", value=int(720 * self.potency))

    def NeutralSect(self) -> Event | None:
        return Event(EventType.Other, "NeutralSect", effect=Effect("NeutralSect", 20))
