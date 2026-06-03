"""
Vercel Serverless 入口 —— 后端 API 处理器。

文件位置：项目根目录 /api/index.py
Vercel 自动将 /api/* 请求路由到此函数。
"""

import sys, os

# 添加 backend 目录到 Python 搜索路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# 设置必要环境变量
os.environ.setdefault("DEEPSEEK_API_KEY", "")
os.environ.setdefault("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
os.environ.setdefault("MODEL_NAME", "deepseek-chat")
os.environ.setdefault("DATABASE_URL", "sqlite:///./interview.db")
os.environ.setdefault("JWT_SECRET", "changeme2024xyz")

from app.main import app
