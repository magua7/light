import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.database.session import get_db
from app.models import User


logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


class AuthService:
    def register(self, db: Session, username: str, password: str) -> dict:
        normalized_username = username.strip()
        if not normalized_username:
            raise HTTPException(status_code=400, detail="请输入用户名")

        exists = db.query(User).filter(User.username == normalized_username).first()
        if exists:
            raise HTTPException(status_code=400, detail="用户名已存在，请更换后重试")

        user = User(
            username=normalized_username,
            password_hash=get_password_hash(password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info("Auth register success username=%s user_id=%s", normalized_username, user.id)
        return self.serialize_user(user)

    def login(self, db: Session, username: str, password: str) -> dict:
        normalized_username = username.strip()
        logger.info("Auth login request received username=%s", normalized_username)

        user = db.query(User).filter(User.username == normalized_username).first()
        if not user:
            logger.warning("Auth login failed: user not found username=%s", normalized_username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
            )

        password_ok = verify_password(password, user.password_hash)
        if not password_ok:
            logger.warning("Auth login failed: password mismatch username=%s", normalized_username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
            )

        access_token = create_access_token(str(user.id))
        logger.info("Auth login success username=%s user_id=%s", normalized_username, user.id)
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "user": self.serialize_user(user),
        }

    def logout(self) -> dict:
        return {"success": True}

    def serialize_user(self, user: User) -> dict:
        return {
            "id": user.id,
            "username": user.username,
            "created_at": user.created_at,
        }


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录后再访问系统",
        )

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录状态已失效，请重新登录",
        )

    try:
        normalized_user_id = int(user_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录状态已失效，请重新登录",
        ) from exc

    user = db.query(User).filter(User.id == normalized_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="当前账号不存在，请重新登录",
        )

    return user
