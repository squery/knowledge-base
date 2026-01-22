"""
日志管理模块
"""
import os
from loguru import logger
from config import settings


def setup_logger():
    """配置日志系统"""
    
    # 创建日志目录
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台处理器
    logger.add(
        sink=lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # 添加文件处理器 - 所有日志
    logger.add(
        sink=os.path.join(settings.LOG_DIR, "app.log"),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="500 MB",
        retention="7 days",
        encoding="utf-8"
    )
    
    # 添加文件处理器 - 错误日志
    logger.add(
        sink=os.path.join(settings.LOG_DIR, "error.log"),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="500 MB",
        retention="30 days",
        encoding="utf-8"
    )
    
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} 日志系统初始化完成")
    return logger


# 获取logger实例
def get_logger(name: str = __name__):
    """获取logger实例"""
    return logger.bind(name=name)
