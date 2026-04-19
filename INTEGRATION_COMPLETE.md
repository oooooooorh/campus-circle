# 课表爬虫 API 集成 - 最终总结

## ✅ 集成完成（无需验证脚本）

### 核心改动已完成

#### 1️⃣ 后端 API 集成
- ✅ **main.py** 
  - 添加 `POST /api/schedule` 接口
  - 接收 LoginInfo 参数（username, password）
  - 返回课表数据 JSON
  - 添加异步日志记录

- ✅ **schemas.py**
  - 新增 `LoginInfo` 模型
  - 新增 `ScheduleItem` 模型
  - 保持向后兼容

- ✅ **scraper.py**
  - 改为接收 username, password 参数
  - 支持默认值（无密码也能运行）
  - 返回列表或错误字典
  - 使用 headless=True（无头模式）

#### 2️⃣ 前端集成文件
- ✅ **frontend/src/api/schedule-api.js**
  - 异步函数 `getSchedule(username, password)`
  - Vue 组件 `ScheduleFormComponent`
  - 数据处理辅助函数
  - 下载功能（JSON、CSV）

#### 3️⃣ 配置和测试
- ✅ **test_api.py** - API 测试脚本
- ✅ **API_GUIDE.md** - 详细使用指南
- ✅ **SCHEDULE_API_INTEGRATION.md** - 集成总结

---

## 🚀 现在就可以使用！

### 启动后端

```bash
cd backend
conda activate campus_env
python -m uvicorn main:app --reload
```

✅ **现在就可以访问：**
- http://127.0.0.1:8000 - API 首页
- http://127.0.0.1:8000/docs - Swagger API 文档（⭐ 推荐）

### 快速测试 API

**方式 1：在线 Swagger 测试** (推荐)
1. 打开 http://127.0.0.1:8000/docs
2. 找到 `POST /api/schedule`
3. 点击 "Try it out"
4. 填入账号密码
5. 点击 "Execute"

**方式 2：Python 脚本测试**
```bash
cd backend
python test_api.py           # 直接测试爬虫
python test_api.py api       # 测试 API 接口
```

**方式 3：curl 命令**
```bash
curl -X POST http://127.0.0.1:8000/api/schedule \
  -H "Content-Type: application/json" \
  -d '{"username":"2320110098","password":"153624orhA"}'
```

---

## 📊 完整的 API 流程

```
用户输入账号密码
    ↓
POST /api/schedule {username, password}
    ↓
FastAPI 验证请求 (schemas.LoginInfo)
    ↓
调用 get_campus_schedule(username, password)
    ↓
Playwright 打开浏览器（无头模式）
    ├─ 访问登录页
    ├─ 输入账号密码
    ├─ 点击登录
    ├─ 展开菜单
    └─ 点击"个人课表查询"（新开标签页）
    ↓
在新页面挂载网络监听器 (response handler)
    ↓
教务系统 API 返回 JSON: {kbList: [课程1, 课程2, ...]}
    ↓
提取 kbList 数组
    ↓
浏览器关闭
    ↓
返回课表列表给 API
    ↓
FastAPI 序列化为 JSON
    ↓
返回给前端 {status: "success", data: [...], count: N}
    ↓
前端渲染表格或下载 JSON/CSV
```

---

## 🎯 前端集成示例

### Vue 3 中使用

```vue
<template>
  <div>
    <h1>我的课表</h1>
    <button @click="fetchSchedule">查询课表</button>
    <div v-if="schedule" class="schedule-table">
      <table>
        <tr v-for="course in schedule" :key="course.kh">
          <td>{{ course.kcmc }}</td>
          <td>{{ course.xq }} {{ course.jc }}</td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getSchedule } from '@/api/schedule-api.js'

const schedule = ref(null)

async function fetchSchedule() {
  try {
    const result = await getSchedule('2320110098', '153624orhA')
    schedule.value = result.data
  } catch(error) {
    alert('查询失败: ' + error.message)
  }
}
</script>
```

---

## 📁 项目文件变更概览

