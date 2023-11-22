from models.boss import Boss
from models.player import Player
from models.event import Event
from queue import PriorityQueue


class Record:
    """
    用于存放每场战斗中发生的事情
    在此, 具体含义为user do event to target
    """

    def __init__(self, event: Event, user: Player | Boss, target: Player) -> None:
        self.user: Player | Boss = user
        self.target: Player = target
        self.event: Event = event
        self.prepared: bool = False


class RecordQueue:
    def __init__(self, timeInterval: float) -> None:
        self.recordqueue: PriorityQueue = PriorityQueue()
        self.timeInterval: float = timeInterval

    def put(self, time: float, record: Record | list[Record]) -> None:
        if isinstance(record, Record):
            self.recordqueue.put((time, record))
            return
        for r in record:
            self.recordqueue.put((time, r))

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
