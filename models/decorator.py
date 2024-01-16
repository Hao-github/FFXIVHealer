import Fight
from models.record import Record
from models.status import Hot


def petSkill(func):
    def wrapper(self, *args, **kwargs):
        ret: Record = func(self, *args, **kwargs)
        ret.eventList = list(
            map(lambda x: x.getBuff(self.petCoefficient), ret.eventList)
        )
        return ret

    return wrapper


def targetSkill(func):
    def wrapper(self, *args, **kwargs):
        ret: Record = func(self, *args, **kwargs)
        event = ret.eventList[0]
        event.target = Fight.Fight.playerList.get(kwargs.get("target", None), self)
        return ret

    return wrapper

def groundSkill(func):
    def wrapper(self, *args, **kwargs):
        ret: Record = func(self, *args, **kwargs)
        for status in ret.eventList[0].statusList:
            if isinstance(status, Hot):
                status.getSnapshot = False
        return ret

    return wrapper
