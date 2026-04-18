# 🔍 前后端对接调试指南

## 📋 问题症状
- 后端已启动 ✓
- 前端已启动 ✓
- 页面显示 "加载中..." 但不显示帖子列表

## 🎯 诊断步骤

### 步骤 1️⃣：验证后端 API

**方法 A：用浏览器直接访问**
```
http://127.0.0.1:8000/api/posts
```

**预期结果**：
- ✅ 显示 `[]` (空列表) 或 `[{...}]` (有数据)
- ❌ 显示错误信息或 404

**方法 B：用诊断工具**
```batch
cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle
FULL_DIAGNOSE.bat
```

---

### 步骤 2️⃣：检查前端控制台

**打开开发工具**：
- 按 **F12** 或 **Ctrl+Shift+I**

**检查 Console 标签**：

**正常情况**下应该看到：
```
获取帖子列表...
发送请求到: http://127.0.0.1:8000/api/posts
响应状态: 200
获取帖子成功: []
```

**错误情况**下可能显示：
```
❌ 获取帖子失败: 网络错误: Failed to fetch
❌ 获取帖子失败: 获取帖子失败: HTTP 404
```

---

### 步骤 3️⃣：检查 Network 标签

**操作步骤**：
1. 打开 F12 → Network 标签
2. 刷新页面 F5
3. 查看请求列表，找到 `/api/posts` 的 GET 请求
4. 点击查看详情：
   - **Headers**：请求头信息
   - **Response**：后端返回的数据
   - **Status**：HTTP 状态码

**预期结果**：
- Status: **200** (成功)
- Response: **`[]`** 或 **`[{...}]`**

**错误示例**：
- Status: **404** (未找到) - 路由错误
- Status: **500** (服务器错误) - 后端代码错误
- Status: **CORS error** - 跨域问题

---

## 🛠️ 常见问题解决

### ❌ 问题 1：后端显示 404

**原因**：路由不存在或拼写错误

**检查**：`backend/main.py` 中的路由定义
```python
@app.get("/api/posts")  # 确保这里没有拼写错误
def get_posts(db: Session = Depends(database.get_db)):
    ...
```

**解决**：
- 检查前端请求 URL 是否正确：`http://127.0.0.1:8000/api/posts`
- 检查后端路由是否定义：`@app.get("/api/posts")`

---

### ❌ 问题 2：后端显示 500 (服务器错误)

**原因**：后端代码出错

**查看错误信息**：
1. 打开后端终端窗口
2. 查看错误堆栈信息
3. 常见错误：
   - `AttributeError: module 'models' has no attribute 'Post'`
   - `ModuleNotFoundError: No module named 'xxx'`
   - `TypeError: ...`

**解决**：
- 检查 `models.py` 和 `database.py` 是否正确
- 确保所有导入都正确
- 重启后端服务

---

### ❌ 问题 3：跨域错误 (CORS)

**症状**：浏览器控制台显示
```
Access to XMLHttpRequest at 'http://127.0.0.1:8000/api/posts' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**原因**：后端没有允许前端的地址

**解决**：检查 `backend/main.py` 的 CORS 配置
```python
origins = [
    "http://localhost:5173",      # ← 必须有这行
    "http://127.0.0.1:5173",      # ← 或这行
]
```

---

### ❌ 问题 4：网络错误 "Failed to fetch"

**原因**：
- 后端服务没有运行
- 地址错误（如 127.0.0.1 vs localhost）
- 防火墙阻止

**解决**：
1. 确保后端运行：访问 `http://127.0.0.1:8000`
2. 确保前端配置的地址正确
3. 检查防火墙设置

---

## 🔧 快速修复清单

| 问题 | 检查项 | 修复方法 |
|------|--------|---------|
| 404 | 路由定义 | 检查 `main.py` 的 `@app.get()` |
| 500 | 后端代码 | 查看后端终端的错误信息 |
| CORS | 跨域配置 | 检查 CORS 中间件配置 |
| Failed to fetch | 服务状态 | 重启后端服务 |
| 空列表 | 数据库 | 正常，数据库没有数据 |

---

## 📊 完整的请求流程

```
前端发送请求
    ↓
HTTP GET http://127.0.0.1:8000/api/posts
    ↓
后端收到请求，调用 get_posts() 函数
    ↓
从数据库查询数据
    ↓
返回 JSON 数据给前端
    ↓
前端接收数据，显示在页面上
```

---

## ✅ 验证成功的标志

当一切正常时，你会看到：

1. **浏览器地址栏**：`http://localhost:5173/forum`
2. **页面显示**：
   - ✅ 导航栏正常
   - ✅ 发帖表单正常
   - ✅ 帖子列表显示（即使是空的）
3. **浏览器控制台**：
   ```
   获取帖子成功: []
   ```
4. **页面提示**：显示 "还没有帖子，来发第一个吧！" 或帖子列表

---

## 🚀 现在就开始诊断！

### 快速测试：

```batch
REM 运行完整诊断
cd /d C:\Users\Administrator\Desktop\Vue_WorkSpace\校园圈\campus-circle
FULL_DIAGNOSE.bat
```

### 或手动测试：

```batch
REM 获取所有帖子
curl http://127.0.0.1:8000/api/posts

REM 发布新帖子
curl -X POST http://127.0.0.1:8000/api/posts ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"测试\",\"content\":\"测试内容\"}"
```

---

**告诉我浏览器控制台显示的具体错误信息，我可以帮你精确定位问题！** 🔍
