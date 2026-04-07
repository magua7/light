from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import WarningRecord


class WarningService:
    def list_warnings(self, db: Session) -> list[dict]:
        warnings = db.query(WarningRecord).order_by(WarningRecord.created_at.desc()).all()

        return [
            {
                "id": item.id,
                "task_id": item.task.id,
                "task_no": item.task.task_no,
                "location_name": item.task.location_name,
                "created_at": item.task.created_at,
                "total_score": item.task.total_score,
                "level": item.task.level,
                "warning_level": item.warning_level,
                "blue_risk": item.task.blue_risk,
                "process_status": item.process_status,
            }
            for item in warnings
        ]

    def update_status(self, db: Session, warning_id: int, process_status: str) -> dict:
        warning = db.query(WarningRecord).filter(WarningRecord.id == warning_id).first()
        if not warning:
            raise HTTPException(status_code=404, detail="预警记录不存在")

        warning.process_status = process_status
        db.commit()
        db.refresh(warning)

        return {
            "id": warning.id,
            "task_id": warning.task_id,
            "warning_level": warning.warning_level,
            "process_status": warning.process_status,
            "updated_at": warning.updated_at,
        }
