import json
import logging
from datetime import datetime, time
from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models import DetectionImage, DetectionResult, DetectionTask, WarningRecord
from app.integrations.light_inspector import (
    CoordinateValidationError,
    DependencyUnavailableError,
    ImageProcessingError,
    LightInspectorError,
    MissingAssetError,
)
from app.services.ai_service import AIService
from app.services.ecology_service import EcologyService
from app.services.geo_service import GeoService
from app.services.satellite_service import SatelliteService
from app.services.scoring_service import ScoringService
from app.utils.coordinates import normalize_coordinate_value
from app.utils.file import build_file_url, save_upload_file


logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self):
        self.ai_service = AIService()
        self.geo_service = GeoService()
        self.satellite_service = SatelliteService()
        self.ecology_service = EcologyService()
        self.scoring_service = ScoringService()

    def create_task(
        self,
        db: Session,
        *,
        longitude: float,
        latitude: float,
        location_name: str | None,
        remark: str | None,
        images: list[UploadFile] | None = None,
        east_image: UploadFile | None = None,
        south_image: UploadFile | None = None,
        west_image: UploadFile | None = None,
        north_image: UploadFile | None = None,
    ) -> dict:
        longitude = normalize_coordinate_value(longitude)
        latitude = normalize_coordinate_value(latitude)

        uploaded_files = self.collect_uploaded_files(
            images=images,
            east_image=east_image,
            south_image=south_image,
            west_image=west_image,
            north_image=north_image,
        )

        if len(uploaded_files) < 4:
            raise HTTPException(status_code=400, detail="请最少上传四张夜景图片")

        task_no = f"LP{datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"
        geo_info = self.geo_service.resolve_location(longitude, latitude, location_name)

        task = DetectionTask(
            task_no=task_no,
            location_name=geo_info["display_name"],
            longitude=longitude,
            latitude=latitude,
            remark=remark,
            status="processing",
        )
        db.add(task)
        db.flush()

        saved_images: list[dict] = []
        for index, file_obj in enumerate(uploaded_files, start=1):
            direction = self.resolve_image_direction(file_obj, index)
            saved = save_upload_file(file_obj, task_no, direction)
            saved_images.append(
                {
                    "direction": direction,
                    "file_path": saved["file_path"],
                    "original_name": saved["original_name"],
                }
            )
            db.add(
                DetectionImage(
                    task_id=task.id,
                    direction=direction,
                    file_path=saved["file_path"],
                    original_name=saved["original_name"],
                )
            )

        try:
            ai_result = self.ai_service.analyze_images(
                image_items=saved_images,
                longitude=longitude,
                latitude=latitude,
            )
        except CoordinateValidationError as exc:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except ImageProcessingError as exc:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except (MissingAssetError, DependencyUnavailableError, LightInspectorError, ValueError) as exc:
            db.rollback()
            logger.exception("Real model analysis failed for task %s", task_no)
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        satellite_info = self.satellite_service.get_satellite_info(longitude, latitude)
        ecology_info = self.ecology_service.get_ecology_info(longitude, latitude)
        scoring = self.scoring_service.calculate_scores(ai_result, satellite_info, ecology_info)

        task.status = "completed"
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
            )
        )

        if scoring["warning_level"]:
            db.add(
                WarningRecord(
                    task_id=task.id,
                    warning_level=scoring["warning_level"],
                    process_status="未处理",
                )
            )

        db.commit()
        db.refresh(task)
        return self.get_task_detail(db, task.id)

    def collect_uploaded_files(
        self,
        *,
        images: list[UploadFile] | None,
        east_image: UploadFile | None,
        south_image: UploadFile | None,
        west_image: UploadFile | None,
        north_image: UploadFile | None,
    ) -> list[UploadFile]:
        if images:
            return [item for item in images if item and getattr(item, "filename", None)]

        legacy_files = [east_image, south_image, west_image, north_image]
        return [item for item in legacy_files if item and getattr(item, "filename", None)]

    def resolve_image_direction(self, _upload_file: UploadFile, index: int) -> str:
        return f"image_{index}"

    def get_task_detail(self, db: Session, task_id: int) -> dict:
        task = db.query(DetectionTask).filter(DetectionTask.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        return self.serialize_task_detail(task)

    def list_tasks(
        self,
        db: Session,
        *,
        page: int = 1,
        page_size: int = 10,
        keyword: str | None = None,
        level: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict:
        query = db.query(DetectionTask)

        if keyword:
            query = query.filter(
                or_(
                    DetectionTask.location_name.contains(keyword),
                    DetectionTask.task_no.contains(keyword),
                    DetectionTask.remark.contains(keyword),
                )
            )
        if level:
            query = query.filter(DetectionTask.level == level)

        parsed_start = self.parse_date(start_time, is_end=False)
        parsed_end = self.parse_date(end_time, is_end=True)
        if parsed_start:
            query = query.filter(DetectionTask.created_at >= parsed_start)
        if parsed_end:
            query = query.filter(DetectionTask.created_at <= parsed_end)

        total = query.with_entities(func.count(DetectionTask.id)).scalar() or 0
        items = (
            query.order_by(DetectionTask.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "items": [self.serialize_task_summary(item) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def serialize_task_summary(self, task: DetectionTask) -> dict:
        warning_info = None
        if task.warning:
            warning_info = {
                "id": task.warning.id,
                "warning_level": task.warning.warning_level,
                "process_status": task.warning.process_status,
            }

        return {
            "id": task.id,
            "task_no": task.task_no,
            "location_name": task.location_name,
            "longitude": normalize_coordinate_value(task.longitude),
            "latitude": normalize_coordinate_value(task.latitude),
            "status": task.status,
            "total_score": task.total_score,
            "level": task.level,
            "blue_risk": task.blue_risk,
            "created_at": task.created_at,
            "warning": warning_info,
        }

    def serialize_task_detail(self, task: DetectionTask) -> dict:
        result_payload = json.loads(task.result.ai_summary_json) if task.result else {}
        suggestions = json.loads(task.result.suggestions_json) if task.result else []
        ai_result = result_payload.get("ai", {})
        geo_info = result_payload.get("geo", {})
        satellite_info = result_payload.get("satellite", {})
        ecology_info = result_payload.get("ecology", {})
        direction_scores = [
            {"direction": item.get("direction"), "score": item.get("score", 0)}
            for item in ai_result.get("images", [])
        ]
        type_distribution = [
            {"name": key, "value": value}
            for key, value in ai_result.get("summary", {}).get("type_count", {}).items()
            if value > 0
        ]

        return {
            "id": task.id,
            "task_no": task.task_no,
            "location_name": task.location_name,
            "longitude": normalize_coordinate_value(task.longitude),
            "latitude": normalize_coordinate_value(task.latitude),
            "remark": task.remark,
            "status": task.status,
            "total_score": task.total_score,
            "level": task.level,
            "blue_risk": task.blue_risk,
            "satellite_score": task.satellite_score,
            "ecology_score": task.ecology_score,
            "image_score": task.image_score,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "images": [
                {
                    "id": item.id,
                    "direction": item.direction,
                    "file_path": item.file_path,
                    "file_url": build_file_url(item.file_path),
                    "original_name": item.original_name,
                }
                for item in task.images
            ],
            "direction_summaries": ai_result.get("images", []),
            "type_count": ai_result.get("summary", {}).get("type_count", {}),
            "analysis_summary": ai_result.get("summary", {}),
            "geo_info": geo_info,
            "satellite_info": satellite_info,
            "ecology_info": ecology_info,
            "suggestions": suggestions,
            "charts": {
                "direction_scores": direction_scores,
                "type_distribution": type_distribution,
            },
            "warning": {
                "id": task.warning.id,
                "warning_level": task.warning.warning_level,
                "process_status": task.warning.process_status,
            }
            if task.warning
            else None,
        }

    def parse_date(self, value: Optional[str], *, is_end: bool) -> Optional[datetime]:
        if not value:
            return None
        try:
            if "T" in value or " " in value:
                return datetime.fromisoformat(value.replace("Z", ""))
            parsed = datetime.fromisoformat(value)
            return datetime.combine(parsed.date(), time.max if is_end else time.min)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"时间格式错误: {value}") from exc
