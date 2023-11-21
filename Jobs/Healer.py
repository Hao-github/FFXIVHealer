from copy import deepcopy
from functools import wraps
from models.effect import (
    DelayHealing,
    Effect,
    HealBonus,
    HealingSpellBonus,
    Hot,
    IncreaseMaxHp,
    MagicMitigation,
    Mitigation,
    Shield,
)
from models.event import Event, EventType
from models.player import Player


def addUser(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        ret: Event = func(self, *args, **kwargs)
        ret.user = self
        return ret

    return wrapper


def singleTarget(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        ret: Event = func(self, *args, **kwargs)
        ret.user = self
        if not ret.target:
            ret.target = self
        return ret

    return wrapper


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
            elif type(effect) == Hot or type(effect) == DelayHealing:
                effect.healing = int(effect.healing * percentage)
        return event


class Scholar(Healer):
    def __init__(self, hp: int, potency: int, criticalNum: float) -> None:
        super().__init__("Scholar", hp, potency, ["Succor", "Physicks", "Adloquium"])
        self.petCoefficient: float = 0.95
        self.criticalNum: float = criticalNum

    def updateEvent(self, event: Event) -> Event:
        event = super().updateEvent(event)
        # 判断目标身上是否有盾, 并进行展开
        if event.name == "Deployment":
            if deploySheild := self.__checkAdloquium(event.target):
                event.effectList.append(deploySheild)
                return event
        # 判断是否有秘策增幅
        if (
            event.name in ["Adloquium", "Succor", "Indomitability", "Excogitation"]
            and self.__checkRecitation()
        ):
            if event.name == "Adloquium":
                event.effectList.append(Shield("Catalyze", 30, int(event.value * 1.8)))
            return self._bonusHealingSpell(event, self.criticalNum)
        return event

    def __checkRecitation(self) -> bool:
        for effect in self.effectList:
            if effect.name == "Recitation":
                effect.remainTime = 0
                return True
        return False

    def __checkAdloquium(self, target: Player | None) -> Shield | None:
        if not target:
            return None
        for effect in target.effectList:
            if effect.name == "Adloquium" and type(effect) == Shield:
                ret = deepcopy(effect)
                effect.remainTime = 0
                return ret
        return None

    # buff类技能

    def Recitation(self) -> Event:
        return Event(EventType.Other, "Recitation", effect=Effect("Recitation", 15))

    def Dissipation(self) -> Event:
        return Event(
            EventType.Other,
            "Dissipation",
            effect=HealingSpellBonus("Dissipation", 30, 0.2),
            target=self,
        )

    @singleTarget
    def Deployment(self, target: Player | None = None) -> Event:
        return Event(EventType.Other, "Deployment", target=target)

    # 单奶

    @singleTarget
    def Physick(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Heal,
            "Physick",
            value=int(450 * self.potency),
            target=target,
        )

    @singleTarget
    def Adloquium(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Heal,
            "Adloquium",
            value=int(300 * self.potency),
            effect=Shield("Galvanize", 30, int(540 * self.potency)),
            target=target,
        )

    @singleTarget
    def Lustrate(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Heal,
            "Lustrate",
            value=int(600 * self.potency),
            target=target,
        )

    @singleTarget
    def Excogitation(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Other,
            "Excogitation",
            effect=DelayHealing("Excogitation", 45, int(800 * self.potency)),
            target=target,
        )

    @singleTarget
    def Aetherpact(self, time: int, target: Player | None = None) -> Event:
        return Event(
            EventType.Heal,
            "Aetherpact",
            effect=Hot(
                "Aetherpact", time, int(300 * self.potency * self.petCoefficient)
            ),
            target=target,
        )

    def Protraction(self, target: Player | None = None) -> Event:
        if not target:
            target = self
        return Event(
            EventType.Heal,
            "Protraction",
            value=int(target.maxHp * 0.1),
            effect=[
                HealBonus("ProtractionHB", 10, 0.1),
                IncreaseMaxHp("ProtractionIMH", 10, 0.1),
            ],
            target=target,
        )

    # 群奶

    def WhisperingDawn(self) -> Event:
        return Event(
            EventType.Heal,
            "WhisperingDawn",
            effect=Hot(
                "WhisperingDawn", 21, int(80 * self.potency * self.petCoefficient)
            ),
        )

    @addUser
    def Succor(self) -> Event:
        return Event(
            EventType.Heal,
            "Succor",
            value=int(200 * self.potency),
            effect=Shield("Galvanize", 30, int(320 * self.potency)),
        )

    def FeyIllumination(self) -> Event:
        return Event(
            EventType.Other,
            "FeyIllumination",
            effect=[
                MagicMitigation("FeyIlluminationMMtg", 20, 0.05),
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

    def updateEvent(self, event: Event) -> Event:
        event = super().updateEvent(event)
        if (
            event.name
            in [
                "Medica",
                "MedicaII",
                "BeneficIII",
                "AfflatusRapture",
            ]
            and self.__checkPI()
        ):
            event.value += int(200 * self.potency)
        return event

    def __checkPI(self) -> bool:
        for effect in self.effectList:
            if effect.name == "PlenaryIndulgence":
                return True
        return False

    def PlenaryIndulgence(self) -> Event:
        """全大赦"""
        return Event(
            EventType.Other,
            "PlenaryIndulgence",
            effect=Effect("PlenaryIndulgence", 10),
            target=self,
        )

    # 单奶
    @singleTarget
    def Cure(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Heal,
            "Cure",
            value=int(500 * self.potency),
            target=target,
        )

    @singleTarget
    def CureII(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Heal,
            "CureII",
            value=int(800 * self.potency),
            target=target,
        )

    @singleTarget
    def Regen(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Other,
            "Regen",
            effect=Hot("Regen", 18, int(250 * self.potency)),
            target=target,
        )

    @singleTarget
    def Benediction(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Heal,
            "Benediction",
            value=1000000,
            target=target,
        )

    @singleTarget
    def AfflatusSolace(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Heal,
            "AfflatusSolace",
            value=int(800 * self.potency),
            target=target,
        )

    @singleTarget
    def Tetragrammaton(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Heal,
            "Tetragrammaton",
            value=int(700 * self.potency),
            target=target,
        )

    @singleTarget
    def DivineBenison(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Other,
            "DivineBenison",
            effect=Shield("DivineBenison", 15, int(500 * self.potency)),
            target=target,
        )

    @singleTarget
    def Aquaveil(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Other,
            "Aquaveil",
            effect=Mitigation("Aquaveil", 8, 0.15),
            target=target,
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

    # def LiturgyOfTheBell(self) -> Event:
    #     return Event(
    #         EventType.Other,
    #         "LiturgyOfTheBell",
    #         effect=Effect("LiturgyOfTheBell5", 20),
    #         target=self,
    #     )


class Astrologian(Healer):
    # TODO: 星位和图, 地星, 天宫图, 大宇宙
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(
            name,
            hp,
            potency,
            ["Helios", "AspectedHelios", "Benefic", "BeneficII", "AspectedBenefic"],
        )

    def updateEvent(self, event: Event) -> Event:
        event = super().updateEvent(event)
        if event.name == "AspectedHelios" and self.__checkNS():
            event.effectList.append(
                Shield("AspectedHeliosShield", 30, int(event.value * 1.25))
            )
        elif event.name == "AspectedBenefic" and self.__checkNS():
            event.effectList.append(
                Shield("AspectedBeneficShield", 30, int(event.value * 2.5))
            )
        return event

    def __checkNS(self) -> bool:
        for effect in self.effectList:
            if effect.name == "NeutralSect":
                return True
        return False

    # 单奶
    @singleTarget
    def Benefic(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Heal,
            "Benefic",
            value=int(500 * self.potency),
            target=target,
        )

    @singleTarget
    def BeneficII(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Heal,
            "BeneficII",
            value=int(800 * self.potency),
            target=target,
        )

    @singleTarget
    def AspectedBenefic(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Heal,
            "AspectedBenefic",
            value=int(250 * self.potency),
            effect=Hot("AspectedBenefic", 15, int(250 * self.potency)),
            target=target,
        )

    @singleTarget
    def CelestialIntersection(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Heal,
            "DivineBenision",
            value=int(200 * self.potency),
            effect=Shield("CelestialIntersection", 15, int(400 * self.potency)),
            target=target,
        )

    @singleTarget
    def Exaltation(self, target: Player | None = None) -> Event:
        return Event(
            EventType.Other,
            "Exaltation",
            effect=[
                Mitigation("Exaltation", 8, 0.1),
                DelayHealing("ExaltationDH", 8, int(500 * self.potency)),
            ],
            target=target,
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

    def NeutralSect(self) -> Event:
        return Event(EventType.Other, "NeutralSect", effect=Effect("NeutralSect", 20))
