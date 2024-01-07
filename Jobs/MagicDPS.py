from models.status import HealBonus, Hot, MagicMtg, PhysicsMtg
from models.event import petSkill
from models.player import Player, allPlayer
from models.record import Record


class MagicDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency, 0.73, 0.84)

    def Addle(self) -> Record:
        return self.buildRecord(
            allPlayer,
            status=[MagicMtg("Addle", 10, 0.9), PhysicsMtg("Addle", 10, 0.95)],
        )


class RedMage(MagicDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("RedMage", hp, potency)

    def MagickBarrier(self) -> Record:
        return self.buildRecord(
            allPlayer,
            status=[
                MagicMtg("MagickBarrier", 10, 0.9),
                HealBonus("MagickBarrier", 10, 1.05),
            ],
        )

    def Vercure(self, target: Player) -> Record:
        return self.buildRecord(target, value=500)


class Summoner(MagicDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Summoner", hp, potency)
        self.petCoefficient: float = 0.95

    @petSkill
    def EverlastingFlight(self) -> Record:
        return self.buildRecord(allPlayer, status=Hot("EverLastingFlight", 21, 100))

    @petSkill
    def Rekindle(self, target: Player) -> Record:
        return self.buildRecord(target, value=400)
