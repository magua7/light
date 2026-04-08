import json
import logging
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


logger = logging.getLogger(__name__)


class SeedService:
    direction_titles = {
        "east": "图片1",
        "south": "图片2",
        "west": "图片3",
        "north": "图片4",
    }

    demo_points = [
        {"location_name": "五一广场商圈", "longitude": 112.9823, "latitude": 28.1970, "remark": "核心商圈夜景巡检", "days_ago": 0},
        {"location_name": "湘江观景长廊", "longitude": 112.9688, "latitude": 28.2034, "remark": "沿江景观照明抽检", "days_ago": 1},
        {"location_name": "岳麓山大学城", "longitude": 112.9318, "latitude": 28.1729, "remark": "高校片区夜间抽测", "days_ago": 2},
        {"location_name": "高铁南站东广场", "longitude": 113.0473, "latitude": 28.1456, "remark": "交通枢纽照明巡检", "days_ago": 3},
        {"location_name": "梅溪湖国际新城", "longitude": 112.9088, "latitude": 28.2314, "remark": "新区景观与广告照明巡检", "days_ago": 5},
        {"location_name": "洋湖湿地北入口", "longitude": 112.9406, "latitude": 28.1421, "remark": "生态敏感区域周边监测", "days_ago": 6},
    ]

    def __init__(self):
        self.ai_service = AIService()
        self.geo_service = GeoService()
        self.satellite_service = SatelliteService()
        self.ecology_service = EcologyService()
        self.scoring_service = ScoringService()

    def seed_demo_data(self, db: Session) -> None:
        try:
            demo_tasks = (
                db.query(DetectionTask)
                .filter(DetectionTask.task_no.like("DEMO%"))
                .order_by(DetectionTask.id.asc())
                .all()
            )

            if demo_tasks:
                self.sync_demo_tasks(db, demo_tasks)
                return

            exists = db.query(func.count(DetectionTask.id)).scalar() or 0
            if exists > 0:
                return

            self.sync_demo_tasks(db, [])
        except Exception:
            db.rollback()
            logger.exception("Seed demo data failed during application startup")
            raise

    def sync_demo_tasks(self, db: Session, demo_tasks: list[DetectionTask]) -> None:
        target_count = len(self.demo_points)

        for extra_task in demo_tasks[target_count:]:
            db.delete(extra_task)
        db.flush()

        active_tasks = demo_tasks[:target_count]

        for index, point in enumerate(self.demo_points, start=1):
            if index <= len(active_tasks):
                task = active_tasks[index - 1]
            else:
                task = DetectionTask(
                    task_no=f"DEMO{datetime.now().strftime('%Y%m%d')}{index:03d}",
                    location_name=point["location_name"],
                    longitude=point["longitude"],
                    latitude=point["latitude"],
                    remark=point["remark"],
                    status="completed",
                    blue_risk=False,
                )
                db.add(task)
                db.flush()

            self.populate_demo_task(db, task, point)

        db.commit()

    def populate_demo_task(self, db: Session, task: DetectionTask, point: dict) -> None:
        created_at = datetime.now().replace(microsecond=0) - timedelta(days=point["days_ago"])
        geo_info = self.geo_service.resolve_location(point["longitude"], point["latitude"], point["location_name"])

        task.location_name = geo_info["display_name"]
        task.longitude = point["longitude"]
        task.latitude = point["latitude"]
        task.remark = point["remark"]
        task.status = "completed"
        task.created_at = created_at
        task.updated_at = created_at

        saved_images = self.sync_demo_images(db, task, point["location_name"], created_at)

        ai_result = self.ai_service.analyze_images(
            saved_images["east"],
            saved_images["south"],
            saved_images["west"],
            saved_images["north"],
        )
        satellite_info = self.satellite_service.get_satellite_info(point["longitude"], point["latitude"])
        ecology_info = self.ecology_service.get_ecology_info(point["longitude"], point["latitude"])
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

        if task.result:
            task.result.ai_summary_json = json.dumps(analysis_bundle, ensure_ascii=False)
            task.result.suggestions_json = json.dumps(scoring["suggestions"], ensure_ascii=False)
            task.result.created_at = created_at
        else:
            db.add(
                DetectionResult(
                    task_id=task.id,
                    ai_summary_json=json.dumps(analysis_bundle, ensure_ascii=False),
                    suggestions_json=json.dumps(scoring["suggestions"], ensure_ascii=False),
                    created_at=created_at,
                )
            )

        warning_level = scoring["warning_level"]
        if warning_level:
            if task.warning:
                task.warning.warning_level = warning_level
                task.warning.process_status = task.warning.process_status or "未处理"
                task.warning.created_at = created_at
                task.warning.updated_at = created_at
            else:
                db.add(
                    WarningRecord(
                        task_id=task.id,
                        warning_level=warning_level,
                        process_status="未处理",
                        created_at=created_at,
                        updated_at=created_at,
                    )
                )
        elif task.warning:
            db.delete(task.warning)

    def sync_demo_images(
        self,
        db: Session,
        task: DetectionTask,
        label: str,
        created_at: datetime,
    ) -> dict[str, str]:
        image_map = {image.direction: image for image in task.images}
        saved_images: dict[str, str] = {}

        for direction in ["east", "south", "west", "north"]:
            relative_path = self.create_placeholder_image(task.task_no, direction, label)
            saved_images[direction] = relative_path
            original_name = f"{self.direction_titles[direction]}.svg"

            if direction in image_map:
                image_map[direction].file_path = relative_path
                image_map[direction].original_name = original_name
                image_map[direction].created_at = created_at
            else:
                db.add(
                    DetectionImage(
                        task_id=task.id,
                        direction=direction,
                        file_path=relative_path,
                        original_name=original_name,
                        created_at=created_at,
                    )
                )

        return saved_images

    def create_placeholder_image(self, task_no: str, direction: str, label: str) -> str:
        relative_dir = Path("seed") / task_no
        absolute_dir = settings.upload_dir / relative_dir
        absolute_dir.mkdir(parents=True, exist_ok=True)
        file_path = absolute_dir / f"{direction}.svg"
        image_label = self.direction_titles[direction]

        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360">
<defs>
  <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
    <stop offset="0%" stop-color="#090a0c"/>
    <stop offset="100%" stop-color="#15171b"/>
  </linearGradient>
</defs>
<rect width="100%" height="100%" fill="url(#bg)" />
<circle cx="520" cy="76" r="44" fill="#f1ede6" opacity="0.16" />
<text x="36" y="72" font-size="28" fill="#f1ede6">城市光污染监测示例图</text>
<text x="36" y="128" font-size="22" fill="#d2ccc1">地点：{label}</text>
<text x="36" y="168" font-size="22" fill="#d2ccc1">{image_label}</text>
<text x="36" y="214" font-size="18" fill="#8f8a81">演示样本图，仅用于系统展示</text>
<rect x="36" y="254" width="204" height="54" rx="12" fill="#f1ede6" opacity="0.14" />
<text x="70" y="288" font-size="22" fill="#f1ede6">城市夜间光环境监测</text>
</svg>
"""
        file_path.write_text(svg_content, encoding="utf-8")
        return (relative_dir / f"{direction}.svg").as_posix()
