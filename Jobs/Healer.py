from models.effect import (
    DelayHeal,
    Effect,
    HealBonus,
    SpellBonus,
    Hot,
    IncreaseMaxHp,
    MagicMtg,
    Mtg,
    Shield,
)
from models.event import Event, EventType
from models.player import Player, allPlayer
from models.record import Record


# TODO: 展开, 铃兰, 合图, 大宇宙, 消化, 海马, 胖海马
class Healer(Player):
    def __init__(
        self, name: str, hp: int, potency: float, spellList: list[str]
    ) -> None:
        super().__init__(name, hp, potency)
        self.spellList: list[str] = spellList

    def asEventUser(self, event: Event, target: Player) -> Event:
        event = super().asEventUser(event, target)
        if event.name in self.spellList:
            event.getPercentage(self.spellBonus)
        return event

    def createRecord(
        self,
        name: str,
        target: Player,
        value: int = 0,
        effect: list[Effect] | Effect = [],
    ) -> Record:
        return Record(Event(EventType.Heal, name, value, effect), self, target)


class Scholar(Healer):
    def __init__(self, hp: int, potency: int, criticalNum: float) -> None:
        super().__init__("Scholar", hp, potency, ["Succor", "Physicks", "Adloquium"])
        self.petCoefficient: float = 0.95
        self.criticalNum: float = criticalNum

    def asEventUser(self, event: Event, target: Player) -> Event:
        if event.name not in ["Adloquium", "Succor", "Indomitability", "Excogitation"]:
            return event
        if effect := self._searchEffect("Recitation"):
            effect.setZero()
            if event.name == "Adloquium":
                event.append(Shield("Catalyze", 30, 540))
            event.getPercentage(self.criticalNum)
        if effect := self._searchEffect("EmergencyTactics"):
            if event.name in self.spellList:
                effect.setZero()
                for e in event.effectList:
                    event.value += int(e.value)
                    e.setZero()
        event = super().asEventUser(event, target)
        return event

    def Recitation(self) -> Record:
        return self.createRecord("Recitation", self, effect=Effect("Recitation", 15, 0))

    def Dissipation(self) -> Record:
        return self.createRecord(
            "Dissipation", self, effect=SpellBonus("Dissipation", 30, 1.2)
        )

    def Deployment(self, target: Player) -> Record:
        return self.createRecord("Deployment", target)

    def EmergencyTactics(self) -> Record:
        return self.createRecord("EmergencyTactics", self)

    # 单奶

    def Physick(self, target: Player) -> Record:
        return self.createRecord("Physick", target, value=450)

    def Adloquium(self, target: Player) -> Record:
        return self.createRecord(
            "Adloquium", target, value=300, effect=Shield("Galvanize", 30, 540)
        )

    def Lustrate(self, target: Player) -> Record:
        return self.createRecord("Lustrate", target, value=600)

    def Excogitation(self, target: Player) -> Record:
        return self.createRecord(
            "Excogitation", target, effect=DelayHeal("Excogitation", 45, 800)
        )

    def Aetherpact(self, time: int, target: Player) -> Record:
        return self.createRecord(
            "Aetherpact",
            target,
            effect=Hot("Aetherpact", time, int(300 * self.petCoefficient)),
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
            allPlayer,
            effect=Hot("WhisperingDawn", 21, int(80 * self.petCoefficient)),
        )

    def Succor(self) -> Record:
        return self.createRecord(
            "Succor", allPlayer, value=200, effect=Shield("Galvanize", 30, 320)
        )

    def FeyIllumination(self) -> Record:
        return self.createRecord(
            "FeyIllumination",
            allPlayer,
            effect=[
                MagicMtg("FeyIlluminationMMtg", 20, 0.95),
                SpellBonus("FeyIlluminationHSB", 20, 1.1),
            ],
        )

    def SacredSoil(self) -> Record:
        return self.createRecord(
            "SacredSoil",
            allPlayer,
            value=100,
            effect=[Mtg("SacredSoilMtg", 17, 0.9), Hot("SacredSoilHB", 15, 100)],
        )

    def Indomitability(self) -> Record:
        return self.createRecord("Indomitability", allPlayer, 400)

    def FeyBlessing(self) -> Record:
        return self.createRecord(
            "FeyBlessing", allPlayer, int(320 * self.petCoefficient)
        )

    def Consolation(self) -> Record:
        return self.createRecord(
            "Consolation",
            allPlayer,
            int(250 * self.petCoefficient),
            Shield("Consolation", 30, int(250 * self.petCoefficient)),
        )

    def Expedient(self) -> Record:
        return self.createRecord(
            "Expedient", allPlayer, effect=Mtg("Expedient", 20, 0.9)
        )


