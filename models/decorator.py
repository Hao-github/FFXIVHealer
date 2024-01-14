import Fight
from models.record import Record


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
        if event.target == self:
            event.target = Fight.Fight.playerList.get(kwargs.get("target", None), self)
        return ret

    return wrapper
