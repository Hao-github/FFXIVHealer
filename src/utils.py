import re
from typing import Literal, Type

from .models.Status import Dot


T = Literal["gcd", "ether", None]

STR2STATUS: dict[str, Type] = {
    "Dot": Dot,
}



def str_to_timestamp(raw_time: str) -> float:
    # 使用正则表达式匹配时间格式
    match = re.match(r"(-?)(\d+):(\d+(?:\.\d+)?)", raw_time.strip())
    if not match:
        raise ValueError(f"Invalid time format: {raw_time}")
    negative, minutes, seconds = match.groups()
    total_seconds = int(minutes) * 60 + float(seconds)

    return -total_seconds if negative else total_seconds
