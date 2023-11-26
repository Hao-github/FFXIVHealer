class Effect:
    def __init__(self, name: str, duration: float, value: float = 0) -> None:
        self.name: str = name
        self.duration: float = duration
        self.remainTime: float = duration
        self.originValue: float = value
        self.value: float = value
        self.getSnapshot: bool = False

    def update(self, timeInterval: float) -> None:
        self.remainTime -= timeInterval

    def __str__(self) -> str:
        return self.name + ": " + str(round(self.remainTime, 2)) + "s"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Effect) or type(self) != type(__value):
            return False
        return self.value == __value.value

    def __lt__(self, __value: object) -> bool:
        if not isinstance(__value, Effect) or type(self) != type(__value):
            return False
        return self.value < __value.value

    def setZero(self) -> None:
        self.remainTime = 0
        self.value = 0