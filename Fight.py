from copy import deepcopy
from functools import reduce
import pandas as pd
from models.player import Player, allPlayer
from models.event import Event
from models.record import RecordQueue, Record
from models.status import Dot
from Settings.jobToClass import jobToClass


class Fight:
    playerList: dict[str, Player] = {}
    recordQueue: RecordQueue = RecordQueue()

    @classmethod
    def addbaseCofig(cls, bossFile: str, playerFile: str) -> None:
        pd.read_csv(bossFile).apply(cls.__rowToRecord, axis=1)
        pd.read_csv(playerFile).apply(cls.__rowToPlayer, axis=1)

    @classmethod
    def run(cls, step: float):
        if not cls.playerList or cls.recordQueue.empty():
            return
        time: float = 0
        while True:
            # 检查buff, 如果dot和hot跳了, 或者延迟治疗时间到了, 就产生立即的prepare事件
            if dotAndHotList := reduce(
                lambda x, y: x + y.update(step), cls.playerList.values(), []
            ):
                cls.recordQueue.push(time, dotAndHotList)
            # 如果当前时间大于等于最近的事件的发生时间
            while time >= cls.recordQueue.nextRecordTime:
                nextRecordList = cls.recordQueue.pop()
                for record in nextRecordList[2]:
                    if not record.event.prepared:
                        cls.recordQueue.push(
                            time + record.delay, cls.__forUnpreparedRecord(record)
                        )
                    else:
                        if a := record.target.dealWithReadyEvent(record.event):
                            cls.recordQueue.push(time, a)
                        cls.showInfo(nextRecordList[0], record.event)

                if cls.recordQueue.empty():
                    return

            time += step

    @classmethod
    def __forUnpreparedRecord(cls, record: Record) -> list[Record]:
        record.event.prepared = True
        record.event, record.target = record.user.asEventUser(
            record.event, record.target
        )
        # 如果目标不是全体成员
        if record.target != allPlayer:
            record.event = record.target.asEventTarget(record.event)
            return [record]

        return list(
            map(
                lambda x: Record(
                    x.asEventTarget(deepcopy(record.event)), record.user, x
                ),
                cls.playerList.values(),
            )
        )

    @classmethod
    def showInfo(cls, time: float, event: Event):
        if event.name == "naturalHeal":
            return
        print("After Event {0} At {1}".format(event.name, time))
        for name, player in cls.playerList.items():
            print(
                "{0}{1:<13}: {2:>6}, statusList: [{3}]".format(
                    name,
                    "(" + player.name + ")",
                    str(player.hp),
                    reduce(
                        lambda x, y: x
                        + (
                            str(y) + ", "
                            if y.name
                            not in ["naturalHeal", "magicDefense", "physicsDefense"]
                            and y.remainTime > 0
                            else ""
                        ),
                        player.statusList,
                        "",
                    ),
                ),
            )

    @classmethod
    def __rowToPlayer(cls, row: pd.Series):
        jobName = row["job"]
        className = jobToClass[jobName]
        jobClass = getattr(__import__("Jobs." + className), jobName)
        cls.playerList[row["name"]] = jobClass(row["hp"], row["potency"])
        return jobName

    @classmethod
    def __rowToRecord(cls, row: pd.Series):
        boss = Player("boss", 0, 0, 0, 0)
        record = Record(
            Event.fromRow(row),
            user=boss,
            target=allPlayer
            if row["target"] == "all"
            else cls.playerList[row["target"]],
            delay=row["delay"],
        )
        if row["hasDot"]:
            record.event.append(Dot(row["name"], row["dotTime"], row["dotDamage"]))

        m, s = row["prepareTime"].strip().split(":")
        cls.recordQueue.push(int(m) * 60 + float(s), [record])
        return row["prepareTime"]
