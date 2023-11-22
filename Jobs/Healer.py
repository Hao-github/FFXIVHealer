from models.effect import (
    DelayHealing,
    Effect,
    HealBonus,
    SpellBonus,
    Hot,
    IncreaseMaxHp,
    MagicMitigation,
    Mitigation,
    Shield,
)
from models.event import Event, EventType
from models.player import Player, totalPlayer
from models.record import Record


class Healer(Player):
    def __init__(
        self, name: str, hp: int, potency: float, spellList: list[str]
    ) -> None:
        super().__init__(name, hp, potency)
        self.spellList: list[str] = spellList

    def asEventUser(self, event: Event, target: Player) -> Event:
        if event.name in self.spellList:
            event.getPercentage(self.spellBonus)
        return event


class Scholar(Healer):
    # TODO: 展开未更新

    def __init__(self, hp: int, potency: int, criticalNum: float) -> None:
        super().__init__("Scholar", hp, potency, ["Succor", "Physicks", "Adloquium"])
        self.petCoefficient: float = 0.95
        self.criticalNum: float = criticalNum

    def asEventUser(self, event: Event, target: Player) -> Event:
        event = super().asEventUser(event, target)
        if event.name not in ["Adloquium", "Succor", "Indomitability", "Excogitation"]:
            return event
        if effect := self._searchEffect("Recitation"):
            effect.remainTime = 0
            if event.name == "Adloquium":
                event.effectList.append(Shield("Catalyze", 30, int(event.value * 1.8)))
            event.getPercentage(self.criticalNum)
        return event

    def createRecord(
        self,
        name: str,
        target: Player,
        value: int = 0,
        effect: list[Effect] | Effect = [],
    ) -> Record:
        return Record(Event(EventType.Heal, name, value, effect), self, target)

    def Recitation(self) -> Record:
        return self.createRecord("Recitation", self, effect=Effect("Recitation", 15, 0))

    def Dissipation(self) -> Record:
        return self.createRecord(
            "Dissipation", self, effect=SpellBonus("Dissipation", 30, 1.2)
        )

    def Deployment(self, target: Player) -> Record:
        return self.createRecord("Deployment", target)

    # 单奶

    def Physick(self, target: Player) -> Record:
        return self.createRecord("Physick", target, value=int(450 * self.potency))

    def Adloquium(self, target: Player) -> Record:
        return self.createRecord(
            "Adloquium",
            target,
            value=int(300 * self.potency),
            effect=Shield("Galvanize", 30, int(540 * self.potency)),
        )

    def Lustrate(self, target: Player) -> Record:
        return self.createRecord("Lustrate", target, value=int(600 * self.potency))

    def Excogitation(self, target: Player) -> Record:
        return self.createRecord(
            "Excogitation",
            target,
            effect=DelayHealing("Excogitation", 45, int(800 * self.potency)),
        )

    def Aetherpact(self, time: int, target: Player) -> Record:
        return self.createRecord(
            "Aetherpact",
            target,
            effect=Hot(
                "Aetherpact", time, int(300 * self.potency * self.petCoefficient)
            ),
        )

    def Protraction(self, target: Player) -> Record:
        return self.createRecord(
            "Protraction",
            target,
            effect=[
                HealBonus("ProtractionHB", 10, 1.1),
                IncreaseMaxHp("ProtractionIMH", 10, 1.1),
            ],
        )

    # 群奶

    def WhisperingDawn(self) -> Record:
        return self.createRecord(
            "WhisperingDawn",
            totalPlayer,
            effect=Hot(
                "WhisperingDawn", 21, int(80 * self.potency * self.petCoefficient)
            ),
        )

    def Succor(self) -> Record:
        return self.createRecord(
            "Succor",
            totalPlayer,
            value=int(200 * self.potency),
            effect=Shield("Galvanize", 30, int(320 * self.potency)),
        )

    def FeyIllumination(self) -> Record:
        return self.createRecord(
            "FeyIllumination",
            totalPlayer,
            effect=[
                MagicMitigation("FeyIlluminationMMtg", 20, 0.95),
                SpellBonus("FeyIlluminationHSB", 20, 1.1),
            ],
        )

    def SacredSoil(self) -> Record:
        return self.createRecord(
            "SacredSoil",
            totalPlayer,
            value=int(100 * self.potency),
            effect=[
                Mitigation("SacredSoilMtg", 18, 0.9),
                Hot("SacredSoilHB", 15, int(100 * self.potency)),
            ],
        )

    def Indomitability(self) -> Record:
        return self.createRecord("Indomitability", totalPlayer, int(400 * self.potency))

    def FeyBlessing(self) -> Record:
        return self.createRecord(
            "FeyBlessing", totalPlayer, int(320 * self.petCoefficient * self.potency)
        )

    def Consolation(self) -> Record:
        return self.createRecord(
            "Consolation",
            totalPlayer,
            int(250 * self.petCoefficient * self.potency),
            Shield("Consolation", 30, int(250 * self.petCoefficient * self.potency)),
        )

    def Expedient(self) -> Record:
        return self.createRecord(
            "Expedient", totalPlayer, effect=Mitigation("Expedient", 20, 0.9)
        )


