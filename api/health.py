"""
Vercel Serverless Function 入口 —— 将 FastAPI 应用暴露为 serverless。
"""

from app.main import app

# Vercel Python runtime 需要这个变量
from vercel_wsgi import make_lambda
handler = make_lambda(app)
