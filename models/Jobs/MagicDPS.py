from models.status import HealBonus, Hot, MagicMtg, PhysicsMtg
from models.decorator import petSkill, targetSkill
from models.player import Player
from models.record import Record


class MagicDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency, 0.73, 0.84)

    def Addle(self) -> Record:
        return self.buildRecord(
            status=[MagicMtg("Addle", 10, 0.9), PhysicsMtg("Addle", 10, 0.95)]
        )


class RedMage(MagicDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("RedMage", hp, potency)

    def MagickBarrier(self, **kwargs) -> Record:
        return self.buildRecord(
            status=[
                MagicMtg("MagickBarrier", 10, 0.9),
                HealBonus("MagickBarrier", 10, 1.05),
            ]
        )

    @targetSkill
    def Vercure(self, **kwargs) -> Record:
        return self.buildRecord(value=500)


class Summoner(MagicDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Summoner", hp, potency)
        self.petCoefficient: float = 0.95

    @petSkill
    def EverlastingFlight(self, **kwargs) -> Record:
        return self.buildRecord(status=Hot("EverLastingFlight", 21, 100))

    @petSkill
    def Rekindle(self, **kwargs) -> Record:
        return self.buildRecord(value=400)
