from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime
import database


class Post(database.Base):
    __tablename__ = "posts"  # 数据库里的表名

    id = Column(Integer, primary_key=True, index=True)  # 主键 ID
    title = Column(String(100), index=True)  # 标题
    content = Column(Text)  # 内容
    created_at = Column(DateTime, default=datetime.now)  # 发帖时间

class Appointment(database.Base):
    __tablename__ = "appointments"  # 数据库里的表名

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)      # 记录日期，如 "2023-10-28"
    time_slot = Column(String)            # 记录时间段，如 "14:30 ~ 15:00"
    user_name = Column(String)            # 预约人姓名
    is_completed = Column(Boolean, default=False) # 是否已完成  