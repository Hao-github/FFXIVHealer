import pandas as pd
import re
from .report.evaluation import Evaluation
from .models.player import allPlayer, Player
from .models.Event import Event
from .models.Record import RecordQueue, Record
from .report.Output import Output
from .models.Jobs import * # noqa: F403


class Fight:
    member: dict[str, Player] = {}
    record_queue: RecordQueue = RecordQueue()

    @classmethod
    def addbaseCofig(cls, excel_file: str) -> None:
        dfDict = pd.read_excel(excel_file, sheet_name=None)
        dfDict["小队列表"].apply(cls.__row_to_player, axis=1)
        dfDict["BOSS时间轴"].apply(cls.__row_to_boss_record, axis=1)
        for r in dfDict["奶轴"].merge(dfDict["技能"], on="name").to_dict("records"):
            cls.record_queue.push(
                cls.__to_timestamp(r["time"]),
                getattr(Fight.member[r["user"]], r["skillName"])(**r),
            )

    @classmethod
    def run(cls, step: float):
        if not cls.member or cls.record_queue.empty():
            return

        time: float = -3
        while True:
            # 检查buff, 如果dot和hot跳了, 或者延迟治疗时间到了, 就产生立即的prepare事件
            cls.__update_member_statuses(step, time)
            # 如果当前时间大于等于最近的事件的发生时间
            while time >= cls.record_queue.next_record_time:
                record = cls.record_queue.pop()
                if not record.prepared:
                    cls.record_queue.push(
                        time + record.delay, cls.__for_unprepared_record(record)
                    )
                else:
                    Evaluation.update(record)
                    cls.__for_prepared_record(record, time)
                    Output.add_snapshot(time, cls.member, record.eventList[0])

                if cls.record_queue.empty():
                    Output.show_line()
                    return

            time += step

    @classmethod
    def __update_member_statuses(cls, step: float, time: float):
        updates: list[Event] = sum((m.update(step) for m in cls.member.values()), [])
        if updates:
            cls.record_queue.push(time, Record(updates, fromHot=True))

    @classmethod
    def __for_unprepared_record(cls, record: Record) -> Record:
        record.prepared = True
        newEventList: list[Event] = []
        for event in record.eventList:
            event = event.user.as_event_user(event)
            if event.target != allPlayer:
                newEventList.append(event.target.as_event_target(event))
            else:
                for player in cls.member.values():
                    newEventList.append(player.as_event_target(event.copy(player)))
        record.eventList = newEventList

        return record

    @classmethod
    def __for_prepared_record(cls, record: Record, time: float) -> None:
        for event in record.eventList:
            ret = event.target.deal_with_ready_event(event)
            if ret is False:
                Output.info(f"{event.target}可能会或已经在{round(time, 2)}死亡")
            elif ret is not True:
                cls.record_queue.push(time, Record([ret]))

    @classmethod
    def __row_to_player(cls, row: pd.Series):
        cls.member[row["name"]] = eval(row["job"])(row["hp"], row["damagePerPotency"])
        return 0

    @classmethod
    def __row_to_boss_record(cls, row: pd.Series):
        event = Event.fromRow(
            row,
            Player("boss", 0, 0, 0, 0),
            allPlayer if row["target"] == "all" else cls.member[row["target"]],
        )
        cls.record_queue.push(
            cls.__to_timestamp(row["prepareTime"]), Record([event], delay=row["delay"])
        )
        return 0

    @staticmethod
    def __to_timestamp(raw_time: str) -> float:
        # 使用正则表达式匹配时间格式
        match = re.match(r"(-?)(\d+):(\d+(?:\.\d+)?)", raw_time.strip())
        if not match:
            raise ValueError(f"Invalid time format: {raw_time}")
        negative, minutes, seconds = match.groups()
        total_seconds = int(minutes) * 60 + float(seconds)

        return -total_seconds if negative else total_seconds
