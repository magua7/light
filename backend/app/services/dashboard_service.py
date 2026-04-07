import json
from datetime import date, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import DetectionTask, WarningRecord


class DashboardService:
    level_colors = {
        "优": "#6d9776",
        "良": "#8f9cac",
        "中": "#c29b63",
        "较差": "#bb735c",
        "差": "#944d44",
    }

    def get_overview(self, db: Session) -> dict:
        total_tasks = db.query(func.count(DetectionTask.id)).scalar() or 0
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        today_tasks = (
            db.query(func.count(DetectionTask.id))
            .filter(DetectionTask.created_at >= today_start, DetectionTask.created_at <= today_end)
            .scalar()
            or 0
        )
        high_risk_warnings = (
            db.query(func.count(WarningRecord.id))
            .filter(WarningRecord.warning_level == "高风险")
            .scalar()
            or 0
        )
        average_score = round(db.query(func.avg(DetectionTask.total_score)).scalar() or 0, 2)

        level_distribution = []
        for level in ["优", "良", "中", "较差", "差"]:
            count = (
                db.query(func.count(DetectionTask.id))
                .filter(DetectionTask.level == level)
                .scalar()
                or 0
            )
            level_distribution.append({"name": level, "value": count})

        recent_tasks = db.query(DetectionTask).order_by(DetectionTask.created_at.desc()).limit(6).all()

        return {
            "total_tasks": total_tasks,
            "today_tasks": today_tasks,
            "high_risk_warnings": high_risk_warnings,
            "average_score": average_score,
            "level_distribution": level_distribution,
            "recent_tasks": [
                {
                    "id": item.id,
                    "task_no": item.task_no,
                    "location_name": item.location_name,
                    "level": item.level,
                    "total_score": item.total_score,
                    "created_at": item.created_at,
                }
                for item in recent_tasks
            ],
        }

    def get_trend(self, db: Session) -> list[dict]:
        today = date.today()
        trend = []
        for offset in range(6, -1, -1):
            current_day = today - timedelta(days=offset)
            day_start = datetime.combine(current_day, datetime.min.time())
            day_end = datetime.combine(current_day, datetime.max.time())
            tasks = (
                db.query(DetectionTask)
                .filter(DetectionTask.created_at >= day_start, DetectionTask.created_at <= day_end)
                .all()
            )
            count = len(tasks)
            average_score = round(sum(item.total_score or 0 for item in tasks) / count, 2) if count else 0
            trend.append(
                {
                    "date": current_day.strftime("%m-%d"),
                    "count": count,
                    "average_score": average_score,
                }
            )
        return trend

    def get_type_distribution(self, db: Session) -> list[dict]:
        type_counter: dict[str, int] = {}
        tasks = db.query(DetectionTask).all()

        for task in tasks:
            if not task.result:
                continue
            payload = json.loads(task.result.ai_summary_json)
            type_count = payload.get("ai", {}).get("summary", {}).get("type_count", {})
            for label, value in type_count.items():
                type_counter[label] = type_counter.get(label, 0) + value

        return [{"name": key, "value": value} for key, value in type_counter.items()]

    def get_map_points(self, db: Session) -> list[dict]:
        tasks = db.query(DetectionTask).order_by(DetectionTask.created_at.desc()).all()
        return [
            {
                "task_id": task.id,
                "task_no": task.task_no,
                "location_name": task.location_name,
                "longitude": task.longitude,
                "latitude": task.latitude,
                "level": task.level,
                "total_score": task.total_score,
                "blue_risk": task.blue_risk,
                "created_at": task.created_at,
                "marker_color": self.level_colors.get(task.level or "", "#c29b63"),
            }
            for task in tasks
        ]