class WhiteMage(Healer):
    # TODO: 铃兰未添加
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__(
            "WhiteMage",
            hp,
            potency,
            [
                "Benefic",
                "BeneficII",
                "Regen",
                "AfflatusSolace",
                "Medica",
                "MedicaII",
                "BeneficIII",
                "AfflatusRapture",
            ],
        )
        self.bellCollDown = 0

    def asEventUser(self, event: Event, target: Player) -> Event:
        event = super().asEventUser(event, target)
        if event.name not in [
            "Medica",
            "MedicaII",
            "BeneficIII",
            "AfflatusRapture",
        ]:
            return event
        if self._searchEffect("PlenaryIndulgence"):
            event.value += int(200 * self.potency)
        return event

    def PlenaryIndulgence(self) -> Event:
        """全大赦"""
        return Event(
            EventType.Other,
            "PlenaryIndulgence",
            effect=Effect("PlenaryIndulgence", 10, 0),
        )

    # def dealWithReayEvent(self, event: Event) -> Event | None:
    #     super().dealWithReadyEvent(event)
    #     if event.eventType in [EventType.Heal, EventType.Other]:
    #         return None
    #     if bell := self.__searchEffect("LiturgyOfTheBell"):
    #         bell.value -= 1
    #         self.bellCollDown = 1
    #         if bell.value == 0:
    #             bell.remainTime = 0
    #         return Event(
    #             EventType.Heal, "LiturgyOfTheBellHeal", int(400 * self.potency)
    #         )
    #     return None

    # 单奶

    def Cure(self) -> Event:
        return Event(EventType.Heal, "Cure", value=int(500 * self.potency))

    def CureII(self) -> Event:
        return Event(EventType.Heal, "CureII", value=int(800 * self.potency))

    def Regen(self) -> Event:
        return Event(
            EventType.Other, "Regen", effect=Hot("Regen", 18, int(250 * self.potency))
        )

    def Benediction(self) -> Event:
        return Event(EventType.Heal, "Benediction", value=1000000)

    def AfflatusSolace(self) -> Event:
        return Event(EventType.Heal, "AfflatusSolace", value=int(800 * self.potency))

    def Tetragrammaton(self) -> Event:
        return Event(EventType.Heal, "Tetragrammaton", value=int(700 * self.potency))

    def DivineBenison(self) -> Event:
        return Event(
            EventType.Other,
            "DivineBenison",
            effect=Shield("DivineBenison", 15, int(500 * self.potency)),
        )

    def Aquaveil(self) -> Event:
        return Event(
            EventType.Other, "Aquaveil", effect=Mitigation("Aquaveil", 8, 0.85)
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
                HealBonus("AsylumHB", 27, 1.1),
            ],
        )

    def Assize(self) -> Event:
        """法令"""
        return Event(EventType.Heal, "Assize", value=int(400 * self.potency))

    def Temperance(self) -> list[Event]:
        """节制"""
        return [
            Event(
                EventType.Other, "Temperance", effect=Mitigation("Temperance", 22, 1.1)
            ),
            Event(
                EventType.Other,
                "Temperance",
                effect=SpellBonus("TemperanceSB", 22, 1.2),
            ),
        ]

    # def LiturgyOfTheBell(self) -> Event:
    #     return Event(
    #         EventType.Other,
    #         "LiturgyOfTheBell",
    #         effect=Effect("LiturgyOfTheBell", 20, 5),
    #     )


class Astrologian(Healer):
    # TODO: 星位和图, 大宇宙
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(
            name,
            hp,
            potency,
            ["Helios", "AspectedHelios", "Benefic", "BeneficII", "AspectedBenefic"],
        )

    def asEventUser(self, event: Event, target: Player) -> Event:
        event = super().asEventUser(event, target)
        if event.name in ["AspectedHelios", "Helios"]:
            if effect := self._searchEffect("Horoscope"):
                effect.remainTime = 30
                effect.value *= 2
        if event.name == "closeHoroscope":
            if effect := self._searchEffect("Horoscope"):
                return Event(EventType.Heal, "Horoscope", int(effect.value))
        if event.name == "AspectedHelios" and self._searchEffect("NeutralSect"):
            event.effectList.append(
                Shield("AspectedHeliosShield", 30, int(event.value * 1.25))
            )
        elif event.name == "AspectedBenefic" and self._searchEffect("NeutralSect"):
            event.effectList.append(
                Shield("AspectedBeneficShield", 30, int(event.value * 2.5))
            )
        return event

    # 单奶

    def Benefic(self) -> Event:
        return Event(EventType.Heal, "Benefic", value=int(500 * self.potency))

    def BeneficII(self) -> Event:
        return Event(EventType.Heal, "BeneficII", value=int(800 * self.potency))

    def AspectedBenefic(self) -> Event:
        return Event(
            EventType.Heal,
            "AspectedBenefic",
            value=int(250 * self.potency),
            effect=Hot("AspectedBenefic", 15, int(250 * self.potency)),
        )

    def CelestialIntersection(self) -> Event:
        return Event(
            EventType.Heal,
            "CelestialIntersection",
            value=int(200 * self.potency),
            effect=Shield("CelestialIntersection", 15, int(400 * self.potency)),
        )

    def Exaltation(self) -> Event:
        return Event(
            EventType.Other,
            "Exaltation",
            effect=[
                Mitigation("Exaltation", 8, 0.9),
                DelayHealing("ExaltationDH", 8, int(500 * self.potency)),
            ],
        )

    # 群奶

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
                Mitigation("CUMtg", 5, 0.9),
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

    def NeutralSect(self) -> Event:
        return Event(
            EventType.Other, "NeutralSect", effect=Effect("NeutralSect", 20, 0)
        )

    def Horoscope(self) -> Event:
        return Event(
            EventType.Other,
            "Horoscope",
            effect=DelayHealing("Horoscope", 10, int(200 * self.potency)),
        )

    def closeHoroscope(self) -> Event:
        return Event(EventType.Other, "closeHoroscope")


# class Sage(Healer):
#     def __init__(self, name: str, hp: int, potency: float, spellList: list[str]) -> None:
#         super().__init__("Sage", hp, potency, spellList)
