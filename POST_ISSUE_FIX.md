# 🔍 帖子发布问题排查指南

## 📝 问题症状
发布帖子后，过一会儿帖子就消失了，页面刷新也看不到。

## 🎯 已实施的修复

### 1️⃣ **前端增强错误处理**

**修改文件**：`frontend/src/components/PostForm.vue`

**新增功能**：
- ✅ 显示发帖成功/失败提示
- ✅ 显示网络错误信息
- ✅ 发帖中时禁用按钮
- ✅ 浏览器控制台输出详细日志

### 2️⃣ **论坛页面增强**

**修改文件**：`frontend/src/views/Forum.vue`

**新增功能**：
- ✅ 显示加载状态
- ✅ 显示错误提示
- ✅ 显示"暂无帖子"提示
- ✅ 浏览器控制台输出详细日志

---

## 🔧 现在如何诊断问题？

### 步骤 1：打开浏览器开发工具

在论坛页面按 **F12** 或 **Ctrl+Shift+I** 打开开发工具

### 步骤 2：查看 Console 标签

查看发帖时的日志输出，应该看到：

**正常情况**：
```
发送请求到: http://127.0.0.1:8000/api/posts
请求体: {title: "...", content: "..."}
响应状态: 200
响应数据: {id: 1, title: "...", content: "...", created_at: "..."}
```

**错误情况**：
```
发送请求到: http://127.0.0.1:8000/api/posts
请求体: {title: "...", content: "..."}
响应状态: 500
响应数据: {detail: "...错误信息..."}
```

### 步骤 3：检查 Network 标签

1. 打开 Network 标签
2. 发布新帖子
3. 查看 POST 请求到 `/api/posts`
4. 检查 Response 部分是否有错误信息

---

## 🛠️ 常见问题排查

### ❌ 问题 1：页面显示"获取帖子失败"

**原因**：后端服务未运行或地址错误

**解决**：
```batch
cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\backend
DIAGNOSE.bat
```

确保看到：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### ❌ 问题 2：发帖后显示错误信息

**原因**：后端没有正确保存到数据库

**排查步骤**：

1. **检查数据库文件是否存在**：
```batch
cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\backend
dir *.db
```

应该看到 `campus.db` 文件

2. **检查数据库权限**：
```batch
cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\backend
attrib campus.db
```

3. **如果文件不存在或权限有问题**，删除后端虚拟环境重建：
```batch
rmdir /s /q campus_env
DIAGNOSE.bat
```

### ❌ 问题 3：跨域请求失败

**症状**：浏览器控制台显示 CORS 错误

**原因**：后端 CORS 配置有问题

**解决**：检查 `backend/main.py` 中的 CORS 配置
```python
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
```

如果前端访问地址不同，需要添加对应的地址

---

## 📊 完整的数据流

发帖流程应该是这样的：

```
用户发布帖子
    ↓
前端 PostForm.vue 发送 POST 请求到 http://127.0.0.1:8000/api/posts
    ↓
后端 main.py 的 create_post() 函数接收请求
    ↓
保存帖子到 SQLite 数据库 (campus.db)
    ↓
返回新帖子的完整数据给前端（包含 ID 和时间戳）
    ↓
前端 PostForm.vue 接收响应，清空表单，触发 @post-success 事件
    ↓
Forum.vue 接收事件，调用 fetchPosts()
    ↓
前端发送 GET 请求到 http://127.0.0.1:8000/api/posts
    ↓
后端查询所有帖子并返回
    ↓
前端收到帖子列表，显示在页面上
```

---

## ✅ 检查清单

- [ ] 后端服务正在运行（能访问 http://127.0.0.1:8000/docs）
- [ ] 前端服务正在运行（能访问 http://localhost:5173）
- [ ] 后端数据库文件存在：`backend/campus.db`
- [ ] 浏览器控制台没有 CORS 错误
- [ ] 浏览器控制台显示响应状态 200
- [ ] 数据库中有新帖子（可用 SQLite 工具查看）

---

## 🔬 手动测试后端 API

用 cmd 测试后端是否正常工作：

```batch
cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle\backend
```

然后用 curl（Windows 10+ 内置）：

```batch
REM 获取所有帖子
curl http://127.0.0.1:8000/api/posts

REM 发布新帖子
curl -X POST http://127.0.0.1:8000/api/posts ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"测试\",\"content\":\"测试内容\"}"
```

如果返回成功的 JSON 数据，说明后端 API 正常

---

## 📱 关键改进

| 功能 | 之前 | 现在 |
|------|------|------|
| 发帖成功提示 | ❌ 无 | ✅ 显示成功信息 |
| 发帖失败提示 | ❌ 无 | ✅ 显示错误原因 |
| 网络错误处理 | ❌ 无 | ✅ 显示错误详情 |
| 加载状态 | ❌ 无 | ✅ 显示加载中 |
| 调试信息 | ❌ 无 | ✅ 浏览器控制台完整日志 |
| 空列表提示 | ❌ 无 | ✅ 显示"暂无帖子" |

---

**刷新浏览器后重新试试！应该能看到完整的错误信息和提示了。** 🚀
