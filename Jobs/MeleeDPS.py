from models.effect import Effect, Mtg
from models.player import allPlayer, Player
from models.event import Event, EventType
from models.record import Record


class MeleeDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def createRecord(
        self,
        name: str,
        target: Player,
        value: float = 0,
        effect: list[Effect] | Effect = [],
    ) -> Record:
        return Record(Event(EventType.Heal, name, value, effect), self, target)

    def Feint(self) -> Record:
        return self.createRecord("Feint", allPlayer, effect=Mtg("Feint", 10, 0.95))
