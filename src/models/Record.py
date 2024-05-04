import heapq
from dataclasses import dataclass, field

from .Event import Event
from ..utils import T


@dataclass
class Record:
    """用于存储战斗中发生的事件。

    Attributes:
        eventList (list[Event]): 包含战斗中发生的事件的列表。
        delay (float): 事件发生的延迟时间。
        fromHot (bool): 指示事件是否来自持续治疗或持续伤害。
        costType (Literal["gcd", "ether", None]): 指示事件的消耗类型。
    """

    eventList: list[Event] = field(default_factory=list)
    delay: float = 0.0
    fromHot: bool = False
    costType: T = None

    def __post_init__(self):
        """初始化事件的状态。

        Attributes:
            prepared (bool): 指示事件是否已准备。
        """
        self.prepared: bool = False


class RecordQueue:
    """用于管理记录的优先级队列。

    Attributes:
        _queue (list[tuple[float, int, Record]]): 优先级队列，包含元组 (时间, 索引, 记录)。
        _index (int): 记录的索引，用于在优先级队列中排序。
    """

    def __init__(self):
        """初始化优先级队列和索引。"""
        self._queue: list[tuple[float, int, Record]] = []
        self._index = 0

    def push(self, time: float, record: Record):
        """将记录推送到优先级队列中。

        Args:
            time (float): 记录的时间戳。
            record (Record): 要推送的记录。
        """
        heapq.heappush(self._queue, (time, self._index, record))
        self._index += 1

    def pop(self) -> Record:
        """从优先级队列中弹出最早的记录。

        Returns:
            Record: 从队列中弹出的记录。
        """
        return heapq.heappop(self._queue)[2]

    @property
    def next_record_time(self) -> float:
        """获取队列中最早的记录时间。

        Returns:
            float: 队列中最早记录的时间戳。
        """
        return self._queue[0][0]

    def empty(self) -> bool:
        """检查队列是否为空。

        Returns:
            bool: 队列为空则返回 True，否则返回 False。
        """
        return len(self._queue) == 0
