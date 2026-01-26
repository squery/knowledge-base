# 数据库设计文档

版本: 1.0.0  
最后更新: 2026-01-26

---

## 概述

系统使用 MySQL 存储文件基础元数据与索引状态，向量数据由 Chroma 持久化管理。数据库初始化与会话管理由 `backend/database.py` 完成，ORM 模型定义位于 `backend/models.py`。

---

## 逻辑模型

### 表：`file_metadata`

- 主键：`id` BIGINT AUTO_INCREMENT
- 字段：
  - `filename` VARCHAR(255): 原始文件名
  - `path` VARCHAR(512): 文件持久化路径（相对 `data/`）
  - `file_type` ENUM: `text` | `markdown` | `pdf` | `docx` | `html` | `code`
  - `extension` VARCHAR(32): 扩展名（统一小写）
  - `size` BIGINT: 字节大小
  - `md5` CHAR(32): 内容哈希（用于去重）
  - `upload_time` DATETIME: 上传时间
  - `index_time` DATETIME NULL: 完成索引时间
  - `index_status` ENUM: `pending` | `indexing` | `indexed` | `failed`
  - `chunk_count` INT: 分块数量（索引完成后更新）
  - `is_deleted` TINYINT(1): 软删除标记

- 索引：
  - `idx_md5_unique` UNIQUE(`md5`)
  - `idx_path` INDEX(`path`)
  - `idx_status` INDEX(`index_status`)

- 约束与业务规则：
  - `md5` 唯一，用于防止重复上传（同内容文件）
  - 删除逻辑：软删除将 `is_deleted=1` 且保留记录；物理删除需同步清理 Chroma 向量并重置索引状态

---

## 物理模型与建表语句（参考）

注意：实际表结构由 SQLAlchemy ORM 自动生成，以下为近似 SQL。

```sql
CREATE TABLE file_metadata (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  filename VARCHAR(255) NOT NULL,
  path VARCHAR(512) NOT NULL,
  file_type VARCHAR(32) NOT NULL,
  extension VARCHAR(32) NOT NULL,
  size BIGINT NOT NULL,
  md5 CHAR(32) NOT NULL,
  upload_time DATETIME NOT NULL,
  index_time DATETIME NULL,
  index_status VARCHAR(32) NOT NULL,
  chunk_count INT NOT NULL DEFAULT 0,
  is_deleted TINYINT(1) NOT NULL DEFAULT 0,
  UNIQUE KEY idx_md5_unique (md5),
  KEY idx_path (path),
  KEY idx_status (index_status)
);
```

---

## ER 图（简化）

```
+--------------------+
|   file_metadata    |
+--------------------+
| id (PK)            |
| filename           |
| path               |
| file_type          |
| extension          |
| size               |
| md5 (UNIQUE)       |
| upload_time        |
| index_time         |
| index_status       |
| chunk_count        |
| is_deleted         |
+--------------------+
```

向量数据存储在 Chroma（`indexes/`），以集合/文档等级管理，文档的 `metadata` 包含 `file_id`、`chunk_index`、`file_type`、`extension` 等。两者通过 `file_id` 进行逻辑关联。

---

## 事务与会话

- 会话管理：`database.get_session()` 上下文管理器与 FastAPI 依赖 `get_db()`
- 事务策略：
  - 写操作（上传、删除、索引更新）使用会话提交；异常时回滚并记录日志
  - 批量操作（批量索引、批量删除）采用分批提交避免长事务

---

## 数据一致性

- 索引完成后更新 `index_status` 与 `chunk_count`，保证与 Chroma 的一致性
- 删除时先清理 Chroma，再更新数据库标记或删除记录
- 失败重试：索引失败状态可重试，重试成功后更新状态

---

## 性能与扩展

- 索引：`idx_status` 便于快速筛选待处理或失败文件
- 去重：通过 `md5` 唯一索引避免冗余存储与重复索引
- 水平扩展：可将 MySQL 替换为云托管实例；Chroma 迁移至外部持久化卷或集群

---

## 备份与恢复

- 数据库定期备份（逻辑/物理）
- Chroma 向量库目录备份（`indexes/`）与一致性校验
- 提供重建索引能力（`/api/index/rebuild_all`）在数据恢复后重建向量
