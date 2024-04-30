import pandas as pd
import re
from .report.Evaluation import Evaluation
from .models.player import allPlayer, Player
from .models.Event import Event
from .models.Record import RecordQueue, Record
from .report.Output import Output
from .models.Jobs.constant import JOB_CLASSES


class Simulation:
    def __init__(self, player_df: pd.DataFrame) -> None:
        self.member: dict[str, Player] = {}
        self.record_queue: RecordQueue = RecordQueue()
        for _, row in player_df.iterrows():
            self.member[row["name"]] = JOB_CLASSES[row["job"]](
                row["hp"], row["damagePerPotency"]
            )

    def add_raid_timeline(self, raid_df: pd.DataFrame):
        boss: Player = Player("boss", 0, 0, 0, 0)
        for _, row in raid_df.iterrows():
            target: str = row["target"]
            time = self.__to_timestamp(row["prepareTime"])
            event = Event.from_row(
                row, boss, allPlayer if target == "all" else self.member[target]
            )
            self.record_queue.push(time, Record([event], delay=row["delay"]))

    def add_healing_timeline(self, healing_df: pd.DataFrame):
        for row in healing_df.to_dict("records"):
            time = self.__to_timestamp(row["time"])
            row["target"] = self.member[
                row["target"] if not pd.isna(row["target"]) else row["user"]
            ]
            self.record_queue.push(
                time, getattr(self.member[row["user"]], row["skillName"])(**row)
            )

    def run(self, step: float):
        if not self.member or self.record_queue.empty():
            return

        time: float = -3
        while True:
            # 检查buff, 如果dot和hot跳了, 或者延迟治疗时间到了, 就产生立即的prepare事件
            self.__update_member_statuses(step, time)
            # 如果当前时间大于等于最近的事件的发生时间
            while time >= self.record_queue.next_record_time:
                record = self.record_queue.pop()
                if not record.prepared:
                    self.record_queue.push(
                        time + record.delay, self.__for_unprepared_record(record)
                    )
                else:
                    Evaluation.update(record)
                    self.__for_prepared_record(record, time)
                    Output.add_snapshot(time, self.member, record.eventList[0])

                if self.record_queue.empty():
                    return

            time += step

    def __update_member_statuses(self, step: float, time: float):
        updates: list[Event] = sum((m.update(step) for m in self.member.values()), [])
        if updates:
            self.record_queue.push(time, Record(updates, fromHot=True))

    def __for_unprepared_record(self, record: Record) -> Record:
        record.prepared = True
        newEventList: list[Event] = []
        for event in record.eventList:
            event = event.user.as_event_user(event)
            if event.target != allPlayer:
                newEventList.append(event.target.as_event_target(event))
            else:
                for player in self.member.values():
                    newEventList.append(player.as_event_target(event.copy(player)))
        record.eventList = newEventList

        return record

    def __for_prepared_record(self, record: Record, time: float) -> None:
        for event in record.eventList:
            ret = event.target.deal_with_ready_event(event)
            if ret is False:
                Output.info(f"{event.target}可能会或已经在{round(time, 2)}死亡")
            elif ret is not True:
                self.record_queue.push(time, Record([ret]))

    @staticmethod
    def __to_timestamp(raw_time: str) -> float:
        # 使用正则表达式匹配时间格式
        match = re.match(r"(-?)(\d+):(\d+(?:\.\d+)?)", raw_time.strip())
        if not match:
            raise ValueError(f"Invalid time format: {raw_time}")
        negative, minutes, seconds = match.groups()
        total_seconds = int(minutes) * 60 + float(seconds)

        return -total_seconds if negative else total_seconds
