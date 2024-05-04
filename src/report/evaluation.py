from ..models.player import Player
from ..models.Record import Record


class Evaluation:
    def __init__(self) -> None:
        self.gcd_cost: float = 0
        self.cooperation: int = 0
        self.tolerance: int = 0
        self.output = open("output.txt", "w", encoding="utf-8")

    def update(self, record: Record, time: float):
        user = record.eventList[0].user
        if time > 0 and record.costType:
            self.gcd_cost += (
                getattr(user, (record.costType + "_potency"), 0)
                * user.damage_per_potency
            )
        if not record.fromHot and user.name not in ["H1", "H2"]:
            self.cooperation += 1

    def warning_danger(self, player: Player, time: float):
        self.output.write(f"{player.name}可能会或已经在{round(time, 2)}死亡")
