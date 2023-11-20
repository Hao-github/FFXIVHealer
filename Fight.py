import pandas as pd
from Jobs.Healer import Scholar, WhiteMage
from models.player import Player
from models.effect import DataType
from models.event import Event, EventType

from copy import deepcopy


class Fight:
    playerList: list[Player] = []

    # 事件, 数值, 时间
    eventList: list[tuple[float, Event]] = []
    eventIndex = 0
    timeInterval: float = 0.01
    eventToEffectDict = {
        EventType.PhysicsDamage: DataType.Physics,
        EventType.MagicDamage: DataType.Magic,
        EventType.TrueDamage: DataType.Real,
        EventType.Heal: DataType.Magic,
        EventType.Other: DataType.Magic,
    }

    @classmethod
    def addPlayer(cls, player: Player) -> None:
        cls.playerList.append(player)

    @classmethod
    def addEvent(cls, time: float, event: Event) -> None:
        cls.eventList.append((time, event))

    @classmethod
    def dealWithEvent(cls, event: Event):
        # print(type(event.user))
        if type(event.user) == Scholar or type(event.user) == WhiteMage:
            event = event.user.updateEvent(event)
            # print(event)
        for player in cls.playerList:
            if not event.target or event.target == player:
                dataType = cls.eventToEffectDict[event.eventType]
                if event.eventType == EventType.Heal:
                    player.getHeal(event.value)
                elif event.eventType != EventType.Other:
                    player.getDamage(event.value, dataType)
                for effect in event.effectList:
                    player.getEffect(deepcopy(effect), dataType)

    @classmethod
    def run(cls):
        if not cls.playerList or not cls.eventList:
            return
        # resultDf: pd.DataFrame = pd.DataFrame(columns=["事件","角色"])
        cls.eventList.sort(key=lambda x: x[0])
        nextEvent: tuple[float, Event] = cls.eventList[cls.eventIndex]
        timeSnapshotList = [
            i * cls.timeInterval
            for i in range(
                0,
                int((cls.eventList[-1][0] + cls.timeInterval) // cls.timeInterval) + 10,
            )
        ]
        for timeSnapshot in timeSnapshotList:
            while timeSnapshot == nextEvent[0]:
                cls.dealWithEvent(nextEvent[1])
                # print("After Event " + nextEvent[1].name)
                cls.showPlayerHp()
                cls.eventIndex += 1
                if len(cls.eventList) == cls.eventIndex:  # 所有事件都处理完了
                    break
                nextEvent = cls.eventList[cls.eventIndex]

            for player in cls.playerList:
                player.update(cls.timeInterval)

    @classmethod
    def showPlayerHp(cls):
        for player in cls.playerList:
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
