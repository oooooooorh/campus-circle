@echo off
chcp 65001 >nul
REM 一键启动后端 - 自动创建虚拟环境并启动

cd /d "C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\backend"

if not exist "campus_env" (
    echo [创建虚拟环境...]
    python -m venv campus_env
)

echo [激活虚拟环境...]
call campus_env\Scripts\activate.bat

echo [安装依赖...]
pip install fastapi uvicorn sqlalchemy python-multipart pydantic python-dotenv -q

echo.
echo ================================================
echo   后端服务已启动
echo ================================================
echo.
echo API 主页: http://127.0.0.1:8000
echo API 文档: http://127.0.0.1:8000/docs
echo.
echo [按 Ctrl+C 停止服务]
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
