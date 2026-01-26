# 模块设计文档

版本: 1.0.0  
最后更新: 2026-01-26

---

## 概述

模块划分遵循分层与职责单一原则：路由只处理 HTTP、服务负责业务流程、处理器专注文本解析与分块、存储模块抽象底层持久化。此文档给出主要模块的职责、关键方法与交互关系。

---

## 路由层（`backend/routers/`）

### `file_routes.py`
- 职责：文件的上传、列表、详情、删除、批量删除、统计、索引状态更新
- 关键端点：
  - POST `/api/files/upload`（单/批）
  - GET `/api/files/list`
  - GET `/api/files/detail/{file_id}`
  - DELETE `/api/files/delete/{file_id}` / POST `/api/files/batch_delete`
  - PUT `/api/files/index_status/{file_id}`
  - GET `/api/files/stats`
- 交互：调用 `FileService` 保存与删除文件；`BackgroundTasks` 触发 `IndexingService`

### `index_routes.py`
- 职责：索引状态查询、重建索引、删除索引、相似检索、文件索引详情
- 关键端点：
  - GET `/api/index/status`
  - POST `/api/index/reindex/{file_id}`
  - DELETE `/api/index/delete/{file_id}`
  - POST `/api/index/rebuild_all`
  - POST `/api/index/search`
  - GET `/api/index/file_info/{file_id}`
- 交互：调用 `IndexingService` 与 `VectorStore` 完成操作

### `qa_routes.py`
- 职责：问答接口（RAG）
- 关键端点：
  - POST `/api/qa/ask`
- 交互：`VectorStore` 相似检索 → `EmbeddingService` 查询向量 → 模板或 LLM 生成答案

---

## 服务层（`backend/services/`）

### `FileService`
- 职责：
  - 校验与保存上传文件（支持 txt/md/markdown/pdf/docx/html/code）
  - 去重（MD5）、入库 `file_metadata`
  - 软/物理删除文件与清理索引
  - 列表、统计、详情查询
- 关键方法：
  - `save_uploaded_file(upload_file, file_type)`
  - `delete_file(file_id, physical=False)` / `batch_delete(file_ids)`
  - `list_files(filters)` / `get_file_detail(file_id)`
  - `update_index_status(file_id, status)` / `get_stats()`

### `IndexingService`
- 职责：
  - 单文件/批量索引：解析→分块→嵌入→写入向量库
  - 重试与状态管理：`pending/indexing/indexed/failed`
  - 重建与删除索引；统计与文件索引信息
- 关键方法：
  - `index_file(file_id)` / `batch_index_pending(limit)`
  - `reindex_file(file_id)` / `delete_index(file_id)` / `rebuild_all()`
  - `get_index_status()` / `get_file_index_info(file_id)`

### `EmbeddingService`
- 职责：加载 Sentence-Transformers 模型，提供单/批量嵌入与相似度计算
- 关键方法：
  - `embed_text(text)` / `embed_texts(texts)`
  - `cosine_similarity(vec_a, vec_b)` / `batch_similarity(query_vec, vectors)`

### `VectorStore`
- 职责：封装 Chroma 持久化客户端，提供添加、查询、删除、清空与计数
- 关键方法：
  - `add_documents(texts, embeddings, metadatas)`
  - `query(query_embeddings, top_k, where)`
  - `delete(where)` / `clear()` / `count()`

---

## 处理器层（`backend/processors/`）

### `TextProcessor`
- 职责：统一解析（txt/md/pdf/docx/html/code），进行段落优先的分块与清理
- 关键方法：
  - `read_text(path)` / `read_markdown(path)` / `read_pdf(path)` / `read_docx(path)` / `read_html(path)` / `read_code(path)`
  - `chunk_text(text, chunk_size, chunk_overlap)`
- 特性：
  - 代码结构标注（语言识别、模块/函数/类标识）
  - 分块时优先按段落/标题，长段落回退为固定窗口分块

---

## 基础设施层

### 数据库（`backend/database.py`）
- 职责：MySQL Engine 与会话工厂、自动建库建表、FastAPI 依赖注入

### 配置（`backend/config.py`）
- 职责：Pydantic Settings，集中管理数据库、嵌入模型、Chroma 路径、分块参数等

### 日志（`backend/logger_config.py`）
- 职责：Loguru 配置，区分访问日志与错误日志，支持轮转与保留

---

## 交互关系

- `file_routes` ←→ `FileService`（CRUD）
- `index_routes` ←→ `IndexingService` / `VectorStore`（索引与检索）
- `qa_routes` ←→ `EmbeddingService` / `VectorStore`（问答）
- `IndexingService` ←→ `TextProcessor` / `EmbeddingService` / `VectorStore` / `database`

---

## 扩展建议

- 抽象 `IVectorStore` 接口，支持切换 FAISS/Weaviate/PGVector
- 增加任务队列（如 RQ/Celery）进行异步索引，提高吞吐
- 引入鉴权与配额控制（API Key/JWT + Rate Limit）
- 为 `qa_routes` 增加 Streaming（Server-Sent Events 或 WebSocket）
