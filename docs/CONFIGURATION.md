# 配置说明

本文档详细说明系统的所有配置选项。

---

## 📋 目录

- [环境变量配置](#环境变量配置)
- [后端配置](#后端配置)
- [前端配置](#前端配置)
- [模型配置](#模型配置)
- [数据库配置](#数据库配置)
- [日志配置](#日志配置)
- [性能调优](#性能调优)

---

## 环境变量配置

### .env 文件

项目根目录的 `.env` 文件包含核心配置。

**示例配置**:
```ini
# ============================================
# 应用配置
# ============================================
APP_NAME=本地知识库系统
APP_VERSION=1.0.0
DEBUG=True
LOG_LEVEL=INFO

# ============================================
# 服务器配置
# ============================================
HOST=0.0.0.0
PORT=8000
FRONTEND_PORT=8501

# 允许跨域
CORS_ORIGINS=["http://localhost:8501", "http://localhost:3000"]

# ============================================
# 文件配置
# ============================================
# 文件上传限制（字节）
MAX_FILE_SIZE=104857600  # 100MB
MAX_BATCH_SIZE=10

# 支持的文件类型
ALLOWED_DOCUMENT_TYPES=[".txt", ".pdf", ".docx", ".md", ".html"]
ALLOWED_CODE_TYPES=[".py", ".js", ".java", ".cpp", ".go", ".rs", ".ts"]

# 存储路径
DATA_DIR=./data
DOCUMENTS_DIR=./data/documents
CODE_DIR=./data/code
INDEX_DIR=./indexes
LOG_DIR=./logs

# ============================================
# 嵌入模型配置
# ============================================
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DEVICE=cpu  # cpu 或 cuda
EMBEDDING_BATCH_SIZE=32

# 模型缓存目录
MODEL_CACHE_DIR=./models

# ============================================
# LLM模型配置
# ============================================
USE_LLM_QA=False
LLM_MODEL_NAME=google/mt5-small
LLM_DEVICE=cpu
LLM_MAX_LENGTH=512

# ============================================
# 向量数据库配置
# ============================================
VECTOR_DB=chroma  # chroma 或 faiss
CHROMA_PERSIST_DIR=./indexes

# ============================================
# 检索配置
# ============================================
# 分块大小
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# 检索参数
RETRIEVAL_K=3
SIMILARITY_THRESHOLD=0.5
MAX_CONTEXT_LENGTH=2000

# ============================================
# 数据库配置
# ============================================
DATABASE_URL=sqlite:///./data/knowledge_base.db
DATABASE_ECHO=False

# ============================================
# 日志配置
# ============================================
LOG_FORMAT=<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>
LOG_ROTATION=10 MB
LOG_RETENTION=7 days
LOG_COMPRESSION=zip

# ============================================
# 性能配置
# ============================================
WORKERS=4
TIMEOUT=120
KEEPALIVE=5
```

### 配置说明

#### 应用配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `APP_NAME` | string | 本地知识库系统 | 应用名称 |
| `APP_VERSION` | string | 1.0.0 | 版本号 |
| `DEBUG` | boolean | True | 调试模式 |
| `LOG_LEVEL` | string | INFO | 日志级别 (DEBUG/INFO/WARNING/ERROR) |

#### 服务器配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `HOST` | string | 0.0.0.0 | 监听地址 |
| `PORT` | integer | 8000 | 后端端口 |
| `FRONTEND_PORT` | integer | 8501 | 前端端口 |
| `CORS_ORIGINS` | list | [] | 允许的跨域源 |

#### 文件配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `MAX_FILE_SIZE` | integer | 104857600 | 单文件最大100MB |
| `MAX_BATCH_SIZE` | integer | 10 | 批量上传最多10个 |
| `ALLOWED_DOCUMENT_TYPES` | list | [...] | 允许的文档类型 |
| `ALLOWED_CODE_TYPES` | list | [...] | 允许的代码类型 |

#### 模型配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `EMBEDDING_MODEL` | string | paraphrase-multilingual-MiniLM-L12-v2 | 嵌入模型名称 |
| `EMBEDDING_DEVICE` | string | cpu | 设备类型 (cpu/cuda) |
| `EMBEDDING_BATCH_SIZE` | integer | 32 | 批处理大小 |
| `USE_LLM_QA` | boolean | False | 是否使用LLM |
| `LLM_MODEL_NAME` | string | google/mt5-small | LLM模型名称 |

#### 检索配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `CHUNK_SIZE` | integer | 500 | 文本分块大小 |
| `CHUNK_OVERLAP` | integer | 50 | 分块重叠大小 |
| `RETRIEVAL_K` | integer | 3 | 返回最相关的K个结果 |
| `SIMILARITY_THRESHOLD` | float | 0.5 | 相似度阈值 (0-1) |

---

## 后端配置

### backend/config.py

后端核心配置文件。

```python
import os
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "本地知识库系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 文件配置
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_DOCUMENT_TYPES: List[str] = [
        ".txt", ".pdf", ".docx", ".md", ".html"
    ]
    ALLOWED_CODE_TYPES: List[str] = [
        ".py", ".js", ".java", ".cpp", ".go", ".rs"
    ]
    
    # 路径配置
    DATA_DIR: str = "./data"
    DOCUMENTS_DIR: str = "./data/documents"
    CODE_DIR: str = "./data/code"
    INDEX_DIR: str = "./indexes"
    LOG_DIR: str = "./logs"
    
    # 模型配置
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DEVICE: str = "cpu"
    
    # 检索配置
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RETRIEVAL_K: int = 3
    SIMILARITY_THRESHOLD: float = 0.5
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/knowledge_base.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局配置实例
settings = Settings()
```

### 自定义配置

可以通过继承`Settings`类添加自定义配置：

```python
from backend.config import Settings

class CustomSettings(Settings):
    # 自定义配置
    CUSTOM_FEATURE: bool = True
    CUSTOM_PARAM: str = "value"
    
    class Config:
        env_file = ".env.custom"
```

---

## 前端配置

### Streamlit 配置

**config.toml** (`.streamlit/config.toml`):

```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
serverAddress = "localhost"
serverPort = 8501

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = true
toolbarMode = "minimal"

[logger]
level = "info"
```

### 前端环境变量

```python
# frontend/config.py
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "100"))
```

---

## 模型配置

### 嵌入模型

#### 推荐模型

| 模型名称 | 大小 | 性能 | 适用场景 |
|----------|------|------|----------|
| paraphrase-multilingual-MiniLM-L12-v2 | 470MB | 快速 | 多语言通用 |
| sentence-transformers/all-MiniLM-L6-v2 | 90MB | 极快 | 英文短文本 |
| BAAI/bge-large-zh | 1.3GB | 优秀 | 中文长文本 |
| BAAI/bge-base-zh-v1.5 | 400MB | 良好 | 中文平衡 |

#### 模型切换

修改 `.env`:
```ini
EMBEDDING_MODEL=BAAI/bge-base-zh-v1.5
```

或在代码中:
```python
from backend.services.embedding_service import EmbeddingService

# 使用自定义模型
embedding_service = EmbeddingService(
    model_name="BAAI/bge-base-zh-v1.5",
    device="cuda"
)
```

### LLM模型

#### 推荐模型

| 模型名称 | 大小 | 内存需求 | 适用场景 |
|----------|------|----------|----------|
| google/mt5-small | 300MB | 2GB | 轻量级 |
| chatglm-6b | 12GB | 16GB | 中文对话 |
| Qwen-7B-Chat | 14GB | 20GB | 中文通用 |
| llama-2-7b | 13GB | 18GB | 英文通用 |

#### 启用LLM

```ini
# .env
USE_LLM_QA=True
LLM_MODEL_NAME=google/mt5-small
LLM_DEVICE=cuda  # 推荐GPU
LLM_MAX_LENGTH=512
```

---

## 数据库配置

### SQLite (默认)

```python
DATABASE_URL=sqlite:///./data/knowledge_base.db
```

优点：
- 无需额外安装
- 配置简单
- 适合小规模部署

缺点：
- 并发性能有限
- 不适合大规模部署

### PostgreSQL (推荐生产环境)

```python
DATABASE_URL=postgresql://user:password@localhost:5432/knowledge_base
```

**安装依赖**:
```bash
pip install psycopg2-binary
```

**创建数据库**:
```sql
CREATE DATABASE knowledge_base;
CREATE USER kb_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE knowledge_base TO kb_user;
```

### MySQL

```python
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/knowledge_base
```

**安装依赖**:
```bash
pip install pymysql
```

---

## 日志配置

### Loguru 配置

**backend/logger_config.py**:

```python
from loguru import logger
import sys

# 移除默认处理器
logger.remove()

# 控制台输出
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    level="INFO",
    colorize=True
)

# 文件输出
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="00:00",  # 每天午夜轮转
    retention="7 days",  # 保留7天
    compression="zip",  # 压缩
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

# 错误日志单独记录
logger.add(
    "logs/error_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    compression="zip",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}"
)
```

### 日志级别

| 级别 | 用途 |
|------|------|
| `DEBUG` | 调试信息 |
| `INFO` | 一般信息 |
| `WARNING` | 警告信息 |
| `ERROR` | 错误信息 |
| `CRITICAL` | 严重错误 |

### 自定义日志

```python
from loguru import logger

# 添加自定义处理器
logger.add(
    "logs/custom_{time}.log",
    filter=lambda record: "custom" in record["extra"],
    level="DEBUG"
)

# 使用
logger.bind(custom=True).info("这是自定义日志")
```

---

## 性能调优

### 1. Worker配置

#### Uvicorn Workers

```bash
uvicorn backend.main:app --workers 4 --host 0.0.0.0 --port 8000
```

**建议**:
- CPU密集型: workers = CPU核心数
- IO密集型: workers = CPU核心数 * 2

#### Gunicorn + Uvicorn

```bash
gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### 2. 数据库连接池

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 最大溢出连接
    pool_timeout=30,  # 超时时间
    pool_recycle=3600  # 连接回收时间
)
```

### 3. 缓存配置

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_embedding(text: str):
    # 缓存嵌入结果
    return embedding_service.embed_text(text)
```

### 4. 模型优化

#### 模型量化

```python
# 8位量化
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_8bit=True
)

model = AutoModel.from_pretrained(
    model_name,
    quantization_config=quantization_config
)
```

#### 模型缓存

```python
# 预加载模型
import torch

# 启动时加载模型到内存
embedding_service = EmbeddingService()
embedding_service.model.eval()

# GPU预热
if torch.cuda.is_available():
    dummy_input = ["预热文本"]
    embedding_service.embed_texts(dummy_input)
```

---

## 配置验证

### 配置检查脚本

```python
# scripts/check_config.py
from backend.config import settings
import os

def check_config():
    print("🔍 检查配置...")
    
    # 检查必需目录
    required_dirs = [
        settings.DATA_DIR,
        settings.DOCUMENTS_DIR,
        settings.CODE_DIR,
        settings.INDEX_DIR,
        settings.LOG_DIR
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"❌ 目录不存在: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
            print(f"✅ 已创建: {dir_path}")
        else:
            print(f"✅ 目录存在: {dir_path}")
    
    # 检查模型配置
    print(f"\n📦 嵌入模型: {settings.EMBEDDING_MODEL}")
    print(f"🖥️  设备: {settings.EMBEDDING_DEVICE}")
    print(f"📊 检索K值: {settings.RETRIEVAL_K}")
    
    print("\n✅ 配置检查完成！")

if __name__ == "__main__":
    check_config()
```

---

## 环境特定配置

### 开发环境

```ini
# .env.development
DEBUG=True
LOG_LEVEL=DEBUG
EMBEDDING_DEVICE=cpu
USE_LLM_QA=False
```

### 生产环境

```ini
# .env.production
DEBUG=False
LOG_LEVEL=INFO
EMBEDDING_DEVICE=cuda
USE_LLM_QA=True
WORKERS=8
```

### 加载特定环境

```python
import os
from backend.config import Settings

env = os.getenv("ENV", "development")
settings = Settings(_env_file=f".env.{env}")
```

---

**最后更新**: 2026年1月26日  
**文档版本**: 1.0.0