class WhiteMage(Healer):
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
        if event.name not in [
            "Medica",
            "MedicaII",
            "BeneficIII",
            "AfflatusRapture",
        ]:
            return event
        if self._searchEffect("PlenaryIndulgence"):
            event.value += 200
        event = super().asEventUser(event, target)
        return event

    def PlenaryIndulgence(self) -> Record:
        """全大赦"""
        return self.createRecord(
            "PlenaryIndulgence", self, effect=Effect("PlenaryIndulgence", 10, 0)
        )

    # def dealWithReayEvent(self, event: Event) -> Record | None:
    #     super().dealWithReadyEvent(event)
    #     if event.eventType in [ EventType.Other]:
    #         return None
    #     if bell := self.__searchEffect("LiturgyOfTheBell"):
    #         bell.value -= 1
    #         self.bellCollDown = 1
    #         if bell.value == 0:
    #             bell.remainTime = 0
    #         return Event(
    #              "LiturgyOfTheBellHeal", 400 )
    #         )
    #     return None

    # 单奶

    def Cure(self, target: Player) -> Record:
        return self.createRecord("Cure", target, value=500)

    def CureII(self, target: Player) -> Record:
        return self.createRecord("CureII", target, value=800)

    def Regen(self, target: Player) -> Record:
        return self.createRecord("Regen", target, effect=Hot("Regen", 18, 250))

    def Benediction(self, target: Player) -> Record:
        return self.createRecord("Benediction", target, value=1000000)

    def AfflatusSolace(self, target: Player) -> Record:
        return self.createRecord("AfflatusSolace", target, value=800)

    def Tetragrammaton(self, target: Player) -> Record:
        return self.createRecord("Tetragrammaton", target, value=700)

    def DivineBenison(self, target: Player) -> Record:
        return self.createRecord(
            "DivineBenison", target, effect=Shield("DivineBenison", 15, 500)
        )

    def Aquaveil(self, target: Player) -> Record:
        return self.createRecord("Aquaveil", target, effect=Mtg("Aquaveil", 8, 0.85))

    def Medica(self) -> Record:
        """医治"""
        return self.createRecord("Medica", allPlayer, value=400)

    def AfflatusRapture(self) -> Record:
        """狂喜之心"""
        return self.createRecord("AfflatusRapture", allPlayer, value=400)

    def CureIII(self) -> Record:
        """愈疗"""
        return self.createRecord("CureIII", allPlayer, value=600)

    def MedicaII(self) -> Record:
        """医济"""
        return self.createRecord(
            "MedicaII", allPlayer, value=250, effect=Hot("MedicaII", 15, 150)
        )

    def Asylum(self) -> Record:
        """庇护所"""
        return self.createRecord(
            "Asylum",
            allPlayer,
            value=100,
            effect=[Hot("AsylumHot", 24, 100), HealBonus("AsylumHB", 27, 1.1)],
        )

    def Assize(self) -> Record:
        """法令"""
        return self.createRecord("Assize", allPlayer, value=400)

    def Temperance(self) -> list[Record]:
        """节制"""
        return [
            self.createRecord(
                "Temperance", allPlayer, effect=Mtg("TemperanceMtg", 22, 1.1)
            ),
            self.createRecord(
                "Temperance", self, effect=SpellBonus("TemperanceSB", 20, 1.2)
            ),
        ]

    # def LiturgyOfTheBell(self) -> Record:
    #     return Event(
    #
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
        if event.name in ["AspectedHelios", "Helios"]:
            if effect := self._searchEffect("Horoscope"):
                effect.remainTime = 30
                effect.value *= 2
        if event.name == "closeHoroscope":
            if effect := self._searchEffect("Horoscope"):
                return Event(EventType.Heal, "Horoscope", int(effect.value))
        if event.name == "AspectedHelios" and self._searchEffect("NeutralSect"):
            event.append(Shield("AspectedHeliosShield", 30, int(250 * 1.25)))
        elif event.name == "AspectedBenefic" and self._searchEffect("NeutralSect"):
            event.append(Shield("AspectedBeneficShield", 30, 625))
        event = super().asEventUser(event, target)
        return event

    # 单奶

    def Benefic(self, target: Player) -> Record:
        return self.createRecord("Benefic", target, value=500)

    def BeneficII(self, target: Player) -> Record:
        return self.createRecord("BeneficII", target, value=800)

    def AspectedBenefic(self, target: Player) -> Record:
        return self.createRecord(
            "AspectedBenefic", target, value=250, effect=Hot("AspectedBenefic", 15, 250)
        )

    def CelestialIntersection(self, target: Player) -> Record:
        return self.createRecord(
            "CelestialIntersection",
            target,
            value=200,
            effect=Shield("CelestialIntersection", 15, 400),
        )

    def Exaltation(self, target: Player) -> Record:
        return self.createRecord(
            "Exaltation",
            target,
            effect=[Mtg("Exaltation", 8, 0.9), DelayHeal("ExaltationDH", 8, 500)],
        )

    # 群奶

    def Helios(self) -> Record:
        return self.createRecord("Helios", allPlayer, value=400)

    def AspectedHelios(self) -> Record:
        return self.createRecord(
            "AspectedHelios",
            allPlayer,
            value=250,
            effect=Hot("AspectedHelios", 15, 150),
        )

    def CollectiveUnconscious(self) -> Record:
        return self.createRecord(
            "CollectiveUnconscious",
            allPlayer,
            effect=[Mtg("CUMtg", 5, 0.9), Hot("CUHot", 15, 100)],
        )

    def CelestialOpposition(self) -> Record:
        return self.createRecord(
            "CelestialOpposition", allPlayer, value=200, effect=Hot("COHot", 15, 100)
        )

    def EarthlyStar(self) -> Record:
        return self.createRecord("EarthlyStar", allPlayer, value=720)

    def NeutralSect(self) -> Record:
        return self.createRecord(
            "NeutralSect", self, effect=Effect("NeutralSect", 20, 0)
        )

    def Horoscope(self) -> Record:
        return self.createRecord(
            "Horoscope", self, effect=DelayHeal("Horoscope", 10, 200)
        )

    def closeHoroscope(self) -> Record:
        return self.createRecord("closeHoroscope", self)


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

    def Dignosis(self, target: Player) -> Record:
        return self.createRecord("Dignosis", target, value=450)

    def Prognosis(self) -> Record:
        return self.createRecord("Prognosis", allPlayer, value=300)

    def PhysisII(self) -> Record:
        return self.createRecord(
            "PhysisII",
            allPlayer,
            effect=[
                Hot("PhysisIIHot", 15, 130),
            ],
        )

    def EkurasianDignosis(self, target: Player) -> Record:
        return self.createRecord(
            "EkurasianDignosis",
            target,
            value=300,
            effect=Shield("EkurasianDignosis", 30, 540),
        )

    def EkurasianPrognosis(self) -> Record:
        return self.createRecord(
            "EkurasianPrognosis",
            allPlayer,
            value=100,
            effect=Shield("EkurasianDignosis", 30, 320),
        )

    def Druochole(self, target: Player) -> Record:
        return self.createRecord("Druochole", target, value=600)

    def Kerachole(self) -> Record:
        return self.createRecord(
            "Kerachole",
            allPlayer,
            effect=[Mtg("KeracholeMtg", 15, 0.9), Hot("KeracholeHB", 15, 100)],
        )

    def Ixochole(self) -> Record:
        return self.createRecord("Ixochole", allPlayer, value=400)

    def Zoe(self) -> Record:
        return self.createRecord("Zoe", self, effect=Effect("Zoe", 30, 0))

    def Taurochole(self, target: Player) -> Record:
        return self.createRecord(
            "Taurochole", target, value=700, effect=Mtg("KeracholeMtg", 15, 0.9)
        )

    def Holos(self) -> Record:
        return self.createRecord(
            "Holos",
            allPlayer,
            value=300,
            effect=[Mtg("HolosMtg", 20, 0.9), Shield("HolosShield", 30, 300)],
        )

    def Krasis(self, target: Player) -> Record:
        return self.createRecord("Krasis", target, effect=HealBonus("Krasis", 10, 1.2))

    def Pneuma(self) -> Record:
        return self.createRecord("Pneuma", allPlayer, value=600)
