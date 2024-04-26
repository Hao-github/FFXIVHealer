from functools import reduce
from models.status import BaseStatus, Hot, Shield, StatusRtn


class StatusList:
    conflict = ["Galvanize", "EkurasianPrognosis", "EkurasianDignosis"]

    def __init__(self, initial: list[BaseStatus]) -> None:
        self.otherStatus: list[BaseStatus] = initial
        self.sheildList: list[Shield] = []

    def append(self, status: BaseStatus) -> None:
        if isinstance(status, Shield):
            for s in self.sheildList:
                if s == status:
                    s = status if status > s else s
                    return
            if status.name not in self.conflict:
                self.sheildList.append(status)
            if status.name != self.conflict[0]:
                self.searchStatus(self.conflict[0], True)
            if status.name != self.conflict[1]:
                self.searchStatus(self.conflict[1], True)
            if status.name != self.conflict[2] and self.searchStatus(self.conflict[2]):
                return
            self.sheildList.append(status)
        else:
            for s in self.otherStatus:
                if s == status:
                    s = status
            self.otherStatus.append(status)

    def searchStatus(
        self, name: str, remove: bool = False, isShield: bool = False
    ) -> BaseStatus | None:
        """检查自身有无对应的status"""
        myList = self.otherStatus if not isShield else self.sheildList
        for status in myList:
            if status.name == name:
                if remove:
                    myList.remove(status)  # type: ignore
                return status
        return None

    def calHotTick(self) -> float:
        return reduce(
            lambda x, y: x + (y.value if isinstance(y, Hot) else 0), self.otherStatus, 0
        )

    def update(self, timeInterval: float, **kwargs) -> list[StatusRtn]:
        """更新所有的status, 如果status, 并返回所有status产生的event"""
        ret: list[StatusRtn] = []
        for status in self.otherStatus:
            if s := status.update(timeInterval, **kwargs):
                ret.append(s)

        # 删除到时的buff
        self.otherStatus = list(filter(lambda x: x.remainTime > 0, self.otherStatus))
        self.sheildList = list(filter(lambda x: x.remainTime > 0, self.sheildList))
        return ret

    def calPct(self, myType: type) -> float:
        return reduce(
            lambda x, y: x * (y.value if isinstance(y, myType) else 1),
            self.otherStatus,
            1,
        )

    def __str__(self) -> str:
        return ",".join(str(i) for i in self.otherStatus if i.display) + ",".join(
            str(i) for i in self.sheildList
        )
