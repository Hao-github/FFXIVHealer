from functools import reduce
import pandas as pd
from models.player import allPlayer, Player
from models.event import Event
from models.record import RecordQueue, Record


class Fight:
    playerList: dict[str, Player] = {}
    recordQueue: RecordQueue = RecordQueue()
    output = open("output.txt", "w", encoding="utf-8")
    boss = Player("boss", 0, 0, 0, 0)

    @classmethod
    def addbaseCofig(cls, excelFile: str) -> None:
        dfDict = pd.read_excel(excelFile, sheet_name=None)
        dfDict["小队列表"].apply(cls.__rowToPlayer, axis=1)
        dfDict["BOSS时间轴"].apply(cls.__rowToBossRecord, axis=1)
        for r in dfDict["奶轴"].merge(dfDict["技能"], on="name").to_dict("records"):
            cls.recordQueue.push(
                cls.__toTimestamp(r["time"]),
                getattr(Fight.playerList[r["user"]], r["skillName"])(**r),
            )

    @classmethod
    def run(cls, step: float):
        if not cls.playerList or cls.recordQueue.empty():
            return
        time: float = -3
        while True:
            # 检查buff, 如果dot和hot跳了, 或者延迟治疗时间到了, 就产生立即的prepare事件

            if x := reduce(
                lambda x, y: x + y.update(step), cls.playerList.values(), []
            ):
                cls.recordQueue.push(time, Record(x, display=False))
            # 如果当前时间大于等于最近的事件的发生时间
            while time >= cls.recordQueue.nextRecordTime:
                record = cls.recordQueue.pop()
                if not record.prepared:
                    cls.recordQueue.push(time + record.delay, cls.forUnprepared(record))
                else:
                    for event in record.eventList:
                        if a := event.target.dealWithReadyEvent(event):
                            cls.recordQueue.push(time, Record([a]))
                    cls.showInfo(time, record.eventList[0])

                if cls.recordQueue.empty():
                    return

            time += step

    @classmethod
    def forUnprepared(cls, record: Record) -> Record:
        record.prepared = True
        newEventList: list[Event] = []
        for event in record.eventList:
            event = event.user.asEventUser(event)
            if event.target != allPlayer:
                newEventList.append(event.target.asEventTarget(event))
            else:
                for player in cls.playerList.values():
                    newEventList.append(player.asEventTarget(event.copy(player)))
        record.eventList = newEventList
        return record

    @classmethod
    def showInfo(cls, time: float, event: Event):
        if event.nameIs("naturalHeal"):
            return
        cls.output.write(
            "After Event {0} At {1}\n".format(event.name, cls.__fromTimestamp(time))
        )
        for name, player in cls.playerList.items():
            cls.output.write("{0}-{1}".format(name, str(player)))

    @classmethod
    def __rowToPlayer(cls, row: pd.Series):
        jobClass = getattr(__import__("models.Jobs." + row["class"]), row["job"])
        cls.playerList[row["name"]] = jobClass(row["hp"], row["potency"])
        return 0

    @classmethod
    def __rowToBossRecord(cls, row: pd.Series):
        event = Event.fromRow(
            row,
            cls.boss,
            allPlayer if row["target"] == "all" else cls.playerList[row["target"]],
        )
        cls.recordQueue.push(
            cls.__toTimestamp(row["prepareTime"]), Record([event], delay=row["delay"])
        )
        return 0

    @staticmethod
    def __toTimestamp(rawTime: str) -> float:
        negative = False
        if rawTime[0] == "-":
            negative = True
            rawTime = rawTime[1:]
        m, s = rawTime.strip().split(":")
        ret = int(m) * 60 + float(s)
        return ret if not negative else -ret

    @staticmethod
    def __fromTimestamp(rawTime: float) -> str:
        begin = ""
        if rawTime < 0:
            begin = "-"
            rawTime = -rawTime
        return "{0}{1}:{2}".format(begin, int(rawTime // 60), round(rawTime % 60, 3))
