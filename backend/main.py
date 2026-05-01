from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text, or_
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
from jose import jwt, JWTError
import base64
import hashlib
import hmac
import secrets

# 添加后端目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import models
import schemas
import database
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

# 启动时自动创建数据库表
database.Base.metadata.create_all(bind=database.engine)

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

app.add_middleware(
    CORSMiddleware,
    # 允许所有域名访问（最简单，先确保跑通）
    allow_origins=["*"], 
    # 或者填你的前端地址：allow_origins=["https://ashy-forest-0df45ff00.7.azurestaticapps.net"],
    allow_credentials=True,
    allow_methods=["*"], # 允许所有方法 (GET, POST, OPTIONS等)
    allow_headers=["*"], # 允许所有请求头
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
    db: Session = Depends(database.get_db),
) -> models.User:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="未登录")
    except JWTError:
        raise HTTPException(status_code=401, detail="登录已过期或无效")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user

def _normalize_tag(name: str) -> str:
    n = (name or "").strip()
    n = " ".join(n.split())
    return n


def _get_tags_for_posts(db: Session, post_ids: list[int]) -> dict[int, list[str]]:
    if not post_ids:
        return {}
    rows = (
        db.query(models.PostTag.post_id, models.Tag.name)
        .join(models.Tag, models.PostTag.tag_id == models.Tag.id)
        .filter(models.PostTag.post_id.in_(post_ids))
        .all()
    )
    m: dict[int, list[str]] = {}
    for pid, name in rows:
        m.setdefault(pid, []).append(name)
    for pid in m:
        m[pid] = sorted(set(m[pid]))
    return m


# ==================== SQLite 轻量迁移（开发用）====================
def _sqlite_column_exists(db: Session, table: str, column: str) -> bool:
    rows = db.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return any(r[1] == column for r in rows)


def ensure_sqlite_schema():
    # 仅对 SQLite 做轻量 ALTER TABLE（本项目默认 SQLite）
    if not str(database.engine.url).startswith("sqlite"):
        return
    db = database.SessionLocal()
    try:
        # posts.user_id：旧库没有该列会导致查询崩溃
        if _sqlite_column_exists(db, "posts", "id") and not _sqlite_column_exists(db, "posts", "user_id"):
            db.execute(text("ALTER TABLE posts ADD COLUMN user_id INTEGER"))
            db.commit()

        # users profile columns
        if _sqlite_column_exists(db, "users", "id") and not _sqlite_column_exists(db, "users", "display_name"):
            db.execute(text("ALTER TABLE users ADD COLUMN display_name VARCHAR(50)"))
            db.commit()
        if _sqlite_column_exists(db, "users", "id") and not _sqlite_column_exists(db, "users", "bio"):
            db.execute(text("ALTER TABLE users ADD COLUMN bio VARCHAR(200)"))
            db.commit()
        if _sqlite_column_exists(db, "users", "id") and not _sqlite_column_exists(db, "users", "avatar_url"):
            db.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(300)"))
            db.commit()
    finally:
        db.close()

