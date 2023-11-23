from copy import deepcopy
import traceback
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
from models.event import Event, EventType, petSkill
from models.player import Player, allPlayer
from models.record import Record


# TODO: 白魔: 铃兰
# TODO: 占星: 合图, 大宇宙
# TODO: 贤者: 消化, 海马, 胖海马
class Healer(Player):
    def __init__(
        self, name: str, hp: int, potency: float, spellList: list[str]
    ) -> None:
        super().__init__(name, hp, potency)
        self.spellList: list[str] = spellList

    def asEventUser(self, event: Event, target: Player) -> tuple[Event, Player]:
        if event.name in self.spellList:
            event.getPercentage(self.spellBonus)
        return super().asEventUser(event, target)

    def createRecord(
        self,
        target: Player,
        value: int = 0,
        effect: list[Effect] | Effect = [],
    ) -> Record:
        return Record(
            Event(EventType.Heal, traceback.extract_stack()[-2][2], value, effect),
            self,
            target,
        )


class Scholar(Healer):
    Spell: list[str] = ["Adloquium", "Succor", "Physicks"]

    def __init__(self, hp: int, potency: int, criticalNum: float) -> None:
        super().__init__("Scholar", hp, potency, self.Spell)
        self.petCoefficient: float = 0.95
        self.criticalNum: float = criticalNum

    def asEventUser(self, event: Event, target: Player) -> tuple[Event, Player]:
        if event.name == "Deployment":
            if e := target.searchEffect("Galvanize"):
                ret = (
                    Event(EventType.Heal, "Deployment", effect=deepcopy(e)),
                    allPlayer,
                )
                e.setZero()
                return ret
        if event.name == "Adloquium" and self.searchEffect("Recitation"):
            event.append(Shield("Catalyze", 30, 540))
        if event.name in self.Spell + ["Indomitability", "Excogitation"]:
            if self.searchEffect("Recitation", remove=True):
                event.getPercentage(self.criticalNum)
        if event.name in self.Spell:
            if self.searchEffect("EmergencyTactics", remove=True):
                for e in event.effectList:
                    event.value += e.value
                    e.setZero()
        return super().asEventUser(event, target)

    def Recitation(self) -> Record:
        return self.createRecord(self, effect=Effect("Recitation", 15))

    def Dissipation(self) -> Record:
        return self.createRecord(self, effect=SpellBonus("Dissipation", 30, 1.2))

    def Deployment(self, target: Player) -> Record:
        return self.createRecord(target)

    def EmergencyTactics(self) -> Record:
        return self.createRecord(self)

    # 单奶

    def Physick(self, target: Player) -> Record:
        return self.createRecord(target, value=450)

    def Adloquium(self, target: Player) -> Record:
        return self.createRecord(target, value=300, effect=Shield("Galvanize", 30, 540))

    def Lustrate(self, target: Player) -> Record:
        return self.createRecord(target, value=600)

    def Excogitation(self, target: Player) -> Record:
        return self.createRecord(target, effect=DelayHeal("Excogitation", 45, 800))

    @petSkill
    def Aetherpact(self, time: int, target: Player) -> Record:
        return self.createRecord(target, effect=Hot("Aetherpact", time, 300))

    def Protraction(self, target: Player) -> Record:
        return self.createRecord(
            target,
            effect=[
                HealBonus("ProtractionHB", 10, 1.1),
                IncreaseMaxHp("ProtractionIMH", 10, 1.1),
            ],
        )

    # 群奶
    @petSkill
    def WhisperingDawn(self) -> Record:
        return self.createRecord(allPlayer, effect=Hot("WhisperingDawn", 21, 80))

    def Succor(self) -> Record:
        return self.createRecord(
            allPlayer, value=200, effect=Shield("Galvanize", 30, 320)
        )

    @petSkill
    def FeyIllumination(self) -> Record:
        return self.createRecord(
            allPlayer,
            effect=[
                MagicMtg("FeyIlluminationMMtg", 20, 0.95),
                SpellBonus("FeyIlluminationHSB", 20, 1.1),
            ],
        )

    def SacredSoil(self) -> Record:
        return self.createRecord(
            allPlayer,
            value=100,
            effect=[Mtg("SacredSoilMtg", 17, 0.9), Hot("SacredSoilHB", 15, 100)],
        )

    def Indomitability(self) -> Record:
        return self.createRecord(allPlayer, value=400)

    @petSkill
    def FeyBlessing(self) -> Record:
        return self.createRecord(allPlayer, value=320)

    @petSkill
    def Consolation(self) -> Record:
        return self.createRecord(
            allPlayer, value=250, effect=Shield("Consolation", 30, 250)
        )

    def Expedient(self) -> Record:
        return self.createRecord(allPlayer, effect=Mtg("Expedient", 20, 0.9))


