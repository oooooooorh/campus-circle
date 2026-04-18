@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 定义项目路径（绝对路径）
set PROJECT_ROOT=C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle
set BACKEND_PATH=%PROJECT_ROOT%\backend
set FRONTEND_PATH=%PROJECT_ROOT%\frontend

REM 检查虚拟环境是否存在
if exist "%BACKEND_PATH%\campus_env\Scripts\activate.bat" (
    echo [✓] 虚拟环境已存在
    cd /d "%BACKEND_PATH%"
    call campus_env\Scripts\activate.bat
    echo [✓] 虚拟环境已激活
) else (
    echo [✗] 虚拟环境不存在，正在创建...
    cd /d "%BACKEND_PATH%"
    python -m venv campus_env
    call campus_env\Scripts\activate.bat
    echo [✓] 虚拟环境已创建并激活
)

echo.
echo ==================================================
echo 校园圈 - 后端启动脚本
echo ==================================================
echo 项目路径: %PROJECT_ROOT%
echo 后端路径: %BACKEND_PATH%
echo 当前目录: %cd%
echo ==================================================
echo.

REM 安装依赖
echo [正在检查依赖...]
pip install -r requirements.txt -q

echo.
echo [✓] 后端服务启动中...
echo API 文档: http://127.0.0.1:8000/docs
echo.

REM 启动 Uvicorn 服务器
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
