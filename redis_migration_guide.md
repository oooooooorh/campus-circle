# 🚀 从 SQLite 到 Redis：全栈改造保姆级教程

针对你之前项目中“部署到 Azure 重启后 SQLite 数据会丢失”的痛点，把存储彻底换成 **Redis** 是一个非常极客且高效的解决方案（线上可以直接使用 Azure Cache for Redis 服务，数据永久保留）。

Redis 和传统的 SQLite/MySQL 完全不同，它是**键值对 (Key-Value) 内存数据库**，没有“表(Table)”的概念。这就要求我们在写代码时，思维要从“二维表格”转换为“大字典”。

下面我将手把手教你如何“大换血”。

---

## 🗑️ 第一阶段：删代码（断舍离）

在关系型数据库中，我们需要繁琐的 ORM 映射，但在 Redis 中，存什么就是什么。

**1. 删除以下不需要的文件：**
*   `backend/models.py` (完全删除，不再需要定义表结构)
*   `backend/database.py` (完全删除，不需要 SQLAlchemy 引擎)
*   `backend/campus.db` (把那个容易丢失的文件删掉)

**2. 卸载/安装依赖：**
打开终端（确保激活了 `campus_env` 虚拟环境）：
```bash
# 卸载旧时代的眼泪
pip uninstall sqlalchemy

# 安装 Redis 的 Python 客户端
pip install redis
```

---

## 🛠️ 第二阶段：后端新增 Redis 驱动 (加代码)

在 `backend` 目录下新建一个文件叫 **`redis_db.py`**，我们将在这里初始化 Redis 连接。

```python
# backend/redis_db.py
import redis
import os

# 从环境变量获取 Redis 地址，方便线上线下切换
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# 建立连接池（逐行解释看下方）
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True # 极其重要：让 Redis 返回纯文本字符串而不是 byte 字节码
)

def get_redis():
    """这是一个依赖注入函数，用来给 FastAPI 的路由提供 Redis 实例"""
    return redis_client
```
**👨‍🏫 逐行教学：**
*   `os.getenv(...)`: 本地开发时默认连 `localhost`。等部署到 Azure 时，只要在网页上配个环境变量，它就能自动连上云端 Redis。
*   `decode_responses=True`: Redis 默认存的是二进制数据，加了这行，读取时会自动帮我们转成 Python 的 `String`，省去很多麻烦。

---

## 🏗️ 第三阶段：改造 `main.py` 业务逻辑

以前我们用 `db.query().filter()` 查数据，现在 we 用 Redis 的指令。
打开 `backend/main.py`，**删掉所有和 `Session`, `database`, `models` 相关的导入和代码**。

引入新的依赖：
```python
# main.py 顶部替换导入
from fastapi import FastAPI, Depends, HTTPException
import json
from redis_db import get_redis
import redis
```

### 改造案例 1：发布帖子 (POST /api/posts)

在 Redis 中存一个帖子，我们需要用到两个数据结构：
1. **Hash (哈希表)**：用来存帖子的详情内容（相当于字典）。
2. **List (列表)**：用来按顺序存帖子的 ID（用来做时间线排列）。

```python
# main.py
from datetime import datetime

@app.post("/api/posts")
def create_post(
    payload: schemas.PostCreate,
    r: redis.Redis = Depends(get_redis) # 注入 redis 客户端
):
    # 1. 拦截空数据
    title = (payload.title or "").strip()
    content = (payload.content or "").strip()
    if not title or not content:
        raise HTTPException(status_code=400, detail="标题和内容不能为空")

    # 2. 生成自增的主键 ID (类似 SQLite 的 AUTOINCREMENT)
    # INCR 命令会自动把 "post_id_counter" 加 1
    post_id = r.incr("global:post_id") 

    # 3. 组装数据字典
    post_data = {
        "id": post_id,
        "title": title,
        "content": content,
        "created_at": datetime.now().isoformat() # Redis 只能存字符串，所以时间要格式化
    }

    # 4. 把数据存入 Redis 的 Hash 表中
    # 键名设计为 "post:1", "post:2" 这种层级格式
    r.hset(f"post:{post_id}", mapping=post_data)

    # 5. 把帖子 ID 塞入一个大列表(List)的最前面，方便查询最新帖子
    r.lpush("posts:timeline", post_id)

    return post_data
```
**👨‍🏫 逐行教学：**
*   `r.incr("global:post_id")`: Redis 没有表，所以我们需要一个专门的计数器来生成唯一 ID。每次调用都会返回 1, 2, 3...
*   `r.hset(...)`: 相当于 `INSERT INTO`，把一个完整的字典对象存进内存。
*   `r.lpush(...)`: Left Push，把新的 `post_id` 推入列表头部。下次查列表时，最新的帖子就在最上面。

