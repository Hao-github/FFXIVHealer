from models.effect import HealBonus, Hot, MagicMitigation, Mitigation
from models.player import Player
from models.event import Event, EventType


class MagicDPS(Player):
    def __init__(self, name: str, hp: int, potency: float) -> None:
        super().__init__(name, hp, potency)

    def Addle(self) -> Event:
        return Event(EventType.Other, "Addle", effect=Mitigation("Addle", 10, 0.1))


class RedMage(MagicDPS):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("RedMage", hp, potency)

    def MagickBarrier(self) -> Event:
        return Event(
            EventType.Other,
            "MagickBarrier",
            effect=[
                MagicMitigation("MagickBarrierMMtg", 10, 0.1),
                HealBonus("MagickBarrierHB", 10, 0.05),
            ],
        )

    def Vercure(self, target: Player | None = None) -> Event:
        if not target:
            target = self
        return Event(
            EventType.Heal, "Vercure", value=int(500 * self.potency), target=target
        )


class Summoner(Player):
    def __init__(self, hp: int, potency: float) -> None:
        super().__init__("Summoner", hp, potency)
        self.petCoefficient: float = 0.95

    def EverlastingFlight(self) -> Event:
        return Event(
            EventType.Heal,
            "EverLastingFlight",
            effect=Hot(
                "EverLastingFlight", 21, int(100 * self.petCoefficient * self.potency)
            ),
        )

    def Rekindle(self, target: Player | None = None) -> Event:
        if not target:
            target = self
        return Event(
            EventType.Heal, "Rekindle", value=int(400 * self.potency), target=target
        )
