# 校园圈 (Campus Circle)

校园圈是一个基于前后端分离架构编排的校园综合服务平台。系统提供了校园课表查询（通过 Playwright 自动化爬取）、论坛讨论、场馆预约等功能。

## 🛠️ 技术栈 (Tech Stack)

### 前端 (Frontend)
*   **框架**: Vue 3 (Composition API)
*   **构建工具**: Vite
*   **路由**: Vue Router

### 后端 (Backend)
*   **框架**: FastAPI (Python)
*   **自动化爬虫**: Playwright (用于异步爬取校园课表数据)
*   **数据库**: SQLite (本地开发) + SQLAlchemy / ORM
*   **服务器**: Uvicorn

---

## 📂 项目结构 (Project Structure)

```text
campus-circle/
├── backend/                # 后端代码目录
│   ├── main.py             # FastAPI 应用入口与系统 lifespan 管理
│   ├── api.py              # 路由 endpoints
│   ├── core.py             # 核心配置
│   ├── database.py         # 数据库连接
│   ├── models.py           # 数据库模型 (SQLAlchemy)
│   ├── schemas.py          # Pydantic 校验模型
│   ├── scraper.py          # Playwright 自动爬虫核心逻辑
│   └── requirements.txt    # Python 依赖清单
├── frontend/               # 前端代码目录
│   ├── package.json        # NPM 依赖与脚本
│   ├── vite.config.js      # Vite 配置文件
│   └── src/                # 源码目录 (components, views, router 等)
└── .gitignore              # Git 忽略配置
```

---

## 🚀 快速启动 (Quick Start)

### 1. 环境准备 (Prerequisites)
*   **Python**: 3.8+ (推荐使用 Conda 虚拟环境)
*   **Node.js**: 16.x+ (建议使用 LTS 版本)
*   **包管理器**: npm 或 yarn, pip

### 2. 后端部署 (Backend Setup)

我们建议您使用 Conda 创建名为 `campus_env` 的虚拟环境：

```bash
# 激活环境
conda activate campus_env

# 进入后端目录
cd backend

# 安装 Python 依赖包
pip install -r requirements.txt

# 安装 Playwright 所需的浏览器内核
playwright install

# 启动后端服务 (默认在 8000 端口)
python run_server.py
# 或使用: python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. 前端部署 (Frontend Setup)

打开一个新的终端窗口：

```bash
# 进入前端目录
cd frontend

# 安装 Node 依赖
npm install

# 启动前端开发服务器 (默认在 5173/5175 端口)
npm run dev
```

---

## ✨ 核心功能 (Key Features)

*   **课表查询**: 通过 Playwright 引擎自动化爬取教务系统数据，映射并在前端进行精确的可视化排版 (支持 1-15 节课的跨度图表展示)。
*   **校园论坛**: 用户可以浏览、发布帖子及参与站内讨论。
*   **场馆预约**: 支持学生在线查看和预约校园可用场地资源。

---

## 🤝 团队协作指南 (Git 工作流)

1. **获取最新代码**: `git pull origin main`
2. **创建分支开发**: `git checkout -b feature/your-feature-name`
3. **提交代码**: `git commit -m "feat: 添加了XXX功能"`
4. **推送到远程**: `git push origin feature/your-feature-name`
5. 注意：本项目已配置 `.gitignore`，诸如 `node_modules/`, `venv/`, `__pycache__/` 及本地 `*.db` 数据库文件已被忽略，提交时请直接执行 `git add .`。
