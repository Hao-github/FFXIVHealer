from typing import Literal, Type

from .models.Status import Dot


T = Literal["gcd", "ether", None]

STR2STATUS: dict[str, Type] = {
    "Dot": Dot,
}
