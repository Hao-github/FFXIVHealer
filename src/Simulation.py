from functools import partial
import pandas as pd
from .utils import str_to_timestamp
from .report.Output import Output
from .report.Evaluation import Evaluation
from .models.player import allPlayer, Player
from .models.Event import Event
from .models.Record import RecordQueue, Record
from .models.Jobs.constant import STR2JOB_CLASSES


class Simulation:
    def __init__(self, player_df: pd.DataFrame) -> None:
        # 初始化成员（角色）字典
        self.member: dict[str, Player] = {
            row["name"]: STR2JOB_CLASSES[row["job"]](row["hp"], row["potency"])
            for _, row in player_df.iterrows()
        }
        # 初始化事件记录队列
        self.record_queue: RecordQueue = RecordQueue()
        # 初始化输出和评价
        self.output: Output = Output()
        self.evaluation: Evaluation = Evaluation()

    def add_raid_timeline(self, raid_df: pd.DataFrame):
        # 创建一个事件构建器
        create_event = partial(Event.from_row, user=Player("boss", 0, 0, 0, 0))
        # 遍历团队数据，添加团队时间轴
        for _, row in raid_df.iterrows():
            time = str_to_timestamp(row["prepare_time"])
            # 使用字典查找目标，如果找不到则默认为全体玩家
            target = self.member.get(row["target"], allPlayer)
            event = create_event(row, target=target)
            # 将事件推送到记录队列中
            self.record_queue.push(time, Record([event], delay=row["delay"]))
        return self

    def add_healing_timeline(self, healing_df: pd.DataFrame):
        # 遍历治疗数据
        for row in healing_df.to_dict("records"):
            time = str_to_timestamp(row["time"])
            # 根据用户和目标设置目标
            row["target"] = self.member[
                row["target"] if not pd.isna(row["target"]) else row["user"]
            ]
            # 获取用户的技能方法
            skill_method = getattr(self.member[row["user"]], row["skillName"])
            # 将事件推送到记录队列中
            self.record_queue.push(time, skill_method(**row))
        return self

    def run(self, step: float) -> tuple[Output, Evaluation]:
        """运行模拟器，返回输出和评价结果"""
        if not self.member or self.record_queue.empty():
            return self.output, self.evaluation

        # 初始化时间
        time: float = -3
        while True:
            # 更新成员状态
            self.__update_member_statuses(step, time)
            # 检查记录队列
            while time >= self.record_queue.next_record_time:
                record = self.record_queue.pop()
                if not record.prepared:
                    # 准备记录
                    self.record_queue.push(
                        time + record.delay, self.__prepare_record(record)
                    )
                else:
                    # 执行记录
                    self.__execute_record(record, time)
                    # 添加快照
                    self.output.add_snapshot(time, self.member, record.eventList[0])

                if self.record_queue.empty():
                    # 如果队列为空，返回输出和评价结果
                    return self.output, self.evaluation

            # 增加时间
            time += step

    def __update_member_statuses(self, step: float, time: float):
        """更新成员状态并返回所有状态产生的事件"""
        # 使用列表解析将所有成员的更新结果合并为事件列表
        updates: list[Event] = sum((m.update(step) for m in self.member.values()), [])
        if updates:
            # 如果有更新，则推送到记录队列中
            self.record_queue.push(time, Record(updates, fromHot=True))

    def __prepare_record(self, record: Record) -> Record:
        """准备记录，将事件列表更新"""
        record.prepared = True
        newEventList: list[Event] = []
        for event in record.eventList:
            # 处理用户事件
            event = event.user.as_event_user(event)
            if event.target != allPlayer:
                # 处理目标事件
                newEventList.append(event.target.as_event_target(event))
            else:
                # 处理所有玩家的目标事件
                for player in self.member.values():
                    newEventList.append(player.as_event_target(event.copy(player)))
        record.eventList = newEventList

        return record

    def __execute_record(self, record: Record, time: float) -> None:
        """执行记录"""
        self.evaluation.update(record, time)
        for event in record.eventList:
            # 处理准备好的事件
            ret = event.target.deal_with_ready_event(event)
            if ret is False:
                # 如果事件失败，则发出警告
                self.evaluation.warning_danger(event.target, time)
            elif ret is not True:
                # 如果有其他事件，则推送到记录队列
                self.record_queue.push(time, Record([ret]))
