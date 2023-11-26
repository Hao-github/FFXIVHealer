import traceback
from models.baseEffect import Effect
from models.effect import MagicMtg, PhysicsMtg
from models.player import allPlayer, Player
from models.event import Event, EventType
from models.record import Record


class MeleeDPS(Player):
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

    def Feint(self) -> Record:
        return self.createRecord(
            allPlayer,
            effect=[MagicMtg("Feint", 10, 0.95), PhysicsMtg("Addle", 10, 0.9)],
        )

    def SecondWind(self) -> Record:
        return self.createRecord(self, value=500)
