@echo off
REM 校园圈项目启动脚本（前端）
cd /d "%~dp0frontend"
echo [校园圈前端] 正在启动开发服务器...
echo 前端将运行在: http://localhost:5173
pause
npm run dev
pause
