from models.Jobs.decorator import selfSkill
from models.status import HealBonus, MagicMtg, Mtg, PhysicMtg, maxHpShield
from models.player import Player
from models.record import Record


class MeleeDPS(Player):
    def __init__(
        self, name: str, hp: int, damagePerPotency: float, physicDefense: float = 0.78
    ) -> None:
        super().__init__(name, hp, damagePerPotency, physicDefense, 0.78)

    def Feint(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[
                MagicMtg("Feint", 10, 0.95),
                PhysicMtg("Feint", 10, 0.9, display=False),
            ]
        )

    @selfSkill
    def SecondWind(self, **kwargs) -> Record:
        return self._buildRecord(value=500)


class Monk(MeleeDPS):
    def __init__(self, hp: int, damagePerPotency: float) -> None:
        super().__init__("Monk", hp, damagePerPotency)

    @selfSkill
    def RiddleOfEarth(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("RiddleOfEarth", 10, 0.8))

    def Mantra(self, **kwargs) -> Record:
        return self._buildRecord(status=HealBonus("Mantra", 15, 1.1))


class Dragoon(MeleeDPS):
    def __init__(self, hp: int, damagePerPotency: float) -> None:
        super().__init__("Dragoon", hp, damagePerPotency, 0.73)


class Samurai(MeleeDPS):
    def __init__(self, hp: int, damagePerPotency: float) -> None:
        super().__init__("Samurai", hp, damagePerPotency)

    @selfSkill
    def ThirdEye(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("ThirdEye", 4, 0.9))


class Ninja(MeleeDPS):
    def __init__(self, hp: int, damagePerPotency: float) -> None:
        super().__init__("Ninja", hp, damagePerPotency)

    @selfSkill
    def ShadeShift(self, **kwargs) -> Record:
        return self._buildRecord(status=maxHpShield("ShadeShift", 20, 20))


class Reaper(MeleeDPS):
    def __init__(self, hp: int, damagePerPotency: float) -> None:
        super().__init__("Reaper", hp, damagePerPotency, 0.73)

    @selfSkill
    def ArcaneCrest(self, **kwargs) -> Record:
        # TODO: 未添加hot
        return self._buildRecord(status=maxHpShield("ArcaneCrest", 5, 10))
