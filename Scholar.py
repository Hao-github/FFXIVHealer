from basic import Event, EventType, Hot, Mitigation, Shield


class Scholar:
    def __init__(self, potency: int, criticalNum: float) -> None:
        self.petCoefficient: float = 0.95
        self.potency: int = potency
        self.criticalNum: int = criticalNum
        self.RecitationRemainTime: float = 0
        self.FeyIlluminationRemainTime: float = 0
        self.DissipationRemainTime: float = 0
        self.HealingSpellBonus: float = 1

    def update(self, timeInterval: float) -> None:
        self.HealingSpellBonus = 1
        if self.FeyIlluminationRemainTime > 0:
            self.HealingSpellBonus = self.HealingSpellBonus * 1.1
        if self.DissipationRemainTime > 0:
            self.HealingSpellBonus = self.HealingSpellBonus * 1.2
        for buff in [
            self.RecitationRemainTime,
            self.FeyIlluminationRemainTime,
            self.DissipationRemainTime,
        ]:
            if buff > 0:
                buff -= timeInterval

    def Recitation(self) -> None:
        self.RecitationRemainTime = 15

    def checkRecitation(self, potency: int) -> None:
        if self.RecitationRemainTime > 0:
            self.RecitationRemainTime = 0
            return potency * self.criticalNum
        return potency

    def WhisperingDawn(self) -> Event:
        return Event(
            EventType.Heal,
            0,
            Hot("WhisperingDawn", 21, 80 * self.potency * self.petCoefficient),
        )

    def Succor(self) -> Event:
        basicPotency: int = self.checkRecitation(200) * self.HealingSpellBonus
        return Event(
            EventType.Heal,
            basicPotency * self.potency,
            [Shield("Succor", 30, basicPotency * 1.6 * self.potency)],
        )

    def FeyIllumination(self) -> Event:
        return Event(
            EventType.Mitigation,
            effectList=[Mitigation("FeyIlluminationMtg", 20, 0.05)],
        )

    def SacredSoil(self) -> Event:
        return Event(
            EventType.Heal,
            value=100 * self.potency,
            effectList=[
                Mitigation("SacredSoilMtg", 18, 0.1),
                Hot("SacredSoilHB", 15, 100 * self.potency),
            ],
        )

    def Indomitability(self) -> Event:
        basicPotency: int = self.checkRecitation(400)
        return Event(EventType.Heal, basicPotency * self.potency)

    def Dissipation(self) -> None:
        self.DissipationRemainTime = 30

    def FeyBlessing(self) -> Event:
        return Event(EventType.Heal, 320 * self.petCoefficient * self.potency)

    def Consolation(self) -> Event:
        return Event(
            EventType.Heal,
            250 * self.petCoefficient * self.potency,
            Shield("Consolation", 30, 250 * self.petCoefficient * self.potency),
        )

    def Expedient(self) -> Event:
        return Event(
            EventType.Mitigation, effectList=[Mitigation("Expedient", 20, 0.1)]
        )
