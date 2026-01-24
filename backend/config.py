"""
后端配置管理模块
"""
# 兼容 pydantic v2/v1：优先使用 pydantic_settings(BaseSettings)，否则回退到 pydantic.BaseSettings
try:
    from pydantic_settings import BaseSettings  # v2 推荐
except Exception:
    from pydantic import BaseSettings  # v1 回退
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
    MYSQL_PASSWORD: str = ""
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
    # LLM默认模型（免费常用）：mT5-multilingual-XLSum 多语言摘要（轻量级）
    # 可选：
    # - "csebuetnlp/mT5-multilingual-XLSum"（summarization管线，支持中文，轻量级）
    # - "uer/t5-v1_1-base-chinese-cluecorpussmall"（text2text-generation，中文专用）
    # - "google/mt5-small"（多语言T5，较小）
    # - "t5-small"（英文为主，资源占用小）
    LLM_MODEL_NAME: str = "csebuetnlp/mT5-multilingual-XLSum"
    LLM_MODEL_PATH: Optional[str] = None  # 本地模型路径
    LLM_DEVICE: str = "cpu"  # 改为 "cuda" 如果有GPU
    MAX_TOKENS: int = 128  # mT5-XLSum摘要倾向于简洁
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    TOP_K: int = 50
    USE_LLM_QA: bool = True  # 是否启用高级生成回答（默认开启，可由前端覆盖）
    LLM_PIPELINE: str = "summarization"  # transformers管线类型: summarization 或 text2text-generation
    
    # 检索配置
    RETRIEVAL_K: int = 3  # 返回最相关的K条文档
    SIMILARITY_THRESHOLD: float = 0.5  # 相似度阈值
    USE_HYBRID_SEARCH: bool = True  # 混合检索
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
