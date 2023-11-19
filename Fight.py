import pandas as pd
from models.player import Player
from models.effect import Dot, Hot, Mitigation
from models.event import Event, EventType

# from basic import Dot, Hot, Mitigation, Event, EventType
from copy import deepcopy


class Fight:
    ## 以仇恨值排序
    playerList: list[Player] = []

    # 事件, 数值, 时间
    eventList: list[tuple[float, Event]] = []
    timeInterval: float = 0.01

    @classmethod
    def addPlayer(cls, playerName: str, playerHp: int, potency: float = 25) -> None:
        player = Player(playerName, playerHp, potency)
        player.getEffect(Hot("naturalHeal", 10000, playerHp // 100))
        cls.playerList.append(player)

    @classmethod
    def addDamageEvent(
        cls, time: float, name: str, value: int, dot: Dot | None = None
    ) -> None:
        cls.eventList.append((time, Event(EventType.MagicDamage, name, value=value)))

    @classmethod
    def addMitigationEvent(
        cls, time: float, name: str, percentage: float, duration: int
    ) -> None:
        cls.eventList.append(
            (
                time,
                Event(
                    EventType.Mitigation,
                    name,
                    effectList=[Mitigation(name, duration, percentage)],
                ),
            )
        )

    @classmethod
    def addEvent(cls, time: float, event: Event) -> None:
        cls.eventList.append((time, event))

    @classmethod
    def updatePlayerstatus(cls, timeInterval: float, event: Event | None = None):
        for player in cls.playerList:
            if event and (not event.target or event.target == player):
                match event.eventType:
                    case EventType.Heal:
                        player.getHeal(event.value)
                    case EventType.MagicDamage:
                        player.getDamage(event.value)

                if event.effectList:
                    if isinstance(event.effectList, list):
                        for effect in event.effectList:
                            player.getEffect(deepcopy(effect))
                    else:
                        player.getEffect(deepcopy(event.effectList))
            player.update(timeInterval)

    @classmethod
    def run(cls):
        if not cls.playerList or not cls.eventList:
            return False
        cls.eventList.sort(key=lambda x: x[0])
        eventIndex: int = 0
        nextEvent: tuple[float, Event] = cls.eventList[eventIndex]
        timeSnapshotList = [
            i * cls.timeInterval
            for i in range(
                0,
                int((cls.eventList[-1][0] + cls.timeInterval) // cls.timeInterval) + 10,
            )
        ]
        for timeSnapshot in timeSnapshotList:
            if timeSnapshot != nextEvent[0]:
                cls.updatePlayerstatus(cls.timeInterval)
            else:
                cls.updatePlayerstatus(cls.timeInterval, nextEvent[1])
                eventIndex += 1
                if len(cls.eventList) == eventIndex:
                    break
                nextEvent = cls.eventList[eventIndex]

    @classmethod
    def showPlayerHp(cls):
        for player in cls.playerList:
            print(player.name + " : " + str(player.hp))

    @classmethod
    def importScholarSkills(cls, df: pd.DataFrame):
        healingSkillList = [
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
            .head(40)
        )
