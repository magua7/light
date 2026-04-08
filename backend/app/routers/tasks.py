from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.task_service import TaskService
from app.utils.response import success_response


router = APIRouter(prefix="/tasks", tags=["检测任务"])
task_service = TaskService()


@router.post("/create")
def create_task(
    longitude: float = Form(...),
    latitude: float = Form(...),
    location_name: str | None = Form(default=None),
    remark: str | None = Form(default=None),
    images: list[UploadFile] | None = File(default=None),
    east_image: UploadFile | None = File(default=None),
    south_image: UploadFile | None = File(default=None),
    west_image: UploadFile | None = File(default=None),
    north_image: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
):
    data = task_service.create_task(
        db,
        longitude=longitude,
        latitude=latitude,
        location_name=location_name,
        remark=remark,
        images=images,
        east_image=east_image,
        south_image=south_image,
        west_image=west_image,
        north_image=north_image,
    )
    return success_response(data)


@router.get("/list")
def list_tasks(
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    level: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    db: Session = Depends(get_db),
):
    data = task_service.list_tasks(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        level=level,
        start_time=start_time,
        end_time=end_time,
    )
    return success_response(data)


@router.get("/{task_id}")
def get_task_detail(task_id: int, db: Session = Depends(get_db)):
    return success_response(task_service.get_task_detail(db, task_id))
