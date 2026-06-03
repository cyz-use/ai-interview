"""
Vercel Serverless 入口 —— 带错误诊断。
"""

import json, sys, os, traceback

os.environ.setdefault("DEEPSEEK_API_KEY", "")
os.environ.setdefault("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
os.environ.setdefault("MODEL_NAME", "deepseek-chat")
os.environ.setdefault("DATABASE_URL", "sqlite:///./interview.db")
os.environ.setdefault("JWT_SECRET", "changeme2024xyz")

sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.main import app
except Exception as e:
    # 如果导入失败，创建一个简单的诊断 app
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/api/health")
    def health():
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}

    @app.get("/{path:path}")
    def catch_all(path: str):
        return {"error": str(e), "traceback": traceback.format_exc(), "path": path}
