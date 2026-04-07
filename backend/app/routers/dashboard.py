from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.dashboard_service import DashboardService
from app.utils.response import success_response


router = APIRouter(prefix="/dashboard", tags=["首页统计"])
dashboard_service = DashboardService()


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    return success_response(dashboard_service.get_overview(db))


@router.get("/trend")
def get_trend(db: Session = Depends(get_db)):
    return success_response(dashboard_service.get_trend(db))


@router.get("/type-distribution")
def get_type_distribution(db: Session = Depends(get_db)):
    return success_response(dashboard_service.get_type_distribution(db))


@router.get("/map-points")
def get_map_points(db: Session = Depends(get_db)):
    return success_response(dashboard_service.get_map_points(db))
