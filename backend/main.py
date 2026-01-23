"""
后端主应用入口
FastAPI应用初始化与路由配置
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config import settings
from logger_config import setup_logger, get_logger
from database import init_database
from routers import file_routes

# 初始化日志
logger = setup_logger()
app_logger = get_logger(__name__)


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="本地知识库系统 - 支持文档和代码的智能检索与问答",
    docs_url="/docs",
    redoc_url="/redoc"
)


# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(file_routes.router)


# 错误处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    app_logger.error(f"HTTP异常: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "success": False}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理器"""
    app_logger.error(f"未预期的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误", "success": False}
    )


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# 基础信息端点
@app.get("/info")
async def app_info():
    """获取应用信息"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "upload_dir": settings.UPLOAD_DIR,
        "max_file_size_mb": settings.MAX_FILE_SIZE // (1024 * 1024)
    }


# 初始化目录
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    app_logger.info("应用启动中...")
    
    # 初始化数据库
    init_database()
    
    # 创建必要的目录
    for directory in [
        settings.DOCUMENTS_DIR,
        settings.CODE_DIR,
        settings.CHROMA_DB_PATH,
        settings.LOG_DIR
    ]:
        os.makedirs(directory, exist_ok=True)
        app_logger.info(f"确保目录存在: {directory}")
    
    app_logger.info("应用启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    app_logger.info("应用关闭中...")


if __name__ == "__main__":
    app_logger.info(f"启动API服务器: {settings.HOST}:{settings.PORT}")
    # reload=True时需要传入导入字符串，但直接运行时设为False
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,  # 直接运行时不启用reload
        log_config=None  # 使用自定义日志配置
    )
