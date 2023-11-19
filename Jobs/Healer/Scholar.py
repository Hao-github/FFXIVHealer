from models.effect import HealingSpellBonus, Hot, Mitigation, Shield
from models.event import Event, EventType
from models.player import Player


class Scholar(Player):
    def __init__(self, hp: int, potency: int, criticalNum: float) -> None:
        super().__init__("Scholar", hp, potency)
        self.petCoefficient: float = 0.95
        self.criticalNum: float = criticalNum
        self.RecitationRemainTime: float = 0

    def update(self, timeInterval: float) -> None:
        super().update(timeInterval)
        if self.RecitationRemainTime > 0:
            self.RecitationRemainTime -= timeInterval

    def Recitation(self) -> Event:
        self.RecitationRemainTime = 15
        return Event(EventType.Nothing, "Recitation")

    def checkRecitation(self, potency: int) -> float:
        if self.RecitationRemainTime > 0:
            self.RecitationRemainTime = 0
            return potency * self.criticalNum
        return potency

    def WhisperingDawn(self) -> Event:
        return Event(
            EventType.Heal,
            "WhisperingDawn",
            0,
            Hot("WhisperingDawn", 21, int(80 * self.potency * self.petCoefficient)),
        )

    def Succor(self) -> Event:
        basicPotency: float = self.checkRecitation(200) * self.totalHealingSpellBonus
        return Event(
            EventType.Heal,
            "Succor",
            int(basicPotency * self.potency),
            Shield("Succor", 30, int(basicPotency * 1.6 * self.potency)),
        )

    def FeyIllumination(self) -> Event:
        return Event(
            EventType.Mitigation,
            "FeyIllumination",
            effectList=[
                Mitigation("FeyIlluminationMtg", 20, 0.05),
                HealingSpellBonus("FeyIlluminationHSB", 20, 0.1),
            ],
        )

    def SacredSoil(self) -> Event:
        return Event(
            EventType.Heal,
            "SacredSoil",
            value=int(100 * self.potency),
            effectList=[
                Mitigation("SacredSoilMtg", 18, 0.1),
                Hot("SacredSoilHB", 15, int(100 * self.potency)),
            ],
        )

    def Indomitability(self) -> Event:
        basicPotency: float = self.checkRecitation(400)
        return Event(EventType.Heal, "Indomitability", int(basicPotency * self.potency))

    def Dissipation(self) -> Event:
        return Event(
            EventType.Nothing,
            "Dissipation",
            effectList=HealingSpellBonus("Dissipation", 30, 0.2),
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
            EventType.Mitigation,
            "Expedient",
            effectList=[Mitigation("Expedient", 20, 0.1)],
        )
