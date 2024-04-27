from dataclasses import dataclass, field
import heapq
from models.event import Event


@dataclass
class Record:
    """
    用于存放每场战斗中发生的事情
    """

    eventList: list[Event] = field(default_factory=list)
    delay: float = 0
    fromHot: bool = True
    cost: float = 0 # 该事情（例如回血）的亏损为cost

    def __post_init__(self):
        self.prepared: bool = False

    def __str__(self) -> str:
        return f"delay: {str(self.delay)}, eventList: [{', '.join(str(i) for i in self.eventList)}]"


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
    def next_record_time(self) -> float:
        return self._queue[0][0]

    def empty(self):
        return True if not self._queue else False
