import heapq
from models.event import Event


class Record:
    """
    用于存放每场战斗中发生的事情
    在此, 具体含义为user do event to target
    """

    def __init__(self, event: list[Event] | Event, delay: float = 0) -> None:
        self.eventList: list[Event] = event if isinstance(event, list) else [event]
        self.delay: float = delay
        self.prepared: bool = False

    # def __str__(self) -> str:
    #     return "user: {0}, target: {1}, event: {2}".format(
    #         self.user.name, self.target.name, self.event
    #     )


class RecordQueue(object):
    def __init__(self):
        self._queue: list[tuple[float, int, Record]] = []
        self._index = 0

    def push(self, time: float, record: Record):
        heapq.heappush(self._queue, (time, self._index, record))
        self._index += 1

    def pop(self) -> Record:
        return heapq.heappop(self._queue)[2]

    @property
    def nextRecordTime(self) -> float:
        return self._queue[0][0]

    def empty(self):
        return True if not self._queue else False
