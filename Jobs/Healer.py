from copy import deepcopy
import traceback
from models.baseStatus import BaseStatus
from models.status import (
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
from models.event import Event, EventType, petSkill
from models.player import Player, allPlayer
from models.record import Record


class Healer(Player):
    def __init__(
        self, name: str, hp: int, potency: float, spellList: list[str]
    ) -> None:
        super().__init__(name, hp, potency, 0.73, 0.84)
        self.spellList: list[str] = spellList

    def asEventUser(self, event: Event, target: Player) -> tuple[Event, Player]:
        if event.name in self.spellList:
            event.getBuff(self.calPct(SpellBonus))
        return super().asEventUser(event, target)

    def createRecord(
        self,
        target: Player,
        value: float = 0,
        status: list[BaseStatus] | BaseStatus = [],
        delay: float = 0,
    ) -> Record:
        return Record(
            Event(EventType.Heal, traceback.extract_stack()[-2][2], value, status),
            self,
            target,
            delay,
        )


class Scholar(Healer):
    Spell: list[str] = ["Adloquium", "Succor", "Physicks"]

    def __init__(self, hp: int, potency: float, critNum: float) -> None:
        super().__init__("Scholar", hp, potency, self.Spell)
        self.petCoefficient: float = 0.95
        self.critNum: float = critNum

    def asEventUser(self, event: Event, target: Player) -> tuple[Event, Player]:
        if event.name == "Deployment":
            if e := target.searchStatus("Galvanize", Shield):
                ret = Event(EventType.Heal, "Deployment", status=deepcopy(e))
                e.setZero()
                return super().asEventUser(ret, allPlayer)
        if event.name == "Adloquium" and self.searchStatus("Recitation", BaseStatus):
            event.append(Shield("Catalyze", 30, 540))
        if event.name in self.Spell + ["Indomitability", "Excogitation"]:
            if self.searchStatus("Recitation", remove=True):
                event.getBuff(self.critNum)
        if event.name in self.Spell:
            if self.searchStatus("EmergencyTactics", remove=True):
                for e in event.statusList:
                    event.value += e.value
                    e.setZero()
        return super().asEventUser(event, target)

    def Recitation(self) -> Record:
        return self.createRecord(self, status=BaseStatus("Recitation", 15))

    def Dissipation(self) -> Record:
        return self.createRecord(self, status=SpellBonus("Dissipation", 30, 1.2))

    def Deployment(self, target: Player) -> Record:
        return self.createRecord(target)

    def EmergencyTactics(self) -> Record:
        return self.createRecord(self)

    # 单奶

    def Physick(self, target: Player) -> Record:
        return self.createRecord(target, value=450)

    def Adloquium(self, target: Player) -> Record:
        return self.createRecord(target, value=300, status=Shield("Galvanize", 30, 540))

    def Lustrate(self, target: Player) -> Record:
        return self.createRecord(target, value=600)

    def Excogitation(self, target: Player) -> Record:
        return self.createRecord(target, status=DelayHeal("Excogitation", 45, 800))

    @petSkill
    def Aetherpact(self, time: int, target: Player) -> Record:
        return self.createRecord(target, status=Hot("Aetherpact", time, 300))

    def Protraction(self, target: Player) -> Record:
        return self.createRecord(target, status=IncreaseMaxHp("Protraction", 10, 1.1))

    # 群奶
    @petSkill
    def WhisperingDawn(self) -> Record:
        return self.createRecord(allPlayer, status=Hot("WhisperingDawn", 21, 80))

    def Succor(self) -> Record:
        return self.createRecord(
            allPlayer, value=200, status=Shield("Galvanize", 30, 320)
        )

    @petSkill
    def FeyIllumination(self) -> Record:
        return self.createRecord(
            allPlayer,
            status=[
                MagicMtg("FeyIllumination", 20, 0.95),
                SpellBonus("FeyIllumination", 20, 1.1),
            ],
        )

    def SacredSoil(self) -> Record:
        return self.createRecord(
            allPlayer,
            value=100,
            status=[
                Mtg("SacredSoil", 17, 0.9),
                Hot("SacredSoil", 15, 100, isGround=True),
            ],
        )

    def Indomitability(self) -> Record:
        return self.createRecord(allPlayer, value=400)

    @petSkill
    def FeyBlessing(self) -> Record:
        return self.createRecord(allPlayer, value=320)

    @petSkill
    def Consolation(self) -> Record:
        return self.createRecord(
            allPlayer, value=250, status=Shield("Consolation", 30, 250)
        )

    def Expedient(self) -> Record:
        return self.createRecord(allPlayer, status=Mtg("Expedient", 20, 0.9))


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

    def asEventUser(self, event: Event, target: Player) -> tuple[Event, Player]:
        if event.name in self.aoeSpell and self.searchStatus("PlenaryIndulgence"):
            event.value += 200
        elif event.name == "closeTheBell":
            if e := self.searchStatus("LiturgyOfTheBell"):
                event = Event(EventType.Heal, "LiturgyHeal", e.value * 200)
                target = allPlayer
                e.setZero()
        return super().asEventUser(event, target)

    def PlenaryIndulgence(self) -> Record:
        """全大赦"""
        return self.createRecord(self, status=BaseStatus("PlenaryIndulgence", 10))

    def update(self, timeInterval: float) -> list[Event]:
        self.bellCD -= timeInterval
        return super().update(timeInterval)

    def dealWithReadyEvent(self, event: Event) -> Record | None:
        super().dealWithReadyEvent(event)
        if event.eventType.value > 2:
            return
        if (bell := self.searchStatus("LiturgyOfTheBell")) and self.bellCD <= 0:
            bell.value -= 1
            self.bellCD = 1
            if bell.value == 0:
                bell.remainTime = 0
            return Record(Event(EventType.Heal, "LiturgyHeal", 400), self, allPlayer)

    # 单奶

    def Cure(self, target: Player) -> Record:
        return self.createRecord(target, value=500)

    def CureII(self, target: Player) -> Record:
        return self.createRecord(target, value=800)

    def Regen(self, target: Player) -> Record:
        return self.createRecord(target, status=Hot("Regen", 18, 250))

    def Benediction(self, target: Player) -> Record:
        return self.createRecord(target, value=1000000)

    def AfflatusSolace(self, target: Player) -> Record:
        return self.createRecord(target, value=800)

    def Tetragrammaton(self, target: Player) -> Record:
        return self.createRecord(target, value=700)

    def DivineBenison(self, target: Player) -> Record:
        return self.createRecord(target, status=Shield("DivineBenison", 15, 500))

    def Aquaveil(self, target: Player) -> Record:
        return self.createRecord(target, status=Mtg("Aquaveil", 8, 0.85))

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
        return self.createRecord(allPlayer, value=250, status=Hot("MedicaII", 15, 150))

    def Asylum(self) -> Record:
        """庇护所"""
        return self.createRecord(
            allPlayer,
            value=100,
            status=[
                Hot("Asylum", 24, 100, isGround=True),
                HealBonus("Asylum", 26, 1.1),
            ],
        )

    def Assize(self) -> Record:
        """法令"""
        return self.createRecord(allPlayer, value=400)

    def Temperance(self) -> list[Record]:
        """节制"""
        return [
            self.createRecord(allPlayer, status=Mtg("Temperance", 22, 0.9)),
            self.createRecord(self, status=SpellBonus("Temperance", 20, 1.2)),
        ]

    def LiturgyOfTheBell(self) -> Record:
        return self.createRecord(self, status=BaseStatus("LiturgyOfTheBell", 20, 5))

    def closeTheBell(self) -> Record:
        return self.createRecord(self)


class Astrologian(Healer):
    aoeSpell: list[str] = ["AspectedHelios", "Helios"]
    singleSpell: list[str] = ["Benefic", "BeneficII", "AspectedBenefic"]

    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Astrologian", hp, potency, self.aoeSpell + self.singleSpell)
        self.SynastryTarget: Player = self

    def asEventUser(self, event: Event, target: Player) -> tuple[Event, Player]:
        if event.name == "Synastry":
            self.SynastryTarget = target
        elif event.name in self.aoeSpell:
            if self.searchStatus("NeutralSect"):
                if event.name == "AspectedHelios":
                    event.append(Shield("AspectedHeliosShield", 30, 312.5))
                else:
                    event.append(Shield("AspectedBeneficShield", 30, 625))
            if status := self.searchStatus("Horoscope"):
                # TODO:会重复计算天宫图的回复
                status.remainTime = 30
                status.value = status.value * 2
        elif event.name == "closeHoroscope":
            if status := self.searchStatus("Horoscope"):
                status.remainTime = 0
        elif event.name == "Horoscope" and event.eventType == EventType.TrueHeal:
            # 表示天宫图时间归0, 将天宫图事件转为群奶
            event.value *= self.potency
            target = allPlayer
        return super().asEventUser(event, target)

    def dealWithReadyEvent(self, event: Event) -> Record | None:
        super().dealWithReadyEvent(event)
        if event.name not in self.singleSpell:
            return
        if self.searchStatus("Synastry") and self.SynastryTarget != self:
            return Record(
                Event(EventType.TrueHeal, "SynastryHeal", event.value * 0.4),
                self,
                self.SynastryTarget,
            )

    # 单奶

    def Synastry(self, target: Player) -> Record:
        return self.createRecord(target)

    def Benefic(self, target: Player) -> Record:
        return self.createRecord(target, value=500)

    def BeneficII(self, target: Player) -> Record:
        return self.createRecord(target, value=800)

    def AspectedBenefic(self, target: Player) -> Record:
        return self.createRecord(
            target, value=250, status=Hot("AspectedBenefic", 15, 250)
        )

    def CelestialIntersection(self, target: Player) -> Record:
        return self.createRecord(
            target, value=200, status=Shield("CelestialIntersection", 30, 400)
        )

    def Exaltation(self, target: Player) -> Record:
        return self.createRecord(
            target,
            status=[Mtg("Exaltation", 8, 0.9), DelayHeal("Exaltation", 8, 500)],
        )

    # 群奶

    def Helios(self) -> Record:
        return self.createRecord(allPlayer, value=400)

    def AspectedHelios(self) -> Record:
        return self.createRecord(
            allPlayer, value=250, status=Hot("AspectedHelios", 15, 150)
        )

    def CollectiveUnconscious(self) -> Record:
        return self.createRecord(
            allPlayer, status=[Mtg("CU", 5, 0.9), Hot("CU", 15, 100)]
        )

    def CelestialOpposition(self) -> Record:
        return self.createRecord(allPlayer, value=200, status=Hot("CO", 15, 100))

    def EarthlyStar(self) -> Record:
        return self.createRecord(allPlayer, value=720)

    def NeutralSect(self) -> Record:
        return self.createRecord(self, status=HealBonus("NeutralSect", 20, 1.2))

    # def Horoscope(self) -> Record:
    #     return self.createRecord(
    #         self, status=DelayHeal("Horoscope", 10, 200, snapshot=False)
    #     )

    # def closeHoroscope(self) -> Record:
    #     return self.createRecord(self)

    def Macrocosmos(self) -> Record:
        return self.createRecord(allPlayer, status=DelayHeal("Macrocosmos", 15, 200))

    def Microcosmos(self) -> Record:
        return self.createRecord(allPlayer)


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
        if self.searchStatus("Zoe", remove=True):
            event.getBuff(1.5)
        return super().asEventUser(event, target)

    def Dignosis(self, target: Player) -> Record:
        return self.createRecord(target, value=450)

    def Prognosis(self) -> Record:
        return self.createRecord(allPlayer, value=300)

    def PhysisII(self) -> Record:
        return self.createRecord(
            allPlayer,
            status=[Hot("PhysisII", 15, 130), HealBonus("PhysisII", 10, 1.1)],
        )

    def EkurasianDignosis(self, target: Player) -> Record:
        return self.createRecord(
            target, value=300, status=Shield("EkurasianDignosis", 30, 540)
        )

    def EkurasianPrognosis(self) -> Record:
        return self.createRecord(
            allPlayer, value=100, status=Shield("EkurasianPrognosis", 30, 320)
        )

    def Druochole(self, target: Player) -> Record:
        return self.createRecord(target, value=600)

    def Kerachole(self) -> Record:
        return self.createRecord(
            allPlayer,
            status=[Mtg("Kerachole", 15, 0.9), Hot("Kerachole", 15, 100)],
        )

    def Ixochole(self) -> Record:
        return self.createRecord(allPlayer, value=400)

    def Zoe(self) -> Record:
        return self.createRecord(self, status=BaseStatus("Zoe", 30))

    def Taurochole(self, target: Player) -> Record:
        return self.createRecord(target, value=700, status=Mtg("Kerachole", 15, 0.9))

    def Holos(self) -> Record:
        return self.createRecord(
            allPlayer,
            value=300,
            status=[Mtg("Holos", 20, 0.9), Shield("Holos", 30, 300)],
        )

    def Krasis(self, target: Player) -> Record:
        return self.createRecord(target, status=HealBonus("Krasis", 10, 1.2))

    def Pneuma(self) -> Record:
        return self.createRecord(allPlayer, value=600)

    def Haima(self, target: Player) -> Record:
        return self.createRecord(target, status=HaimaShield("haima", 15, 300))

    def Panhaima(self) -> Record:
        return self.createRecord(allPlayer, status=HaimaShield("Panhaima", 15, 200))

    def Pepsis(self) -> Record:
        return self.createRecord(allPlayer, 350)
