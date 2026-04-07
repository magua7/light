from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.warning import WarningStatusUpdate
from app.services.warning_service import WarningService
from app.utils.response import success_response


router = APIRouter(prefix="/warnings", tags=["预警管理"])
warning_service = WarningService()


@router.get("/list")
def list_warnings(db: Session = Depends(get_db)):
    return success_response(warning_service.list_warnings(db))


@router.put("/{warning_id}/status")
def update_warning_status(
    warning_id: int,
    payload: WarningStatusUpdate,
    db: Session = Depends(get_db),
):
    data = warning_service.update_status(db, warning_id, payload.process_status)
    return success_response(data)
