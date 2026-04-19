# 🎉 课表爬虫 API 集成完成！

## 📝 完成情况总结

### ✅ 已集成的模块

| 文件 | 改动 | 说明 |
|------|------|------|
| `backend/main.py` | ✅ 添加 `/api/schedule` 接口 | FastAPI 路由 + 日志 |
| `backend/schemas.py` | ✅ 添加 `LoginInfo` 模型 | 请求/响应数据验证 |
| `backend/scraper.py` | ✅ 参数化函数 + 无头模式 | 核心爬虫逻辑 |
| `frontend/src/api/schedule-api.js` | ✅ Vue 调用示例 | 前端集成模板 |
| `backend/test_api.py` | ✅ 测试脚本 | API 测试工具 |
| `backend/API_GUIDE.md` | ✅ 详细文档 | 使用指南 |

---

## 🚀 快速启动

### 后端启动（需要运行）

```bash
# 终端 1：启动后端服务
cd backend
conda activate campus_env
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 输出应为：
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 前端启动（可选）

```bash
# 终端 2：启动前端
cd frontend
npm run dev

# 访问：http://localhost:5173
```

---

## 📡 API 使用方式

### 1️⃣ 浏览器测试（推荐）

访问 API 文档：**http://127.0.0.1:8000/docs**

在 "Try it out" 中填入：
```json
{
  "username": "2320110098",
  "password": "153624orhA"
}
```

点击 "Execute" 即可测试！

### 2️⃣ Python 脚本测试

```bash
# 直接测试爬虫函数
python test_api.py

# 测试 API 接口
python test_api.py api
```

### 3️⃣ curl 命令测试

```bash
curl -X POST http://127.0.0.1:8000/api/schedule \
  -H "Content-Type: application/json" \
  -d '{"username":"2320110098","password":"153624orhA"}'
```

### 4️⃣ 前端 Vue 调用

```javascript
// 在 Vue 组件中使用
import { getSchedule } from '@/api/schedule-api.js'

const result = await getSchedule('2320110098', '153624orhA')
console.log(result.data)  // 课表数据数组
```

---

## 📊 API 接口定义

### 请求

```http
POST /api/schedule
Content-Type: application/json

{
  "username": "学号",
  "password": "密码"
}
```

### 成功响应（200）

```json
{
  "status": "success",
  "data": [
    {
      "kh": "G006",
      "kcmc": "高等数学（一）",
      "xf": 4,
      "jxb": "1班",
      "zc": "1-18周",
      "xq": "星期一",
      "jc": "1-2节"
    }
  ],
  "count": 11
}
```

### 失败响应（400/500）

```json
{
  "detail": "登录失败，请检查账号密码"
}
```

---

## 🏗️ 代码架构

```
请求流程：

前端表单 (Vue)
    ↓
POST /api/schedule {username, password}
    ↓
FastAPI 路由 (main.py)
    ↓
get_campus_schedule() 异步函数 (scraper.py)
    ↓
Playwright 浏览器自动化
    ├─ 打开教务系统
    ├─ 登录账号
    ├─ 点击课表查询
    └─ 拦截 API 响应
    ↓
解析 JSON 数据
    ↓
返回课表列表
    ↓
前端展示
```

---

## 🔑 核心特性

### ✨ 支持参数化账号

```python
# 支持动态账号密码
result = await get_campus_schedule(
    username="your_student_id",
    password="your_password"
)
```

### ✨ 网络拦截

- 直接拦截教务系统 API 返回
- 获取纯净的 JSON 数据
- 无需 DOM 解析

### ✨ 无头模式

```python
browser = await p.chromium.launch(headless=True)
```

- 不打开浏览器窗口
- 更轻量级
- 适合服务器环境

### ✨ 异步处理

```python
async def get_campus_schedule(username, password):
    # 支持并发多个请求
    # 性能更优
```

---

## 📂 项目文件变更

```
campus-circle/
├── backend/
│   ├── main.py                  (✏️ 修改：添加 /api/schedule)
│   ├── scraper.py               (✏️ 修改：参数化 + 返回列表)
│   ├── schemas.py               (✏️ 修改：添加 LoginInfo)
│   ├── test_api.py              (✨ 新增：测试脚本)
│   ├── API_GUIDE.md             (✨ 新增：使用指南)
│   ├── my_schedule.json         (📄 爬虫数据输出)
│   └── requirements.txt          (无变化)
├── frontend/
│   └── src/api/
│       └── schedule-api.js       (✨ 新增：前端调用模板)
└── README.md                     (推荐更新)
```

---

## 🎯 下一步建议

### 1. 添加数据库持久化
```python
class Schedule(database.Base):
    __tablename__ = "schedules"
    user_id = Column(String)
    course_name = Column(String)
    created_at = Column(DateTime)
```

### 2. 实现缓存机制
```python
# 防止重复爬虫
@cache(ttl=86400)  # 24小时缓存
async def get_schedule(username, password):
    ...
```

### 3. 添加认证
```python
# JWT Token 验证
@app.post("/api/schedule")
async def get_schedule(
    info: LoginInfo,
    token: str = Depends(oauth2_scheme)
):
    ...
```

### 4. 错误重试机制
```python
for attempt in range(3):  # 重试 3 次
    try:
        result = await get_campus_schedule(...)
        return result
    except Exception as e:
        if attempt == 2:
            raise
```

---

## 💡 常见问题

**Q: 为什么要在新页面上挂载监听器？**  
A: 教务系统在新标签页打开课表，必须在新页面上才能捕获网络请求

**Q: 爬虫为什么要用 headless=True？**  
A: 无头模式更轻量级，适合服务器环境，减少资源占用

**Q: 数据会被保存吗？**  
A: 目前只返回给前端，如需持久化请集成数据库

**Q: 支持多个学生同时查询吗？**  
A: 支持，使用异步可以同时处理多个请求

**Q: 密码安全吗？**  
A: 建议添加 HTTPS、加密存储、审计日志等安全措施

---

## 📞 技术支持

如遇问题，按以下顺序排查：

1. ✅ 确认后端已启动：`http://127.0.0.1:8000`
2. ✅ 检查账号密码是否正确
3. ✅ 查看控制台日志输出
4. ✅ 尝试用 API 文档重新测试
5. ✅ 运行 `python test_api.py` 直接测试爬虫

---

## 🎉 完成！

**现在你的校园圈项目已拥有完整的课表爬虫 API！**

- ✅ 后端 API 接口完成
- ✅ 前端调用示例完成  
- ✅ 测试工具完成
- ✅ 文档完成

**下一步：启动后端，集成到前端页面！🚀**
