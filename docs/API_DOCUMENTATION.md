# API 文档

**版本**: v1.0.0  
**基础URL**: `http://localhost:8000`  
**API文档**: `http://localhost:8000/docs` (Swagger UI)  
**备选文档**: `http://localhost:8000/redoc` (ReDoc)

---

## 📋 目录

- [概述](#概述)
- [认证](#认证)
- [通用响应格式](#通用响应格式)
- [文件管理](#文件管理)
- [索引管理](#索引管理)
- [问答接口](#问答接口)
- [系统接口](#系统接口)
- [错误代码](#错误代码)

---

## 概述

本地知识库系统提供RESTful API，支持文件上传、索引管理、智能问答等功能。所有接口返回JSON格式数据。

### 基础信息

- **协议**: HTTP/HTTPS
- **端口**: 8000 (默认)
- **Content-Type**: application/json
- **字符编码**: UTF-8

---

## 认证

当前版本为本地部署，暂不需要认证。后续版本将支持：
- API Key认证
- JWT Token认证

---

## 通用响应格式

### 成功响应

```json
{
  "success": true,
  "data": {},
  "message": "操作成功"
}
```

### 错误响应

```json
{
  "success": false,
  "error": "错误信息",
  "code": "ERROR_CODE"
}
```

---

## 文件管理

### 1. 上传文件

上传单个或多个文件到知识库。

**接口**: `POST /api/files/upload`

**请求**:
- Content-Type: `multipart/form-data`
- 参数:
  - `files`: 文件列表 (required)
  - `category`: 文件分类 (optional, default: "document")

**示例**:
```bash
curl -X POST "http://localhost:8000/api/files/upload" \
  -F "files=@document.pdf" \
  -F "files=@code.py" \
  -F "category=document"
```

**响应**:
```json
{
  "success": true,
  "data": {
    "uploaded": 2,
    "failed": 0,
    "files": [
      {
        "id": "uuid-1",
        "filename": "document.pdf",
        "size": 1024000,
        "category": "document",
        "upload_time": "2026-01-26T10:30:00"
      }
    ]
  },
  "message": "上传成功"
}
```

### 2. 获取文件列表

获取所有已上传的文件列表。

**接口**: `GET /api/files/list`

**参数**:
- `category`: 过滤分类 (optional)
- `status`: 过滤状态 (optional: indexed, pending, failed)
- `page`: 页码 (optional, default: 1)
- `page_size`: 每页数量 (optional, default: 20)

**示例**:
```bash
curl "http://localhost:8000/api/files/list?category=document&page=1"
```

**响应**:
```json
{
  "success": true,
  "data": {
    "total": 10,
    "page": 1,
    "page_size": 20,
    "files": [
      {
        "id": "uuid-1",
        "filename": "document.pdf",
        "size": 1024000,
        "category": "document",
        "status": "indexed",
        "upload_time": "2026-01-26T10:30:00",
        "indexed_time": "2026-01-26T10:30:15"
      }
    ]
  }
}
```

### 3. 获取文件详情

获取指定文件的详细信息。

**接口**: `GET /api/files/{file_id}`

**参数**:
- `file_id`: 文件ID (required)

**响应**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-1",
    "filename": "document.pdf",
    "size": 1024000,
    "category": "document",
    "status": "indexed",
    "upload_time": "2026-01-26T10:30:00",
    "indexed_time": "2026-01-26T10:30:15",
    "chunks": 45,
    "md5": "abc123..."
  }
}
```

### 4. 删除文件

删除指定文件及其索引。

**接口**: `DELETE /api/files/{file_id}`

**参数**:
- `file_id`: 文件ID (required)

**示例**:
```bash
curl -X DELETE "http://localhost:8000/api/files/uuid-1"
```

**响应**:
```json
{
  "success": true,
  "message": "文件删除成功"
}
```

### 5. 批量删除文件

删除多个文件。

**接口**: `POST /api/files/batch-delete`

**请求体**:
```json
{
  "file_ids": ["uuid-1", "uuid-2", "uuid-3"]
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "deleted": 3,
    "failed": 0
  },
  "message": "批量删除成功"
}
```

---

## 索引管理

### 1. 创建索引

为指定文件创建向量索引。

**接口**: `POST /api/index/create`

**请求体**:
```json
{
  "file_id": "uuid-1",
  "chunk_size": 500,
  "overlap": 50
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "file_id": "uuid-1",
    "chunks": 45,
    "status": "completed",
    "time_taken": 3.5
  },
  "message": "索引创建成功"
}
```

### 2. 获取索引统计

获取索引系统的统计信息。

**接口**: `GET /api/index/statistics`

**响应**:
```json
{
  "success": true,
  "data": {
    "total_files": 10,
    "indexed_files": 8,
    "pending_files": 2,
    "total_chunks": 450,
    "index_size": "125MB",
    "last_update": "2026-01-26T10:30:00"
  }
}
```

### 3. 重建索引

重新构建指定文件的索引。

**接口**: `POST /api/index/rebuild`

**请求体**:
```json
{
  "file_id": "uuid-1"
}
```

### 4. 清空索引

清空所有索引数据。

**接口**: `DELETE /api/index/clear`

**响应**:
```json
{
  "success": true,
  "message": "索引已清空"
}
```

---

## 问答接口

### 1. 提问查询

基于知识库内容回答问题。

**接口**: `POST /api/qa/ask`

**请求体**:
```json
{
  "question": "什么是人工智能？",
  "top_k": 3,
  "similarity_threshold": 0.5,
  "use_llm": true
}
```

**参数说明**:
- `question`: 用户问题 (required)
- `top_k`: 返回最相关的文档数量 (optional, default: 3)
- `similarity_threshold`: 相似度阈值 (optional, default: 0.5)
- `use_llm`: 是否使用LLM生成答案 (optional, default: true)

**响应**:
```json
{
  "success": true,
  "data": {
    "question": "什么是人工智能？",
    "answer": "人工智能是计算机科学的一个分支...",
    "sources": [
      {
        "file_id": "uuid-1",
        "filename": "AI_intro.pdf",
        "content": "相关文本片段...",
        "similarity": 0.85,
        "page": 5
      }
    ],
    "response_time": 2.3
  }
}
```

### 2. 相似文档检索

检索与查询最相关的文档片段。

**接口**: `POST /api/qa/search`

**请求体**:
```json
{
  "query": "机器学习算法",
  "top_k": 5,
  "filters": {
    "category": "document",
    "file_ids": ["uuid-1", "uuid-2"]
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "file_id": "uuid-1",
        "filename": "ML_book.pdf",
        "content": "机器学习算法包括...",
        "similarity": 0.92,
        "metadata": {}
      }
    ]
  }
}
```

---

## 系统接口

### 1. 健康检查

检查系统运行状态。

**接口**: `GET /health`

**响应**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-26T10:30:00"
}
```

### 2. 系统信息

获取系统配置和统计信息。

**接口**: `GET /api/system/info`

**响应**:
```json
{
  "success": true,
  "data": {
    "version": "1.0.0",
    "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
    "vector_db": "Chroma",
    "total_files": 10,
    "total_chunks": 450,
    "uptime": "2h 30m"
  }
}
```

### 3. 系统配置

获取或更新系统配置。

**接口**: `GET /api/system/config`

**响应**:
```json
{
  "success": true,
  "data": {
    "chunk_size": 500,
    "chunk_overlap": 50,
    "retrieval_k": 3,
    "similarity_threshold": 0.5,
    "use_llm": true
  }
}
```

---

## 错误代码

| 代码 | 说明 |
|------|------|
| `FILE_NOT_FOUND` | 文件不存在 |
| `FILE_TOO_LARGE` | 文件超过大小限制 |
| `INVALID_FILE_TYPE` | 不支持的文件类型 |
| `UPLOAD_FAILED` | 上传失败 |
| `INDEX_ERROR` | 索引创建失败 |
| `DATABASE_ERROR` | 数据库错误 |
| `VALIDATION_ERROR` | 参数验证失败 |
| `INTERNAL_ERROR` | 内部服务器错误 |
| `MODEL_NOT_LOADED` | 模型未加载 |
| `QUERY_FAILED` | 查询失败 |

---

## 速率限制

当前版本无速率限制。生产环境建议：
- 文件上传: 10次/分钟
- 问答查询: 30次/分钟
- 其他接口: 100次/分钟

---

## WebSocket 接口

### 实时索引进度

**接口**: `ws://localhost:8000/ws/index-progress`

**消息格式**:
```json
{
  "file_id": "uuid-1",
  "progress": 45,
  "status": "processing",
  "message": "正在处理第45个分块..."
}
```

---

## 示例代码

### Python

```python
import requests

# 上传文件
files = {'files': open('document.pdf', 'rb')}
response = requests.post('http://localhost:8000/api/files/upload', files=files)
print(response.json())

# 提问查询
query = {
    "question": "什么是人工智能？",
    "top_k": 3
}
response = requests.post('http://localhost:8000/api/qa/ask', json=query)
print(response.json())
```

### JavaScript

```javascript
// 上传文件
const formData = new FormData();
formData.append('files', fileInput.files[0]);

fetch('http://localhost:8000/api/files/upload', {
  method: 'POST',
  body: formData
})
.then(res => res.json())
.then(data => console.log(data));

// 提问查询
fetch('http://localhost:8000/api/qa/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: '什么是人工智能？',
    top_k: 3
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

**最后更新**: 2026年1月26日  
**文档版本**: 1.0.0
