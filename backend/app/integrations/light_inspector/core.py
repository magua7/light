from __future__ import annotations

import logging
from collections import Counter
from pathlib import Path

from app.integrations.light_inspector.helpers import (
    CANONICAL_TYPES,
    CLASS_SCORE_MAP,
    DependencyUnavailableError,
    ImageProcessingError,
    LightInspectorError,
    build_full_type_count,
    build_stable_suggestions,
    build_type_ratio,
    get_area_type,
    get_grade,
    normalize_label,
    validate_coordinates,
)

logger = logging.getLogger(__name__)

IMPORT_ERROR: Exception | None = None

try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
    import rasterio  # type: ignore
    from rasterio.transform import rowcol  # type: ignore
    from ultralytics import YOLO  # type: ignore
except Exception as exc:  # pragma: no cover - dependency absence is runtime-handled
    IMPORT_ERROR = exc
    cv2 = None
    np = None
    rasterio = None
    rowcol = None
    YOLO = None


class LightInspectorCore:
    def __init__(
        self,
        *,
        model_path: Path,
        score_tif_path: Path,
        cover_tif_path: Path,
        tips_dir: Path,
    ):
        self.model_path = Path(model_path)
        self.score_tif_path = Path(score_tif_path)
        self.cover_tif_path = Path(cover_tif_path)
        self.tips_dir = Path(tips_dir)
        self._model = None

    def analyze_images(self, *, longitude: float, latitude: float, image_items: list[dict]) -> dict:
        self.ensure_ready()
        lon, lat = validate_coordinates(longitude, latitude)

        if not image_items:
            raise ImageProcessingError("未收到任何可分析的图片。")

        model = self.get_model()
        mat_score, area_type = self.read_mat_score(lon, lat)

        images: list[dict] = []
        type_counter: Counter[str] = Counter()
        blue_risk = False
        image_scores: list[float] = []

        for index, item in enumerate(image_items, start=1):
            direction = item.get("direction") or f"image_{index}"
            file_path = item.get("file_path") or item.get("path")
            if not file_path:
                raise ImageProcessingError(f"{direction} 缺少图片路径，无法进行分析。")

            image_result = self.analyze_single_image(model, direction, Path(file_path))
            images.append(image_result)
            image_scores.append(float(image_result["score"]))
            type_counter.update(image_result["type_count"])
            blue_risk = blue_risk or bool(image_result["blue_risk"])

        full_type_count = build_full_type_count(dict(type_counter))
        image_avg_score = round(sum(image_scores) / len(image_scores), 2) if image_scores else 0.0
        image_std_score = (
            float(np.std(np.asarray(image_scores, dtype=np.float32), ddof=1))
            if len(image_scores) > 1
            else 0.0
        )
        model_total_score = round(image_avg_score * (1 + 0.3 * (image_std_score / 17.5)), 2)
        final_score = round(model_total_score + mat_score, 2)
        grade = get_grade(final_score, area_type)
        suggestions = build_stable_suggestions(
            full_type_count,
            self.tips_dir,
            blue_risk=blue_risk,
            area_type=area_type,
        )

        return {
            "images": images,
            "summary": {
                "image_count": len(images),
                "type_count": full_type_count,
                "type_ratio": build_type_ratio(full_type_count),
                "blue_risk": blue_risk,
                "image_avg_score": image_avg_score,
                "mat_score": round(mat_score, 2),
                "area_type": area_type,
                "model_total_score": model_total_score,
                "final_score": final_score,
                "grade": grade,
                "suggestions": suggestions,
            },
        }

    def ensure_ready(self) -> None:
        if IMPORT_ERROR is not None:
            raise DependencyUnavailableError(
                "真实模型依赖未安装完整，请安装 ultralytics、opencv-python-headless、rasterio、numpy、Pillow。"
            ) from IMPORT_ERROR

        if not self.model_path.exists():
            raise LightInspectorError(f"YOLO 模型文件不存在：{self.model_path}")
        if not self.score_tif_path.exists():
            raise LightInspectorError(f"分数栅格文件不存在：{self.score_tif_path}")
        if not self.cover_tif_path.exists():
            raise LightInspectorError(f"覆盖类型栅格文件不存在：{self.cover_tif_path}")
        if not self.tips_dir.exists():
            raise LightInspectorError(f"建议文本目录不存在：{self.tips_dir}")

    def get_model(self):
        if self._model is None:
            try:
                self._model = YOLO(str(self.model_path))
            except Exception as exc:  # pragma: no cover - depends on local runtime
                logger.exception("Failed to initialize YOLO model from %s", self.model_path)
                raise LightInspectorError(f"YOLO 模型初始化失败：{exc}") from exc
        return self._model

    def analyze_single_image(self, model, direction: str, image_path: Path) -> dict:
        image_bgr = self.read_image_bgr(image_path)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        try:
            results = model.predict(source=image_rgb, conf=0.25, verbose=False)
        except Exception as exc:  # pragma: no cover - depends on local runtime
            logger.exception("YOLO inference failed for %s", image_path)
            raise LightInspectorError(f"图片推理失败：{image_path.name}，{exc}") from exc

        result = results[0]
        names = result.names if hasattr(result, "names") else {}

        brightness_map: dict[str, list[float]] = {label: [] for label in CANONICAL_TYPES}
        type_counter: Counter[str] = Counter()
        objects: list[dict] = []

        for box in getattr(result, "boxes", []) or []:
            cls_id = int(box.cls[0])
            raw_label = names.get(cls_id, str(cls_id)) if isinstance(names, dict) else names[cls_id]
            label = normalize_label(str(raw_label))
            if not label:
                continue

            confidence = round(float(box.conf[0]), 4)
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(image_bgr.shape[1], x2)
            y2 = min(image_bgr.shape[0], y2)
            if x2 <= x1 or y2 <= y1:
                continue

            crop = image_bgr[y1:y2, x1:x2]
            brightness_map[label].append(self.calculate_brightness_coeff(crop))
            type_counter[label] += 1
            objects.append(
                {
                    "label": label,
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2],
                }
            )

        recognition_score = self.calculate_recognition_score(brightness_map)
        whole_light_score = self.calculate_whole_score(image_rgb)
        blue_score = self.calculate_blue_score(image_rgb)
        image_score = round(recognition_score + whole_light_score + blue_score, 2)
        image_type_count = build_full_type_count(dict(type_counter))
        image_blue_risk = blue_score >= 3.2 or (
            image_type_count.get("up_light", 0) + image_type_count.get("ad_light", 0) > 0 and blue_score >= 2.6
        )

        return {
            "direction": direction,
            "score": image_score,
            "blue_risk": image_blue_risk,
            "objects": objects,
            "object_count": len(objects),
            "type_count": image_type_count,
            "recognition_score": recognition_score,
            "whole_light_score": whole_light_score,
            "blue_score": blue_score,
        }

    def calculate_recognition_score(self, brightness_map: dict[str, list[float]]) -> float:
        total_score = 0.0
        total_max_possible = 0.0

        for label, base_score in CLASS_SCORE_MAP.items():
            values = brightness_map.get(label) or []
            if not values:
                continue
            total_score += base_score * float(np.mean(values))
            total_max_possible += base_score

        if total_max_possible <= 0:
            return 0.0

        return round((total_score / total_max_possible) * 18, 2)

    def calculate_brightness_coeff(self, image_crop_bgr) -> float:
        gray = cv2.cvtColor(image_crop_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
        avg_brightness = float(np.mean(gray))
        score_base = avg_brightness / 255.0
        glare_threshold = 180
        glare_mask = gray > glare_threshold
        glare_ratio = float(np.sum(glare_mask) / (gray.shape[0] * gray.shape[1]))
        k1 = 0.8 * score_base + 0.2 * glare_ratio
        return float(np.clip(k1 * 2.5, 0.0, 1.0))

    def calculate_whole_score(self, image_rgb) -> float:
        r = image_rgb[:, :, 0].astype(np.float32)
        g = image_rgb[:, :, 1].astype(np.float32)
        b = image_rgb[:, :, 2].astype(np.float32)
        brightness = 0.299 * r + 0.587 * g + 0.114 * b
        avg_bright = float(np.mean(brightness))
        k0 = avg_bright / 255.0
        bright_mask = brightness > 180
        bright_ratio = float(np.sum(bright_mask) / (brightness.shape[0] * brightness.shape[1]))
        k0 = 0.8 * k0 + 0.2 * bright_ratio
        return round(float(np.clip(k0, 0.0, 1.0)) * 10 * 2.5, 2)

    def calculate_blue_score(self, image_rgb) -> float:
        r = image_rgb[:, :, 0].astype(np.float32)
        g = image_rgb[:, :, 1].astype(np.float32)
        b = image_rgb[:, :, 2].astype(np.float32)
        total = float(np.sum(r) + np.sum(g) + np.sum(b))
        if total < 1e-6:
            return 0.0
        blue_ratio = float(np.sum(b) / total)
        blue_raw_score = blue_ratio * 100
        return round(blue_raw_score * (7 / 100), 2)

    def read_mat_score(self, longitude: float, latitude: float) -> tuple[float, str]:
        score_value = self.read_raster_value(self.score_tif_path, longitude, latitude)
        cover_value = self.read_raster_value(self.cover_tif_path, longitude, latitude)
        area_type = get_area_type(cover_value)
        if not float(score_value) == float(score_value):  # NaN
            score_value = 0.0
        return round(float(score_value), 2), area_type

    def read_raster_value(self, raster_path: Path, longitude: float, latitude: float) -> float:
        try:
            with rasterio.open(raster_path) as src:
                data = src.read(1)
                row, col = rowcol(src.transform, longitude, latitude)
                row = max(0, min(int(row), data.shape[0] - 1))
                col = max(0, min(int(col), data.shape[1] - 1))
                value = data[row, col]
                return float(value)
        except Exception as exc:  # pragma: no cover - depends on local raster file
            logger.exception("Failed to read raster value from %s", raster_path)
            raise LightInspectorError(f"栅格文件读取失败：{raster_path.name}，{exc}") from exc

    def read_image_bgr(self, image_path: Path):
        if not image_path.exists():
            raise ImageProcessingError(f"图片文件不存在：{image_path}")

        try:
            file_bytes = np.fromfile(str(image_path), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        except Exception as exc:
            logger.exception("Failed to decode image %s", image_path)
            raise ImageProcessingError(f"图片读取失败：{image_path.name}，{exc}") from exc

        if image is None or image.size == 0:
            raise ImageProcessingError(f"图片为空或格式不受支持：{image_path.name}")
        return image
