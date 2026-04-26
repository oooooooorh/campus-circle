from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging
import asyncio
import json
import sys
import os
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright
from openai import OpenAI
from pydantic import BaseModel

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

# 根路由
@app.get("/")
def root():
    logger.info("访问根路径")
    return {
        "status": "success",
        "message": "校园圈后端服务正在运行",
        "version": "1.0.0"
    }


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
def get_all_posts(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    posts = db.query(models.Post).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts

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
