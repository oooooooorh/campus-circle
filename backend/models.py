from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .database import Base  # 继承刚才创建的基类


class Post(Base):
    __tablename__ = "posts"  # 数据库里的表名

    id = Column(Integer, primary_key=True, index=True)  # 主键 ID
    title = Column(String(100), index=True)  # 标题
    content = Column(Text)  # 内容
    created_at = Column(DateTime, default=datetime.now)  # 发帖时间
