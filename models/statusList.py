from functools import reduce
from models.status import BaseStatus, Hot, Shield, StatusRtn
from itertools import chain


class StatusList:
    conflict = ["Galvanize", "EkurasianPrognosis", "EkurasianDignosis"]

    def __init__(self, initial: list[BaseStatus]) -> None:
        self.other_status: list[BaseStatus] = initial
        self.shield_list: list[Shield] = []

    def append(self, status: BaseStatus) -> None:
        if isinstance(status, Shield):
            existing_status = self.has_status(status.name, isShield=True)
            if existing_status:
                if status > existing_status:
                    existing_status = status
                return
            if status.name in self.conflict:
                if status.name != self.conflict[0]:
                    self.has_status(self.conflict[0], True)
                if status.name != self.conflict[1]:
                    self.has_status(self.conflict[1], True)
                if status.name != self.conflict[2] and self.has_status(
                    self.conflict[2]
                ):
                    return
            self.shield_list.append(status)
        else:
            existing_status = self.has_status(status.name)
            if existing_status:
                existing_status = status
            else:
                self.other_status.append(status)

    def has_status(
        self, name: str, remove: bool = False, isShield: bool = False
    ) -> BaseStatus | None:
        """检查自身有无对应的status"""
        # 根据 isShield 决定要搜索的状态列表
        status_list = self.shield_list if isShield else self.other_status

        matched_status = next((s for s in status_list if s.name == name), None)
        # 如果找到匹配的状态且需要移除
        if matched_status and remove:
            status_list.remove(matched_status)  # type: ignore

        return matched_status

    def calHotTick(self) -> float:
        return sum(y.value for y in self.other_status if isinstance(y, Hot))

    def update(self, time_interval: float, **kwargs) -> list[StatusRtn]:
        """更新所有的status, 如果status, 并返回所有status产生的event"""
        ret: list[StatusRtn] = []

        for status in chain(self.other_status, self.shield_list):
            if status_update := status.update(time_interval, **kwargs):
                ret.append(status_update)

        # 删除到时的buff
        self.other_status = [s for s in self.other_status if s.remain_time > 0]
        self.shield_list = [s for s in self.shield_list if s.remain_time > 0]
        return ret

    def calPct(self, myType: type) -> float:
        filtered_status = (s.value for s in self.other_status if isinstance(s, myType))
        return reduce(lambda x, y: x * y, filtered_status, 1)

    def __str__(self) -> str:
        other_status_str = ",".join(str(i) for i in self.other_status if i.display)
        shield_list_str = ",".join(str(i) for i in self.shield_list)
        return f"{other_status_str},{shield_list_str}"

    def get_remaining_times(self) -> dict[str, float]:
        """返回一个字典，其中键为所有状态的名称，值为它们的剩余时间"""
        return {
            status.name: status.remain_time
            for status in chain(self.other_status, self.shield_list)
            if status.display
        }
