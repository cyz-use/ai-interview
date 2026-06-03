"""
认证 API —— 用户注册、登录、Token 管理（基于 SQLAlchemy 数据库）。
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.config import settings
from app.models.db import User
from app.models.schemas import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter()

# ========== JWT ==========
security = HTTPBearer()


def create_access_token(user_id: str) -> str:
    """生成 JWT Token。"""
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """验证 JWT Token，返回 user_id。"""
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub", "")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token 无效")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")


def hash_password(password: str) -> str:
    """哈希密码。"""
    password_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """验证密码。"""
    password_bytes = password.encode("utf-8")[:72]
    return bcrypt.checkpw(password_bytes, hashed.encode("utf-8"))


# ========== 端点 ==========


@router.post("/register", response_model=TokenResponse)
async def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """注册新用户。"""
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == request.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否已存在
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    user = User(
        username=request.username,
        email=request.email,
        password_hash=hash_password(request.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expire_minutes * 60,
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """用户登录。"""
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """获取当前用户信息。"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserResponse(
        id=UUID(user.id),
        username=user.username,
        email=user.email,
        trial_interviews_used=user.trial_interviews_used or 0,
        max_trial_interviews=user.max_trial_interviews or 3,
        subscription_tier=user.subscription_tier or "free",
        created_at=user.created_at,
    )
