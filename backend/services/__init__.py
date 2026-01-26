"""
Services包初始化

本模块提供业务服务层的导出，包括：
- EmbeddingService: 嵌入模型封装与向量计算
- VectorStore: 向量数据库（Chroma）封装
- IndexingService: 索引流程自动化（解析→分块→嵌入→存储）
- FileService: 文件管理（上传、删除、统计）
"""

__all__ = [
    "EmbeddingService",
    "VectorStore",
    "IndexingService",
    "FileService",
]
