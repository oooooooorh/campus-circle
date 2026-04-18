@echo off
REM 快速打开 cmd 并进入项目目录

cd /d "C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle"

REM 显示菜单
echo.
echo ========================================
echo   校园圈项目 - 快速启动菜单
echo ========================================
echo.
echo 当前目录: %cd%
echo.
echo 请选择操作:
echo   1. 启动后端服务 (python uvicorn)
echo   2. 启动前端服务 (npm dev)
echo   3. 进入后端目录
echo   4. 进入前端目录
echo   5. 查看项目结构
echo   6. 打开项目根目录 (explorer)
echo   0. 退出
echo.

set /p choice=请输入选择 (0-6): 

if "%choice%"=="1" (
    start cmd /k "cd /d %cd%\backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
) else if "%choice%"=="2" (
    start cmd /k "cd /d %cd%\frontend && npm run dev"
) else if "%choice%"=="3" (
    cd /d "%cd%\backend"
    cmd /k
) else if "%choice%"=="4" (
    cd /d "%cd%\frontend"
    cmd /k
) else if "%choice%"=="5" (
    tree /f
    pause
) else if "%choice%"=="6" (
    explorer "%cd%"
) else if "%choice%"=="0" (
    exit
) else (
    echo 无效的选择
    pause
    goto :start
)
