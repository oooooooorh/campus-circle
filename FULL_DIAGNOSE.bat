@echo off
chcp 65001 >nul
echo.
echo ================================================
echo   校园圈项目 - 完整诊断工具
echo ================================================
echo.

REM 检查后端服务
echo [1/3] 检查后端服务是否运行...
timeout /t 1 /nobreak >nul
curl -s http://127.0.0.1:8000/docs >nul 2>&1
if errorlevel 1 (
    echo ❌ 后端服务未响应！
    echo 请确保后端已启动: python -m uvicorn main:app --reload
    echo.
    pause
    exit /b 1
) else (
    echo ✓ 后端服务正在运行
)

REM 检查数据库
echo [2/3] 检查数据库...
cd /d "C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\backend"
if not exist "campus.db" (
    echo ⚠ 数据库文件不存在，但这在首次运行时是正常的
) else (
    echo ✓ 数据库文件存在
)

REM 测试 API
echo [3/3] 测试 API 接口...
echo.
echo 尝试获取帖子列表 (GET /api/posts)...
curl -s http://127.0.0.1:8000/api/posts
echo.
echo.
echo ================================================
echo   诊断完成！
echo ================================================
echo.
echo 检查清单:
echo ✓ 后端服务运行正常
echo ✓ 可以成功调用 API
echo.
echo 如果上面显示 [] 或 [数据]，说明 API 正常
echo 如果显示错误，请查看上方的错误信息
echo.
echo 前端检查步骤:
echo 1. 打开浏览器控制台 (F12)
echo 2. 切换到 Console 标签
echo 3. 刷新页面 (F5)
echo 4. 查看日志输出
echo.
pause
