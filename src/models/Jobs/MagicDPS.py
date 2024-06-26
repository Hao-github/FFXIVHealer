from .decorator import pet_skill, single_skill
from ..Status import (
    DelayHeal,
    HealBonus,
    Hot,
    MagicMtg,
    PhysicMtg,
    MaxHpShield,
)
from ..player import Player
from ..Record import Record


class MagicDPS(Player):
    def __init__(self, name: str, hp: int, damage_per_potency: float) -> None:
        super().__init__(name, hp, damage_per_potency, 0.73, 0.84)

    def Addle(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[
                MagicMtg("Addle", 10, 0.9),
                PhysicMtg("Addle", 10, 0.95, display=False),
            ]
        )


class RedMage(MagicDPS):
    def __init__(self, hp: int, damage_per_potency: float) -> None:
        super().__init__("RedMage", hp, damage_per_potency)

    def MagickBarrier(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[
                MagicMtg("MagickBarrier", 10, 0.9),
                HealBonus("MagickBarrier", 10, 1.05, display=False),
            ]
        )

    @single_skill
    def Vercure(self, **kwargs) -> Record:
        return self._buildRecord(value=500)


class Summoner(MagicDPS):
    def __init__(self, hp: int, damage_per_potency: float) -> None:
        super().__init__("Summoner", hp, damage_per_potency)
        self.pet_coefficient: float = 0.95

    @pet_skill
    def EverlastingFlight(self, **kwargs) -> Record:
        return self._buildRecord(status=Hot("EverLastingFlight", 21, 100))

    @pet_skill
    def Rekindle(self, **kwargs) -> Record:
        return self._buildRecord(
            value=400, status=DelayHeal("Rekindle", 30, isRekindle=True)
        )


class BlackMage(MagicDPS):
    def __init__(self, hp: int, damage_per_potency: float) -> None:
        super().__init__("BlackMage", hp, damage_per_potency)

    def Manaward(self, **kwargs) -> Record:
        return self._buildRecord(status=MaxHpShield("Manaward", 20, 30))
