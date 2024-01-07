from enum import Enum


jobToClass = {
    "DarkKnight": "Tank",
    "Knight": "Tank",
    "GunBreaker": "Tank",
    "Warrior": "Tank",
    "Dancer": "PhysicsDPS",
    "Machinist": "PhysicsDPS",
    "Bard": "PhysicsDPS",
    "Monk": "MeleeDPS",
    "Samurai": "MeleeDPS",
    "Dragoon": "MeleeDPS",
    "WhiteMage": "Healer",
    "Scholar": "Healer",
    "Sage": "Healer",
    "RedMage": "MagicDPS",
    "Summoner": "MagicDPS",
    "BlackMage": "MagicDPS",
}


class EventType(Enum):
    TrueHeal = 0  # 快照后的治疗
    Heal = 1  # 普通治疗
    GroundHeal = 2  # 特殊治疗, 吃施法者快照但目标身上实时判定
    PhysicsDmg = 3  # 物理伤害
    MagicDmg = 4  # 魔法伤害
    TrueDamage = 5  # dot伤害
    MaxHpChange = 6  # 关于最大生命值的变动事件
