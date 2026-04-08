import hashlib
import random
from collections import Counter


class AIService:
    """
    统一 AI 服务入口。
    当前使用 mock 数据，后续可替换为：
    1. HTTP 调用外部 AI / YOLO 推理服务
    2. 本地模型推理
    """

    light_types = ["ad_light", "up_light", "move_light", "stay_light"]

    def analyze_images(
        self,
        *legacy_image_paths: str,
        image_items: list[dict] | None = None,
    ) -> dict:
        normalized_items = self.normalize_inputs(legacy_image_paths, image_items)

        images = []
        type_counter: Counter[str] = Counter()
        blue_risk = False

        for index, item in enumerate(normalized_items, start=1):
            direction = item.get("direction") or f"image_{index}"
            image_path = item["file_path"]
            seed = int(hashlib.md5(f"{direction}:{image_path}".encode("utf-8")).hexdigest(), 16)
            generator = random.Random(seed)
            score = generator.randint(35, 92)
            object_count = generator.randint(2, 5)
            current_blue_risk = False
            objects = []

            for _ in range(object_count):
                label = generator.choice(self.light_types)
                confidence = round(generator.uniform(0.78, 0.98), 2)
                bbox = [
                    generator.randint(30, 150),
                    generator.randint(20, 120),
                    generator.randint(180, 320),
                    generator.randint(220, 360),
                ]
                objects.append(
                    {
                        "label": label,
                        "confidence": confidence,
                        "bbox": bbox,
                    }
                )
                type_counter[label] += 1

                if label in {"ad_light", "stay_light"} and generator.random() > 0.45:
                    current_blue_risk = True

            if score >= 75:
                current_blue_risk = True

            blue_risk = blue_risk or current_blue_risk
            images.append(
                {
                    "direction": direction,
                    "score": score,
                    "blue_risk": current_blue_risk,
                    "objects": objects,
                }
            )

        return {
            "images": images,
            "summary": {
                "image_count": len(images),
                "type_count": dict(type_counter),
                "blue_risk": blue_risk,
            },
        }

    def normalize_inputs(self, legacy_image_paths: tuple[str, ...], image_items: list[dict] | None) -> list[dict]:
        if image_items:
            normalized = []
            for index, item in enumerate(image_items, start=1):
                file_path = item.get("file_path") or item.get("path")
                if not file_path:
                    continue
                normalized.append(
                    {
                        "direction": item.get("direction") or f"image_{index}",
                        "file_path": file_path,
                    }
                )
            return normalized

        legacy_directions = ["east", "south", "west", "north"]
        return [
            {
                "direction": legacy_directions[index] if index < len(legacy_directions) else f"image_{index + 1}",
                "file_path": path,
            }
            for index, path in enumerate(legacy_image_paths)
            if path
        ]
