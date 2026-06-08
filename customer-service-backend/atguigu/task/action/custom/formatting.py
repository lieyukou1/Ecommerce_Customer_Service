from __future__ import annotations

from decimal import Decimal
from typing import Any


def stringify_value(value: Any, default: str = "") -> str:
    """
    功能：把各种类型的值稳定转成字符串。

    输入：
    - value: 待转换的原始值。
    - default: value 为空时使用的默认字符串。

    输出：
    - str: 规整后的字符串值。

    调用情况：
    - 多个对象构造函数和自定义 action 复用。

    副作用：
    - 无。
    """
    if value is None:
        return default
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)
