import json
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import DetectionImage, DetectionResult, DetectionTask, WarningRecord
from app.services.ai_service import AIService
from app.services.ecology_service import EcologyService
from app.services.geo_service import GeoService
from app.services.satellite_service import SatelliteService
from app.services.scoring_service import ScoringService


class SeedService:
    def __init__(self):
        self.ai_service = AIService()
        self.geo_service = GeoService()
        self.satellite_service = SatelliteService()
        self.ecology_service = EcologyService()
        self.scoring_service = ScoringService()

    def seed_demo_data(self, db: Session) -> None:
        exists = db.query(func.count(DetectionTask.id)).scalar() or 0
        if exists > 0:
            return

        seed_points = [
            {"location_name": "解放广场商圈", "longitude": 121.487, "latitude": 31.238, "remark": "商圈夜景巡检", "days_ago": 0},
            {"location_name": "滨江步道景观带", "longitude": 121.515, "latitude": 31.225, "remark": "滨水景观抽检", "days_ago": 1},
            {"location_name": "大学城东门", "longitude": 121.402, "latitude": 31.172, "remark": "校园周边监测", "days_ago": 2},
            {"location_name": "科创园主入口", "longitude": 121.366, "latitude": 31.209, "remark": "园区道路照明巡检", "days_ago": 3},
            {"location_name": "高架桥匝道口", "longitude": 121.451, "latitude": 31.264, "remark": "交通节点巡检", "days_ago": 5},
            {"location_name": "老城区居民街区", "longitude": 121.472, "latitude": 31.204, "remark": "居住区夜间抽测", "days_ago": 6},
        ]

        for index, item in enumerate(seed_points, start=1):
            task_no = f"DEMO{datetime.now().strftime('%Y%m%d')}{index:03d}"
            created_at = datetime.now().replace(microsecond=0) - timedelta(days=item["days_ago"])
            geo_info = self.geo_service.resolve_location(item["longitude"], item["latitude"], item["location_name"])

            task = DetectionTask(
                task_no=task_no,
                location_name=geo_info["display_name"],
                longitude=item["longitude"],
                latitude=item["latitude"],
                remark=item["remark"],
                status="completed",
                created_at=created_at,
                updated_at=created_at,
            )
            db.add(task)
            db.flush()

            saved_images = {}
            for direction in ["east", "south", "west", "north"]:
                relative_path = self.create_placeholder_image(task_no, direction, item["location_name"])
                saved_images[direction] = relative_path
                db.add(
                    DetectionImage(
                        task_id=task.id,
                        direction=direction,
                        file_path=relative_path,
                        original_name=f"{direction}.svg",
                        created_at=created_at,
                    )
                )

            ai_result = self.ai_service.analyze_images(
                saved_images["east"],
                saved_images["south"],
                saved_images["west"],
                saved_images["north"],
            )
            satellite_info = self.satellite_service.get_satellite_info(item["longitude"], item["latitude"])
            ecology_info = self.ecology_service.get_ecology_info(item["longitude"], item["latitude"])
            scoring = self.scoring_service.calculate_scores(ai_result, satellite_info, ecology_info)

            task.total_score = scoring["total_score"]
            task.level = scoring["level"]
            task.blue_risk = scoring["blue_risk"]
            task.satellite_score = scoring["satellite_score"]
            task.ecology_score = scoring["ecology_score"]
            task.image_score = scoring["image_score"]

            analysis_bundle = {
                "ai": ai_result,
                "geo": geo_info,
                "satellite": satellite_info,
                "ecology": ecology_info,
                "scoring": {
                    "weights": self.scoring_service.score_weights,
                    "warning_level": scoring["warning_level"],
                },
            }

            db.add(
                DetectionResult(
                    task_id=task.id,
                    ai_summary_json=json.dumps(analysis_bundle, ensure_ascii=False),
                    suggestions_json=json.dumps(scoring["suggestions"], ensure_ascii=False),
                    created_at=created_at,
                )
            )

            if scoring["warning_level"]:
                db.add(
                    WarningRecord(
                        task_id=task.id,
                        warning_level=scoring["warning_level"],
                        process_status="未处理",
                        created_at=created_at,
                        updated_at=created_at,
                    )
                )

        db.commit()

    def create_placeholder_image(self, task_no: str, direction: str, label: str) -> str:
        relative_dir = Path("seed") / task_no
        absolute_dir = settings.upload_dir / relative_dir
        absolute_dir.mkdir(parents=True, exist_ok=True)
        file_path = absolute_dir / f"{direction}.svg"

        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360">
<defs>
  <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
    <stop offset="0%" stop-color="#0f172a"/>
    <stop offset="100%" stop-color="#1d4ed8"/>
  </linearGradient>
</defs>
<rect width="100%" height="100%" fill="url(#bg)" />
<circle cx="500" cy="70" r="38" fill="#fde68a" opacity="0.85" />
<text x="36" y="70" font-size="28" fill="#ffffff">城市光污染监测示例图</text>
<text x="36" y="128" font-size="22" fill="#bfdbfe">地点：{label}</text>
<text x="36" y="168" font-size="22" fill="#bfdbfe">方向：{direction.upper()}</text>
<text x="36" y="208" font-size="20" fill="#dbeafe">Mock Image For Demo</text>
<rect x="36" y="250" width="180" height="56" rx="10" fill="#38bdf8" opacity="0.85" />
<text x="72" y="286" font-size="24" fill="#082f49">Light Inspector</text>
</svg>
"""
        file_path.write_text(svg_content, encoding="utf-8")
        return (relative_dir / f"{direction}.svg").as_posix()
