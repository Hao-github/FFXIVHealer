from enum import Enum

class DataType(Enum):
    Physics = 0
    Magic = 1
    Real = 2

class EventType(Enum):
    Other = 0
    Heal = 1
    PhysicsDamage = 2
    MagicDamage = 3
    TrueDamage = 4
