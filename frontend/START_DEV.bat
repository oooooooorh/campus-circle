@echo off
REM 一键启动前端 - 自动安装依赖并启动

cd /d "C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\frontend"

if not exist "node_modules" (
    echo [安装依赖...]
    call npm install
)

echo.
echo ================================================
echo   前端服务已启动
echo ================================================
echo.
echo 访问地址: http://localhost:5173
echo.
echo [按 Ctrl+C 停止服务]
echo.

call npm run dev
