from models.baseEffect import Effect
from enum import Enum


class EventType(Enum):
    TrueHeal = 0  # 快照后的治疗
    Heal = 1  # 普通治疗
    PhysicsDamage = 2  # 物理伤害
    MagicDamage = 3  # 魔法伤害
    TrueDamage = 4  # dot伤害
    GroundHeal = 5 # 特殊治疗, 吃目标快照不吃施法者快照


class Event:
    def __init__(
        self,
        eventType: EventType,
        name: str,
        value: float = 0,
        effect: list[Effect] | Effect = [],
    ) -> None:
        self.name: str = name
        self.eventType: EventType = eventType
        self.value: float = value
        self.effectList: list[Effect] = []
        if isinstance(effect, list):
            self.effectList.extend(effect)
        else:
            self.append(effect)
        self.prepared: bool = False

    def getBuff(self, percentage: float) -> None:
        self.value = self.value * percentage
        for effect in self.effectList:
            if effect.getSnapshot:
                effect.value = effect.value * percentage
                effect.originValue = effect.originValue * percentage

    def __str__(self) -> str:
        return self.name + ": " + str(self.value)

    def append(self, effect: Effect) -> None:
        self.effectList.append(effect)


def petSkill(func):
    def wrapper(self, *args, **kwargs):
        ret: Event = func(self, *args, **kwargs)
        ret.getBuff(self.petCoefficient)
        return ret

    return wrapper
