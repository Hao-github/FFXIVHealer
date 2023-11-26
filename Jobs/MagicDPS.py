import traceback
from models.effect import Effect, HealBonus, Hot, MagicMtg, Mtg
from models.event import Event, EventType, petSkill
from models.player import Player, allPlayer
from models.record import Record


class MagicDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def createRecord(
        self,
        target: Player,
        value: float = 0,
        effect: list[Effect] | Effect = [],
    ) -> Record:
        return Record(
            Event(EventType.Heal, traceback.extract_stack()[-2][2], value, effect),
            self,
            target,
        )

    def Addle(self) -> Record:
        return self.createRecord(allPlayer, effect=Mtg("Addle", 10, 0.9))


class RedMage(MagicDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("RedMage", hp, potency)

    def MagickBarrier(self) -> Record:
        return self.createRecord(
            allPlayer,
            effect=[
                MagicMtg("MagickBarrierMMtg", 10, 0.9),
                HealBonus("MagickBarrierHB", 10, 1.05),
            ],
        )

    def Vercure(self, target: Player) -> Record:
        return self.createRecord(target, value=500)


class Summoner(MagicDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Summoner", hp, potency)
        self.petCoefficient: float = 0.95

    @petSkill
    def EverlastingFlight(self) -> Record:
        return self.createRecord(allPlayer, effect=Hot("EverLastingFlight", 21, 100))

    @petSkill
    def Rekindle(self, target: Player) -> Record:
        return self.createRecord(target, value=400)
