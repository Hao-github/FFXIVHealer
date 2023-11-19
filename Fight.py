from player import Player
from basic import Hot, Dot, Mitigation, Event, EventType


class Fight:
    ## 以仇恨值排序
    playerList: list[Player] = []
    # 事件, 数值, 时间
    eventList: list[tuple[float, Event]] = []
    timeInterval: float = 0.01

    @classmethod
    def addPlayer(cls, playerName: str, playerHp: int) -> None:
        player = Player(playerName, playerHp)
        player.getEffect(Hot("naturalHeal", float("inf"), playerHp // 100))
        cls.playerList.append(player)

    @classmethod
    def addHealEvent(cls, time: float, value: int, hot: Hot | None = None) -> None:
        cls.eventList.append((time, Event(EventType.Heal, value=value, effectList=hot)))

    @classmethod
    def addDamageEvent(cls, time: float, value: int, dot: Dot | None = None) -> None:
        cls.eventList.append(
            (time, Event(EventType.MagicDamage, value=value, effectList=dot))
        )

    @classmethod
    def addShieldEvent(cls, time: float, value: int) -> None:
        cls.eventList.append((time, Event(EventType.Shield, value=value)))

    @classmethod
    def addMitigationEvent(cls, time: float, percentage: float, duration: int) -> None:
        cls.eventList.append(
            (
                time,
                Event(
                    EventType.Mitigation,
                    effectList=[Mitigation("test", duration, percentage)],
                ),
            )
        )

    @classmethod
    def addEvent(cls, time: float, event: Event) -> None:
        cls.eventList.append((time, event))

    @classmethod
    def updatePlayerstatus(
        cls, timeInterval: float, event: Event | None = None
    ) -> bool:
        for player in cls.playerList:
            if event:
                match event.eventType:
                    case EventType.Heal:
                        player.getHeal(event.value)
                    case EventType.MagicDamage:
                        player.getDamage(event.value)
                    case EventType.Shield:
                        player.getShield(event.value)
                        # comment:
                if event.effectList:
                    for effect in event.effectList:
                        player.getEffect(effect)
            player.update(timeInterval)

    @classmethod
    def run(cls) -> True:
        if not cls.playerList or not cls.eventList:
            return False
        cls.eventList.sort(key = lambda x: x[0])
        eventIndex: int = 0
        nextEvent: tuple[float, Event] = cls.eventList[eventIndex]
        timeSnapshotList = [
            i * cls.timeInterval
            for i in range(
                0, int((cls.eventList[-1][0] + cls.timeInterval) // cls.timeInterval) + 10
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
                print(nextEvent)

    @classmethod
    def showPlayerHp(cls):
        for player in cls.playerList:
            print(player.name + " : " + str(player.hp))
