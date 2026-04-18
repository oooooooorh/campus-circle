# 🪟 Windows 系统快速启动指南

## ⚠️ 常见问题解决

### 问题：`系统找不到指定的路径`

**原因**：中文路径 + PowerShell + 虚拟环境激活造成的路径问题

**解决方案**：

#### ✅ 方法 1：使用专用启动脚本（推荐）

在项目根目录 `C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\` 双击运行：

```
run_backend.bat    # 启动后端
run_frontend.bat   # 启动前端
menu.bat           # 快速菜单
```

这些脚本已配置**绝对路径**，完全避免 PowerShell 兼容性问题。

---

#### ✅ 方法 2：手动使用 CMD（不用 PowerShell）

1. **打开 CMD**（不是 PowerShell）
2. 复制粘贴以下命令：

**启动后端：**
```batch
cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**启动前端：**
```batch
cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\frontend
npm run dev
```

---

#### ✅ 方法 3：创建虚拟环境后台启动（高级）

```batch
@echo off
cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\backend
python -m venv campus_env
call campus_env\Scripts\activate.bat
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🎯 正确的启动流程

### 第一次启动（完整流程）：

1. **打开 CMD** （Win + R，输入 `cmd`）

2. **进入项目根目录**：
```batch
cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle
```

3. **后端启动**（新开 CMD 窗口）：
```batch
start cmd /k "cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
```

4. **前端启动**（新开 CMD 窗口）：
```batch
start cmd /k "cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\frontend && npm run dev"
```

### 后续启动（简单方式）：

双击 `run_backend.bat` 和 `run_frontend.bat`

---

## 📋 检查清单

- [ ] 已安装 Python 3.8+
- [ ] 已安装 Node.js 16+
- [ ] 后端依赖已安装：`pip install -r backend/requirements.txt`
- [ ] 前端依赖已安装：`cd frontend && npm install`
- [ ] 可以访问 http://127.0.0.1:8000/docs（后端 API）
- [ ] 可以访问 http://localhost:5173（前端应用）

---

## 🔍 排查步骤

**如果还是出错：**

1. **确认路径存在**：
```batch
dir "C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle"
```

2. **检查 Python 版本**：
```batch
python --version
```

3. **检查 Node 版本**：
```batch
node --version
npm --version
```

4. **清空虚拟环境重建**：
```batch
cd C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\backend
rmdir /s /q campus_env
python -m venv campus_env
call campus_env\Scripts\activate.bat
pip install -r requirements.txt
```

---

## 💡 快速命令参考

| 命令 | 作用 |
|------|------|
| `cd /d <路径>` | 切换到指定路径（/d 用于跨盘符） |
| `dir` | 列出当前目录文件 |
| `start cmd /k <命令>` | 在新 CMD 窗口执行命令并保持窗口打开 |
| `python -m venv <名字>` | 创建虚拟环境 |
| `python -m uvicorn main:app --reload` | 启动 FastAPI 开发服务器 |
| `npm run dev` | 启动 Vite 开发服务器 |

---

## ❌ 避免的操作

- ❌ 不要在 PowerShell 中使用 `&&`（用 `;` 替代）
- ❌ 不要在虚拟环境中重复激活
- ❌ 不要混用 `cd` 和 `chdir`
- ❌ 不要用中文空格或特殊符号在 path 中

---

**需要帮助？直接双击 `menu.bat` 文件！**
