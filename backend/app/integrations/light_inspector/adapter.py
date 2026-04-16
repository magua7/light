from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.integrations.light_inspector.core import LightInspectorCore
from app.integrations.light_inspector.helpers import LightInspectorError


@lru_cache(maxsize=1)
def get_light_inspector_core() -> LightInspectorCore:
    return LightInspectorCore(
        model_path=settings.light_inspector_model_path,
        score_tif_path=settings.light_inspector_score_tif,
        cover_tif_path=settings.light_inspector_cover_tif,
        tips_dir=settings.light_inspector_tips_dir,
    )


class LightInspectorAdapter:
    def analyze_images(self, *, longitude: float, latitude: float, image_items: list[dict]) -> dict:
        if not settings.light_inspector_enabled:
            raise LightInspectorError("真实模型已在配置中禁用，请检查 LIGHT_INSPECTOR_ENABLED。")
        core = get_light_inspector_core()
        return core.analyze_images(longitude=longitude, latitude=latitude, image_items=image_items)
