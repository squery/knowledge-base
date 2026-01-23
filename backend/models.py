"""
数据库模型定义
使用SQLAlchemy定义文件元数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class FileType(str, enum.Enum):
    """文件类型枚举"""
    DOCUMENT = "document"
    CODE = "code"


class IndexStatus(str, enum.Enum):
    """索引状态枚举"""
    PENDING = "pending"  # 待索引
    INDEXING = "indexing"  # 索引中
    INDEXED = "indexed"  # 已索引
    FAILED = "failed"  # 索引失败


class FileMetadata(Base):
    """文件元数据模型"""
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(191), nullable=False, index=True)  # 文件名 (utf8mb4索引安全长度)
    original_filename = Column(String(255), nullable=False)  # 原始文件名
    file_path = Column(String(191), nullable=False, unique=True)  # 文件存储路径 (utf8mb4索引安全长度)
    file_type = Column(Enum(FileType), nullable=False, index=True)  # 文件类型
    file_extension = Column(String(16), nullable=False)  # 文件扩展名
    file_size = Column(BigInteger, nullable=False)  # 文件大小(字节)
    md5_hash = Column(String(32), nullable=False, unique=True, index=True)  # MD5哈希
    upload_time = Column(DateTime, default=datetime.now, nullable=False)  # 上传时间
    index_status = Column(Enum(IndexStatus), default=IndexStatus.PENDING, nullable=False)  # 索引状态
    index_time = Column(DateTime, nullable=True)  # 索引完成时间
    error_message = Column(String(512), nullable=True)  # 错误信息
    chunk_count = Column(Integer, default=0)  # 分块数量
    is_deleted = Column(Boolean, default=False)  # 软删除标记

    def __repr__(self):
        return f"<FileMetadata(id={self.id}, filename={self.filename}, status={self.index_status})>"

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_path": self.file_path,
            "file_type": self.file_type.value if self.file_type else None,
            "file_extension": self.file_extension,
            "file_size": self.file_size,
            "md5_hash": self.md5_hash,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None,
            "index_status": self.index_status.value if self.index_status else None,
            "index_time": self.index_time.isoformat() if self.index_time else None,
            "error_message": self.error_message,
            "chunk_count": self.chunk_count,
            "is_deleted": self.is_deleted
        }
