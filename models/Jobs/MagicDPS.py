from models.status import DelayHeal, HealBonus, Hot, MagicMtg, PhysicMtg, maxHpShield
from models.decorator import petSkill, targetSkill
from models.player import Player
from models.record import Record


class MagicDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency, 0.73, 0.84)

    def Addle(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[
                MagicMtg("Addle", 10, 0.9),
                PhysicMtg("Addle", 10, 0.95, display=False),
            ]
        )


class RedMage(MagicDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("RedMage", hp, potency)

    def MagickBarrier(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[
                MagicMtg("MagickBarrier", 10, 0.9),
                HealBonus("MagickBarrier", 10, 1.05, display=False),
            ]
        )

    @targetSkill
    def Vercure(self, **kwargs) -> Record:
        return self._buildRecord(value=500)


class Summoner(MagicDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Summoner", hp, potency)
        self.petCoefficient: float = 0.95

    @petSkill
    def EverlastingFlight(self, **kwargs) -> Record:
        return self._buildRecord(status=Hot("EverLastingFlight", 21, 100))

    @petSkill
    def Rekindle(self, **kwargs) -> Record:
        return self._buildRecord(
            value=400, status=DelayHeal("Rekindle", 30, isRekindle=True)
        )


class BlackMage(MagicDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("BlackMage", hp, potency)

    def Manaward(self, **kwargs) -> Record:
        return self._buildRecord(status=maxHpShield("Manaward", 20, 30))
