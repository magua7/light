from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

from app.utils.coordinates import normalize_coordinate_value


CLASS_NAME_MAP = {
    "ad light": "ad_light",
    "ad_light": "ad_light",
    "ad-light": "ad_light",
    "up light": "up_light",
    "up_light": "up_light",
    "up-light": "up_light",
    "move light": "move_light",
    "move_light": "move_light",
    "move-light": "move_light",
    "stay light": "stay_light",
    "stay_light": "stay_light",
    "stay-light": "stay_light",
}

CANONICAL_TYPES = ("ad_light", "up_light", "move_light", "stay_light")

CLASS_SCORE_MAP = {
    "move_light": 40,
    "ad_light": 80,
    "stay_light": 60,
    "up_light": 90,
}

TIP_FILE_MAP = {
    "stay_light": "路灯.txt",
    "move_light": "车灯.txt",
    "up_light": "上射光.txt",
    "ad_light": "广告牌.txt",
}

TIP_PRIORITY = ("up_light", "ad_light", "stay_light", "move_light")


class LightInspectorError(RuntimeError):
    """Base exception for the Light Inspector integration."""


class DependencyUnavailableError(LightInspectorError):
    """Raised when required runtime dependencies are missing."""


class MissingAssetError(LightInspectorError):
    """Raised when required model assets are missing."""


class CoordinateValidationError(LightInspectorError):
    """Raised when longitude or latitude is invalid."""


class ImageProcessingError(LightInspectorError):
    """Raised when an input image cannot be processed."""


def normalize_label(raw_label: str | None) -> str | None:
    if not raw_label:
        return None
    normalized = raw_label.strip().lower().replace("-", " ").replace("_", " ")
    normalized = " ".join(normalized.split())
    return CLASS_NAME_MAP.get(normalized)


def empty_type_count() -> dict[str, int]:
    return {label: 0 for label in CANONICAL_TYPES}


def build_full_type_count(type_count: dict[str, int] | None) -> dict[str, int]:
    result = empty_type_count()
    for label, value in (type_count or {}).items():
        if label in result:
            result[label] = int(value)
    return result


def build_type_ratio(type_count: dict[str, int]) -> dict[str, float]:
    total = sum(type_count.values())
    if total <= 0:
        return {label: 0.0 for label in CANONICAL_TYPES}
    return {
        label: round((type_count.get(label, 0) / total), 4)
        for label in CANONICAL_TYPES
    }


def validate_coordinates(longitude: float, latitude: float) -> tuple[float, float]:
    try:
        lon = normalize_coordinate_value(longitude)
        lat = normalize_coordinate_value(latitude)
    except (TypeError, ValueError) as exc:
        raise CoordinateValidationError("经纬度格式错误，无法进行真实模型分析。") from exc

    if not (-180 <= lon <= 180):
        raise CoordinateValidationError(f"经度超出范围：{lon}，应位于 -180 到 180 之间。")
    if not (-90 <= lat <= 90):
        raise CoordinateValidationError(f"纬度超出范围：{lat}，应位于 -90 到 90 之间。")
    return lon, lat


def ensure_file(path: Path, description: str) -> Path:
    if not path.exists():
        raise MissingAssetError(f"{description}不存在：{path}")
    return path


def dedupe_keep_order(items: list[str]) -> list[str]:
    return list(OrderedDict.fromkeys(item for item in items if item))


def read_tip_lines(tips_dir: Path, label: str) -> list[str]:
    file_name = TIP_FILE_MAP[label]
    tip_file = ensure_file(tips_dir / file_name, f"{label}建议文件")
    lines = [line.strip() for line in tip_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    return lines


def build_stable_suggestions(
    type_count: dict[str, int],
    tips_dir: Path,
    *,
    blue_risk: bool = False,
    area_type: str | None = None,
    max_items: int = 6,
) -> list[str]:
    suggestions: list[str] = []

    for label in TIP_PRIORITY:
        if type_count.get(label, 0) <= 0:
            continue
        suggestions.extend(read_tip_lines(tips_dir, label)[:2])
        if len(suggestions) >= max_items:
            break

    if blue_risk:
        suggestions.append("建议优先控制高色温 LED 与高亮广告面，降低蓝光溢散风险。")

    if area_type == "生态区":
        suggestions.append("当前点位位于生态敏感区域周边，建议纳入重点时段照明管控。")

    suggestions = dedupe_keep_order(suggestions)
    if not suggestions:
        suggestions.append("当前未识别到明显的人造光源污染目标，建议结合现场巡查持续观察。")

    return suggestions[:max_items]


def get_area_type(cover_value: float | int) -> str:
    try:
        normalized = int(round(float(cover_value)))
    except (TypeError, ValueError):
        return "未知区域"
    return "城市区" if normalized == 7 else "生态区"


def get_grade(score: float, area_type: str) -> str:
    score = max(0, min(float(score), 100))

    if area_type == "城市区":
        if score < 20:
            return "优"
        if score < 40:
            return "良"
        if score < 60:
            return "中"
        if score < 80:
            return "较差"
        return "差"

    if area_type == "生态区":
        if score < 10:
            return "优"
        if score < 25:
            return "良"
        if score < 45:
            return "中"
        if score < 70:
            return "较差"
        return "差"

    if score <= 20:
        return "优"
    if score <= 40:
        return "良"
    if score <= 60:
        return "中"
    if score <= 80:
        return "较差"
    return "差"
