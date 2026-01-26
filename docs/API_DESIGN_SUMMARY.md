# API 设计概要

版本: 1.0.0  
最后更新: 2026-01-26

---

## 范围与目标

本概要面向开发者，概述后端 REST API 的设计原则、端点分组、通用响应、错误处理、分页与扩展方案。详细接口说明与示例请参考 `docs/API_DOCUMENTATION.md`。

---

## 端点分组

- 文件接口（`/api/files/*`）
  - 上传（单/批）：`POST /api/files/upload`
  - 列表与详情：`GET /api/files/list`、`GET /api/files/detail/{file_id}`
  - 删除（单/批）：`DELETE /api/files/delete/{file_id}`、`POST /api/files/batch_delete`
  - 索引状态更新：`PUT /api/files/index_status/{file_id}`
  - 统计：`GET /api/files/stats`

- 索引接口（`/api/index/*`）
  - 总体状态：`GET /api/index/status`
  - 重建/删除索引：`POST /api/index/reindex/{file_id}`、`DELETE /api/index/delete/{file_id}`、`POST /api/index/rebuild_all`
  - 相似检索：`POST /api/index/search`
  - 文件索引信息：`GET /api/index/file_info/{file_id}`

- 问答接口（`/api/qa/*`）
  - 提问：`POST /api/qa/ask`

- 系统接口
  - 健康检查：`GET /health`
  - 系统信息：`GET /info`

---

## 请求与响应约定

- 编码与格式：`Content-Type: application/json; charset=utf-8`
- 成功响应：
  - `{"success": true, "data": ...}` 或直接返回数据对象（依路由定义）
- 失败响应（统一错误处理）：
  - `{"success": false, "error": {"code": "BadRequest", "message": "...", "details": {...}}}`
- 分页约定（如列表接口）：
  - 请求：`page`, `page_size`
  - 响应：`{"items": [...], "page": 1, "page_size": 20, "total": 123}`

---

## 错误代码与HTTP状态

- 400 BadRequest：参数或文件格式错误
- 404 NotFound：资源不存在（文件ID、索引信息等）
- 409 Conflict：重复上传（MD5已存在）
- 500 ServerError：内部错误（数据库/向量库等）

错误对象：
```json
{
  "success": false,
  "error": {
    "code": "NotFound",
    "message": "File not found",
    "details": {"file_id": 123}
  }
}
```

---

## 模型与枚举（简要）

- `FileMetadata`：`id`, `filename`, `path`, `file_type`, `extension`, `size`, `md5`, `upload_time`, `index_time`, `index_status`, `chunk_count`, `is_deleted`
- 枚举：
  - `FileType`：`text|markdown|pdf|docx|html|code`
  - `IndexStatus`：`pending|indexing|indexed|failed`

---

## 版本与扩展

- 版本前缀（建议）：未来支持 `/v1` 前缀以避免破坏性更新
- 鉴权（规划）：API Key 或 JWT（生产环境建议开启）
- 速率限制（规划）：基于反向代理或中间件的 Rate Limit
- 流式输出（规划）：问答支持 SSE/WebSocket Streaming

---

## 性能与幂等性

- 上传接口：MD5 去重保证幂等；冲突返回 409
- 索引接口：
  - 重建与删除需序列化操作（对同一 `file_id`）
  - 批量索引采用限制并发与分批提交
- 检索与问答接口：无副作用（只读）

---

## 参考

- 详细接口与示例：`docs/API_DOCUMENTATION.md`
- 架构与模块设计：`docs/ARCHITECTURE.md`、`docs/MODULE_DESIGN.md`
