"""Pydantic 请求/响应模型 —— 定义所有 API 的数据契约。"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# =========================== 认证相关 ===========================

class UserRegisterRequest(BaseModel):
    """注册请求。"""
    username: str = Field(..., min_length=2, max_length=64, description="用户名")
    email: str = Field(..., max_length=255, description="邮箱")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class UserLoginRequest(BaseModel):
    """登录请求。"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """Token 响应。"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """用户信息。"""
    id: UUID
    username: str
    email: str
    trial_interviews_used: int = 0
    max_trial_interviews: int = 3
    subscription_tier: str = "free"
    created_at: datetime


class SubscriptionStatus(BaseModel):
    """订阅状态。"""
    trial_interviews_used: int
    max_trial_interviews: int
    trial_remaining: int
    subscription_tier: str
    can_interview: bool


# =========================== 面试相关 ===========================

class StartInterviewRequest(BaseModel):
    """开始面试请求。"""
    resume_text: str = Field(..., min_length=10, description="简历文本内容")
    target_job: str = Field(..., min_length=1, max_length=128, description="目标岗位")


class CandidateProfile(BaseModel):
    """候选人画像。"""
    skills: list[str] = []
    years_of_experience: int = 0
    education: str = "未知"
    project_keywords: list[str] = []
    match_score: int = 0
    summary: str = ""


class StartInterviewResponse(BaseModel):
    """开始面试响应。"""
    session_id: str
    first_question: str
    candidate_profile: CandidateProfile


class AnswerRequest(BaseModel):
    """提交回答请求。"""
    answer: str = Field(..., min_length=1, description="候选人的回答")


class RoundScore(BaseModel):
    """单轮评分。"""
    tech_score: float = 0
    communication_score: float = 0
    logic_score: float = 0
    brief_comment: str = ""


class FinalReport(BaseModel):
    """最终评估报告。"""
    total_score: int = 0
    dimensions: dict = {}
    strengths: list[str] = []
    weak_points: list[str] = []
    improvement_suggestions: list[str] = []


class InterviewSessionResponse(BaseModel):
    """面试会话信息。"""
    session_id: UUID
    target_job: str
    status: str
    total_score: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class InterviewHistoryResponse(BaseModel):
    """面试历史列表。"""
    items: list[InterviewSessionResponse]
    total: int
    page: int
    size: int


# =========================== 简历相关 ===========================

class ResumeUploadResponse(BaseModel):
    """简历上传响应。"""
    resume_id: UUID
    filename: str
    status: str = "PENDING"


class ResumeStatusResponse(BaseModel):
    """简历分析状态。"""
    resume_id: UUID
    status: str  # PENDING | PROCESSING | COMPLETED | FAILED
    candidate_profile: Optional[CandidateProfile] = None
    error: Optional[str] = None


class ResumeListItem(BaseModel):
    """简历列表项。"""
    id: UUID
    filename: str
    created_at: datetime
    status: str
    match_score: Optional[int] = None


# =========================== Demo 简历 ===========================

class DemoResumeItem(BaseModel):
    """Demo 简历摘要。"""
    index: int
    preview: str
    length: int


class DemoResumeDetail(BaseModel):
    """Demo 简历详情。"""
    text: str


# =========================== RAG 知识库 ===========================

class DocumentUploadResponse(BaseModel):
    """文档上传响应。"""
    document_id: UUID
    filename: str
    chunk_count: int


class DocumentListItem(BaseModel):
    """文档列表项。"""
    id: UUID
    filename: str
    file_type: str
    chunk_count: int
    created_at: datetime


class RAGChatRequest(BaseModel):
    """RAG 对话请求。"""
    query: str = Field(..., min_length=1, description="查询内容")


# =========================== SSE 事件 ===========================

class SSEEvent(BaseModel):
    """SSE 流事件。"""
    node: str = ""
    status: str = ""
    question: Optional[str] = None
    round_scores: Optional[list[RoundScore]] = None
    next_question_type: Optional[str] = None
    main_question_index: Optional[int] = None
    followup_count: Optional[int] = None
    interview_completed: bool = False
    final_report: Optional[FinalReport] = None


# =========================== 通用 ===========================

class HealthResponse(BaseModel):
    """健康检查响应。"""
    status: str = "ok"
    version: str = "3.0.0"
    postgres: str = "unknown"
    redis: str = "unknown"
