import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService, get_current_user
from app.utils.response import success_response


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["认证"])
auth_service = AuthService()


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    logger.info("Auth register endpoint entered username=%s", payload.username.strip())
    user = auth_service.register(db, payload.username, payload.password)
    return success_response(user, message="注册成功")


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    logger.info("Auth login endpoint entered username=%s", payload.username.strip())
    data = auth_service.login(db, payload.username, payload.password)
    return success_response(data, message="登录成功")


@router.get("/me")
def me(user=Depends(get_current_user)):
    return success_response(
        {
            "id": user.id,
            "username": user.username,
            "created_at": user.created_at,
        }
    )


@router.post("/logout")
def logout(_=Depends(get_current_user)):
    return success_response(auth_service.logout(), message="已退出登录")
