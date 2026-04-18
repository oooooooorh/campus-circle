@echo off
REM 校园圈项目启动脚本（后端）
cd /d "%~dp0backend"
echo [校园圈后端] 正在启动服务器...
echo 后端将运行在: http://127.0.0.1:8000
echo API文档: http://127.0.0.1:8000/docs
pause
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
