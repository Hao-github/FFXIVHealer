from models.status import HealBonus, MagicMtg, Mtg, PhysicsMtg
from models.player import Player
from models.record import Record


class MeleeDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency, 0.78, 0.78)

    def Feint(self, **kwargs) -> Record:
        return self._buildRecord(
            status=[MagicMtg("Feint", 10, 0.95), PhysicsMtg("Feint", 10, 0.9)]
        )

    def SecondWind(self, **kwargs) -> Record:
        return self._buildRecord(True, value=500)


class Monk(MeleeDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Monk", hp, potency)

    def RiddleOfEarth(self, **kwargs) -> Record:
        return self._buildRecord(True, status=Mtg("RiddleOfEarth", 10, 0.8))

    def Mantra(self, **kwargs) -> Record:
        return self._buildRecord(status=HealBonus("Mantra", 15, 1.1))


class Dragoon(MeleeDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Dragoon", hp, potency)


class Samurai(MeleeDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Samurai", hp, potency)

    def ThirdEye(self, **kwargs) -> Record:
        return self._buildRecord(True, status=Mtg("ThirdEye", 4, 0.9))
