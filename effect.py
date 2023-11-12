from random import random
from basic import Timer


class Effect:
    def __init__(self, name: str, duration: float) -> None:
        self.name: str = name
        self.duration: float = duration
        self.type: str = ""
        self.remainTime: float = duration

    def update(self, timeInterval: float) -> None:
        self.remainTime -= timeInterval


class Mitigation(Effect):
    def __init__(self, name: str, duration: float, percentage: float) -> None:
        super(Mitigation, self).__init__(name, duration)
        self.percentage: float = percentage
        self.type = "Mitigation"


class Dot(Effect):
    def __init__(self, name: str, duration: float, damage: float) -> None:
        super(Dot, self).__init__(name, duration)
        self.damage: float = damage
        self.timer: Timer = Timer(random() * 3)
        self.type = "Dot"

    def update(self, timeInterval: float) -> bool:
        super().update(timeInterval)
        return self.timer.update()