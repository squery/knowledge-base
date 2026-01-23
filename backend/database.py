"""
数据库管理模块
SQLite数据库连接和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os

from models import Base
from logger_config import get_logger

logger = get_logger(__name__)

# 数据库文件路径
DATABASE_DIR = "./data"
DATABASE_FILE = "knowledge_base.db"
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_FILE)
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite特定配置
    echo=False  # 设置为True可以看到SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """初始化数据库,创建所有表"""
    try:
        # 确保数据库目录存在
        os.makedirs(DATABASE_DIR, exist_ok=True)
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info(f"数据库初始化成功: {DATABASE_PATH}")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}", exc_info=True)
        raise


@contextmanager
def get_db_session() -> Session:
    """
    获取数据库会话上下文管理器
    使用示例:
        with get_db_session() as db:
            db.query(FileMetadata).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"数据库操作失败: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


def get_db():
    """
    获取数据库会话依赖注入
    用于FastAPI路由中的依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
