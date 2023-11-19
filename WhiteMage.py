from basic import Event, EventType, HealBonus, Hot, Mitigation


class WhiteMage:
    def __init__(self) -> None:
        self.potency = 2500
        self.underPlenaryIndulgence: bool = False

    def OpenPlenaryIndulgence(self) -> None:
        self.underPlenaryIndulgence = True

    def ClosePlenaryIndulgence(self) -> None:
        self.underPlenaryIndulgence = False

    def Medica(self) -> Event:
        basicPotency = 600 if self.underPlenaryIndulgence else 400
        return Event(EventType.Heal, value=basicPotency * self.potency)

    def CureIII(self) -> Event:
        basicPotency = 800 if self.underPlenaryIndulgence else 600
        return Event(EventType.Heal, value=basicPotency * self.potency)

    def MedicaII(self) -> Event:
        basicPotency = 450 if self.underPlenaryIndulgence else 250
        return Event(
            EventType.Heal,
            value=basicPotency * self.potency,
            effectList=[Hot("MedicaIII", 15, 150 * self.potency)],
        )

    def Asylum(self) -> Event:
        return Event(
            EventType.Heal,
            value=100 * self.potency,
            effectList=[
                Hot("AsylumHot", 24, 100 * self.potency),
                HealBonus("AsylumHB", 27, 0.1),
            ],
        )

    def Assize(self) -> Event:
        return Event(
            EventType.Heal,
            value=400 * self.potency,
        )

    def Temperance(self) -> Event:
        return Event(
            EventType.Mitigation,
            effectList=[
                HealBonus("TemperanceHB", 20, 0.2),
                Mitigation("Temperance", 22, 0.1),
            ],
        )
