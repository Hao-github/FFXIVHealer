from playerPart import Hot, Player, Dot, Effect, Mitigation
from enum import Enum


class EventType(Enum):
    Nothing = 0
    Heal = 1
    Mitigation = 2
    Shield = 3
    PhysicsDamage = 4
    MagicDamage = 5


class Event:
    def __init__(
        self, eventType: EventType, value: int, eventTime: float, effect: Effect | None
    ) -> None:
        self.eventType: EventType = eventType
        self.value: int = value
        self.eventTime: float = eventTime
        self.effect: Effect = effect


class Fight:
    ## 以仇恨值排序
    playerList: list[Player] = []
    # 事件, 数值, 时间
    eventList: list[Event] = []
    timeInterval: float = 0.01

    @classmethod
    def addPlayer(cls, playerName: str, playerHp: int) -> None:
        player = Player(playerName, playerHp)
        player.getEffect(Hot("naturalHeal", float("inf"), playerHp // 100))
        cls.playerList.append(player)

    @classmethod
    def addHealEvent(cls, time: float, value: int, hot: Hot | None = None) -> None:
        cls.eventList.append(Event(EventType.Heal, value, time, hot))

    @classmethod
    def addDamageEvent(cls, time: float, value: int, dot: Dot | None = None) -> None:
        cls.eventList.append(Event(EventType.MagicDamage, value, time, dot))

    @classmethod
    def addShieldEvent(cls, time: float, value: int) -> None:
        cls.eventList.append(Event(EventType.Shield, value, time, None))

    @classmethod
    def addMitigationEvent(cls, time: float, percentage: float, duration: int) -> None:
        cls.eventList.append(
            Event(
                EventType.Mitigation, 0, time, Mitigation("test", duration, percentage)
            )
        )

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
                if event.effect:
                    player.getEffect(event.effect)
            player.update(timeInterval)

    @classmethod
    def run(cls) -> True:
        if not cls.playerList or not cls.eventList:
            return False
        cls.eventList.sort(key=lambda x: x.eventTime)
        endTime: float = cls.eventList[-1].eventTime + cls.timeInterval
        eventIndex: int = 0
        nextEvent: Event = cls.eventList[eventIndex]
        for timeSnapshot in range(0, endTime, cls.timeInterval):
            if timeSnapshot != nextEvent.eventTime:
                cls.updatePlayerstatus(cls.timeInterval)
            else:
                cls.updatePlayerstatus(cls.timeInterval, nextEvent)
                eventIndex += 1
                if len(cls.eventList) == eventIndex:
                    break
                nextEvent = cls.eventList[eventIndex]
        pass
