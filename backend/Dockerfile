# 使用官方的 Playwright Python 镜像作为基础，已经内置了 Chromium 及其系统依赖
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# 设置工作目录
WORKDIR /app

# 设置环境变量，确保 Python 输出直接打印到终端，不被缓冲
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 首先复制依赖文件并安装，这样可以利用 Docker 缓存
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码到工作目录
COPY . .

# 暴露 FastAPI 运行的端口
EXPOSE 8000

# 直接使用 uvicorn 单进程运行
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
