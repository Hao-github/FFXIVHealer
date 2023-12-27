from copy import deepcopy
from functools import reduce
import pandas as pd
from models.player import Player, allPlayer
from models.event import Event, EventType
from models.record import RecordQueue, Record
from models.status import Dot


class Fight:
    playerList: dict[str, Player] = {}
    recordQueue: RecordQueue = RecordQueue()

    @classmethod
    def addPlayer(cls, name: str, player: Player) -> None:
        cls.playerList[name] = player

    @classmethod
    def addBossSkills(cls, fileName: str, boss: Player) -> None:
        def RowToRecord(row: pd.Series):
            record = Record(
                Event(
                    EventType.MagicDamage
                    if row["type"] == "magic"
                    else EventType.PhysicsDamage,
                    name=row["name"],
                    value=row["damage"],
                ),
                user=boss,
                target=allPlayer,
                delay=row["delay"],
            )
            if row["hasDot"]:
                record.event.append(
                    Dot(record.event.name, row["dotTime"], row["dotDamage"])
                )

            m, s = row["prepareTime"].strip().split(":")
            cls.recordQueue.push(int(m) * 60 + float(s), [record])
            return row["prepareTime"]

        pd.read_csv(fileName).apply(RowToRecord, axis=1)

    @classmethod
    def run(cls, step: float):
        if not cls.playerList or cls.recordQueue.empty():
            return
        time: float = 0
        while True:
            # 检查buff, 如果dot和hot跳了, 或者延迟治疗时间到了, 就产生立即的prepare事件
            cls.recordQueue.push(
                time,
                reduce(lambda x, y: x + y.update(step), cls.playerList.values(), []),
            )
            # 如果当前时间大于等于最近的事件的发生时间
            while time >= cls.recordQueue.nextRecordTime:
                for record in cls.recordQueue.pop():
                    if not record.event.prepared:
                        cls.recordQueue.push(
                            time + record.delay, cls.__forUnpreparedRecord(record)
                        )
                    else:
                        if a := record.target.dealWithReadyEvent(record.event):
                            cls.recordQueue.push(time, a)
                        cls.showInfo(record.event)

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
    def showInfo(cls, event: Event):
        if event.name == "naturalHeal":
            return
        print("After Event " + event.name)
        for player in cls.playerList.values():
            print("状态列表: [", end="")
            for status in player.statusList:
                if status.name != "naturalHeal" and status.remainTime > 0:
                    print(str(status) + ", ", end="")
            print("]")
            print(player.name + " : " + str(player.hp))