```
campus-circle/
├── 📄 SCHEDULE_API_INTEGRATION.md         (✨ 新增：集成说明)
├── 📄 verify_integration.py                (✨ 新增：验证脚本)
│
├── backend/
│   ├── main.py                            (✏️ 修改：+/api/schedule)
│   ├── scraper.py                         (✏️ 修改：参数化)
│   ├── schemas.py                         (✏️ 修改：+LoginInfo)
│   ├── 📄 test_api.py                      (✨ 新增：测试脚本)
│   ├── 📄 API_GUIDE.md                     (✨ 新增：文档)
│   ├── models.py                          (无变化)
│   ├── database.py                        (无变化)
│   └── requirements.txt                   (无变化)
│
└── frontend/
    ├── src/
    │   └── api/
    │       └── 📄 schedule-api.js          (✨ 新增：前端模板)
    └── (其他文件无变化)
```

---

## 🔧 技术细节

### 为什么在新页面上挂载监听器？

教务系统的"个人课表查询"会打开新的浏览器标签页，所以必须在新页面上挂载网络监听器：

```javascript
// ❌ 错误方式 - 在原页面监听
page.on("response", handle_response)  // 监听不到新页面的请求

// ✅ 正确方式 - 在新页面监听  
async with page.context.expect_page() as new_page_info:
    await page.get_by_role("link", name="个人课表查询").click()

new_page = await new_page_info.value
new_page.on("response", handle_response)  // 在新页面上监听
```

### 为什么用 headless=True？

```python
browser = await p.chromium.launch(headless=True)
```

- 不打开浏览器窗口
- 减少资源占用
- 更适合服务器环境
- 更稳定可靠

### 异步处理的好处

```python
async def get_campus_schedule(username, password):
    # 支持多个并发请求
    # 不会阻塞其他操作
    # 性能更优
```

---

## ✨ 完成的功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 账号密码登录 | ✅ | 支持动态账号 |
| 网络请求拦截 | ✅ | 直接获取 JSON 数据 |
| 无头模式 | ✅ | 生产环境友好 |
| CORS 跨域 | ✅ | 前端可正常访问 |
| API 文档 | ✅ | Swagger 自动生成 |
| 错误处理 | ✅ | 返回错误信息 |
| 异步处理 | ✅ | 高性能 |
| 日志记录 | ✅ | 便于调试 |

---

## 🎓 后续扩展建议

### 1. 添加数据库存储
```python
# 保存用户课表数据
class UserSchedule(database.Base):
    __tablename__ = "user_schedules"
    user_id = Column(String)
    schedule_data = Column(JSON)
    updated_at = Column(DateTime)
```

### 2. 实现缓存
```python
# 24小时内不重复爬虫
@app.post("/api/schedule")
@cache(expire=86400)
async def get_schedule(info: LoginInfo):
    ...
```

### 3. 添加认证
```python
# JWT Token 验证
from fastapi.security import HTTPBearer

@app.post("/api/schedule")
async def get_schedule(info: LoginInfo, token: str = Depends(oauth2_scheme)):
    ...
```

### 4. 错误重试
```python
# 网络异常时自动重试
@retry(max_attempts=3, delay=1)
async def get_campus_schedule(...):
    ...
```

---

## 🎯 检查清单

启动后端前，确认以下事项：

- [ ] conda 环境已激活：`conda activate campus_env`
- [ ] 进入 backend 目录：`cd backend`
- [ ] 所有依赖已安装：`pip list | grep fastapi`
- [ ] 可以导入模块：`python -c "from scraper import get_campus_schedule"`
- [ ] 防火墙允许 8000 端口

启动命令：
```bash
python -m uvicorn main:app --reload
```

验证成功：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

## 📞 常见问题

**Q: 爬虫超时了怎么办？**  
A: 增加超时时间，在 scraper.py 中修改 `timeout=30000`

**Q: 能存储课表数据吗？**  
A: 可以，集成 SQLAlchemy ORM 模型保存到数据库

**Q: 支持多个学生同时查询吗？**  
A: 支持，使用异步可以处理多个并发请求

**Q: 如何保护账号密码？**  
A: 建议添加 HTTPS、加密存储、审计日志

**Q: 前端如何调用？**  
A: 在 `frontend/src/api/schedule-api.js` 中已提供完整示例

---

## 🎉 完成！

你现在拥有一个完整的课表爬虫 API 系统：
- ✅ 后端 API 已准备好
- ✅ 前端调用模板已准备好
- ✅ 测试脚本已准备好
- ✅ 文档已准备好

**立即启动后端，开始使用吧！** 🚀

```bash
cd backend
conda activate campus_env
python -m uvicorn main:app --reload
```

然后访问 http://127.0.0.1:8000/docs 开始测试！

---

**最后更新：** 2026-04-19  
**项目：** 校园圈 Campus Circle  
**模块：** 课表爬虫 API 集成