class WhiteMage(Healer):
    aoeSpell: list[str] = ["Medica", "MedicaII", "BeneficIII", "AfflatusRapture"]

    def __init__(self, hp: int, potency: float) -> None:
        super().__init__(
            "WhiteMage",
            hp,
            potency,
            ["Benefic", "BeneficII", "Regen", "AfflatusSolace"] + self.aoeSpell,
        )
        self.bellCollDown = 0

    def asEventUser(self, event: Event, target: Player) -> tuple[Event, Player]:
        if event.name in self.aoeSpell and self.searchEffect("PlenaryIndulgence"):
            event.value += 200
        return super().asEventUser(event, target)

    def PlenaryIndulgence(self) -> Record:
        """全大赦"""
        return self.createRecord(self, effect=Effect("PlenaryIndulgence", 10))

    # def dealWithReayEvent(self, event: Event) -> Record | None:
    #     super().dealWithReadyEvent(event)
    #     if bell := self.searchEffect("LiturgyOfTheBell"):
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
        return self.createRecord(target, value=500)

    def CureII(self, target: Player) -> Record:
        return self.createRecord(target, value=800)

    def Regen(self, target: Player) -> Record:
        return self.createRecord(target, effect=Hot("Regen", 18, 250))

    def Benediction(self, target: Player) -> Record:
        return self.createRecord(target, value=1000000)

    def AfflatusSolace(self, target: Player) -> Record:
        return self.createRecord(target, value=800)

    def Tetragrammaton(self, target: Player) -> Record:
        return self.createRecord(target, value=700)

    def DivineBenison(self, target: Player) -> Record:
        return self.createRecord(target, effect=Shield("DivineBenison", 15, 500))

    def Aquaveil(self, target: Player) -> Record:
        return self.createRecord(target, effect=Mtg("Aquaveil", 8, 0.85))

    def Medica(self) -> Record:
        """医治"""
        return self.createRecord(allPlayer, value=400)

    def AfflatusRapture(self) -> Record:
        """狂喜之心"""
        return self.createRecord(allPlayer, value=400)

    def CureIII(self) -> Record:
        """愈疗"""
        return self.createRecord(allPlayer, value=600)

    def MedicaII(self) -> Record:
        """医济"""
        return self.createRecord(allPlayer, value=250, effect=Hot("MedicaII", 15, 150))

    def Asylum(self) -> Record:
        """庇护所"""
        return self.createRecord(
            allPlayer,
            value=100,
            effect=[Hot("AsylumHot", 24, 100), HealBonus("AsylumHB", 27, 1.1)],
        )

    def Assize(self) -> Record:
        """法令"""
        return self.createRecord(allPlayer, value=400)

    def Temperance(self) -> list[Record]:
        """节制"""
        return [
            self.createRecord(allPlayer, effect=Mtg("TemperanceMtg", 22, 1.1)),
            self.createRecord(self, effect=SpellBonus("TemperanceSB", 20, 1.2)),
        ]

    def LiturgyOfTheBell(self) -> Record:
        return self.createRecord(self, effect=Effect("LiturgyOfTheBell", 20, 5))


