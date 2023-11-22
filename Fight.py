from copy import deepcopy
import pandas as pd
from models.player import Player
from models.event import Event
from models.record import RecordQueue


class Fight:
    playerList: list[Player] = []
    recordqueue: RecordQueue = RecordQueue(0.01)
    timeInterval: float = 0.01

    @classmethod
    def addPlayer(cls, player: Player) -> None:
        cls.playerList.append(player)

    @classmethod
    def addRecord(
        cls,
        time: float,
        event: Event | list[Event],
        user: Player,
        target: Player | None = None,
    ) -> None:
        if target:
            cls.recordqueue.put(time, event, user, target)
            return
        for player in cls.playerList:
            cls.recordqueue.put(time, deepcopy(event), user, player)

    @classmethod
    def run(cls):
        if not cls.playerList:
            return
        # resultDf: pd.DataFrame = pd.DataFrame(columns=["事件","角色"])
        time: float = 0
        while True:
            # 如果已经没有记录要发生了
            if cls.recordqueue.empty():
                return
            # 检查dot和hot判定, 如果dot和hot跳了, 就产生一个没有延迟的prepare事件
            for player in cls.playerList:
                cls.recordqueue.put(
                    time, player.update(cls.timeInterval), player, player
                )
            while cls.recordqueue.happen(time):
                record = cls.recordqueue.get()
                if not record:
                    return
                # 对于prepare事件
                if not record.event.hasPrepared:
                    event = record.user.asEventUser(record.event, record.target)
                    event = record.target.asEventTarget(event, record.user)
                    # 经过生效延迟后重新丢入队列
                    event.hasPrepared = True
                    cls.recordqueue.put(
                        time + cls.timeInterval, event, record.user, record.target
                    )
                # 否则直接找target来判定事件
                else:
                    record.target.dealWithReadyEvent(record.event)

            time += cls.timeInterval

    @classmethod
    def showInfo(cls, event: Event):
        print("After Event " + event.name)
        for player in cls.playerList:
            print("状态列表: [", end="")
            for effect in player.effectList:
                if effect.name != "naturalHeal" and effect.remainTime > 0:
                    print(str(effect) + ", ", end="")
            print("]")
            print(player.name + " : " + str(player.hp))
            print("\n")

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
