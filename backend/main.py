from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
import schemas
import database
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 启动时自动创建数据库表
database.Base.metadata.create_all(bind=database.engine)

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
