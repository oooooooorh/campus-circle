from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database

# 启动时自动创建数据库表
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# ... 之前的 CORS 配置保持不变 ...


# 接口 1：获取所有帖子
@app.get("/api/posts", response_model=list[schemas.Post])
def get_posts(db: Session = Depends(database.get_db)):
    # 逐行解释：从数据库查询所有 Post 记录，按 ID 倒序排列
    posts = db.query(models.Post).order_by(models.Post.id.desc()).all()
    return posts


# 接口 2：发布新帖子
@app.post("/api/posts", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(database.get_db)):
    # 逐行解释：
    # 1. 将前端传来的数据(post)转换成数据库模型(db_post)
    db_post = models.Post(title=post.title, content=post.content)
    # 2. 添加到会话
    db.add(db_post)
    # 3. 提交到数据库（真正写入硬盘）
    db.commit()
    # 4. 刷新数据（获取数据库生成的 ID 和时间）
    db.refresh(db_post)
    return db_post
