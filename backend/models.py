from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from datetime import datetime
import database


class User(database.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    display_name = Column(String(50), nullable=True)
    bio = Column(String(200), nullable=True)
    avatar_url = Column(String(300), nullable=True)


class Post(database.Base):
    __tablename__ = "posts"  # 数据库里的表名

    id = Column(Integer, primary_key=True, index=True)  # 主键 ID
    title = Column(String(100), index=True)  # 标题
    content = Column(Text)  # 内容
    created_at = Column(DateTime, default=datetime.now)  # 发帖时间
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)


class Favorite(database.Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)