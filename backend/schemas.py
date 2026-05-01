from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any


# ==================== 站内账号（注册/登录）====================
class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: int
    username: str
    created_at: datetime
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


# ==================== 登录和课表相关模型 ====================
class LoginInfo(BaseModel):
    """用户登录信息"""
    username: str
    password: str


class ScheduleItem(BaseModel):
    """课表项目"""
    class Config:
        extra = "allow"  # 允许额外字段


# ==================== 论坛相关模型 ====================
# 前端发帖时传过来的数据格式
class PostCreate(BaseModel):
    title: str
    content: str


# 后端返回给前端的数据格式（多了 ID 和时间）
class Post(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    user_id: Optional[int] = None
    author: Optional[UserPublic] = None

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换


class PublicUser(BaseModel):
    id: int
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True