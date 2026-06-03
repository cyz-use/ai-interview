"""
Vercel Python Serverless 入口。
"""

import sys, os

# 添加 backend 到搜索路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("DATABASE_URL", "sqlite:///./interview.db")
os.environ.setdefault("JWT_SECRET", "changeme2024xyz")

from app.main import app

# Vercel Python Runtime 自动检测 ASGI app
