"""
FastAPI 应用入口 —— AI 面试系统 v3.0。

运行方式：uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, interview, resume, rag, voice, subscription
from app.models.db import init_db
from app.models.schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。"""
    # 启动时：初始化数据库表
    print("[INFO] AI 面试系统 v3.0 启动中...")
    print("[INFO] 初始化数据库...")
    init_db()
    print("[INFO] API 文档: http://localhost:8000/docs")
    print("[INFO] 健康检查: http://localhost:8000/api/health")
    yield
    # 关闭时
    print("[INFO] AI 面试系统 v3.0 已关闭")


app = FastAPI(
    title="AI 面试系统 v3.0",
    description="基于 LangGraph 多智能体协同的 AI 模拟面试平台",
    version="3.0.0",
    lifespan=lifespan,
)

# ========== CORS 配置 ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 路由注册 ==========
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(interview.router, prefix="/api/interview", tags=["面试"])
app.include_router(resume.router, prefix="/api/resume", tags=["简历"])
app.include_router(rag.router, prefix="/api/rag", tags=["知识库"])
app.include_router(voice.router, prefix="/ws", tags=["语音面试"])
app.include_router(subscription.router, prefix="/api/subscription", tags=["订阅"])


# ========== 健康检查 ==========


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点 —— 供 Docker / K8s 探活使用。"""
    return HealthResponse(
        status="ok",
        version="3.0.0",
        postgres="sqlite",
        redis="disabled",
    )
