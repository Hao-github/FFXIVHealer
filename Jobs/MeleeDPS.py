from models.status import MagicMtg, Mtg, PhysicsMtg
from models.player import allPlayer, Player
from models.record import Record


class MeleeDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency, 0.78, 0.78)

    def Feint(self) -> Record:
        return self.createRecord(
            allPlayer,
            status=[MagicMtg("Feint", 10, 0.95), PhysicsMtg("Addle", 10, 0.9)],
        )

    def SecondWind(self) -> Record:
        return self.createRecord(self, value=500)


class Monk(MeleeDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Monk", hp, potency)

    def RiddleOfEarth(self) -> Record:
        return self.createRecord(self, status=Mtg("RiddleOfEarth", 10, 0.8))


class Dragoon(MeleeDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Dragoon", hp, potency)


class Samurai(MeleeDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Samurai", hp, potency)

    def ThirdEye(self) -> Record:
        return self.createRecord(self, status=Mtg("ThirdEye", 4, 0.9))
