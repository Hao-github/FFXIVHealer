from __future__ import annotations
import traceback

from .Record import Record
from .Event import Event
from .Status import (
    EventType,
    BaseStatus,
    HealBonus,
    Hot,
    IncreaseMaxHp,
    MagicMtg,
    PhysicMtg,
    MaxHpShield,
)
from .StatusList import StatusList


class Player:
    def __init__(
        self,
        name: str,
        hp: int,
        damage_per_potency: float,
        magic_defense: float,
        physic_defense: float,
        gcd_potency: int = 0,
    ) -> None:
        self.name: str = name
        self.max_hp: int = hp
        self.hp: int = hp
        base_status_list: list[BaseStatus] = [
            Hot("naturalHeal", 10000, hp / 100, get_snapshot=False, display=False),
            MagicMtg("magicDefense", 10000, magic_defense, display=False),
            PhysicMtg("physicDefense", 10000, physic_defense, display=False),
        ]
        self.status_list: StatusList = StatusList(base_status_list)

        self.damage_per_potency: float = damage_per_potency
        self.is_survival: bool = True
        self.gcd_potency: int = gcd_potency

    def as_event_user(self, event: Event) -> Event:
        """作为事件的使用者, 如果是治疗事件, 计算自身身上的威力"""
        match event.eventType:
            case EventType.Heal | EventType.GroundInit:
                return event.apply_buff(self.damage_per_potency)
            case _:
                return event

    def as_event_target(self, event: Event) -> Event:
        """作为事件的对象, 计算受疗或者减伤等"""
        match event.eventType:
            case EventType.GroundInit:
                event.value *= self.calPct(HealBonus)
            case EventType.MaxHpChange:
                self.__change_max_hp(-int(event.value))
            case EventType.Heal | EventType.GroundHeal:
                event.apply_buff(self.calPct(HealBonus))
            case EventType.MagicDmg:
                mtg_pct = self.calPct(MagicMtg)
                event.reduced_pct = mtg_pct
                event.apply_buff(mtg_pct)
                event = self.calculate_shield_reduced(event)
            case EventType.PhysicDmg:
                mtg_pct = self.calPct(PhysicMtg)
                event.reduced_pct = mtg_pct
                event.apply_buff(mtg_pct)
                event = self.calculate_shield_reduced(event)
            case EventType.TrueDamage:
                event = self.calculate_shield_reduced(event)
        return event

    def calculate_shield_reduced(self, event: Event) -> Event:
        origin_damage = int(event.value)
        for shield in self.status_list.shield_list:
            if shield.value > event.value:
                # Reduce shield value by damage and return 0 as no remaining damage
                shield.value -= event.value
                event.value = 0
                return event
            # Subtract shield value from damage and reset shield remain time
            event.value -= shield.value
            shield.remain_time = 0
        event.reduced_value = origin_damage - int(event.value)
        return event

    def deal_with_ready_event(self, event: Event) -> Event | bool:
        if not self.is_survival:
            return True
        for status in event.status_list:
            self.__get_status(status)
        # 对于治疗事件
        if event.eventType.value < 4:
            return self.__handle_healing_event(event)
        else:
            return self.__handle_damage_event(event)

    def __handle_healing_event(self, event: Event) -> bool:
        if event.name_is("Pepsis"):
            if self.remove_shield("EkurasianDignosis"):
                event.apply_buff(1.4)
            elif not self.remove_shield("EkurasianPrognosis"):
                event.apply_buff(0)
        self.hp = min(self.max_hp, self.hp + int(event.value))
        return True

    def __handle_damage_event(self, event: Event) -> bool:
        self.hp -= int(event.value)
        if self.hp > 0:
            return self.status_list.calHotTick() < self.hp
        self.is_survival = False
        return False

    def update(self, time_interval: float) -> list[Event]:
        """更新所有的status, 并返回所有status产生的event"""
        if not self.is_survival:
            return []
        return [
            Event.from_StatusRtn(x, self, self)
            for x in self.status_list.update(
                time_interval, hpPercentage=self.hp / self.max_hp, hp=self.hp
            )
        ]

    def calPct(self, myType: type) -> float:
        return self.status_list.calPct(myType)

    def has_status(self, name: str) -> BaseStatus | None:
        """检查自身有无对应的status"""
        return self.status_list.has_status(name)

    def remove_status(self, name: str) -> BaseStatus | None:
        return self.status_list.has_status(name, True)

    def remove_shield(self, name: str) -> BaseStatus | None:
        return self.status_list.has_status(name, True, True)

    def __str__(self) -> str:
        return (
            f"{self.name:<13}: {str(self.hp):>6}/{str(self.max_hp):<6},"
            f"statusList: [{str(self.status_list)}]\n"
        )

    def _buildRecord(
        self,
        value: float = 0,
        status: list[BaseStatus] | BaseStatus = [],
        delay: float = 0,
    ) -> Record:
        return Record([self._buildEvent(value=value, status=status)], delay)

    def _buildEvent(
        self,
        selfTarget: bool = False,
        value: float = 0,
        status: list[BaseStatus] | BaseStatus = [],
    ):
        return Event(
            EventType.Heal,
            traceback.extract_stack()[-3][2],
            self,
            self if selfTarget else allPlayer,
            value,
            status if isinstance(status, list) else [status],
        )

    def __change_max_hp(self, hp_change_num: int) -> None:
        self.max_hp += hp_change_num
        self.hp = min(
            self.hp + hp_change_num if hp_change_num > 0 else self.hp, self.max_hp
        )

    def __get_status(self, status: BaseStatus) -> None:
        """获取buff, 如果是基于自身最大生命值的盾, 则转化为对应数值"""

        # 对基于目标最大生命值百分比的盾而非自己的进行特殊处理
        if isinstance(status, MaxHpShield):
            status = status.to_shield(self.max_hp)
        elif isinstance(status, IncreaseMaxHp):
            status.increase_hp_num = int(self.max_hp * (status.value - 1))
            self.__change_max_hp(status.increase_hp_num)

        self.status_list.append(status)

    @property
    def job(self):
        return type(self).__name__

    @property
    def remaining_status(self) -> dict[str, float]:
        return self.status_list.get_remaining_times()


allPlayer = Player("totalPlayer", 0, 0, 0, 0)
