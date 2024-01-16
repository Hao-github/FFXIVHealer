from functools import reduce
from typing import Any, Hashable
import pandas as pd
from models.player import allPlayer, boss, Player
from models.event import Event
from models.record import RecordQueue, Record
from Settings.baseConfig import jobToClass


class Fight:
    playerList: dict[str, Player] = {}
    recordQueue: RecordQueue = RecordQueue()

    @classmethod
    def addbaseCofig(cls, bossFile: str, playerFile: str, skillFile: str) -> None:
        pd.read_csv(bossFile).apply(cls.__rowToBossRecord, axis=1)
        pd.read_csv(playerFile).apply(cls.__rowToPlayer, axis=1)
        list(
            map(
                cls.__rowToHealRecord,
                pd.read_csv(skillFile)
                .merge(pd.read_csv("Settings/translate.csv"), on="name")
                .drop(columns=["name"])
                .to_dict("records"),
            )
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
                    if record.display:
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
        if event.name == "naturalHeal":
            return
        print("After Event {0} At {1}".format(event.name, time))
        for name, player in cls.playerList.items():
            print(
                "{0}-{1:<13}: {2:>6}, statusList: [{3}]".format(
                    name,
                    player.name,
                    str(player.hp),
                    ", ".join(
                        str(i)
                        for i in player.statusList
                        if i.name
                        not in ["naturalHeal", "magicDefense", "physicsDefense"]
                    ),
                ),
            )

    @classmethod
    def __rowToPlayer(cls, row: pd.Series):
        jobName = row["job"]
        jobClass = getattr(__import__("models.Jobs." + jobToClass[jobName]), jobName)
        cls.playerList[row["name"]] = jobClass(row["hp"], row["potency"])
        return jobName

    @classmethod
    def __rowToBossRecord(cls, row: pd.Series):
        cls.recordQueue.push(
            cls.__toTimestamp(row["prepareTime"]),
            Record(
                [
                    Event.fromRow(
                        row,
                        boss,
                        allPlayer
                        if row["target"] == "all"
                        else cls.playerList[row["target"]],
                    )
                ],
                delay=row["delay"],
            ),
        )
        return row["prepareTime"]

    @classmethod
    def __rowToHealRecord(cls, myDict: dict[Hashable, Any]):
        cls.recordQueue.push(
            cls.__toTimestamp(myDict["time"]),
            getattr(Fight.playerList[myDict["user"]], myDict["skillName"])(**myDict),
        )

    @staticmethod
    def __toTimestamp(rawTime: str) -> float:
        negative = False
        if rawTime[0] == "-":
            negative = True
            rawTime = rawTime[1:]
        m, s = rawTime.strip().split(":")
        ret = int(m) * 60 + float(s)
        return ret if not negative else -ret
