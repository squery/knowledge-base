"""
文件服务模块
处理文件的存储、检索、删除等业务逻辑
"""
import os
import hashlib
import shutil
from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

try:
    from backend.models import FileMetadata, FileType, IndexStatus
except Exception:
    from models import FileMetadata, FileType, IndexStatus
try:
    from backend.config import settings
except Exception:
    from config import settings
try:
    from backend.logger_config import get_logger
except Exception:
    from logger_config import get_logger

logger = get_logger(__name__)


class FileService:
    """文件服务类"""

    @staticmethod
    def calculate_md5(file_path: str, chunk_size: int = 8192) -> str:
        """
        计算文件的MD5哈希值
        
        Args:
            file_path: 文件路径
            chunk_size: 分块读取大小
            
        Returns:
            MD5哈希字符串
        """
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    @staticmethod
    def get_file_type(extension: str) -> FileType:
        """
        根据文件扩展名判断文件类型
        
        Args:
            extension: 文件扩展名(包含.)
            
        Returns:
            FileType枚举
        """
        if extension.lower() in settings.ALLOWED_DOCUMENT_TYPES:
            return FileType.DOCUMENT
        elif extension.lower() in settings.ALLOWED_CODE_TYPES:
            return FileType.CODE
        else:
            raise ValueError(f"不支持的文件类型: {extension}")

    @staticmethod
    def is_allowed_file(filename: str) -> Tuple[bool, str]:
        """
        检查文件是否允许上传
        
        Args:
            filename: 文件名
            
        Returns:
            (是否允许, 错误信息)
        """
        if not filename:
            return False, "文件名不能为空"
        
        # 获取文件扩展名
        _, ext = os.path.splitext(filename)
        if not ext:
            return False, "文件必须有扩展名"
        
        # 检查是否在允许的类型中
        allowed_types = settings.ALLOWED_DOCUMENT_TYPES + settings.ALLOWED_CODE_TYPES
        if ext.lower() not in allowed_types:
            return False, f"不支持的文件类型: {ext}。支持的类型: {', '.join(allowed_types)}"
        
        return True, ""

    @staticmethod
    def check_file_exists_by_md5(db: Session, md5_hash: str) -> Optional[FileMetadata]:
        """
        通过MD5检查文件是否已存在
        
        Args:
            db: 数据库会话
            md5_hash: MD5哈希值
            
        Returns:
            已存在的文件元数据或None
        """
        return db.query(FileMetadata).filter(
            FileMetadata.md5_hash == md5_hash,
            FileMetadata.is_deleted == False
        ).first()

    @staticmethod
    def save_uploaded_file(
        db: Session,
        filename: str,
        file_content: bytes,
        file_size: int
    ) -> FileMetadata:
        """
        保存上传的文件
        
        Args:
            db: 数据库会话
            filename: 原始文件名
            file_content: 文件内容
            file_size: 文件大小
            
        Returns:
            文件元数据对象
        """
        try:
            # 检查文件大小
            if file_size > settings.MAX_FILE_SIZE:
                max_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
                raise ValueError(f"文件大小超过限制({max_mb}MB)")

            # 检查文件类型
            allowed, error_msg = FileService.is_allowed_file(filename)
            if not allowed:
                raise ValueError(error_msg)

            # 获取文件扩展名和类型
            _, ext = os.path.splitext(filename)
            file_type = FileService.get_file_type(ext)

            # 确定存储目录
            if file_type == FileType.DOCUMENT:
                base_dir = settings.DOCUMENTS_DIR
            else:
                base_dir = settings.CODE_DIR

            # 创建存储目录
            os.makedirs(base_dir, exist_ok=True)

            # 生成唯一文件名(使用时间戳+原始文件名)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(base_dir, unique_filename)

            # 保存文件到临时位置以计算MD5
            temp_path = file_path + ".tmp"
            with open(temp_path, "wb") as f:
                f.write(file_content)

            # 计算MD5
            md5_hash = FileService.calculate_md5(temp_path)

            # 检查是否已存在相同文件
            existing_file = FileService.check_file_exists_by_md5(db, md5_hash)
            if existing_file:
                # 删除临时文件
                os.remove(temp_path)
                logger.info(f"文件已存在: {filename} (MD5: {md5_hash})")
                return existing_file

            # 重命名临时文件为正式文件
            os.rename(temp_path, file_path)

            # 创建文件元数据记录
            file_metadata = FileMetadata(
                filename=unique_filename,
                original_filename=filename,
                file_path=file_path,
                file_type=file_type,
                file_extension=ext,
                file_size=file_size,
                md5_hash=md5_hash,
                upload_time=datetime.now(),
                index_status=IndexStatus.PENDING
            )

            # 保存到数据库
            db.add(file_metadata)
            db.commit()
            db.refresh(file_metadata)

            logger.info(f"文件保存成功: {filename} -> {file_path}")
            return file_metadata

        except Exception as e:
            # 清理可能创建的文件
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            logger.error(f"文件保存失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_file_list(
        db: Session,
        file_type: Optional[FileType] = None,
        index_status: Optional[IndexStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[FileMetadata]:
        """
        获取文件列表
        
        Args:
            db: 数据库会话
            file_type: 文件类型过滤
            index_status: 索引状态过滤
            skip: 跳过记录数
            limit: 返回记录数
            
        Returns:
            文件元数据列表
        """
        query = db.query(FileMetadata).filter(FileMetadata.is_deleted == False)

        if file_type:
            query = query.filter(FileMetadata.file_type == file_type)

        if index_status:
            query = query.filter(FileMetadata.index_status == index_status)

        return query.order_by(FileMetadata.upload_time.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_file_by_id(db: Session, file_id: int) -> Optional[FileMetadata]:
        """
        通过ID获取文件元数据
        
        Args:
            db: 数据库会话
            file_id: 文件ID
            
        Returns:
            文件元数据或None
        """
        return db.query(FileMetadata).filter(
            FileMetadata.id == file_id,
            FileMetadata.is_deleted == False
        ).first()

    @staticmethod
    def delete_file(db: Session, file_id: int, physical_delete: bool = False) -> bool:
        """
        删除文件
        
        Args:
            db: 数据库会话
            file_id: 文件ID
            physical_delete: 是否物理删除(删除文件本身),否则仅标记删除
            
        Returns:
            是否成功删除
        """
        try:
            file_metadata = FileService.get_file_by_id(db, file_id)
            if not file_metadata:
                logger.warning(f"文件不存在: ID={file_id}")
                return False

            if physical_delete:
                # 物理删除文件
                if os.path.exists(file_metadata.file_path):
                    os.remove(file_metadata.file_path)
                    logger.info(f"物理删除文件: {file_metadata.file_path}")

                # 从数据库删除
                db.delete(file_metadata)
            else:
                # 软删除(仅标记)
                file_metadata.is_deleted = True

            db.commit()
            logger.info(f"文件删除成功: {file_metadata.filename}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"文件删除失败: {str(e)}", exc_info=True)
            return False

    @staticmethod
    def batch_delete_files(db: Session, file_ids: List[int], physical_delete: bool = False) -> Tuple[int, int]:
        """
        批量删除文件
        
        Args:
            db: 数据库会话
            file_ids: 文件ID列表
            physical_delete: 是否物理删除
            
        Returns:
            (成功数量, 失败数量)
        """
        success_count = 0
        fail_count = 0

        for file_id in file_ids:
            if FileService.delete_file(db, file_id, physical_delete):
                success_count += 1
            else:
                fail_count += 1

        return success_count, fail_count

    @staticmethod
    def update_index_status(
        db: Session,
        file_id: int,
        status: IndexStatus,
        error_message: Optional[str] = None,
        chunk_count: int = 0
    ) -> bool:
        """
        更新文件索引状态
        
        Args:
            db: 数据库会话
            file_id: 文件ID
            status: 新的索引状态
            error_message: 错误信息(如果有)
            chunk_count: 分块数量
            
        Returns:
            是否更新成功
        """
        try:
            file_metadata = FileService.get_file_by_id(db, file_id)
            if not file_metadata:
                return False

            file_metadata.index_status = status
            file_metadata.error_message = error_message
            file_metadata.chunk_count = chunk_count

            if status == IndexStatus.INDEXED:
                file_metadata.index_time = datetime.now()

            db.commit()
            logger.info(f"更新索引状态: {file_metadata.filename} -> {status.value}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"更新索引状态失败: {str(e)}", exc_info=True)
            return False

    @staticmethod
    def get_statistics(db: Session) -> dict:
        """
        获取文件统计信息
        
        Args:
            db: 数据库会话
            
        Returns:
            统计信息字典
        """
        total_files = db.query(FileMetadata).filter(FileMetadata.is_deleted == False).count()
        document_count = db.query(FileMetadata).filter(
            FileMetadata.is_deleted == False,
            FileMetadata.file_type == FileType.DOCUMENT
        ).count()
        code_count = db.query(FileMetadata).filter(
            FileMetadata.is_deleted == False,
            FileMetadata.file_type == FileType.CODE
        ).count()
        indexed_count = db.query(FileMetadata).filter(
            FileMetadata.is_deleted == False,
            FileMetadata.index_status == IndexStatus.INDEXED
        ).count()
        pending_count = db.query(FileMetadata).filter(
            FileMetadata.is_deleted == False,
            FileMetadata.index_status == IndexStatus.PENDING
        ).count()

        return {
            "total_files": total_files,
            "document_count": document_count,
            "code_count": code_count,
            "indexed_count": indexed_count,
            "pending_count": pending_count
        }
