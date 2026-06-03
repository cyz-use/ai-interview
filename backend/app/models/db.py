"""
SQLAlchemy ORM 模型 —— 数据库表定义。

支持两种模式：
- 开发模式（默认）：SQLite（无需额外安装，即开即用）
- 生产模式：PostgreSQL + pgvector（向量检索）
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker


class Base(DeclarativeBase):
    """ORM 基类。"""
    pass


# =========================== 用户表 ===========================


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    trial_interviews_used = Column(Integer, default=0)  # 已使用试用次数
    max_trial_interviews = Column(Integer, default=3)    # 最大试用次数
    subscription_tier = Column(String(20), default="free")  # free | pro | enterprise
    subscription_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")


# =========================== 简历表 ===========================


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_text = Column(Text, nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf, docx, doc, txt
    content_hash = Column(String(64), nullable=False)  # SHA-256 去重
    file_size_bytes = Column(Integer, default=0)
    minio_object_key = Column(String(512), nullable=True)
    candidate_profile_json = Column(Text, nullable=True)  # JSON 格式的候选人画像
    analysis_status = Column(String(20), default="PENDING")  # PENDING | PROCESSING | COMPLETED | FAILED
    analysis_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联
    user = relationship("User", back_populates="resumes")
    interviews = relationship("Interview", back_populates="resume")


# =========================== 面试会话表 ===========================


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)
    target_job = Column(String(128), nullable=False)
    candidate_profile_json = Column(Text, nullable=True)  # JSON
    status = Column(String(20), default="IN_PROGRESS")  # IN_PROGRESS | COMPLETED | ABANDONED
    main_question_index = Column(Integer, default=0)
    max_main_questions = Column(Integer, default=5)
    followup_count = Column(Integer, default=0)
    current_round = Column(Integer, default=0)
    state_snapshot_json = Column(Text, nullable=True)  # 完整 InterviewState JSON，断线恢复
    total_score = Column(Integer, nullable=True)
    final_report_json = Column(Text, nullable=True)  # JSON
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # 关联
    user = relationship("User", back_populates="interviews")
    resume = relationship("Resume", back_populates="interviews")
    rounds = relationship("InterviewRound", back_populates="interview", cascade="all, delete-orphan")


# =========================== 面试轮次表 ===========================


class InterviewRound(Base):
    __tablename__ = "interview_rounds"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String(36), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    round_number = Column(Integer, nullable=False)
    question_type = Column(String(10), nullable=False)  # main | followup
    main_topic = Column(String(64), nullable=True)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=True)
    tech_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    logic_score = Column(Float, nullable=True)
    brief_comment = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联
    interview = relationship("Interview", back_populates="rounds")


# =========================== 知识库文档表 ===========================


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    content_hash = Column(String(64), nullable=False)
    minio_object_key = Column(String(512), nullable=True)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联
    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


# =========================== 文档分块表 ===========================


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    # embedding 仅在 PostgreSQL + pgvector 时可用
    embedding_json = Column(Text, nullable=True)  # JSON 序列化的向量（SQLite 兼容）
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联
    document = relationship("Document", back_populates="chunks")


# =========================== 数据库引擎工厂 ===========================


from app.config import settings


def get_engine():
    """根据配置创建数据库引擎（开发: SQLite, 生产: PostgreSQL）。"""
    if settings.database_url.startswith("sqlite"):
        return create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
            echo=False,
        )
    else:
        return create_engine(settings.database_url, echo=False, pool_size=10, max_overflow=20)


def get_session_factory():
    """获取 Session 工厂。"""
    engine = get_engine()
    return sessionmaker(bind=engine)


def init_db():
    """初始化数据库表结构（开发用，生产请用 Alembic 迁移）。"""
    engine = get_engine()
    Base.metadata.create_all(engine)
