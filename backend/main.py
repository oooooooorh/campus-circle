from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright
from openai import OpenAI
from pydantic import BaseModel
from redis_db import get_redis
from upstash_redis import Redis
import hmac
import secrets
from datetime import datetime, timedelta

# 添加后端目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import schemas
from scraper import get_campus_schedule
from scraper import get_campus_schedule

# ==================== 配置硅基流动大模型 API ====================
SILICONFLOW_API_KEY = os.getenv(
    "SILICONFLOW_API_KEY", "sk-byakstymalszdmtswgokqspuexjyauwwzgpiaarxpzfbogzh"
)
ai_client = OpenAI(
    api_key=SILICONFLOW_API_KEY,
    base_url="https://api.siliconflow.cn/v1"
)

class ChatRequest(BaseModel):
    user_message: str

# 配置日志，确保UTF-8编码处理中文
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 移除了数据库自动创建逻辑（Redis 不需要建表）

# ==================== 应用生命周期事件 ====================
# 全局 Playwright 和 Browser 实例
playwright_instance = None
browser_instance = None
# 设置并发控制，比如最多允许 3-5 个并发抓取请求以节省内存
browser_semaphore = asyncio.Semaphore(3)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global playwright_instance, browser_instance
    logger.info("========== 应用启动：初始化 Playwright ==========")
    try:
        playwright_instance = await async_playwright().start()
        # 启动一个全局 Browser
        browser_instance = await playwright_instance.chromium.launch(headless=True)
        logger.info("Playwright Browser 已成功启动并全局复用")
    except Exception as e:
        logger.error(f"Playwright 启动失败: {e}", exc_info=True)
    yield
    logger.info("========== 应用关闭：清理 Playwright ==========")
    if browser_instance:
        await browser_instance.close()
    if playwright_instance:
        await playwright_instance.stop()
    logger.info("Playwright 资源已清理")

# 创建 FastAPI 应用
app = FastAPI(title="校园圈后端中心", lifespan=lifespan)

# 静态文件（头像等）
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
AVATAR_DIR = os.path.join(STATIC_DIR, "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 如果之前的 @app.on_event("startup") 还存在，可以安全地注释或删除
# 为了兼容之前的代码结构，把它们替换掉:
# ==================== CORS 中间件配置 ====================
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# 从环境变量中读取额外的跨域白名单（使用逗号分隔，如 https://my-frontend.azurestaticapps.net）
env_origins = os.getenv("CORS_ORIGINS", "")
if env_origins:
    origins.extend([origin.strip() for origin in env_origins.split(",") if origin.strip()])

# 添加线上前端地址到跨域列表
origins.append("https://ashy-forest-0df45ff00.7.azurestaticapps.net")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 站内账号鉴权（JWT）====================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "43200"))  # 默认30天


PBKDF2_ITERATIONS = int(os.getenv("PBKDF2_ITERATIONS", "210000"))


def hash_password(password: str) -> str:
    # pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS, dklen=32)
    salt_b64 = base64.urlsafe_b64encode(salt).decode("ascii").rstrip("=")
    dk_b64 = base64.urlsafe_b64encode(dk).decode("ascii").rstrip("=")
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt_b64}${dk_b64}"


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        algo, iters_s, salt_b64, dk_b64 = password_hash.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        iters = int(iters_s)
        pad = "=" * (-len(salt_b64) % 4)
        salt = base64.urlsafe_b64decode(salt_b64 + pad)
        pad2 = "=" * (-len(dk_b64) % 4)
        expected = base64.urlsafe_b64decode(dk_b64 + pad2)
        actual = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iters, dklen=len(expected))
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def create_access_token(*, sub: str, expires_delta: timedelta) -> str:
    now = datetime.utcnow()
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": now + expires_delta}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    r: Redis = Depends(get_redis),
):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="未登录")
    except JWTError:
        raise HTTPException(status_code=401, detail="登录已过期或无效")

    # 这里的逻辑将改为从 Redis 查询用户信息
    user_data = r.hgetall(f"user:{username}")
    if not user_data:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user_data

def _normalize_tag(name: str) -> str:
    n = (name or "").strip()
    n = " ".join(n.split())
    return n


