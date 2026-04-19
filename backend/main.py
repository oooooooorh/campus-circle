from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging
import asyncio
import json
import sys
import os

# 添加后端目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import models
import schemas
import database
from scraper import get_campus_schedule

# 配置日志，确保UTF-8编码处理中文
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 启动时自动创建数据库表
database.Base.metadata.create_all(bind=database.engine)

# 创建 FastAPI 应用
app = FastAPI(title="校园圈后端中心")

# CORS 配置：允许前端跨域请求
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        # 在线程池中运行异步爬虫，避免事件循环冲突
        # 这是处理 Playwright + FastAPI 兼容性问题的标准做法
        from concurrent.futures import ThreadPoolExecutor
        import concurrent.futures
        
        def run_scraper():
            """在独立事件循环中运行爬虫"""
            try:
                # 为线程创建新的事件循环
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        get_campus_schedule(info.username, info.password)
                    )
                    return result
                finally:
                    loop.close()
            except Exception as e:
                logger.error(f"爬虫线程异常: {e}", exc_info=True)
                return {"error": str(e) if str(e) else "未知错误"}
        
        # 使用线程池执行
        with ThreadPoolExecutor(max_workers=1) as executor:
            result = executor.submit(run_scraper).result(timeout=180)
        
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
    except concurrent.futures.TimeoutError:
        logger.error("课表抓取超时（180秒）")
        raise HTTPException(status_code=408, detail="课表抓取超时，请稍后重试")
    except Exception as e:
        error_msg = str(e) if str(e) else "未知错误"
        logger.error(f"课表抓取异常: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"课表抓取失败: {error_msg}")


# 接口 1：获取所有帖子
@app.get("/api/posts", response_model=list[schemas.Post])
def get_posts(db: Session = Depends(database.get_db)):
    logger.info("收到获取帖子请求")
    try:
        posts = db.query(models.Post).order_by(models.Post.id.desc()).all()
        logger.info(f"成功获取 {len(posts)} 条帖子")
        return posts
    except Exception as e:
        logger.error(f"获取帖子失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取帖子失败: {str(e)}")


# 接口 2：发布新帖子
@app.post("/api/posts", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(database.get_db)):
    logger.info(f"收到发布帖子请求: {post.title}")
    try:
        db_post = models.Post(title=post.title, content=post.content)
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        logger.info(f"成功发布帖子: ID={db_post.id}, 标题={db_post.title}")
        return db_post
    except Exception as e:
        db.rollback()
        logger.error(f"发布帖子失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"发布帖子失败: {str(e)}")


# 接口3：获取指定日期的预约占用情况
@app.get("/api/appointments/status/{date}")
def get_status(date: str, db: Session = Depends(database.get_db)):
    # 查找数据库中该日期所有已被约的记录
    booked_slots = (
        db.query(models.Appointment).filter(models.Appointment.date == date).all()
    )
    # 只返回时间段列表，例如 ["10:00 ~ 10:30", "11:00 ~ 11:30"]
    return [slot.time_slot for slot in booked_slots]


# 接口4：提交预约请求
@app.post("/api/appointments")
def create_appointment(
    data: schemas.AppointmentCreate, db: Session = Depends(database.get_db)
):
    # --- 核心：防冲突检查 ---
    # 在存入之前，先查一遍：这个日期和时间段是否已经存在？
    exists = (
        db.query(models.Appointment)
        .filter(
            models.Appointment.date == data.date,
            models.Appointment.time_slot == data.time_slot,
        )
        .first()
    )

    if exists:
        # 如果已经存在，直接抛出 400 错误，告诉前端“被人抢先了”
        raise HTTPException(status_code=400, detail="该时间段已被预约，请选择其他时段")

    # 如果不存在，才执行写入
    db_appointment = models.Appointment(**data.dict())
    db.add(db_appointment)
    db.commit()
    return {"message": "预约成功"}
