from models.decorator import selfSkill
from models.status import Mtg, HealBonus, Hot, maxHpShield
from models.player import Player
from models.record import Record


class RangedDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency, 0.78, 0.78)

    def Tactician(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Tactician", 15, 0.9))

    @selfSkill
    def SecondWind(self, **kwargs) -> Record:
        return self._buildRecord(value=500)


class Bard(RangedDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Bard", hp, potency)

    def NaturesMinne(self, **kwargs) -> Record:
        return self._buildRecord(status=HealBonus("NaturesMinne", 15, 1.15))


class Dancer(RangedDPS):
    stackList = [5, 6, 7, 8, 10]

    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Dancer", hp, potency)

    def Improvisation(self, **kwargs) -> Record:
        stack: int = min(4, int(kwargs.get("duration", 0)) // 3)
        return self._buildRecord(
            status=[
                maxHpShield("ImprovisationShield", 30, self.stackList[stack]),
                Hot("ImprovisationHot", 15 + stack * 3, 100),
            ],
        )

    def CuringWaltz(self, **kwargs) -> Record:
        return self._buildRecord(value=300)


class Machinist(RangedDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Machinist", hp, potency)

    def Dismantle(self, **kwargs) -> Record:
        return self._buildRecord(status=Mtg("Dismantle", 10, 0.9))
