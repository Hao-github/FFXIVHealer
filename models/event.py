from models.effect import Effect
from models.basicEnum import EventType


class Event:
    def __init__(
        self,
        eventType: EventType,
        name: str,
        value: int = 0,
        effect: list[Effect] | Effect = []
    ) -> None:
        self.name: str = name
        self.eventType: EventType = eventType
        self.value: int = value
        self.effectList: list[Effect] = []
        if isinstance(effect, list):
            self.effectList.extend(effect)
        else:
            self.effectList.append(effect)
        self.hasPrepared: bool = False