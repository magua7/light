from fastapi import APIRouter

from app.utils.response import success_response


router = APIRouter(prefix="/health", tags=["系统"])


@router.get("")
def health_check():
    return success_response({"status": "ok"})
