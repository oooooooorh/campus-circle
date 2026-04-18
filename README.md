# 校园圈 Campus Circle

一个集论坛、课表同步、按摩预约于一体的校园社交应用。

## 📋 项目结构

```
campus-circle/
├── backend/                # FastAPI 后端
│   ├── main.py            # 主应用文件
│   ├── database.py        # 数据库配置
│   ├── models.py          # SQLAlchemy 数据模型
│   ├── schemas.py         # Pydantic 数据验证模型
│   ├── requirements.txt    # Python 依赖
│   └── .env               # 环境变量
├── frontend/              # Vue 3 前端
│   ├── src/
│   │   ├── components/    # 可复用组件
│   │   ├── views/         # 页面
│   │   ├── router/        # 路由配置
│   │   ├── App.vue        # 主容器
│   │   ├── main.js        # 入口文件
│   │   └── style.css      # 全局样式
│   ├── package.json       # Node 依赖
│   ├── vite.config.js     # Vite 配置
│   └── index.html         # HTML 入口
├── start_backend.bat      # 启动后端脚本
├── start_frontend.bat     # 启动前端脚本
└── README.md             # 本文件
```

## 🚀 快速启动

### 前置条件

- **后端**：Python 3.8+ 
- **前端**：Node.js 16+

### 方式一：使用启动脚本（推荐）

在项目根目录打开 cmd，双击或运行：

```bash
# 后端（新开 cmd 窗口）
start_backend.bat

# 前端（新开 cmd 窗口）
start_frontend.bat
```

### 方式二：手动启动

**启动后端：**

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端地址：http://127.0.0.1:8000  
API 文档：http://127.0.0.1:8000/docs

**启动前端：**

```bash
cd frontend
npm install
npm run dev
```

前端地址：http://localhost:5173

## 📡 API 接口

### 获取所有帖子
- **请求**：`GET /api/posts`
- **响应**：
```json
[
  {
    "id": 1,
    "title": "帖子标题",
    "content": "帖子内容",
    "created_at": "2026-04-18T10:30:00"
  }
]
```

### 发布新帖子
- **请求**：`POST /api/posts`
- **请求体**：
```json
{
  "title": "新帖子标题",
  "content": "新帖子内容"
}
```
- **响应**：同上

## 🔧 已修复的问题

✅ 后端 database.py 导入错误修复  
✅ 添加 CORS 跨域配置  
✅ 前端路由导入路径修正  
✅ Vite 服务器配置补全  
✅ 数据库配置统一  
✅ 创建路由配置文件  
✅ 创建页面组件  
✅ 创建 PostForm 组件  

## 📝 开发指南

- 前端新增组件：放在 `frontend/src/components/`
- 新增页面：放在 `frontend/src/views/`
- 后端新增接口：在 `backend/main.py` 中定义
- 数据库表定义：在 `backend/models.py` 中定义

## 🐛 常见问题

**Q: 后端启动失败？**  
A: 确保已安装依赖：`pip install -r requirements.txt`

**Q: 前端打不开？**  
A: 检查 node_modules，运行 `npm install`

**Q: 跨域错误？**  
A: 已在 main.py 中配置 CORS，允许 5173 端口访问

## 📚 技术栈

- **后端**：FastAPI + SQLAlchemy + SQLite
- **前端**：Vue 3 + Vue Router + Vite
- **数据库**：SQLite3
