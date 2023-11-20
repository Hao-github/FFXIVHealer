from models.effect import Dot
from models.event import Event, EventType
from models.player import Player


class Boss:
    def createMagicAttack(
        self,
        name: str,
        damage: int,
        dot: Dot | None = None,
        target: Player | None = None,
    ) -> Event:
        ret = Event(EventType.MagicDamage, name, value=damage, target=target)
        if dot:
            ret.effectList.append(dot)
        return ret

    def createPhysicsAOE(
        self,
        name: str,
        damage: int,
        dot: Dot | None = None,
        target: Player | None = None,
    ) -> Event:
        ret = Event(EventType.PhysicsDamage, name, value=damage, target=target)
        if dot:
            ret.effectList.append(dot)
        return ret