# 移除了 SQL 版本的标签辅助函数，后续将改用 Redis Set 或 Hash 存储标签信息


# 移除了旧的 SQLite 迁移代码，现在改用 Redis 存储

# 根路由
@app.get("/")
def root():
    logger.info("访问根路径")
    return {
        "status": "success",
        "message": "校园圈后端服务正在运行",
        "version": "1.0.0"
    }

# ==================== 注册/登录 ====================
@app.post("/api/auth/register", response_model=schemas.UserPublic)
def register(payload: schemas.RegisterRequest, r: Redis = Depends(get_redis)):
    # TODO: 实现 Redis 用户注册逻辑
    return {"message": "Redis 注册逻辑待实现"}


@app.post("/api/auth/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, r: Redis = Depends(get_redis)):
    # TODO: 实现 Redis 登录验证逻辑
    return {"access_token": "dummy_token", "token_type": "bearer"}


@app.get("/api/me", response_model=schemas.UserPublic)
def me(current_user: dict = Depends(get_current_user)):
    return current_user


@app.patch("/api/me", response_model=schemas.UserPublic)
def update_me(
    payload: schemas.UserUpdate,
    r: Redis = Depends(get_redis),
    current_user: dict = Depends(get_current_user),
):
    # TODO: 实现 Redis 用户信息更新逻辑
    return current_user


@app.post("/api/me/avatar", response_model=schemas.UserPublic)
def upload_my_avatar(
    file: UploadFile = File(...),
    r: Redis = Depends(get_redis),
    current_user: dict = Depends(get_current_user),
):
    # TODO: 实现 Redis 头像更新逻辑
    return current_user


@app.get("/api/me/posts", response_model=list[schemas.Post])
def my_posts(
    r: Redis = Depends(get_redis),
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    # TODO: 实现 Redis 获取个人帖子逻辑
    return []


# ==================== 公开用户信息 ====================
@app.get("/api/users/{user_id}", response_model=schemas.PublicUser)
def get_public_user(user_id: int, r: Redis = Depends(get_redis)):
    # TODO: 实现 Redis 获取公开用户信息逻辑
    return {"id": user_id, "username": "unknown"}


# ==================== 课表爬虫相关接口 ====================
@app.post("/api/schedule")
async def get_schedule(info: schemas.LoginInfo):
    """
    获取个人课表 API
    接收用户的教务系统账号密码，返回爬取的课表数据（JSON格式）
    """
    logger.info(f"正在为用户 {info.username} 抓取课表...")
    try:
        global browser_instance, browser_semaphore
        if not browser_instance:
            raise HTTPException(status_code=500, detail="服务器内部错误：Playwright 浏览器未初始化")

        # 使用 Semaphore 控制并发请求数量，避免内存耗尽
        async with browser_semaphore:
            logger.info("创建独立 BrowserContext 避免缓存/Cookie冲突...")
            # 每个请求创建一个新的 Context
            context = await browser_instance.new_context()
            try:
                # 调用 scraper 中的抓取逻辑，并传入 Context
                result = await get_campus_schedule(
                   context=context,
                   username=info.username,
                   password=info.password,
                   save_to_file=False
                )
            finally:
                # 非常重要：用完 Context 后立刻关闭！
                await context.close()
                logger.info("清理完毕当前的 BrowserContext")
        
        # 检查是否有错误
        if isinstance(result, dict) and "error" in result:
            error_msg = result['error']
            logger.error(f"课表抓取失败: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # 成功返回课表数据
        schedule_data = result if isinstance(result, list) else []
        logger.info(f"成功为用户 {info.username} 抓取课表，共 {len(schedule_data)} 条记录")
        return {
            "status": "success",
            "data": schedule_data,
            "count": len(schedule_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e) if str(e) else "未知错误"
        error_type = type(e).__name__
        logger.error(f"课表抓取异常 [{error_type}]: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"课表抓取失败: {error_msg}")


# ==================== 获取全部帖子 (改进版 支持分页或者一次性获取) ====================
@app.get("/api/posts")
def get_all_posts(
    skip:int=0,
    limit:int=100,
    r:Redis=Depends(get_redis),
):
    #使用 lrange 切片取出帖子 ID 列表
    post_ids=r.lrange("posts:timeline",skip,skip+limit-1)
    if not post_ids:
        return []
    result=[]
    for pid in post_ids:
        #遍历ID，去Hash表里把完整的帖子数据捞出来
        # HGETALL 能获取该键下的整个字典
        post_data=r.hgetall(f"post:{pid}")
        if post_data:
            #因为从redis取出来都是字节串，所以要转一下
            post_data["id"]=int(post_data["id"])
            result.append(post_data)
    
    return result


@app.get("/api/posts/{post_id}", response_model=schemas.Post)
def get_post_detail(post_id: int, r: Redis = Depends(get_redis)):
    post_data = r.hgetall(f"post:{post_id}")
    if not post_data:
        raise HTTPException(status_code=404, detail="帖子不存在")
    post_data["id"] = int(post_data["id"])
    return post_data

# ==================== 发布帖子 ====================
@app.post("/api/posts", response_model=schemas.Post)
def create_post(
    payload: schemas.PostCreate,
    r: Redis = Depends(get_redis),
):
    #拦截空数据
    title=(payload.title or "").strip()
    content=(payload.content or "").strip()
    if not title or not content:
        raise HTTPException(status_code=400,detail="标题和内容不能为空")
    
    #生成自增的主键ID
    # INCR 命令会自动把 "post_id_counter" 加 1
    post_id=r.incr("global:post_id")
    
    #组装数据字典
    post_data={
        "id":post_id,
        "title":title,
        "content":content,
        "created_at":datetime.now().isoformat(),#时间格式化
    }
    # 把数据存入Redis的Hash表
    # 键名设计为"post:1","post:2"这种层级格式，upstash 中多字段字典通过 values= 传入
    r.hset(f"post:{post_id}", values=post_data)

    # 把帖子ID塞入一个大列表（List）的最前面，方便查询最新帖子
    r.lpush("posts:timeline", post_id)

    return post_data


# ==================== 收藏（Favorite）====================
@app.get("/api/me/favorites/ids", response_model=list[int])
def my_favorite_ids(
    r: Redis = Depends(get_redis),
    current_user: dict = Depends(get_current_user),
):
    # TODO: 实现 Redis 获取收藏 ID 列表逻辑
    return []


@app.get("/api/me/favorites", response_model=list[schemas.Post])
def my_favorites(
    r: Redis = Depends(get_redis),
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    # TODO: 实现 Redis 获取收藏帖子列表逻辑
    return []


@app.post("/api/posts/{post_id}/favorite")
def favorite_post(
    post_id: int,
    r: Redis = Depends(get_redis),
    current_user: dict = Depends(get_current_user),
):
    # TODO: 实现 Redis 收藏逻辑
    return {"success": True}


@app.delete("/api/posts/{post_id}/favorite")
def unfavorite_post(
    post_id: int,
    r: Redis = Depends(get_redis),
    current_user: dict = Depends(get_current_user),
):
    # TODO: 实现 Redis 取消收藏逻辑
    return {"success": True}

# ==================== AI 问答接口 ====================
@app.post("/api/ai/chat")
def ai_campus_chat(request: ChatRequest):
    if not request.user_message:
        raise HTTPException(status_code=400, detail="发点什么吧~")
    
    SYSTEM_PROMPT = """
    你现在是“校园圈”的专属 AI 助手，名叫“小圈”。你的人设是一位热情、幽默、懂很多的大学长/大学姐。
    你的任务是解答同学们关于校园生活、学习指南、吃喝玩乐的疑问。
    规则：
    1. 语气亲切自然，多使用 emoji ✨🎓。
    2. 如果遇到你不知道的具体学校规定，请建议同学在【校园圈论坛】发帖求助。
    3. 字数控制在 200 字以内。
    """

    try:
        response = ai_client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct", 
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.user_message}
            ],
            temperature=0.7 
        )
        ai_reply = response.choices[0].message.content
        return {"success": True, "reply": ai_reply}
        
    except Exception as e:
        logger.error(f"硅基流动调用报错: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="小圈学长/学姐的脑子短路了，稍后再试吧~")

# 注意：下面的路由如果是启动应用（如 if __name__ == '__main__':）需要保留在文件最底部
