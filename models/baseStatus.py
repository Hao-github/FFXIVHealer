from __future__ import annotations


class BaseStatus:
    conflict = ["Galavinze", "EkurasianPrognosis", "EkurasianDignosis"]

    def __init__(self, name: str, duration: float, value: float = 0) -> None:
        self.name: str = name
        self.duration: float = duration
        self.remainTime: float = duration
        self.value: float = value
        self.getSnapshot: bool = False

    def update(self, timeInterval: float, **kwargs) -> None:
        self.remainTime -= timeInterval

    def __str__(self) -> str:
        return self.name + ": " + str(round(self.remainTime, 2)) + "s"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, BaseStatus) or type(self) != type(__value):
            return False
        return self.value == __value.value

    def __lt__(self, __value: object) -> bool:
        if not isinstance(__value, BaseStatus) or type(self) != type(__value):
            return False
        return self.value < __value.value

    def setZero(self) -> BaseStatus:
        self.remainTime = 0
        return self

    def getBuff(self, percentage: float) -> BaseStatus:
        if self.getSnapshot:
            self.value *= percentage
        return self
