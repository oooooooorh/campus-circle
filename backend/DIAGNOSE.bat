@echo off
chcp 65001 >nul
cd /d "C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\backend"

echo.
echo ================================================
echo   校园圈后端 - 快速诊断工具
echo ================================================
echo.

REM 检查 Python
echo [1/4] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未找到
    goto :end
) else (
    echo ✓ Python 已安装
)

REM 检查虚拟环境
echo [2/4] 检查虚拟环境...
if not exist "campus_env" (
    echo ⚠ 虚拟环境不存在，正在创建...
    python -m venv campus_env
)
call campus_env\Scripts\activate.bat

REM 检查依赖
echo [3/4] 检查依赖...
pip list | findstr fastapi >nul 2>&1
if errorlevel 1 (
    echo ⚠ 依赖缺失，正在安装...
    pip install fastapi uvicorn sqlalchemy python-multipart pydantic python-dotenv -q
) else (
    echo ✓ 依赖已安装
)

REM 测试导入
echo [4/4] 测试模块导入...
python -c "import models, schemas, database; print('✓ 模块导入成功')" 2>&1

echo.
echo ================================================
echo   诊断完成！现在启动服务器...
echo ================================================
echo.
echo API 文档: http://127.0.0.1:8000/docs
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

:end
pause
