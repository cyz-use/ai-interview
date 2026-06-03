"""
Vercel Serverless 入口 —— 后端 API 处理器。
"""

import os

os.environ.setdefault("DEEPSEEK_API_KEY", "")
os.environ.setdefault("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
os.environ.setdefault("MODEL_NAME", "deepseek-chat")
os.environ.setdefault("DATABASE_URL", "sqlite:///./interview.db")
os.environ.setdefault("JWT_SECRET", "changeme2024xyz")

from app.main import app
