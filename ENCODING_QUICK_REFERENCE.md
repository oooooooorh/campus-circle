# ✨ 防乱码快速参考

## 🚀 核心防乱码代码（直接复制使用）

### 1️⃣ 保存 JSON 文件（最重要！）
```python
import json

data = {"课程": "计算机基础", "学分": 4}

# ✅ 正确做法
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
```

### 2️⃣ 修复控制台输出
```python
import sys
import io

# Windows PowerShell 防乱码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("你好，世界！")  # ✅ 正确显示中文
```

### 3️⃣ 日志配置
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
    # ⚠️ 不要添加 encoding='utf-8'（Windows 兼容性问题）
)
```

### 4️⃣ HTTP 响应（FastAPI）
```python
from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/api/data")
def get_data():
    return {
        "status": "success",
        "message": "获取数据成功"  # ✅ 自动处理 UTF-8
    }
```

---

## 🎯 三个必记要点

| 要点 | 代码 | 说明 |
|------|------|------|
| **文件编码** | `encoding="utf-8"` | 文件打开时指定编码 |
| **JSON 编码** | `ensure_ascii=False` | JSON 不转义中文 |
| **美化输出** | `indent=4` | 可视化 JSON 结构 |

---

## ❌ 常见错误（避免这些！）

```python
# ❌ 错误 1：忘记指定编码
with open("data.json", "w") as f:
    json.dump(data, f)  # Windows 上会乱码！

# ❌ 错误 2：JSON 转义中文
json_str = json.dumps(data)  # "\u4e2d\u6587" 乱码显示

# ❌ 错误 3：日志配置冲突
logging.basicConfig(encoding='utf-8')  # PowerShell 上报错！

# ❌ 错误 4：直接打印字典
print(data_dict)  # 可能出现 '\u' 转义序列
```

---

## ✅ 正确做法总结

```python
# 完整示例
import sys
import io
import json
import logging

# 1. 修复输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 2. 配置日志
logging.basicConfig(format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# 3. 处理文件
def save_data(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logger.info(f"已保存到 {filename}")

# 4. 测试
test_data = {
    "姓名": "张三",
    "课程": ["Python", "JavaScript", "Java"],
    "成绩": 95.5
}

save_data(test_data, "student.json")
print("✅ 完成！")
```

---

## 📍 项目中的防乱码实现

### 在 `scraper.py` 中
```python
# 保存课表数据
with open(save_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
```

### 在 `main.py` 中
```python
# 错误处理
except Exception as e:
    error_msg = str(e) if str(e) else "未知错误"
    logger.error(f"课表抓取异常: {error_msg}", exc_info=True)
```

### 在脚本中
```python
# 修复输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

---

## 🔗 相关文件

- 详细说明：[UTF8_ENCODING_GUIDE.md](UTF8_ENCODING_GUIDE.md)
- 爬虫脚本：[backend/scraper.py](backend/scraper.py)
- API 主文件：[backend/main.py](backend/main.py)
- 测试脚本：[backend/test_api_utf8.py](backend/test_api_utf8.py)

---

## 💡 记住这三行代码！

```python
# 文件保存
with open("file.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

# 标准输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 日志输出
logging.basicConfig(format='%(asctime)s - %(message)s')
```

就这样，乱码问题 **99% 的情况下可以解决**！🎉
