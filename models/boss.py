import pandas as pd
from models.status import Dot
from models.event import Event, EventType
from models.record import Record
from models.player import Player, allPlayer


class Boss(Player):
    def __init__(self, name: str) -> None:
        super().__init__(name, 0, 0, 0, 0)

    def createDamage(
        self,
        name: str,
        damage: int,
        eventType: EventType = EventType.MagicDamage,
        dot: Dot | None = None,
        target: Player = allPlayer,
    ) -> Record:
        ret = Event(eventType, name, value=damage)
        if dot:
            ret.append(dot)
        return Record(ret, self, target)

    def RowToRecord(self, row: pd.Series):
        record = Record(
            Event(
                EventType.MagicDamage
                if row["type"] == "magic"
                else EventType.PhysicsDamage,
                name=row["name"],
                value=row["damage"],
            ),
            user=self,
            target=allPlayer,
            delay=row["delay"],
        )
        if row["hasDot"]:
            record.event.append(Dot(record.event.name, row["dotTime"], row["dotDamage"]))
        return record
    
    def fileToRecordList(self, fileName: str) -> list[Record]:
        df: pd.DataFrame = pd.read_csv(fileName)
        return list(df.apply(self.RowToRecord)) # type: ignore