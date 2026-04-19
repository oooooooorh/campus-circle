# 🔧 防乱码措施实施清单

## ✅ 已实施的防乱码措施

### 1. **Scraper 模块** (`scraper.py`)

#### 文件保存防乱码
```python
# 关键：指定 encoding='utf-8' 和 ensure_ascii=False
with open(save_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
```

**关键参数说明：**
- ✅ `encoding="utf-8"` - 文件写入时使用 UTF-8 编码
- ✅ `ensure_ascii=False` - 不转义中文字符，直接保存中文
- ✅ `indent=4` - 美化输出，便于查看

#### 标准输出防乱码
```python
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

**目的：**
- Windows 上 PowerShell 默认为 GBK 编码
- 此配置强制使用 UTF-8，防止控制台输出乱码

#### 异常处理改进
```python
except Exception as e:
    error_detail = f"{type(e).__name__}: {str(e)}"
    print(f"❌ 发生错误: {error_detail}")
```

**改进点：**
- 显示异常类型名称，便于调试
- 规范错误消息格式

### 2. **Main 模块** (`main.py`)

#### 日志配置（简化版本）
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

**注意：** `encoding='utf-8'` 参数在 Windows PowerShell 上可能有兼容性问题，已移除

#### JSON 导入
```python
import json
```

**用途：** 支持 JSON 序列化和反序列化

#### 改进的异常处理
```python
except Exception as e:
    error_msg = str(e) if str(e) else "未知错误"
    logger.error(f"课表抓取异常: {error_msg}", exc_info=True)  # 记录完整的堆栈信息
    raise HTTPException(status_code=500, detail=f"课表抓取失败: {error_msg}")
```

**改进点：**
- ✅ 空错误检查
- ✅ 完整堆栈跟踪 (`exc_info=True`)
- ✅ 规范错误消息

### 3. **新增测试脚本**

#### `test_api_utf8.py` - UTF-8 编码测试
- 完整的 API 测试流程
- 验证中文字符正确显示
- 详细的响应信息输出

#### `debug_api.py` - 调试脚本
- 独立调用爬虫函数
- 日志输出到文件 (`api_debug.log`)
- 用于追踪异步问题

#### `schedule_logs/` - 日志目录
- 自动创建
- 保存爬虫返回的 JSON 数据
- 文件名格式：`schedule_20260419_152537.json`

---

## 📊 防乱码机制对比

| 阶段 | 防乱码措施 | 状态 |
|------|-----------|------|
| **文件 I/O** | `encoding="utf-8"` + `ensure_ascii=False` | ✅ 完成 |
| **标准输出** | `sys.stdout` UTF-8 重定向 | ✅ 完成 |
| **日志输出** | 统一格式，移除不兼容参数 | ✅ 完成 |
| **JSON 序列化** | `ensure_ascii=False` 配置 | ✅ 完成 |
| **错误信息** | 规范化字符串处理 | ✅ 完成 |
| **异常信息** | 完整堆栈跟踪 | ✅ 完成 |

---

## 🔍 验证方式

### 直接运行爬虫（验证成功 ✅）
```bash
cd backend
conda activate campus_env
python scraper.py
```

**输出：**
```
✅ 成功抓取 11 条课表记录
✅ 课表数据已保存到: schedule_logs\schedule_20260419_152537.json
✅ 成功: 获得 11 条课表

【首条课程示例】
  课程名称: 项目开发实训2
  教师: 张彤宇
  地点: 3实212
```

### 调试 API（验证异步调用）
```bash
cd backend
conda activate campus_env
python debug_api.py
```

---

## ⚠️ 已知问题与解决方案

### 问题：FastAPI 异步上下文
**现象：** 通过 API 调用时返回 500 错误
**原因：** Uvicorn 后台运行的异步上下文问题
**状态：** 🔍 进行中

**调试步骤：**
1. ✅ 直接调用爬虫函数 - **成功**
2. ✅ 验证 JSON 编码 - **成功**
3. 🔍 通过 API 调用 - **待解决**

---

## 📝 关键代码片段

### Python 3 标准做法 - 文件编码
```python
# ❌ 错误做法
with open("file.json", "w") as f:
    json.dump(data, f)

# ✅ 正确做法
with open("file.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
```

### JSON 序列化
```python
# ❌ 错误做法
json_str = json.dumps(data)  # ensure_ascii=True (默认)
# 结果："\u4e2d\u6587" (转义)

# ✅ 正确做法
json_str = json.dumps(data, ensure_ascii=False)
# 结果："中文" (直接显示)
```

### 日志编码
```python
# ❌ 避免在 Windows 上使用 encoding 参数
# logging.basicConfig(encoding='utf-8')

# ✅ 改用平台无关做法
logging.basicConfig(format='%(message)s')
```

---

## 🎯 后续步骤

1. **诊断 FastAPI 异步问题**
   - 检查 Uvicorn 进程编码
   - 验证环境变量设置
   - 考虑重启后台服务

2. **性能优化**
   - 缓存爬虫结果
   - 实现增量更新
   - 添加超时重试

3. **生产部署**
   - 配置 PYTHONIOENCODING=utf-8
   - 设置系统区域设置
   - 使用 Docker 容器化

---

## 📚 参考资源

- [Python 3 JSON 文档](https://docs.python.org/3/library/json.html)
- [Python 编码声明](https://www.python.org/dev/peps/pep-0263/)
- [FastAPI 国际化](https://fastapi.tiangolo.com/)
- [Uvicorn 环境配置](https://www.uvicorn.org/)

