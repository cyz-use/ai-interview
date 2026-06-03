"""
Vercel Python Serverless Function 入口。

路径说明：
- 此文件在 backend/api/index.py
- Vercel Python Runtime 自动将 /api/* 的请求路由到这里
- app 变量（ASGI 应用）会被 Vercel 自动识别
"""

import sys
import os

# 把 backend/ 加入 Python 搜索路径
backend_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, backend_dir)

# 设置默认环境变量
os.environ.setdefault("DEEPSEEK_API_KEY", "")
os.environ.setdefault("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
os.environ.setdefault("MODEL_NAME", "deepseek-chat")
os.environ.setdefault("DATABASE_URL", "sqlite:///./interview.db")
os.environ.setdefault("JWT_SECRET", "changeme2024xyz")

from app.main import app

# Vercel 自动识别 app 变量（ASGI 应用）
