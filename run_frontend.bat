@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 定义项目路径（绝对路径）
set PROJECT_ROOT=C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle
set FRONTEND_PATH=%PROJECT_ROOT%\frontend

cd /d "%FRONTEND_PATH%"

echo.
echo ==================================================
echo 校园圈 - 前端启动脚本
echo ==================================================
echo 项目路径: %PROJECT_ROOT%
echo 前端路径: %FRONTEND_PATH%
echo 当前目录: %cd%
echo ==================================================
echo.

REM 检查 node_modules 是否存在
if not exist "node_modules" (
    echo [正在安装依赖...]
    call npm install
)

echo.
echo [✓] 前端服务启动中...
echo 访问地址: http://localhost:5173
echo.

REM 启动 Vite 开发服务器
call npm run dev

pause
