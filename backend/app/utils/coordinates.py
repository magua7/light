from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


COORDINATE_TEXT_PATTERN = re.compile(r"^-?\d+\.\d{4}$")
COORDINATE_QUANTIZER = Decimal("0.0001")


def parse_coordinate_text(raw_value: str, *, field_label: str, min_value: float, max_value: float) -> float:
    value = (raw_value or "").strip()
    if not COORDINATE_TEXT_PATTERN.fullmatch(value):
        raise ValueError(f"{field_label}必须为小数点后恰好 4 位。")

    try:
        decimal_value = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{field_label}格式错误。") from exc

    if decimal_value < Decimal(str(min_value)) or decimal_value > Decimal(str(max_value)):
        raise ValueError(f"{field_label}超出范围，应位于 {min_value} 到 {max_value} 之间。")

    return float(decimal_value.quantize(COORDINATE_QUANTIZER, rounding=ROUND_HALF_UP))


def normalize_coordinate_value(value: float | str | Decimal) -> float:
    try:
        decimal_value = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("经纬度格式错误。") from exc
    return float(decimal_value.quantize(COORDINATE_QUANTIZER, rounding=ROUND_HALF_UP))

