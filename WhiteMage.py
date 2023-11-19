from basic import Event, EventType, HealBonus, Hot, Mitigation


class WhiteMage:
    def __init__(self) -> None:
        self.potency = 2500
        self.PlenaryIndulgenceRemainTime: float = 0
        self.TemperanceRemainTime: float = 0
        self.HealingSpellBonus: float = 1

    def update(self, timeInterval: float) -> None:
        self.HealingSpellBonus = 1.2 if self.TemperanceRemainTime > 0 else 1
        for buff in [self.PlenaryIndulgenceRemainTime, self.TemperanceRemainTime]:
            if buff > 0:
                buff -= timeInterval

    def PlenaryIndulgence(self) -> None:
        self.PlenaryIndulgenceRemainTime = 10

    def PIHealing(self) -> int:
        if self.PlenaryIndulgenceRemainTime > 0:
            return 200
        return 0

    def Medica(self) -> Event:
        basicPotency = 400 * self.HealingSpellBonus + self.PIHealing
        return Event(EventType.Heal, value=basicPotency * self.potency)

    def CureIII(self) -> Event:
        basicPotency = 600 * self.HealingSpellBonus + self.PIHealing
        return Event(EventType.Heal, value=basicPotency * self.potency)

    def MedicaII(self) -> Event:
        basicPotency = 250 * self.HealingSpellBonus + self.PIHealing
        basicHotPotency = 150 * self.HealingSpellBonus
        return Event(
            EventType.Heal,
            value=basicPotency * self.potency,
            effectList=[Hot("MedicaII", 15, basicHotPotency * self.potency)],
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
        self.TemperanceRemainTime = 20
        return Event(
            EventType.Mitigation,
            effectList=[
                Mitigation("Temperance", 22, 0.1),
            ],
        )
