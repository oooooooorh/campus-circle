# 🎓 课表爬虫 API 集成完成指南

## ✅ 已完成的集成工作

### 1. **数据模型定义** (`schemas.py`)
- ✅ `LoginInfo` - 登录信息模型（username, password）
- ✅ `ScheduleItem` - 课表项目模型（支持扩展字段）

### 2. **API 接口** (`main.py`)
- ✅ `POST /api/schedule` - 获取个人课表接口
  - 接收：`{"username": "账号", "password": "密码"}`
  - 返回：`{"status": "success", "data": [...], "count": N}`

### 3. **爬虫函数** (`scraper.py`)
- ✅ `get_campus_schedule(username, password)` - 支持参数化
  - 默认值：教务系统凭证
  - 返回：课表列表或错误字典

### 4. **网络拦截**
- ✅ 在新开标签页上正确挂载响应监听器
- ✅ 解析教务系统 API 返回的 `kbList` 数据
- ✅ 支持 JSON 序列化和文件保存

---

## 🚀 快速使用

### 方式 1：启动完整后端服务（推荐）

```bash
# 激活环境
conda activate campus_env

# 进入后端目录
cd backend

# 启动 FastAPI
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**输出示例：**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 方式 2：用 API 测试脚本

```bash
# 在另一个终端运行
conda activate campus_env
cd backend

# 测试爬虫函数（无需 API）
python test_api.py

# 或测试 API 接口
python test_api.py api
```

### 方式 3：用 curl 测试

```bash
curl -X POST http://127.0.0.1:8000/api/schedule \
  -H "Content-Type: application/json" \
  -d '{"username":"2320110098", "password":"153624orhA"}'
```

---

## 📡 API 接口详解

### 请求示例

```json
POST /api/schedule
Content-Type: application/json

{
  "username": "2320110098",
  "password": "153624orhA"
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
    },
    ...
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

## 🔧 核心技术点

### 1. 异步爬虫架构

```python
async def get_campus_schedule(username: str, password: str):
    """支持传入动态账号密码"""
    intercepted_schedule_data = []
    
    async def handle_response(response):
        # 网络响应拦截
        if "xskbcx_cxXsgrkb" in response.url:
            json_data = await response.json()
            if "kbList" in json_data:
                intercepted_schedule_data.extend(json_data["kbList"])
    
    # 核心：在新页面上挂载监听器
    new_page.on("response", handle_response)
```

### 2. FastAPI 整合

```python
@app.post("/api/schedule")
async def get_schedule(info: schemas.LoginInfo):
    result = await get_campus_schedule(info.username, info.password)
    return {"status": "success", "data": result, "count": len(result)}
```

### 3. 无头模式

爬虫已配置 `headless=True`（生产环境推荐）：
- 不打开浏览器窗口
- 资源占用更少
- 更适合服务器环境

---

## 📊 数据流程图

```
用户请求
   ↓
POST /api/schedule {username, password}
   ↓
FastAPI 路由处理
   ↓
get_campus_schedule(username, password)
   ↓
Playwright 打开浏览器
   ↓
登录教务系统
   ↓
点击"个人课表查询"（新开标签页）
   ↓
挂载网络监听器
   ↓
教务系统 API 返回 {kbList: [...]}
   ↓
提取 kbList 数据
   ↓
浏览器关闭
   ↓
返回课表列表 JSON
```

---

## 🐛 常见问题

### Q: 登录失败
**A:** 检查账号密码是否正确，或教务系统是否在维护

### Q: 爬虫超时
**A:** 网络较慢，可增加超时时间

```python
await page.wait_for_selector("#yhm", timeout=20000)  # 改为 20 秒
```

### Q: 无法连接到 API
**A:** 确保后端已启动
```bash
# 查看是否有错误
python -m uvicorn main:app --reload
```

### Q: 为什么要在新页面上挂载监听器？
**A:** 教务系统在新标签页打开课表页面，必须在新页面上才能拦截到网络请求

---

## 📁 文件结构

```
backend/
├── main.py              # FastAPI 主应用（已集成课表 API）
├── scraper.py           # 爬虫核心函数（支持参数化）
├── schemas.py           # 数据模型（已添加 LoginInfo）
├── models.py            # ORM 模型
├── database.py          # 数据库配置
├── test_api.py          # API 测试脚本
├── my_schedule.json     # 爬虫保存的数据
└── requirements.txt     # 依赖列表
```

---

## ✨ 后续优化建议

1. **添加数据库存储**
   ```python
   class Schedule(database.Base):
       __tablename__ = "schedules"
       user_id = Column(String, index=True)
       course_name = Column(String)
       time_slot = Column(String)
   ```

2. **实现缓存机制**
   - 同一用户同一天内不重复爬虫
   - 使用 Redis 缓存

3. **添加认证**
   - JWT Token 验证
   - 防止恶意请求

4. **批量爬取**
   - 支持爬取多个学期
   - 支持多用户异步爬取

5. **数据清洗**
   - 规范化时间格式
   - 提取关键字段
   - 去除冗余数据

---

## 🎯 测试检查清单

- [ ] 后端启动成功（http://127.0.0.1:8000）
- [ ] API 文档可访问（http://127.0.0.1:8000/docs）
- [ ] POST /api/schedule 接口可用
- [ ] 爬虫成功登录教务系统
- [ ] 成功拦截课表数据
- [ ] 返回 JSON 格式正确
- [ ] 前端可正常调用 API

---

**集成完成！🎉 现在你的项目拥有完整的课表爬虫 API 服务！**
