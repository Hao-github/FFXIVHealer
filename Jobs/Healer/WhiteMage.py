from models.player import Player
from ...models.effect import HealBonus, Hot, Mitigation
from ...models.event import Event, EventType


class WhiteMage(Player):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("WhiteMage", hp, potency)
        self.PlenaryIndulgenceRemainTime: float = 0

    def update(self, timeInterval: float) -> None:
        if self.PlenaryIndulgenceRemainTime > 0:
            self.PlenaryIndulgenceRemainTime -= timeInterval

    def PlenaryIndulgence(self) -> Event:
        self.PlenaryIndulgenceRemainTime = 10
        return Event(EventType.Nothing, "PlenaryIndulgence")

    def PIHealing(self) -> int:
        if self.PlenaryIndulgenceRemainTime > 0:
            return 200
        return 0

    def Medica(self) -> Event:
        basicPotency = 400 * self.totalHealingSpellBonus + self.PIHealing()
        return Event(EventType.Heal, "Medica", value=int(basicPotency * self.potency))

    def AfflatusRapture(self) -> Event:
        basicPotency = 400 * self.totalHealingSpellBonus + self.PIHealing()
        return Event(
            EventType.Heal, "AfflatusRapture", value=int(basicPotency * self.potency)
        )

    def CureIII(self) -> Event:
        basicPotency = 600 * self.totalHealingSpellBonus + self.PIHealing()
        return Event(EventType.Heal, "CureIII", value=int(basicPotency * self.potency))

    def MedicaII(self) -> Event:
        basicPotency = 250 * self.totalHealingSpellBonus + self.PIHealing()
        basicHotPotency = 150 * self.totalHealingSpellBonus
        return Event(
            EventType.Heal,
            "MedicaII",
            value=int(basicPotency * self.potency),
            effectList=[Hot("MedicaII", 15, int(basicHotPotency * self.potency))],
        )

    def Asylum(self) -> Event:
        return Event(
            EventType.Heal,
            "Asylum",
            value=int(100 * self.potency),
            effectList=[
                Hot("AsylumHot", 24, int(100 * self.potency)),
                HealBonus("AsylumHB", 27, 0.1),
            ],
        )

    def Assize(self) -> Event:
        return Event(
            EventType.Heal,
            "Assize",
            value=int(400 * self.potency),
        )

    def Temperance(self) -> Event:
        self.TemperanceRemainTime = 20
        return Event(
            EventType.Mitigation,
            "Temperance",
            effectList=[
                Mitigation("Temperance", 22, 0.1),
                # HealingSpellBonus("TemperanceHSB", 22, 0.2),
            ],
        )
