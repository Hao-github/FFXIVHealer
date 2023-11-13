from random import random


class Timer:
    def __init__(self, initialTime: float = 0):
        self.__time = initialTime

    def update(self, time: float) -> bool:
        self.__time += time
        if self.__time >= 3:
            self.__time -= 3
            return True
        return False


class Effect:
    def __init__(self, name: str, duration: int) -> None:
        self.name: str = name
        self.duration: int = duration
        self.type: str = ""
        self.remainTime: float = duration

    def update(self, timeInterval: float) -> None:
        self.remainTime -= timeInterval


class Mitigation(Effect):
    def __init__(self, name: str, duration: int, percentage: float) -> None:
        super().__init__(name, duration)
        self.percentage: float = percentage
        self.type = "Mitigation"


class HealBonus(Effect):
    def __init__(self, name: str, duration: int, percentage) -> None:
        super().__init__(name, duration)
        self.percentage = percentage
        self.type = "HealBonus"


class Dot(Effect):
    def __init__(self, name: str, duration: int, damage: float) -> None:
        super().__init__(name, duration)
        self.damage: float = damage
        self.timer: Timer = Timer(random() * 3)
        self.type = "Dot"

    def update(self, timeInterval: float) -> bool:
        super().update(timeInterval)
        return self.timer.update()


class Hot(Effect):
    def __init__(self, name: str, duration: int, healing: float) -> None:
        super().__init__(name, duration)
        self.healing: float = healing
        self.timer: Timer = Timer(random() * 3)
        self.type = "Hot"

    def update(self, timeInterval: float) -> bool:
        super().update(timeInterval)
        return self.timer.update()
