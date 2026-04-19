# 🎉 完整项目启动指南 - 课表爬虫功能

## ✅ 项目现状

### 后端完成
- ✅ FastAPI 框架集成
- ✅ `/api/schedule` POST 接口
- ✅ Playwright 爬虫核心
- ✅ 网络请求拦截
- ✅ 异步处理
- ✅ CORS 跨域支持

### 前端完成
- ✅ Schedule.vue 完整实现
- ✅ 账号密码输入框
- ✅ 获取课表按钮
- ✅ 课程表格展示
- ✅ 周日程可视化
- ✅ 响应式设计
- ✅ 错误提示
- ✅ 成功提示
- ✅ JSON 下载

### 文档完成
- ✅ API 使用指南 (API_GUIDE.md)
- ✅ 集成完成说明 (INTEGRATION_COMPLETE.md)
- ✅ 前端使用指南 (FRONTEND_SCHEDULE_GUIDE.md)
- ✅ 启动脚本和测试工具

---

## 🚀 一键启动（推荐）

### 方式 1：两个终端同时启动

**终端 1 - 启动后端：**
```bash
cd backend
conda activate campus_env
python -m uvicorn main:app --reload
```

预期输出：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**终端 2 - 启动前端：**
```bash
cd frontend
npm run dev
```

预期输出：
```
  VITE v... ready in ... ms

  ➜  Local:   http://localhost:5173/
```

### 方式 2：使用批处理脚本（Windows）

```bash
# 如果有现成的启动脚本
start_backend.bat
start_frontend.bat
```

---

## 📖 使用步骤

### Step 1: 打开课程表页面
访问 **http://localhost:5173**，导航到 "我的课表" 页面

### Step 2: 输入凭证
- 学号：例 `2320110098`
- 密码：教务系统密码

### Step 3: 点击获取课表
点击 "🔄 获取课表" 按钮，等待爬虫完成（约 5-10 秒）

### Step 4: 查看课表
- 📊 **表格视图**：完整的课程列表
- 📅 **日程视图**：按星期组织的课程块
- 📈 **统计信息**：课程数量、周次范围等

### Step 5: 导出数据（可选）
点击 "💾 下载 JSON" 按钮下载课表数据

---

## 🔗 关键 URL

| 地址 | 说明 |
|------|------|
| http://localhost:5173 | 前端应用首页 |
| http://localhost:5173/schedule | 课程表页面（目标页面） |
| http://127.0.0.1:8000 | 后端 API 首页 |
| http://127.0.0.1:8000/docs | 📘 Swagger API 文档（强烈推荐） |
| http://127.0.0.1:8000/redoc | ReDoc API 文档（备选） |

---

## 📊 功能演示

### 登录表单
```
┌────────────────────────────────────┐
│   🔐 教务系统登录                  │
│                                     │
│  学号：   [2320110098]             │
│  密码：   [••••••••]               │
│                                     │
│  [🔄 获取课表] [💾 下载JSON]      │
│                                     │
│  ✅ 成功加载 11 门课程！            │
└────────────────────────────────────┘
```

### 课程表格
```
课程代码 │ 课程名称        │ 学分 │ 班级 │ 周次    │ 星期 │ 节次
────────┼─────────────────┼──────┼──────┼─────────┼──────┼────
G006    │ 高等数学（一）  │  4   │ 1班  │ 1-18周 │ 星期一│1-2
D022    │ C语言程序设计   │  4   │ 1班  │ 1-18周 │ 星期二│3-4
...
```

### 周日程
```
 星期一      星期二      星期三      星期四      星期五
┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
│高数一 │  │C语言  │  │数据库 │  │物理  │  │英语   │
│1-2节  │  │3-4节  │  │1-2节  │  │5-6节  │  │3-4节  │
└───────┘  └───────┘  └───────┘  └───────┘  └───────┘
│高数二│  │计算机 │  │线性代│  │        │  │        │
│3-4节 │  │5-6节  │  │3-4节 │  │        │  │        │
└───────┘  └───────┘  └───────┘  └───────┘  └───────┘
```

---

## 🔧 技术架构

```
前端 (Vue 3)
  ├─ Schedule.vue (课程表页面)
  ├─ Components (可选子组件)
  └─ API (schedule-api.js)
         │
         ├─ HTTP POST 请求
         │
后端 (FastAPI)
  ├─ main.py (/api/schedule 接口)
  ├─ schemas.py (LoginInfo 模型)
  ├─ scraper.py (爬虫函数)
  └─ database.py (数据库配置)
         │
         └─ Playwright
            ├─ 登录教务系统
            ├─ 导航到课表页面
            ├─ 拦截网络请求
            └─ 提取 JSON 数据
```

---

## 📝 请求/响应格式

### 前端请求
```javascript
POST http://127.0.0.1:8000/api/schedule
Content-Type: application/json

{
  "username": "2320110098",
  "password": "your_password"
}
```

