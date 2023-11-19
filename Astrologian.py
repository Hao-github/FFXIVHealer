from basic import Event, EventType, Hot, Mitigation, Shield


class Astrologian:
    def __init__(self, potency: int) -> None:
        self.potency: int = potency
        self.EarthlyStarRemainTime: float = -1
        self.NeutralSectRemainTime: float = 0
        self.HoroscopeRemainTime: float = -1
        self.MacrocosmosRemainTime: float = -1
        self.BigHoroscopeRemainTime: float = -1
        self.HealingSpellBonus: float = 1

    def update(self) -> Event:
        pass

    def Helios(self) -> Event:
        basicPotency: int = 400 * self.HealingSpellBonus
        if self.HoroscopeRemainTime > 0:
            self.HoroscopeRemainTime = -1
            self.BigHoroscopeRemainTime = 30
        return Event(EventType.Heal, value=basicPotency * self.potency)

    def AspectedHelios(self) -> Event:
        basicPotency: int = 250 * self.HealingSpellBonus
        basicHotPotency: int = 150 * self.HealingSpellBonus
        if self.HoroscopeRemainTime > 0:
            self.HoroscopeRemainTime = -1
            self.BigHoroscopeRemainTime = 30
        ret: Event = Event(
            EventType.Heal,
            value=basicPotency * self.potency,
            effectList=[Hot("AspectedHeliosHot", 15, basicHotPotency * self.potency)],
        )
        if self.NeutralSectRemainTime > 0:
            ret.effectList.append(
                Shield("AspectedHeliosShield", 30, basicPotency * 1.25 * self.potency)
            )
        return ret

    def CollectiveUnconscious(self) -> Event:
        return Event(
            EventType.Heal,
            effectList=[
                Mitigation("CUMtg", 5, 0.1),
                Hot("CUHot", 15, 100),
            ],
        )

    def CelestialOpposition(self) -> Event:
        return Event(EventType.Heal, value=200, effectList=[Hot("COHot", 15, 100)])

    def SetEarthlyStar(self) -> None:
        self.EarthlyStarRemainTime = 20

    def EarthlyStar(self) -> Event | None:
        if self.EarthlyStarRemainTime > 10:
            return Event(EventType.Heal, value=540 * self.potency)
        elif self.EarthlyStarRemainTime >= 0:
            return Event(EventType.Heal, value=720 * self.potency)
        else:
            return None

    def SetHoroscope(self) -> None:
        self.HoroscopeRemainTime = 10

    def Horoscope(self) -> Event | None:
        if self.HoroscopeRemainTime > 0:
            self.HoroscopeRemainTime = -1
            return Event(EventType.Heal, 200 * self.potency)
        if self.BigHoroscopeRemainTime > 0:
            self.HoroscopeRemainTime = -1
            return Event(EventType.Heal, 400 * self.potency)
        return None

    def NeutralSect(self) -> Event | None:
        self.NeutralSectRemainTime = 20
