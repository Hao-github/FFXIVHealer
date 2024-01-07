import heapq
from models.event import Event
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.player import Player


class Record:
    """
    用于存放每场战斗中发生的事情
    在此, 具体含义为user do event to target
    """

    def __init__(
        self, event: Event, user: "Player", target: "Player", delay: float = 0
    ) -> None:
        self.user: Player = user
        self.target: Player = target
        self.event: Event = event
        self.delay: float = delay

    def __str__(self) -> str:
        return "user: {0}, target: {1}, event: {2}".format(
            self.user.name, self.target.name, self.event
        )


class RecordQueue(object):
    def __init__(self):
        self._queue: list[tuple[float, int, list[Record]]] = []
        self._index = 0

    def push(self, time: float, record: list[Record]):
        heapq.heappush(self._queue, (time, self._index, record))
        self._index += 1

    def pop(self) -> tuple[float, int, list[Record]]:
        return heapq.heappop(self._queue)

    @property
    def nextRecordTime(self) -> float:
        return self._queue[0][0]

    def empty(self):
        return True if not self._queue else False
