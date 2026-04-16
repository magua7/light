from __future__ import annotations

from pathlib import Path

from app.core.config import settings
from app.integrations.light_inspector import LightInspectorAdapter


class AIService:
    """
    统一 AI 服务入口。
    当前默认接入本地真实模型分析能力。
    """

    def __init__(self):
        self.adapter = LightInspectorAdapter()

    def analyze_images(
        self,
        *legacy_image_paths: str,
        image_items: list[dict] | None = None,
        longitude: float | None = None,
        latitude: float | None = None,
    ) -> dict:
        normalized_items = self.normalize_inputs(legacy_image_paths, image_items)
        if not normalized_items:
            raise ValueError("未提供任何可分析的图片。")
        if longitude is None or latitude is None:
            raise ValueError("真实模型分析必须提供经度和纬度。")

        return self.adapter.analyze_images(
            longitude=longitude,
            latitude=latitude,
            image_items=normalized_items,
        )

    def normalize_inputs(self, legacy_image_paths: tuple[str, ...], image_items: list[dict] | None) -> list[dict]:
        if image_items:
            normalized = []
            for index, item in enumerate(image_items, start=1):
                file_path = item.get("file_path") or item.get("path")
                if not file_path:
                    continue
                normalized_path = Path(file_path)
                if not normalized_path.is_absolute():
                    normalized_path = settings.upload_dir / normalized_path
                normalized.append(
                    {
                        "direction": item.get("direction") or f"image_{index}",
                        "file_path": normalized_path.as_posix(),
                    }
                )
            return normalized

        legacy_directions = ["east", "south", "west", "north"]
        return [
            {
                "direction": legacy_directions[index] if index < len(legacy_directions) else f"image_{index + 1}",
                "file_path": (Path(path) if Path(path).is_absolute() else (settings.upload_dir / Path(path))).as_posix(),
            }
            for index, path in enumerate(legacy_image_paths)
            if path
        ]
