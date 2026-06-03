@echo off
echo ========================================
echo   AI 面试系统 v3.0 - 后端启动脚本
echo ========================================
echo.
echo 启动后端服务...
cd /d d:\Projects\ai_interview_v2\backend
start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
timeout /t 3 /nobreak >nul
echo 后端已启动: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
echo 按任意键停止服务...
pause >nul
taskkill /f /im python.exe /fi "WINDOWTITLE eq *uvicorn*" >nul 2>&1
