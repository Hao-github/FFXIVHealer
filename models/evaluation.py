from models.record import Record


class Evaluation:
    gcdCost: float = 0
    cooperation: int = 0
    tolerance: int = 0

    @classmethod
    def update(cls, record: Record):
        user = record.eventList[0].user
        cls.gcdCost += record.cost * user.gcdPotency
        if not record.fromHot and user.name not in ["h1", "h2"]:
            cls.cooperation += 1
        
