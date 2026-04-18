# 🎯 校园圈项目启动指南

## 📂 项目路径
```
C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle
```

## ⚡ 最快启动方式（推荐）

### 只需 2 步：

#### 步骤 1️⃣：启动后端
在项目根目录找到 `backend` 文件夹，双击运行：
```
backend/START_SERVER.bat
```

**预期输出：**
```
后端服务已启动
API 文档: http://127.0.0.1:8000/docs
```

#### 步骤 2️⃣：启动前端
在项目根目录找到 `frontend` 文件夹，双击运行：
```
frontend/START_DEV.bat
```

**预期输出：**
```
前端服务已启动
访问地址: http://localhost:5173
```

---

## 🌐 访问应用

| 应用 | 地址 | 说明 |
|------|------|------|
| 前端应用 | http://localhost:5173 | Vue 应用界面 |
| 后端 API | http://127.0.0.1:8000 | FastAPI 首页 |
| API 文档 | http://127.0.0.1:8000/docs | Swagger 交互式文档 |
| API 备选文档 | http://127.0.0.1:8000/redoc | ReDoc 文档 |

---

## 📁 项目文件说明

### 🚀 启动脚本

| 脚本 | 位置 | 用途 |
|------|------|------|
| `START_SERVER.bat` | `/backend/` | 启动后端服务（推荐） |
| `START_DEV.bat` | `/frontend/` | 启动前端服务（推荐） |
| `run_backend.bat` | `/` | 后端启动（带菜单） |
| `run_frontend.bat` | `/` | 前端启动（带菜单） |
| `menu.bat` | `/` | 快速菜单选择 |

### 📚 文档

| 文件 | 说明 |
|------|------|
| `README.md` | 项目总体说明 |
| `WINDOWS_SETUP.md` | Windows 详细设置指南 |
| `QUICK_START.md` | 本文件 |

---

## ❓ 遇到问题？

### 问题 1：双击脚本没反应

**解决**：用 cmd 手动运行
```batch
cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\backend
START_SERVER.bat
```

### 问题 2：缺少依赖

**解决**：手动安装
```batch
cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\backend
pip install -r requirements.txt

cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\frontend
npm install
```

### 问题 3：端口被占用

**解决**：修改脚本中的端口号
- 后端：改 `--port 8000` 为其他端口如 `8001`
- 前端：改 `vite.config.js` 中的 `port: 5173` 为其他如 `5174`

### 问题 4：虚拟环境出错

**解决**：删除并重建
```batch
cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\backend
rmdir /s /q campus_env
python -m venv campus_env
```

---

## ✅ 检查清单

启动前确保：
- [ ] Python 已安装（`python --version`）
- [ ] Node.js 已安装（`node --version`）
- [ ] 路径正确：`C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle`

---

## 💡 进阶使用

### 开发流程
1. 后端修改 → 自动重载（`--reload` 标志）
2. 前端修改 → 热更新（HMR 自动更新浏览器）

### 停止服务
- 按 `Ctrl + C` 在命令行中停止

### 查看详细设置
参考 `WINDOWS_SETUP.md` 了解更多技术细节

---

**问题？查看 `WINDOWS_SETUP.md` 的详细故障排除指南！** 🔧
