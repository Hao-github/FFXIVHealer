import src.Fight as Fight
from ..Record import Record
from ..Status import EventType, Hot


def pet_skill(func):
    def wrapper(self, *args, **kwargs):
        ret: Record = func(self, *args, **kwargs)
        ret.eventList = [x.apply_buff(self.pet_coefficient) for x in ret.eventList]
        return ret

    return wrapper


def target_skill(func):
    def wrapper(self, *args, **kwargs):
        ret: Record = func(self, *args, **kwargs)
        event = ret.eventList[0]
        event.target = Fight.Fight.member.get(kwargs.get("target", None), self)
        return ret

    return wrapper


def ground_skill(func):
    def wrapper(self, *args, **kwargs):
        ret: Record = func(self, *args, **kwargs)
        for status in ret.eventList[0].status_list:
            if isinstance(status, Hot):
                status.isGround = True
        ret.eventList[0].eventType = EventType.GroundInit
        return ret

    return wrapper


def self_skill(func):
    def wrapper(self, *args, **kwargs):
        ret: Record = func(self, *args, **kwargs)
        for event in ret.eventList:
            event.target = self
        return ret

    return wrapper


def cost(costType: str):
    def costCal(func):
        def wrapper(self, *args, **kwargs):
            ret: Record = func(self, *args, **kwargs)
            ret.cost = getattr(self, costType + "_potency")
            return ret

        return wrapper

    return costCal