### 改造案例 2：获取全部帖子 (GET /api/posts)

```python
@app.get("/api/posts")
def get_all_posts(
    skip: int = 0,
    limit: int = 100,
    r: redis.Redis = Depends(get_redis)
):
    # 1. 从列表(List)中切片取出帖子 ID
    # 相当于 OFFSET skip LIMIT limit
    post_ids = r.lrange("posts:timeline", skip, skip + limit - 1)
    
    if not post_ids:
        return []

    result = []
    # 2. 遍历 ID，去 Hash 表里把完整的帖子数据捞出来
    for pid in post_ids:
        # HGETALL 能获取该键下的整个字典
        post_data = r.hgetall(f"post:{pid}")
        if post_data:
            # 因为从 redis 取出来都是字符串，需要把 ID 转回整数
            post_data["id"] = int(post_data["id"]) 
            result.append(post_data)
            
    return result
```
**👨‍🏫 逐行教学：**
*   `r.lrange(key, start, end)`: 完美取代 SQL 的分页功能。
*   `r.hgetall(key)`: 完美取代 SQL 的 `SELECT * FROM posts WHERE id = ?`。

---

## 💻 第四阶段：前端联动怎么搞？

**答案是：前端代码一行都不用改！🤯**

这就是**前后端分离**架构的魅力所在。只要你的 FastAPI 接口依然叫 `/api/posts`，依然返回一样的 JSON 格式：
```json
[
  {
    "id": 1,
    "title": "今天饭堂好好吃",
    "content": "如题",
    "created_at": "2026-05-10T12:00:00"
  }
]
```
不管你后端是用 SQLite 查硬盘，还是用 Redis 查内存，甚至是用算盘手摇出来的，前端的 `Vue`、`fetch` 和 `Schedule.vue` 都完全不在乎。数据流向是一致的。

---

## 🚢 第五阶段：部署与运行环境

太棒了！你已经通过 Docker 成功跑通了 Redis。这意味着你的本地环境已经**完全就绪**。

### 1. 本地运行 (Docker)
你之前运行的命令非常标准：
```bash
docker run -d --name my-redis -p 6379:6379 redis:latest
```
*   **连接地址**：`localhost` (127.0.0.1)
*   **端口**：`6379`
*   **密码**：目前没有设置（在内网开发环境是安全的）。
*   **数据管理**：你可以随时通过 `docker exec -it my-redis redis-cli` 进去查看数据。

### 2. 线上部署 (Azure)
当你准备好部署到 Azure 时，流程如下：
1.  在 Azure 门户里，搜索并创建一个 **Azure Cache for Redis** 服务。
2.  创建好后，从“访问密钥”页面拿到它的 **主机名** 和 **主要访问密钥**。
3.  去你的 Azure App Service (campus-api) 的 **配置** -> **应用设置** 里，添加两个环境变量：
    *   `REDIS_HOST`: 填入 Azure Redis 的主机名。
    *   `REDIS_PASSWORD`: 填入那个长长的访问密钥。
    *   `REDIS_PORT`: 填入 `6380` (Azure 默认加密端口) 或 `6379`。

这样，你的应用从此变成了真正的云原生、无状态服务。随便重启，哪怕摧毁了重建，数据依然安全地存在云端的 Redis 数据库中！

