# 架构设计文档

版本: 1.0.0  
最后更新: 2026-01-26

---

## 概述

本地知识库系统采用前后端分离架构：后端使用 FastAPI 提供文件管理、索引与问答 API；前端使用 Streamlit 提供交互界面。系统通过文本分块与嵌入向量化，将文档内容持久化到 Chroma 向量数据库中，实现高效语义检索与轻量 RAG 问答。

---

## 系统组件

- 后端 (`backend/`)
  - `main.py`: FastAPI 应用入口、路由注册、CORS、异常处理、健康检查
  - `routers/`: API 路由层
    - `file_routes.py`: 文件上传、列表、删除、统计
    - `index_routes.py`: 索引状态、重建/删除索引、相似检索
    - `qa_routes.py`: RAG 问答接口
  - `services/`: 业务服务层
    - `file_service.py`: 文件保存、校验、删除、统计
    - `indexing_service.py`: 文本解析→分块→嵌入→持久化的全流程
    - `embedding_service.py`: Sentence-Transformers 模型封装
    - `vector_store.py`: Chroma 向量库封装
  - `processors/text_processor.py`: 文档/代码解析与分块策略
  - `database.py`: MySQL 连接、会话与初始化（自动建库建表）
  - `models.py`: SQLAlchemy ORM 模型（`FileMetadata`）
  - `config.py`: 配置管理（Pydantic Settings）
  - `logger_config.py`: Loguru 日志配置
- 前端 (`frontend/`)
  - `app.py`: Streamlit UI，文件上传、问答、状态展示
- 数据与索引
  - `data/`: 文档与代码持久化目录
  - `indexes/`: Chroma 向量数据库持久化目录
  - `logs/`: 应用与错误日志

---

## 运行时拓扑

```
+--------------------+        REST API        +--------------------+
|   Streamlit App    |  <------------------>  |      FastAPI       |
|  (frontend/app.py) |                        |    (backend/app)   |
+--------------------+                        +----------+---------+
                                                         |
                                                         | ORM
                                                         v
                                               +--------------------+
                                               |     MySQL DB       |
                                               |  file_metadata     |
                                               +--------------------+
                                                         |
                                                         | Embeddings + Docs
                                                         v
                                               +--------------------+
                                               |   Chroma Vector    |
                                               |   (indexes/)       |
                                               +--------------------+
```

---

## 数据流与索引流程

1. 文件上传（`/api/files/upload`）
   - 校验类型与大小 → 保存到 `data/documents` 或 `data/code`
   - 生成 MD5 去重 → 入库 `file_metadata`
   - 后台任务触发索引
2. 索引流程（`IndexingService.index_file`）
   - 解析文本（含代码结构标注） → 段落优先分块（`chunk_size`/`chunk_overlap`）
   - Sentence-Transformers 批量嵌入（归一化）
   - 元数据（`file_id`、`chunk_index`、`file_type`）+ 文本 + 向量 → 写入 Chroma
   - 更新 `file_metadata.index_status = indexed` 与分块计数
3. 相似检索与问答
   - 查询向量化 → Chroma 召回 Top-K 文档片段
   - 返回相似度与来源 → 模板或 LLM 生成答案（可选）

### 时序图（索引）

```
User -> FastAPI(file_routes): POST /api/files/upload
FastAPI -> FileService: save_uploaded_file()
FileService -> MySQL: INSERT file_metadata
FastAPI -> BackgroundTasks: index_file(file_id)
BackgroundTasks -> IndexingService: index_file()
IndexingService -> TextProcessor: process_file()
TextProcessor --> IndexingService: chunks
IndexingService -> EmbeddingService: embed_texts(chunks)
EmbeddingService --> IndexingService: embeddings
IndexingService -> VectorStore: add_documents(docs, embeddings, metadatas)
VectorStore -> Chroma: persist
IndexingService -> MySQL: UPDATE file_metadata(indexed)
```

---

## 关键设计决策

- 文本分块优先保持语义段落，长段落退化为固定窗口分块，支持重叠以保留上下文
- 嵌入向量默认归一化，相似度基于余弦（Chroma 返回距离，转换为 `1 - d`）
- 元数据精简（仅关键字段），降低 Chroma 存储压力
- Indexing 采用指数退避重试（最多 3 次）
- 文件删除支持软删除与物理删除（向量清理与索引状态重置）

---

## 配置与扩展性

- 数据库：默认 MySQL，`database.py` 自动创建数据库与表；可替换为 PostgreSQL（修改 `database.py` 与 `config.py`）
- 向量库：Chroma，可替换为 FAISS（实现 `VectorStore` 接口）
- 模型：通过 `.env` 或 `config.py` 切换嵌入模型与 LLM
- 并发：Uvicorn Workers + 连接池；批量索引支持

---

## 可靠性与容错

- 全局异常处理（HTTP 与通用），统一 JSON 错误响应
- 文件与索引操作完整日志记录（双日志，轮转与保留）
- 数据库事务与回滚、会话上下文管理器

---

## 安全性

- CORS 全开放（本地开发），生产建议收敛 `allow_origins`
- 上传大小与类型校验；路径安全
- 未来支持鉴权（API Key/JWT）

---

## 部署建议

- 生产环境建议：Nginx 反向代理 + Supervisor 进程守护 + Gunicorn 多进程
- 数据与索引目录使用持久化卷；定期备份与日志轮转

---

## 监控与指标

- 索引统计：`/api/index/status`（文件总数、索引比例、向量数）
- 性能指标见 README 与 Phase 6 测试报告
