from basic import Event, EventType, HealBonus, Hot, Mitigation


class Scholar:
    def __init__(self) -> None:
        self.petCoefficient = 0.95
        self.potency = 2500
        self.criticalNum = 1.6
        self.underRecitation: bool = False

    def Recitation(self) -> None:
        self.underRecitation = True

    def checkRecitation(self, potency: int) -> None:
        if self.underRecitation:
            self.underRecitation = False
            return potency * self.criticalNum
        return potency

    def WhisperingDawn(self) -> Event:
        return Event(
            EventType.Heal,
            0,
            Hot("WhisperingDawn", 21, 80 * self.potency, self.petCoefficient),
        )

    def Succor(self) -> list[Event]:
        basicPotency: int = self.checkRecitation(200)
        return [
            Event(EventType.Heal, basicPotency * self.potency),
            Event(EventType.Shield, basicPotency * 1.6 * self.potency),
        ]

    def FeyIllumination(self) -> Event:
        return Event(
            EventType.Mitigation,
            effectList=[
                Mitigation("FeyIlluminationMtg", 20, 0.05),
                HealBonus("FeyIlluminationHB", 20, 0.1),
            ],
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

    def Dissipation(self) -> Event:
        return Event(
            EventType.Mitigation, effectList=[HealBonus("Dissipation", 30, 0.2)]
        )

    def FeyBlessing(self) -> Event:
        return Event(EventType.Heal, 320 * self.petCoefficient)

    def Consolation(self) -> list[Event]:
        return [
            Event(EventType.Heal, 250 * self.petCoefficient),
            Event(EventType.Shield, 250 * self.petCoefficient),
        ]

    def Expedient(self) -> Event:
        return Event(
            EventType.Mitigation, effectList=[Mitigation("Expedient", 20, 0.1)]
        )
