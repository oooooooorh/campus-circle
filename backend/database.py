from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

# 1. 定义数据库文件的位置（项目根目录下的 campus.db，或通过环境变量设置以适应生产环境）
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./campus.db")

# 2. 创建引擎：负责与 SQLite 通讯
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. 创建会话工厂：每次存取数据都要开一个“会话”
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 创建基类：以后所有的数据库表都要继承它
Base = declarative_base()


# 5. 依赖项：获取数据库连接，用完自动关闭
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