ensure_sqlite_schema()

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
def register(payload: schemas.RegisterRequest, db: Session = Depends(database.get_db)):
    username = (payload.username or "").strip()
    password = payload.password or ""
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="用户名至少3位")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="密码至少6位")

    exists = db.query(models.User).filter(models.User.username == username).first()
    if exists:
        raise HTTPException(status_code=409, detail="用户名已存在")

    user = models.User(username=username, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/api/auth/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    username = (payload.username or "").strip()
    password = payload.password or ""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(
        sub=user.username,
        expires_delta=timedelta(minutes=JWT_EXPIRES_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}


@app.get("/api/me", response_model=schemas.UserPublic)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.patch("/api/me", response_model=schemas.UserPublic)
def update_me(
    payload: schemas.UserUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    if payload.display_name is not None:
        current_user.display_name = (payload.display_name or "").strip() or None
    if payload.bio is not None:
        current_user.bio = (payload.bio or "").strip() or None
    if payload.avatar_url is not None:
        current_user.avatar_url = (payload.avatar_url or "").strip() or None
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@app.post("/api/me/avatar", response_model=schemas.UserPublic)
def upload_my_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件")

    # 简单白名单：常见图片扩展
    ext = ""
    if file.filename and "." in file.filename:
        ext = "." + file.filename.rsplit(".", 1)[-1].lower().strip()
    if ext not in [".png", ".jpg", ".jpeg", ".webp", ".gif", ""]:
        raise HTTPException(status_code=400, detail="不支持的图片格式")

    filename = f"user_{current_user.id}_{int(datetime.utcnow().timestamp())}{ext or '.png'}"
    save_path = os.path.join(AVATAR_DIR, filename)

    data = file.file.read()
    if len(data) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片不能超过 2MB")
    with open(save_path, "wb") as f:
        f.write(data)

    current_user.avatar_url = f"/static/avatars/{filename}"
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@app.get("/api/me/posts", response_model=list[schemas.Post])
def my_posts(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    posts = (
        db.query(models.Post)
        .filter(models.Post.user_id == current_user.id)
        .order_by(models.Post.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    tag_map = _get_tags_for_posts(db, [p.id for p in posts])
    result = []
    for p in posts:
        item = schemas.Post.model_validate(p)
        item.tags = tag_map.get(p.id, [])
        result.append(item)
    return result


# ==================== 公开用户信息 ====================
@app.get("/api/users/{user_id}", response_model=schemas.PublicUser)
def get_public_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return schemas.PublicUser.model_validate(user)


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
@app.get("/api/posts", response_model=list[schemas.Post])
def get_all_posts(
    skip: int = 0,
    limit: int = 100,
    q: str | None = None,
    db: Session = Depends(database.get_db),
):
    query = db.query(models.Post)
    if q and q.strip():
        kw = f"%{q.strip()}%"
        query = (
            query.outerjoin(models.User, models.Post.user_id == models.User.id)
            .outerjoin(models.PostTag, models.PostTag.post_id == models.Post.id)
            .outerjoin(models.Tag, models.PostTag.tag_id == models.Tag.id)
            .filter(
                or_(
                    models.Post.title.ilike(kw),
                    models.Post.content.ilike(kw),
                    models.User.username.ilike(kw),
                    models.User.display_name.ilike(kw),
                    models.Tag.name.ilike(kw),
                )
            )
            .distinct()
        )

    posts = query.order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()

    user_ids = [p.user_id for p in posts if p.user_id]
    author_map = {}
    if user_ids:
        users = db.query(models.User).filter(models.User.id.in_(list(set(user_ids)))).all()
        author_map = {u.id: u for u in users}

    tag_map = _get_tags_for_posts(db, [p.id for p in posts])

    result = []
    for p in posts:
        item = schemas.Post.model_validate(p)
        if p.user_id and p.user_id in author_map:
            item.author = schemas.UserPublic.model_validate(author_map[p.user_id])
        item.tags = tag_map.get(p.id, [])
        result.append(item)
    return result


@app.get("/api/posts/{post_id}", response_model=schemas.Post)
def get_post_detail(post_id: int, db: Session = Depends(database.get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    item = schemas.Post.model_validate(post)
    if post.user_id:
        u = db.query(models.User).filter(models.User.id == post.user_id).first()
        if u:
            item.author = schemas.UserPublic.model_validate(u)
    item.tags = _get_tags_for_posts(db, [post.id]).get(post.id, [])
    return item

# ==================== 发布帖子 ====================
@app.post("/api/posts", response_model=schemas.Post)
def create_post(
    payload: schemas.PostCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    title = (payload.title or "").strip()
    content = (payload.content or "").strip()
    if not title or not content:
        raise HTTPException(status_code=400, detail="标题和内容不能为空")

    post = models.Post(title=title, content=content, user_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)

    # tags
    tags = payload.tags or []
    norm = []
    for t in tags:
        n = _normalize_tag(t)
        if n:
            norm.append(n)
    # 去重 & 限制 7 个
    norm = list(dict.fromkeys(norm))[:7]
    for name in norm:
        if len(name) > 20:
            raise HTTPException(status_code=400, detail="单个分区标签最多20个字符")
        tag = db.query(models.Tag).filter(models.Tag.name == name).first()
        if not tag:
            tag = models.Tag(name=name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        link = models.PostTag(post_id=post.id, tag_id=tag.id)
        db.add(link)
    db.commit()

    item = schemas.Post.model_validate(post)
    item.author = schemas.UserPublic.model_validate(current_user)
    item.tags = norm
    return item


# ==================== 收藏（Favorite）====================
@app.get("/api/me/favorites/ids", response_model=list[int])
def my_favorite_ids(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    rows = db.query(models.Favorite.post_id).filter(models.Favorite.user_id == current_user.id).all()
    return [r[0] for r in rows]


@app.get("/api/me/favorites", response_model=list[schemas.Post])
def my_favorites(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    fav_post_ids = (
        db.query(models.Favorite.post_id)
        .filter(models.Favorite.user_id == current_user.id)
        .order_by(models.Favorite.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    ids = [r[0] for r in fav_post_ids]
    if not ids:
        return []

    posts = db.query(models.Post).filter(models.Post.id.in_(ids)).all()
    post_map = {p.id: p for p in posts}

    # author hydrate
    user_ids = [p.user_id for p in posts if p.user_id]
    author_map = {}
    if user_ids:
        users = db.query(models.User).filter(models.User.id.in_(list(set(user_ids)))).all()
        author_map = {u.id: u for u in users}

    tag_map = _get_tags_for_posts(db, [p.id for p in posts])

    result = []
    for pid in ids:
        p = post_map.get(pid)
        if not p:
            continue
        item = schemas.Post.model_validate(p)
        if p.user_id and p.user_id in author_map:
            item.author = schemas.UserPublic.model_validate(author_map[p.user_id])
        item.tags = tag_map.get(p.id, [])
        result.append(item)
    return result


@app.post("/api/posts/{post_id}/favorite")
def favorite_post(
    post_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    exists = (
        db.query(models.Favorite)
        .filter(models.Favorite.user_id == current_user.id, models.Favorite.post_id == post_id)
        .first()
    )
    if exists:
        return {"success": True}

    fav = models.Favorite(user_id=current_user.id, post_id=post_id)
    db.add(fav)
    db.commit()
    return {"success": True}


@app.delete("/api/posts/{post_id}/favorite")
def unfavorite_post(
    post_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id, models.Favorite.post_id == post_id
    )
    q.delete()
    db.commit()
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
