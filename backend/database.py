"""
数据库管理模块
MySQL数据库连接和会话管理
"""
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

try:
    from backend.models import Base
except Exception:
    from models import Base
try:
    from backend.logger_config import get_logger
except Exception:
    from logger_config import get_logger
try:
    from backend.config import settings
except Exception:
    from config import settings

logger = get_logger(__name__)

def _build_mysql_url(database: str | None = None) -> URL:
    """构建MySQL连接URL"""
    return URL.create(
        drivername="mysql+pymysql",
        username=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        database=database,
        query={"charset": "utf8mb4"}
    )


# 创建数据库引擎
engine = create_engine(
    _build_mysql_url(settings.MYSQL_DB),
    pool_size=settings.MYSQL_POOL_SIZE,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """初始化数据库,创建所有表"""
    try:
        # 确保数据库存在
        server_engine = create_engine(_build_mysql_url())
        with server_engine.connect() as conn:
            conn.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS `{settings.MYSQL_DB}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            )
            conn.commit()

        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info(
            "数据库初始化成功: %s@%s:%s/%s",
            settings.MYSQL_USER,
            settings.MYSQL_HOST,
            settings.MYSQL_PORT,
            settings.MYSQL_DB,
        )
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
