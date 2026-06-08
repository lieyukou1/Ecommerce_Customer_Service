from __future__ import annotations

from decimal import Decimal
from typing import Any


def stringify_value(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)
