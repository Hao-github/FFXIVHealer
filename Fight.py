from copy import deepcopy
import pandas as pd
from models.player import Player, allPlayer
from models.event import Event, EventType
from models.record import Record, RecordQueue
from models.status import Dot


class Fight:
    playerList: dict[str, Player] = {}
    recordQueue: RecordQueue = RecordQueue(0.01)
    step: float = 0.01

    @classmethod
    def addPlayer(cls, name: str, player: Player) -> None:
        cls.playerList[name] = player

    @classmethod
    def addRecord(cls, time: float, record: Record) -> None:
        cls.recordQueue.putRecord(time, record)

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
            cls.addRecord(int(m) * 60 + float(s), record)
            return row["prepareTime"]
        pd.read_csv(fileName).apply(RowToRecord, axis=1)

    @classmethod
    def setTimeInterval(cls, timeInterval: float) -> None:
        cls.step = timeInterval

    @classmethod
    def run(cls):
        if not cls.playerList:
            return
        # resultDf: pd.DataFrame = pd.DataFrame(columns=["事件","角色"])
        time: float = -cls.step
        while True:
            # 如果已经没有记录要发生了
            if cls.recordQueue.empty():
                return
            time += cls.step
            # 检查buff, 如果dot和hot跳了, 或者延迟治疗时间到了, 就产生立即的prepare事件
            for player in cls.playerList.values():
                cls.recordQueue.putEvent(time, player.update(cls.step), player, player)
            # 从队列中抽取这一刻发生的事件
            while cls.recordQueue.happen(time):
                record = cls.recordQueue.get()
                if not record:
                    return
                # 对于已经prepare的事件直接找target判定
                if record.event.prepared:
                    if a := record.target.dealWithReadyEvent(record.event):
                        cls.recordQueue.putRecord(time, a)
                    cls.showInfo(record.event)
                    continue
                # 否则经过生效延迟后重新丢入队列
                record.event.prepared = True
                cls.recordQueue.putRecord(
                    time + record.delay, cls.__forUnpreparedRecord(record)
                )

    @classmethod
    def __forUnpreparedRecord(cls, record: Record) -> Record | list[Record]:
        record.event.prepared = True
        record.event, record.target = record.user.asEventUser(
            record.event, record.target
        )
        # 如果目标不是全体成员
        if record.target != allPlayer:
            record.event, record.user = record.target.asEventTarget(
                record.event, record.user
            )
            return record

        ret: list[Record] = []
        for player in cls.playerList.values():
            tmp = player.asEventTarget(deepcopy(record.event), record.user)
            ret.append(Record(tmp[0], tmp[1], player))
        return ret

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

    @classmethod
    def importScholarSkills(cls, df: pd.DataFrame):
        healingSkillList = [  # noqa: F841
            "仙光的低语",
            "转化",
            "野战治疗阵",
            "不屈不挠之策",
            "士气高扬之策",
            "秘策",
            "慰藉",
            "异想的幻光",
            "疾风怒涛之策",
            "异想的祥光",
        ]
        return (
            df.drop(columns=["Unnamed: 4"], axis=1)
            .assign(技能=lambda x: x["技能"].apply(lambda x: x.split(" ")[0]))
            .query("技能 in @healingSkillList")[["时间", "技能"]]
            .reset_index(drop=True)
        )
