import hashlib
import random
from collections import Counter


class AIService:
    """
    统一 AI 服务入口。
    当前使用 mock 数据，后续可以替换为：
    1. 请求外部 AI/YOLO 推理 HTTP 服务
    2. 在本地调用真实模型推理
    """

    light_types = ["ad_light", "up_light", "move_light", "stay_light"]

    def analyze_images(
        self,
        east_image: str,
        south_image: str,
        west_image: str,
        north_image: str,
    ) -> dict:
        image_paths = {
            "east": east_image,
            "south": south_image,
            "west": west_image,
            "north": north_image,
        }

        images = []
        type_counter: Counter[str] = Counter()
        blue_risk = False

        for direction, image_path in image_paths.items():
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
                "type_count": dict(type_counter),
                "blue_risk": blue_risk,
            },
        }
