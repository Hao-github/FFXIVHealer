from models.effect import Dot
from models.event import Event, EventType
from models.record import Record
from models.player import Player, totalPlayer


class Boss(Player):
    def __init__(self, name: str) -> None:
        super().__init__(name, 0, 0)

    def createMagicAOE(self, name: str, damage: int, dot: Dot | None = None) -> Record:
        ret = Event(EventType.MagicDamage, name, value=damage)
        if dot:
            ret.effectList.append(dot)
        return Record(ret, self, totalPlayer)

    def createPhysicsAOE(
        self, name: str, damage: int, dot: Dot | None = None
    ) -> Record:
        ret = Event(EventType.PhysicsDamage, name, value=damage)
        if dot:
            ret.effectList.append(dot)
        return Record(ret, self, totalPlayer)
