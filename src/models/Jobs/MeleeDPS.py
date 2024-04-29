from .decorator import single_skill
from ..Status import (
    HealBonus,
    MagicMtg,
    Mtg,
    PhysicMtg,
    MaxHpShield,
)
from ..player import Player
from ..Record import Record


class MeleeDPS(Player):
    def __init__(
        self,
        name: str,
        hp: int,
        damage_per_potency: float,
        physic_defense: float = 0.78,
    ) -> None:
        super().__init__(name, hp, damage_per_potency, physic_defense, 0.78)

    def Feint(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[
                MagicMtg("Feint", 10, 0.95),
                PhysicMtg("Feint", 10, 0.9, display=False),
            ]
        )

    @single_skill
    def SecondWind(self, **kwargs) -> Record:
        return self._buildRecord(value=500)


class Monk(MeleeDPS):
    def __init__(self, hp: int, damage_per_potency: float) -> None:
        super().__init__("Monk", hp, damage_per_potency)

    @single_skill
    def RiddleOfEarth(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("RiddleOfEarth", 10, 0.8))

    def Mantra(self, **kwargs) -> Record:
        return self._buildRecord(status=HealBonus("Mantra", 15, 1.1))


class Dragoon(MeleeDPS):
    def __init__(self, hp: int, damage_per_potency: float) -> None:
        super().__init__("Dragoon", hp, damage_per_potency, 0.73)


class Samurai(MeleeDPS):
    def __init__(self, hp: int, damage_per_potency: float) -> None:
        super().__init__("Samurai", hp, damage_per_potency)

    @single_skill
    def ThirdEye(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("ThirdEye", 4, 0.9))


class Ninja(MeleeDPS):
    def __init__(self, hp: int, damage_per_potency: float) -> None:
        super().__init__("Ninja", hp, damage_per_potency)

    @single_skill
    def ShadeShift(self, **kwargs) -> Record:
        return self._buildRecord(status=MaxHpShield("ShadeShift", 20, 20))


class Reaper(MeleeDPS):
    def __init__(self, hp: int, damage_per_potency: float) -> None:
        super().__init__("Reaper", hp, damage_per_potency, 0.73)

    @single_skill
    def ArcaneCrest(self, **kwargs) -> Record:
        # TODO: 未添加hot
        return self._buildRecord(status=MaxHpShield("ArcaneCrest", 5, 10))
