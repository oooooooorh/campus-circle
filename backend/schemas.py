from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any


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

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换

class AppointmentCreate(BaseModel):
    date: str
    time_slot: str
    user_name: str
    
class Appointment(BaseModel):
    id: int
    class Config:
        from_attributes = True  # 允许从 ORM 模型转换