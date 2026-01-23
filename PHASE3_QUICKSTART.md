# Phase 3 快速开始指南

## 功能说明

Phase 3 实现了本地知识库的**索引系统**，包括：

1. **文本处理** - 支持多种文件格式的智能分块
2. **向量化** - 使用 Transformer 模型的文本向量化  
3. **向量存储** - Chroma 向量数据库
4. **自动索引** - 文件上传后自动建立索引
5. **语义搜索** - 基于向量相似度的智能搜索

## 环境准备

### 前置要求
- Python 3.8+
- MySQL 数据库
- 20GB+ 磁盘空间（用于模型和索引）

### 安装依赖

```bash
# 进入项目目录
cd d:\Git\ Workspace\knowledge-base

# 创建虚拟环境（如果未创建）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 启动应用

### 方式 1: 使用启动脚本（推荐）

```bash
# Windows
start_all.bat

# Linux/Mac
./start_all.sh
```

### 方式 2: 分别启动

**终端 1 - 启动后端 API**
```bash
python backend/main.py
```
服务器将运行在 `http://localhost:8000`

**终端 2 - 启动前端**
```bash
streamlit run frontend/app.py
```
前端将运行在 `http://localhost:8501`

## 使用流程

### 1. 文件管理 (📚 文件管理)
- 上传文档 (txt, md, pdf, docx, html 等)
- 查看已上传的文件列表
- 删除不需要的文件

### 2. 索引管理 (📊 索引管理)
- **查看统计**: 总文件数、已索引、待索引等统计
- **进度显示**: 索引完成率和向量库状态
- **批量操作**:
  - 批量索引: 对所有待索引文件创建索引
  - 刷新状态: 实时更新统计信息
  - 清空索引: 清除所有索引（谨慎操作）
- **单个文件**:
  - 重新索引: 更新文件索引
  - 删除索引: 移除文件索引
- **语义搜索**: 输入查询文本，查看最相关的文档片段

### 3. 智能问答 (🔍 智能问答)
- 暂未实现（Phase 4）

## API 文档

### 索引管理 API 端点

#### 获取索引统计
```
GET /api/index/status
```
响应:
```json
{
  "total_files": 5,
  "indexed_files": 4,
  "pending_files": 1,
  "indexing_files": 0,
  "failed_files": 0,
  "total_chunks": 128,
  "vector_count": 128,
  "index_ratio": "80%"
}
```

#### 重新索引文件
```
POST /api/index/files/{file_id}
```

#### 删除文件索引
```
DELETE /api/index/files/{file_id}
```

#### 重建所有索引
```
POST /api/index/rebuild
```

#### 语义相似度搜索
```
POST /api/index/search?query=<搜索文本>&top_k=3
```
响应:
```json
{
  "query": "机器学习",
  "results": [
    {
      "content": "机器学习是人工智能的重要分支...",
      "similarity": 0.92,
      "file_id": 1,
      "file_path": "./data/documents/xxx.txt",
      "chunk_index": 5
    }
  ],
  "total_results": 1
}
```

## 测试

运行快速测试验证功能：

```bash
python test_phase3_quick.py
```

预期输出：
```
总体: 5/5 通过
✅ 文本处理器
✅ 向量存储初始化
✅ API 路由结构
✅ 索引服务
✅ 向量化服务
```

## 配置文件

编辑 `backend/config.py` 调整：

```python
# 文本分块配置
CHUNK_SIZE = 800           # 分块大小（字符）
CHUNK_OVERLAP = 200        # 分块重叠（字符）

# 向量化配置
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DEVICE = "cpu"   # 改为 "cuda" 如果有 GPU

# 检索配置
RETRIEVAL_K = 3            # 返回最相关的 K 条文档
SIMILARITY_THRESHOLD = 0.5 # 相似度阈值

# 数据库配置
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "knowledge_base"
```

## 常见问题

### Q: 首次运行很慢？
A: 需要下载 ~500MB 的预训练模型，首次会自动下载到 ~/.cache/huggingface/

### Q: 如何使用 GPU 加速？
A: 将 `EMBEDDING_DEVICE = "cuda"` 和 `LLM_DEVICE = "cuda"`，需要安装 CUDA 版本的 torch

### Q: 索引出错如何处理？
A: 查看 `logs/` 目录中的错误日志，可重新索引该文件

### Q: 如何清空所有数据？
A: 
```bash
# 清空向量库
rm -rf indexes/

# 重置数据库
# 在 MySQL 中执行: DROP DATABASE knowledge_base;
```

## 性能指标

- 文本处理: ~1000 字符/秒
- 向量化: ~100 文本/秒 (batch_size=32)
- 向量查询: <100ms (单次查询)
- 存储效率: 每个块 ~384×4 字节 = 1.5KB 的向量

## 后续计划

- Phase 4: AI 问答模块（LLM 集成）
- Phase 5: 完整启动脚本
- Phase 6: 性能优化和测试
- Phase 7: 生产部署方案

## 获取帮助

- 查看日志: `logs/error.log`, `logs/app.log`
- 阅读代码注释
- 查看 API 文档: http://localhost:8000/docs
- 查看完成报告: `PHASE3_COMPLETION.md`

---

祝您使用愉快！🎉
