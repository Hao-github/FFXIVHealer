class Timer:
    def __init__(self, initialTime: float = 0):
        self.__time = initialTime

    def update(self, time: float) -> bool:
        self.__time += time
        if self.__time >= 3:
            self.__time -= 3
            return True
        return False
