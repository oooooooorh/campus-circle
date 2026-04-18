@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ================================================
echo   校园圈 API 测试工具
echo ================================================
echo.

set API_URL=http://127.0.0.1:8000

REM 测试后端连接
echo [测试 1] 检查后端服务...
curl -s %API_URL%/ | find "status" >nul
if errorlevel 1 (
    echo ❌ 后端服务无法连接！
    echo 请确保后端已启动: python -m uvicorn main:app --reload
    pause
    exit /b 1
)
echo ✓ 后端服务正常

echo.
echo [测试 2] 获取所有帖子 (GET /api/posts)
echo.
curl -s %API_URL%/api/posts | find /v "" && echo.
echo.

echo [测试 3] 发布新帖子 (POST /api/posts)
echo.
curl -s -X POST %API_URL%/api/posts ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"测试帖子\",\"content\":\"这是一个测试帖子内容\"}" | find /v "" && echo.
echo.

echo [测试 4] 再次获取所有帖子
echo.
curl -s %API_URL%/api/posts | find /v "" && echo.
echo.

echo ================================================
echo   测试完成！
echo ================================================
echo.
echo 解读结果:
echo 如果显示 [] 说明数据库为空，正常
echo 如果显示 [{...}] 说明有数据，正常
echo 如果显示错误信息，说明 API 有问题
echo.
pause