### 后端响应（成功）
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
      "jc": "1-2节",
      "kcjs": "李老师",
      "skdd": "307教室"
    },
    ...
  ],
  "count": 11
}
```

### 后端响应（失败）
```json
{
  "detail": "登录失败，请检查账号密码"
}
```

---

## 🐛 调试技巧

### 查看浏览器控制台
打开开发者工具 (F12)，查看 Console 标签
```javascript
// 你会看到类似这样的日志：
🔄 正在获取课表...
✅ 成功获取课表！
```

### 查看网络请求
在 Network 标签中，找到 POST /api/schedule 请求
- 查看请求体（Request payload）
- 查看响应体（Response）
- 查看响应时间（通常 5-10 秒）

### 查看后端日志
后端终端会显示：
```
INFO:     127.0.0.1:60000 "POST /api/schedule HTTP/1.1" 200 OK
🔄 正在获取课表...
```

---

## ✅ 常见问题排查

### 问题 1：页面加载失败
**症状：** 前端打不开或 404  
**解决：**
```bash
# 确保前端服务运行
cd frontend
npm run dev

# 或检查 package.json 中的 dev 脚本
cat package.json | grep '"dev"'
```

### 问题 2：API 无响应
**症状：** 点击按钮没反应  
**解决：**
```bash
# 检查后端服务
curl http://127.0.0.1:8000/

# 查看是否有错误日志
# 在后端终端中查看输出
```

### 问题 3：爬虫登录失败
**症状：** "登录失败，请检查账号密码"  
**解决：**
1. 确认账号密码正确
2. 教务系统是否在维护
3. 网络是否连接正常
4. 查看后端日志获取更多信息

### 问题 4：课表为空
**症状：** 登录成功但没有课程数据  
**解决：**
1. 该学期是否真的有课程
2. 查看后端日志中的网络拦截信息
3. 尝试在浏览器中直接访问教务系统

### 问题 5：样式错乱（仅 Windows）
**症状：** 页面显示不正常  
**解决：**
```bash
# 清除缓存并重启
npm run build
npm run dev

# 或硬刷新浏览器 (Ctrl + Shift + R)
```

---

## 🎯 测试检查清单

### 环境检查
- [ ] Python 3.8+ 已安装
- [ ] Node.js 16+ 已安装
- [ ] conda 环境已创建（campus_env）
- [ ] npm 依赖已安装（frontend）
- [ ] pip 依赖已安装（backend）

### 后端检查
- [ ] http://127.0.0.1:8000 可访问
- [ ] http://127.0.0.1:8000/docs 可访问
- [ ] POST /api/schedule 接口存在
- [ ] Playwright 浏览器已安装

### 前端检查
- [ ] http://localhost:5173 可访问
- [ ] 能找到 Schedule 页面
- [ ] 输入框能输入文字
- [ ] 按钮能点击

### 功能检查
- [ ] 输入正确凭证能获取课表
- [ ] 显示课程表格
- [ ] 显示周日程
- [ ] 能下载 JSON
- [ ] 手机上能正常显示

---

## 📚 相关文档

| 文件名 | 位置 | 说明 |
|--------|------|------|
| API_GUIDE.md | backend/ | API 详细文档 |
| INTEGRATION_COMPLETE.md | 项目根目录 | 集成说明 |
| FRONTEND_SCHEDULE_GUIDE.md | 项目根目录 | 前端使用指南 |
| Schedule.vue | frontend/src/views/ | 前端完整代码 |
| schedule-api.js | frontend/src/api/ | API 调用函数 |
| scraper.py | backend/ | 爬虫核心逻辑 |
| main.py | backend/ | FastAPI 应用 |

---

## 🎨 自定义和扩展

### 修改主题色
编辑 `Schedule.vue` 的 `<style>` 部分：
```css
/* 修改这些颜色值 */
#667eea  /* 主色 */
#764ba2  /* 副色 */
#FF6B6B  /* 强调色 */
```

### 添加新的课程字段
在表格中添加新的 `<th>` 和 `<td>`：
```html
<th>新字段</th>
<td>{{ course.新字段名 }}</td>
```

### 修改课程颜色
编辑 colors 数组：
```javascript
const colors = [
  '#FF6B6B',  // 红色
  '#4ECDC4',  // 青色
  '#45B7D1',  // 蓝色
  // 添加更多颜色...
]
```

---

## 🚀 生产部署（可选）

### 前端部署
```bash
cd frontend
npm run build
# 生成 dist 文件夹，部署到 Nginx / Apache 等

# 修改 API 地址
# 在 frontend/src/api/schedule-api.js 中修改
const API_BASE = "http://your-domain.com"
```

### 后端部署
```bash
cd backend

# 使用 Gunicorn (生产级)
gunicorn -w 4 -b 0.0.0.0:8000 main:app

# 或使用 Uvicorn 反向代理
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 安全建议
- [ ] 添加 HTTPS
- [ ] 加密密码存储
- [ ] 添加认证和授权
- [ ] 限制请求频率
- [ ] 添加审计日志
- [ ] 定期备份数据

---

## 📞 获取帮助

### 查看日志
```bash
# 后端日志在终端中显示
# 前端日志在浏览器 F12 中显示

# 查看具体的爬虫日志
tail -f backend.log
```

### 测试 API
```bash
# 使用 curl 测试
curl -X POST http://127.0.0.1:8000/api/schedule \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# 或使用 Swagger UI
# 访问 http://127.0.0.1:8000/docs
```

---

## ✨ 完成！🎉

所有功能已实现，现在可以：
1. 启动后端和前端
2. 输入学号和密码
3. 获取并查看课程表
4. 下载课程数据

祝你使用愉快！🎓

有任何问题，请查阅相关文档或查看控制台日志。