class Astrologian(Healer):
    aoeSpell: list[str] = ["AspectedHelios", "Helios"]

    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(
            name,
            hp,
            potency,
            self.aoeSpell + ["Benefic", "BeneficII", "AspectedBenefic"],
        )

    def asEventUser(self, event: Event, target: Player) -> tuple[Event, Player]:
        if event.name in self.aoeSpell:
            if effect := self.searchEffect("Horoscope"):
                effect.remainTime = 30
                effect.value *= 2
        if event.name == "closeHoroscope":
            if effect := self.searchEffect("Horoscope"):
                event = Event(EventType.Heal, "Horoscope", effect.value)
                target = allPlayer
        if event.name == "AspectedHelios" and self.searchEffect("NeutralSect"):
            event.append(Shield("AspectedHeliosShield", 30, int(250 * 1.25)))
        elif event.name == "AspectedBenefic" and self.searchEffect("NeutralSect"):
            event.append(Shield("AspectedBeneficShield", 30, 625))
        return super().asEventUser(event, target)

    # 单奶

    def Benefic(self, target: Player) -> Record:
        return self.createRecord(target, value=500)

    def BeneficII(self, target: Player) -> Record:
        return self.createRecord(target, value=800)

    def AspectedBenefic(self, target: Player) -> Record:
        return self.createRecord(
            target, value=250, effect=Hot("AspectedBenefic", 15, 250)
        )

    def CelestialIntersection(self, target: Player) -> Record:
        return self.createRecord(
            target, value=200, effect=Shield("CelestialIntersection", 15, 400)
        )

    def Exaltation(self, target: Player) -> Record:
        return self.createRecord(
            target,
            effect=[Mtg("Exaltation", 8, 0.9), DelayHeal("ExaltationDH", 8, 500)],
        )

    # 群奶

    def Helios(self) -> Record:
        return self.createRecord(allPlayer, value=400)

    def AspectedHelios(self) -> Record:
        return self.createRecord(
            allPlayer, value=250, effect=Hot("AspectedHelios", 15, 150)
        )

    def CollectiveUnconscious(self) -> Record:
        return self.createRecord(
            allPlayer, effect=[Mtg("CUMtg", 5, 0.9), Hot("CUHot", 15, 100)]
        )

    def CelestialOpposition(self) -> Record:
        return self.createRecord(allPlayer, value=200, effect=Hot("COHot", 15, 100))

    def EarthlyStar(self) -> Record:
        return self.createRecord(allPlayer, value=720)

    def NeutralSect(self) -> Record:
        return self.createRecord(self, effect=Effect("NeutralSect", 20))

    def Horoscope(self) -> Record:
        return self.createRecord(self, effect=DelayHeal("Horoscope", 10, 200))

    def closeHoroscope(self) -> Record:
        return self.createRecord(self)


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

    def asEventUser(self, event: Event, target: Player) -> tuple[Event, Player]:
        if self.searchEffect("Zoe", remove=True):
            event.getPercentage(1.5)
        return super().asEventUser(event, target)

    def Dignosis(self, target: Player) -> Record:
        return self.createRecord(target, value=450)

    def Prognosis(self) -> Record:
        return self.createRecord(allPlayer, value=300)

    def PhysisII(self) -> Record:
        return self.createRecord(allPlayer, effect=Hot("PhysisIIHot", 15, 130))

    def EkurasianDignosis(self, target: Player) -> Record:
        return self.createRecord(
            target, value=300, effect=Shield("EkurasianDignosis", 30, 540)
        )

    def EkurasianPrognosis(self) -> Record:
        return self.createRecord(
            allPlayer, value=100, effect=Shield("EkurasianDignosis", 30, 320)
        )

    def Druochole(self, target: Player) -> Record:
        return self.createRecord(target, value=600)

    def Kerachole(self) -> Record:
        return self.createRecord(
            allPlayer,
            effect=[Mtg("KeracholeMtg", 15, 0.9), Hot("KeracholeHot", 15, 100)],
        )

    def Ixochole(self) -> Record:
        return self.createRecord(allPlayer, value=400)

    def Zoe(self) -> Record:
        return self.createRecord(self, effect=Effect("Zoe", 30))

    def Taurochole(self, target: Player) -> Record:
        return self.createRecord(target, value=700, effect=Mtg("KeracholeMtg", 15, 0.9))

    def Holos(self) -> Record:
        return self.createRecord(
            allPlayer,
            value=300,
            effect=[Mtg("HolosMtg", 20, 0.9), Shield("HolosShield", 30, 300)],
        )

    def Krasis(self, target: Player) -> Record:
        return self.createRecord(target, effect=HealBonus("Krasis", 10, 1.2))

    def Pneuma(self) -> Record:
        return self.createRecord(allPlayer, value=600)
