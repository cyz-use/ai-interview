"""
依赖注入 —— 数据库会话、认证等可复用的 FastAPI 依赖。
"""

from typing import Generator

from sqlalchemy.orm import Session

from app.models.db import get_session_factory, init_db


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话（FastAPI 依赖注入）。"""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()
