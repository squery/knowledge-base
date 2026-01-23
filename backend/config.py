"""
后端配置管理模块
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本配置
    APP_NAME: str = "本地知识库系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # 数据库配置
    CHROMA_DB_PATH: str = "./indexes"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DB: str = "knowledge_base"
    MYSQL_POOL_SIZE: int = 10
    
    # 文件配置
    UPLOAD_DIR: str = "./data"
    DOCUMENTS_DIR: str = "./data/documents"
    CODE_DIR: str = "./data/code"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_DOCUMENT_TYPES: list = [".txt", ".pdf", ".docx", ".md", ".html"]
    ALLOWED_CODE_TYPES: list = [".py", ".js", ".java", ".cpp", ".go", ".rs", ".ts", ".jsx", ".tsx", ".cs"]
    
    # 日志配置
    LOG_DIR: str = "./logs"
    LOG_LEVEL: str = "INFO"
    
    # 文本分块配置
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 200
    
    # 向量化配置
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DEVICE: str = "cpu"  # 改为 "cuda" 如果有GPU
    
    # AI模型配置
    LLM_MODEL_NAME: str = "chatglm-6b"  # 或其他开源模型
    LLM_MODEL_PATH: Optional[str] = None  # 本地模型路径
    LLM_DEVICE: str = "cpu"  # 改为 "cuda" 如果有GPU
    MAX_TOKENS: int = 512
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    TOP_K: int = 50
    
    # 检索配置
    RETRIEVAL_K: int = 3  # 返回最相关的K条文档
    SIMILARITY_THRESHOLD: float = 0.5  # 相似度阈值
    USE_HYBRID_SEARCH: bool = True  # 混合检索
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
