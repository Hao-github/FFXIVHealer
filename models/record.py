from models.player import Player
from models.event import Event
from queue import PriorityQueue


class Record:
    """
    用于存放每场战斗中发生的事情
    在此, 具体含义为user do event to target
    """

    def __init__(
        self, event: Event, user: Player, target: Player, delay: float = 0
    ) -> None:
        self.user: Player = user
        self.target: Player = target
        self.event: Event = event
        self.delay: float = delay

    def __str__(self) -> str:
        return "user: {0}, target: {1}, event: {2}".format(
            self.user.name, self.target.name, self.event
        )
        
    def __lt__(self, __value: object) -> bool:
        return False


class RecordQueue:
    def __init__(self, timeInterval: float) -> None:
        self.recordqueue: PriorityQueue = PriorityQueue()
        self.timeInterval: float = timeInterval

    def putRecord(self, time: float, record: Record | list[Record]) -> None:
        if isinstance(record, Record):
            self.recordqueue.put((time, record))
            return
        for r in record:
            self.recordqueue.put((time, r))

    def putEvent(
        self, time: float, event: Event | list[Event], user: Player, target: Player
    ) -> None:
        if isinstance(event, Event):
            self.recordqueue.put((time, Record(event, user, target)))
            return
        for e in event:
            self.recordqueue.put((time, Record(e, user, target)))

    def get(self) -> Record | None:
        if self.empty():
            return None
        return self.recordqueue.get()[1]

    def happen(self, time: float) -> bool | None:
        if self.empty():
            return None
        return 0 <= (self.recordqueue.queue[0][0] - time) < self.timeInterval

    def empty(self) -> bool:
        return self.recordqueue.empty()
