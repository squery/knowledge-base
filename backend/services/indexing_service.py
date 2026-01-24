"""
自动索引服务
完整的索引流程: 文件 -> 分块 -> 向量化 -> 存储
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import time

from sqlalchemy.orm import Session
from logger_config import get_logger
from config import settings
from models import FileMetadata
from processors.text_processor import processor
from services.embedding_service import get_embedding_service
from services.vector_store import get_vector_store
from database import SessionLocal

logger = get_logger(__name__)


class IndexingService:
    """索引服务 - 管理文件索引流程"""
    
    def __init__(self, max_retries: int = 3):
        """初始化索引服务
        
        Args:
            max_retries: 索引失败最大重试次数
        """
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()
        self.logger = logger
        self.max_retries = max_retries
    
    def index_file(
        self,
        file_id: int,
        file_path: str,
        file_type: str,
        db: Optional[Session] = None,
        retry_count: int = 0
    ) -> Tuple[bool, str, int]:
        """
        索引单个文件（带重试机制）
        
        Args:
            file_id: 文件ID
            file_path: 文件路径
            file_type: 文件类型
            db: 数据库会话
            retry_count: 当前重试次数
            
        Returns:
            (是否成功, 错误信息或提示, 分块数)
        """
        session = db or SessionLocal()
        start_time = time.time()
        
        try:
            logger.info(f"开始索引文件: ID={file_id}, 路径={file_path}")
            
            # 1. 文本处理 - 分块
            logger.debug(f"处理文件文本...")
            chunks = processor.process_file(file_path)
            
            if not chunks:
                raise ValueError("未能从文件中提取文本")
            
            chunk_count = len(chunks)
            logger.info(f"文本分块完成: {chunk_count} 个块")
            
            # 2. 提取分块内容
            chunk_contents = [chunk.content for chunk in chunks]
            
            # 3. 向量化 - 批处理
            logger.debug(f"向量化 {len(chunk_contents)} 个块...")
            embeddings = self.embedding_service.embed_texts(
                chunk_contents,
                batch_size=32,
                normalize=True
            )
            logger.info(f"向量化完成: {len(embeddings)} 个向量")
            
            # 4. 准备元数据（精简版，避免冗余）
            metadatas = []
            for i, chunk in enumerate(chunks):
                metadata = {
                    "file_id": str(file_id),
                    "chunk_index": str(i),
                    "file_type": file_type,
                    # 仅保留关键元数据，减少存储开销
                }
                metadatas.append(metadata)
            
            # 5. 存储到向量数据库
            logger.debug(f"存储向量到数据库...")
            vector_ids = self.vector_store.add_documents(
                documents=chunk_contents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=[f"file_{file_id}_chunk_{i}" for i in range(len(chunks))]
            )
            logger.info(f"向量存储完成: {len(vector_ids)} 个向量")
            
            # 6. 更新数据库
            file_meta = session.query(FileMetadata).filter(
                FileMetadata.id == file_id
            ).first()
            
            if file_meta:
                file_meta.index_status = "indexed"
                file_meta.index_time = datetime.now()
                file_meta.chunk_count = chunk_count
                file_meta.error_message = None
                session.commit()
                logger.info(f"文件索引状态已更新: indexed, 分块数: {chunk_count}")
            
            elapsed_time = time.time() - start_time
            logger.info(f"文件索引完成: ID={file_id}, 耗时={elapsed_time:.2f}s")
            
            return True, f"索引成功: {chunk_count} 个块", chunk_count
            
        except FileNotFoundError:
            error_msg = f"文件不存在: {file_path}"
            self._update_file_status(file_id, "failed", error_msg)
            logger.error(error_msg)
            return False, error_msg, 0
            
        except Exception as e:
            error_msg = f"索引失败: {str(e)}"
            
            # 重试逻辑
            if retry_count < self.max_retries:
                logger.warning(f"索引失败，准备重试 ({retry_count + 1}/{self.max_retries}): ID={file_id}")
                time.sleep(2 ** retry_count)  # 指数退避
                return self.index_file(file_id, file_path, file_type, db, retry_count + 1)
            
            # 重试次数用尽，标记为失败
            self._update_file_status(file_id, "failed", error_msg)
            logger.error(f"索引文件失败（已重试{retry_count}次）: ID={file_id}, 错误={error_msg}", exc_info=True)
            return False, error_msg, 0
            
        finally:
            if db is None:
                session.close()
    
    def index_pending_files(self, db: Optional[Session] = None) -> Dict[str, any]:
        """
        索引所有待索引的文件
        
        Args:
            db: 数据库会话
            
        Returns:
            统计信息字典
        """
        session = db or SessionLocal()
        stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "elapsed_time": 0,
            "details": []
        }
        
        start_time = time.time()
        
        try:
            # 查询待索引的文件
            pending_files = session.query(FileMetadata).filter(
                FileMetadata.index_status == "pending",
                FileMetadata.is_deleted == False
            ).all()
            
            stats["total"] = len(pending_files)
            logger.info(f"发现 {len(pending_files)} 个待索引文件")
            
            for file_meta in pending_files:
                try:
                    # 更新为索引中状态
                    file_meta.index_status = "indexing"
                    session.commit()
                    
                    # 执行索引
                    success, message, chunk_count = self.index_file(
                        file_meta.id,
                        file_meta.file_path,
                        file_meta.file_type,
                        db=session
                    )
                    
                    if success:
                        stats["success"] += 1
                        stats["details"].append({
                            "file_id": file_meta.id,
                            "filename": file_meta.filename,
                            "status": "success",
                            "chunk_count": chunk_count
                        })
                    else:
                        stats["failed"] += 1
                        stats["details"].append({
                            "file_id": file_meta.id,
                            "filename": file_meta.filename,
                            "status": "failed",
                            "error": message
                        })
                
                except Exception as e:
                    stats["failed"] += 1
                    logger.error(f"批量索引时出错: {str(e)}", exc_info=True)
                    stats["details"].append({
                        "file_id": file_meta.id,
                        "filename": file_meta.filename,
                        "status": "error",
                        "error": str(e)
                    })
            
            stats["elapsed_time"] = time.time() - start_time
            logger.info(f"批量索引完成: 成功={stats['success']}, 失败={stats['failed']}, "
                       f"耗时={stats['elapsed_time']:.2f}s")
            
            return stats
            
        finally:
            if db is None:
                session.close()
    
    def delete_index(self, file_id: int, db: Optional[Session] = None) -> bool:
        """
        删除文件的索引
        
        Args:
            file_id: 文件ID
            db: 数据库会话
            
        Returns:
            是否成功
        """
        session = db or SessionLocal()
        
        try:
            logger.info(f"删除文件索引: ID={file_id}")
            
            # 从向量库中删除
            deleted_count = self.vector_store.delete_by_metadata({
                "file_id": str(file_id)
            })
            logger.info(f"从向量库删除 {deleted_count} 个向量")
            
            # 更新数据库状态
            file_meta = session.query(FileMetadata).filter(
                FileMetadata.id == file_id
            ).first()
            
            if file_meta:
                file_meta.index_status = "pending"
                file_meta.index_time = None
                file_meta.chunk_count = 0
                session.commit()
                logger.info(f"文件索引状态已重置为: pending")
            
            return True
            
        except Exception as e:
            logger.error(f"删除索引失败: {str(e)}", exc_info=True)
            return False
            
        finally:
            if db is None:
                session.close()
    
    def reindex_file(
        self,
        file_id: int,
        file_path: str,
        file_type: str,
        db: Optional[Session] = None
    ) -> Tuple[bool, str]:
        """
        重新索引文件 (先删除再索引)
        
        Args:
            file_id: 文件ID
            file_path: 文件路径
            file_type: 文件类型
            db: 数据库会话
            
        Returns:
            (是否成功, 消息)
        """
        # 删除旧索引
        self.delete_index(file_id, db)
        
        # 重新索引
        success, message, _ = self.index_file(file_id, file_path, file_type, db)
        return success, message
    
    def get_indexing_stats(self, db: Optional[Session] = None) -> Dict[str, any]:
        """
        获取索引统计信息
        
        Args:
            db: 数据库会话
            
        Returns:
            统计信息字典
        """
        session = db or SessionLocal()
        
        try:
            total = session.query(FileMetadata).filter(
                FileMetadata.is_deleted == False
            ).count()
            
            indexed = session.query(FileMetadata).filter(
                FileMetadata.index_status == "indexed",
                FileMetadata.is_deleted == False
            ).count()
            
            pending = session.query(FileMetadata).filter(
                FileMetadata.index_status == "pending",
                FileMetadata.is_deleted == False
            ).count()
            
            indexing = session.query(FileMetadata).filter(
                FileMetadata.index_status == "indexing",
                FileMetadata.is_deleted == False
            ).count()
            
            failed = session.query(FileMetadata).filter(
                FileMetadata.index_status == "failed",
                FileMetadata.is_deleted == False
            ).count()
            
            total_chunks = session.query(FileMetadata).filter(
                FileMetadata.is_deleted == False
            ).with_entities(FileMetadata.chunk_count).all()
            
            total_chunks_count = sum(c[0] for c in total_chunks if c[0])
            
            vector_count = self.vector_store.count()
            
            return {
                "total_files": total,
                "indexed_files": indexed,
                "pending_files": pending,
                "indexing_files": indexing,
                "failed_files": failed,
                "total_chunks": total_chunks_count,
                "vector_count": vector_count,
                "index_ratio": f"{(indexed / total * 100):.1f}%" if total > 0 else "0%"
            }
            
        finally:
            if db is None:
                session.close()
    
    def _update_file_status(
        self,
        file_id: int,
        status: str,
        error_msg: str = None
    ):
        """
        更新文件索引状态
        
        Args:
            file_id: 文件ID
            status: 新状态
            error_msg: 错误信息
        """
        session = SessionLocal()
        try:
            file_meta = session.query(FileMetadata).filter(
                FileMetadata.id == file_id
            ).first()
            
            if file_meta:
                file_meta.index_status = status
                if error_msg:
                    file_meta.error_message = error_msg
                if status == "indexed":
                    file_meta.index_time = datetime.now()
                session.commit()
        except Exception as e:
            logger.error(f"更新文件状态失败: {str(e)}")
        finally:
            session.close()


# 全局索引服务实例
indexing_service = None


def get_indexing_service() -> IndexingService:
    """获取索引服务实例"""
    global indexing_service
    if indexing_service is None:
        indexing_service = IndexingService()
    return indexing_service
