# 故障排查指南

本指南帮助您快速诊断和解决常见问题。

---

## 📋 目录

- [快速诊断](#快速诊断)
- [启动问题](#启动问题)
- [文件上传问题](#文件上传问题)
- [索引问题](#索引问题)
- [问答功能问题](#问答功能问题)
- [性能问题](#性能问题)
- [数据库问题](#数据库问题)
- [模型加载问题](#模型加载问题)
- [网络问题](#网络问题)
- [日志分析](#日志分析)

---

## 快速诊断

### 健康检查

```bash
# 检查后端服务
curl http://localhost:8000/health

# 预期响应
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-26T10:30:00"
}
```

### 端口检查

```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# Linux/macOS
lsof -i :8000
lsof -i :8501
```

### 进程检查

```bash
# Windows
tasklist | findstr python
tasklist | findstr streamlit

# Linux/macOS
ps aux | grep python
ps aux | grep streamlit
```

---

## 启动问题

### ❌ 问题: ModuleNotFoundError

**症状**:
```
ModuleNotFoundError: No module named 'fastapi'
```

**原因**: 依赖包未安装

**解决方案**:
```bash
# 确认虚拟环境已激活
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# 重新安装依赖
pip install -r requirements_v2.txt
```

### ❌ 问题: 端口被占用

**症状**:
```
[ERROR] [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

**原因**: 端口已被其他程序占用

**解决方案**:

**方法1: 更改端口**
```bash
# 修改 .env
PORT=8001
FRONTEND_PORT=8502

# 或启动时指定
uvicorn backend.main:app --port 8001
streamlit run frontend/app.py --server.port 8502
```

**方法2: 释放端口**
```bash
# Windows - 查找占用进程
netstat -ano | findstr :8000
# 记下PID，然后
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8000 | xargs kill -9
```

### ❌ 问题: 虚拟环境问题

**症状**:
```
'python' 不是内部或外部命令
```

**解决方案**:
```bash
# 删除现有虚拟环境
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# 重新创建
python -m venv venv

# 激活
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# 重新安装
pip install -r requirements_v2.txt
```

### ❌ 问题: 权限问题

**症状**:
```
PermissionError: [Errno 13] Permission denied: './data'
```

**解决方案**:
```bash
# Linux/macOS
chmod -R 755 data/
chmod -R 755 logs/
chmod -R 755 indexes/

# Windows (以管理员身份运行)
icacls data /grant Users:F /t
```

---

## 文件上传问题

### ❌ 问题: 文件太大

**症状**:
```
文件超过最大限制100MB
```

**解决方案**:

修改 `.env`:
```ini
MAX_FILE_SIZE=209715200  # 200MB
```

修改 Nginx 配置（如果使用）:
```nginx
client_max_body_size 200M;
```

### ❌ 问题: 不支持的文件类型

**症状**:
```
不支持的文件类型: .xlsx
```

**解决方案**:

修改 `backend/config.py`:
```python
ALLOWED_DOCUMENT_TYPES = [
    ".txt", ".pdf", ".docx", ".md", ".html", 
    ".xlsx", ".csv"  # 添加新类型
]
```

添加相应的解析器:
```python
# backend/processors/text_processor.py
def process_excel(file_path):
    import pandas as pd
    df = pd.read_excel(file_path)
    return df.to_string()
```

### ❌ 问题: 上传失败

**症状**:
```
Upload failed: Connection timeout
```

**诊断步骤**:
1. 检查网络连接
2. 检查磁盘空间
3. 查看后端日志
4. 验证文件权限

**解决方案**:
```bash
# 检查磁盘空间
df -h  # Linux/macOS
wmic logicaldisk get size,freespace,caption  # Windows

# 检查日志
tail -f logs/app.log

# 增加超时时间
# .env
API_TIMEOUT=60
```

---

## 索引问题

### ❌ 问题: 索引创建失败

**症状**:
```
IndexError: Index creation failed
```

**诊断**:
```bash
# 检查索引目录权限
ls -la indexes/

# 检查Chroma数据库
sqlite3 indexes/chroma.sqlite3 "SELECT COUNT(*) FROM collections;"
```

**解决方案**:

**清空并重建索引**:
```python
# Python脚本
from backend.services.vector_store import VectorStore

vector_store = VectorStore()
vector_store.clear_all()  # 清空索引
# 重新上传文件
```

### ❌ 问题: 索引速度慢

**症状**: 索引创建耗时过长

**优化方案**:

1. **增加批处理大小**:
```python
# .env
EMBEDDING_BATCH_SIZE=64  # 从32增加到64
```

2. **使用GPU加速**:
```python
# .env
EMBEDDING_DEVICE=cuda
```

3. **减小chunk大小**:
```python
# .env
CHUNK_SIZE=300  # 从500减少到300
```

### ❌ 问题: 向量数据库损坏

**症状**:
```
sqlite3.DatabaseError: database disk image is malformed
```

**解决方案**:
```bash
# 备份现有数据
cp -r indexes/ indexes_backup/

# 删除损坏的数据库
rm indexes/chroma.sqlite3

# 重启服务，系统会自动创建新数据库
./start_all.sh
```

---

## 问答功能问题

### ❌ 问题: 无法找到相关文档

**症状**: 问答返回"未找到相关信息"

**原因分析**:
1. 文件未索引
2. 相似度阈值太高
3. 问题表述不当

**解决方案**:

1. **检查索引状态**:
```bash
curl http://localhost:8000/api/index/statistics
```

2. **降低相似度阈值**:
```python
# .env
SIMILARITY_THRESHOLD=0.3  # 从0.5降低到0.3
```

3. **增加检索数量**:
```python
# .env
RETRIEVAL_K=5  # 从3增加到5
```

### ❌ 问题: LLM响应慢

**症状**: 问答等待时间超过30秒

**解决方案**:

1. **使用更小的模型**:
```python
# .env
LLM_MODEL_NAME=google/mt5-small  # 使用小模型
```

2. **禁用LLM，使用模板**:
```python
# .env
USE_LLM_QA=False
```

3. **使用GPU**:
```python
# .env
LLM_DEVICE=cuda
```

4. **减少最大长度**:
```python
# .env
LLM_MAX_LENGTH=256  # 从512减少
```

### ❌ 问题: 答案质量差

**症状**: 回答不准确或不相关

**优化方案**:

1. **改进文本分块**:
```python
# .env
CHUNK_SIZE=800  # 增加chunk大小
CHUNK_OVERLAP=100  # 增加重叠
```

2. **使用更好的嵌入模型**:
```python
# .env
EMBEDDING_MODEL=BAAI/bge-large-zh
```

3. **优化提示词**:
```python
# backend/services/qa_service.py
PROMPT_TEMPLATE = """
基于以下上下文信息，详细回答用户问题。
如果无法从上下文中找到答案，请明确说明。

上下文：
{context}

问题：{question}

详细回答：
"""
```

---

## 性能问题

### ❌ 问题: 内存占用高

**症状**: 系统内存占用超过8GB

**诊断**:
```bash
# 查看进程内存
ps aux --sort=-%mem | head

# Python内存分析
pip install memory_profiler
python -m memory_profiler backend/main.py
```

**解决方案**:

1. **减少worker数量**:
```bash
# 从4个减少到2个
uvicorn backend.main:app --workers 2
```

2. **使用模型量化**:
```python
# 8位量化可减少50%内存
from transformers import BitsAndBytesConfig
quantization_config = BitsAndBytesConfig(load_in_8bit=True)
```

3. **清理缓存**:
```python
import gc
import torch

gc.collect()
if torch.cuda.is_available():
    torch.cuda.empty_cache()
```

### ❌ 问题: CPU使用率高

**症状**: CPU持续100%

**解决方案**:

1. **优化批处理**:
```python
# .env
EMBEDDING_BATCH_SIZE=16  # 减小批次
```

2. **添加限流**:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/qa/ask")
@limiter.limit("5/minute")
async def ask_question():
    pass
```

3. **使用缓存**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_embedding(text):
    return embedding_service.embed_text(text)
```

### ❌ 问题: 响应时间长

**症状**: API响应超过10秒

**优化**:

1. **启用数据库索引**:
```sql
CREATE INDEX idx_file_id ON files(file_id);
CREATE INDEX idx_status ON files(status);
```

2. **使用连接池**:
```python
from sqlalchemy.pool import QueuePool
engine = create_engine(DATABASE_URL, poolclass=QueuePool, pool_size=10)
```

3. **添加查询超时**:
```python
# .env
DATABASE_TIMEOUT=30
QUERY_TIMEOUT=10
```

---

## 数据库问题

### ❌ 问题: 数据库锁定

**症状**:
```
sqlite3.OperationalError: database is locked
```

**解决方案**:

1. **增加超时时间**:
```python
engine = create_engine(
    DATABASE_URL,
    connect_args={"timeout": 30}
)
```

2. **迁移到PostgreSQL**:
```bash
# 安装PostgreSQL
sudo apt-get install postgresql

# 修改配置
DATABASE_URL=postgresql://user:password@localhost/knowledge_base
```

### ❌ 问题: 数据丢失

**症状**: 文件列表为空

**恢复步骤**:

1. **检查备份**:
```bash
ls -la /backup/knowledge-base/
```

2. **恢复数据库**:
```bash
cp /backup/knowledge-base/db_latest.db data/database.db
```

3. **验证数据**:
```bash
sqlite3 data/database.db "SELECT COUNT(*) FROM files;"
```

---

## 模型加载问题

### ❌ 问题: 模型下载失败

**症状**:
```
HTTPError: 403 Client Error: Forbidden
```

**解决方案**:

1. **使用国内镜像**:
```python
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
```

2. **手动下载模型**:
```bash
# 使用git lfs
git lfs install
git clone https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# 移动到模型目录
mv paraphrase-multilingual-MiniLM-L12-v2 ./models/
```

3. **使用本地模型**:
```python
# .env
EMBEDDING_MODEL=./models/paraphrase-multilingual-MiniLM-L12-v2
```

### ❌ 问题: CUDA out of memory

**症状**:
```
RuntimeError: CUDA out of memory
```

**解决方案**:

1. **减小批次大小**:
```python
# .env
EMBEDDING_BATCH_SIZE=8
```

2. **使用CPU**:
```python
# .env
EMBEDDING_DEVICE=cpu
LLM_DEVICE=cpu
```

3. **使用模型量化**:
```python
load_in_8bit=True
```

---

## 网络问题

### ❌ 问题: 无法访问前端

**症状**: http://localhost:8501 无响应

**检查清单**:
1. ☐ Streamlit进程运行中
2. ☐ 端口8501未被占用
3. ☐ 防火墙未阻止
4. ☐ 浏览器无代理问题

**解决方案**:
```bash
# 检查进程
ps aux | grep streamlit

# 重启前端
pkill -f streamlit
streamlit run frontend/app.py
```

### ❌ 问题: CORS错误

**症状**:
```
Access to XMLHttpRequest blocked by CORS policy
```

**解决方案**:

修改 `backend/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 日志分析

### 查看实时日志

```bash
# 后端日志
tail -f logs/app.log

# 错误日志
tail -f logs/error.log

# 同时查看多个日志
tail -f logs/app.log logs/error.log
```

### 搜索错误

```bash
# 查找ERROR
grep "ERROR" logs/app.log

# 查找特定时间
grep "2026-01-26 10:" logs/app.log

# 统计错误数量
grep -c "ERROR" logs/app.log
```

### 常见错误模式

| 错误信息 | 可能原因 | 解决方案 |
|----------|----------|----------|
| `Connection refused` | 服务未启动 | 启动后端服务 |
| `File not found` | 路径错误 | 检查文件路径配置 |
| `Permission denied` | 权限不足 | 修改文件权限 |
| `Out of memory` | 内存不足 | 减少batch size |
| `Timeout` | 响应超时 | 增加超时时间 |

---

## 紧急恢复

### 完全重置

```bash
#!/bin/bash
# reset.sh - 完全重置系统

# 停止所有服务
pkill -f uvicorn
pkill -f streamlit

# 备份数据
cp -r data/ data_backup_$(date +%Y%m%d)/
cp -r indexes/ indexes_backup_$(date +%Y%m%d)/

# 清理
rm -rf indexes/*
rm -rf logs/*
rm data/database.db

# 重新创建目录
mkdir -p data/documents data/code indexes logs

# 重启服务
./start_all.sh

echo "系统已重置，请重新上传文件"
```

### 数据恢复

```bash
#!/bin/bash
# restore.sh - 从备份恢复

BACKUP_DATE=$1

# 恢复数据库
cp data_backup_$BACKUP_DATE/database.db data/

# 恢复索引
cp -r indexes_backup_$BACKUP_DATE/* indexes/

# 恢复文件
cp -r data_backup_$BACKUP_DATE/documents/* data/documents/

echo "数据已从 $BACKUP_DATE 恢复"
```

---

## 获取帮助

### 收集诊断信息

```bash
#!/bin/bash
# diagnostic.sh - 收集诊断信息

echo "=== 系统信息 ===" > diagnostic.txt
uname -a >> diagnostic.txt
python --version >> diagnostic.txt

echo "\n=== 进程信息 ===" >> diagnostic.txt
ps aux | grep -E "(python|streamlit|uvicorn)" >> diagnostic.txt

echo "\n=== 端口信息 ===" >> diagnostic.txt
netstat -tuln | grep -E "(8000|8501)" >> diagnostic.txt

echo "\n=== 磁盘空间 ===" >> diagnostic.txt
df -h >> diagnostic.txt

echo "\n=== 最近错误 ===" >> diagnostic.txt
tail -50 logs/error.log >> diagnostic.txt

echo "\n诊断信息已保存到 diagnostic.txt"
```

### 联系支持

提交Issue时请包含:
1. 错误描述
2. 重现步骤
3. 系统信息
4. 相关日志
5. diagnostic.txt

---

**最后更新**: 2026年1月26日  
**文档版本**: 1.0.0
