"""
索引管理 API 路由
提供索引的增删改查功能
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from logger_config import get_logger
from database import SessionLocal
from models import FileMetadata
from services.indexing_service import get_indexing_service
from services.vector_store import get_vector_store

logger = get_logger(__name__)

router = APIRouter(prefix="/api/index", tags=["Index Management"])


# 响应模型
class IndexStatusResponse(BaseModel):
    """索引状态响应"""
    total_files: int
    indexed_files: int
    pending_files: int
    indexing_files: int
    failed_files: int
    total_chunks: int
    vector_count: int
    index_ratio: str


class FileIndexResponse(BaseModel):
    """文件索引结果"""
    success: bool
    message: str
    file_id: int
    index_status: str
    chunk_count: int = 0


class SearchResult(BaseModel):
    """搜索结果"""
    content: str
    similarity: float
    file_id: Optional[int]
    file_path: Optional[str]
    chunk_index: Optional[int]
    metadata: dict = {}


class SearchResponse(BaseModel):
    """搜索响应"""
    query: str
    results: List[SearchResult]
    total_results: int


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/status", response_model=IndexStatusResponse)
async def get_index_status(db: Session = Depends(get_db)):
    """
    获取索引统计状态
    
    Returns:
        索引统计信息
    """
    try:
        indexing_service = get_indexing_service()
        stats = indexing_service.get_indexing_stats(db)
        return stats
    except Exception as e:
        logger.error(f"获取索引状态失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@router.post("/files/{file_id}", response_model=FileIndexResponse)
async def reindex_file(file_id: int, db: Session = Depends(get_db)):
    """
    重新索引指定文件
    
    Args:
        file_id: 文件ID
        
    Returns:
        索引结果
    """
    try:
        # 获取文件信息
        file_meta = db.query(FileMetadata).filter(
            FileMetadata.id == file_id
        ).first()
        
        if not file_meta:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        if file_meta.is_deleted:
            raise HTTPException(status_code=410, detail="文件已删除")
        
        logger.info(f"重新索引文件: ID={file_id}, 路径={file_meta.file_path}")
        
        # 执行索引
        indexing_service = get_indexing_service()
        success, message = indexing_service.reindex_file(
            file_id,
            file_meta.file_path,
            file_meta.file_type,
            db
        )
        
        # 刷新文件信息
        db.refresh(file_meta)
        
        return FileIndexResponse(
            success=success,
            message=message,
            file_id=file_id,
            index_status=file_meta.index_status,
            chunk_count=file_meta.chunk_count or 0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"索引文件失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"索引失败: {str(e)}")


@router.delete("/files/{file_id}")
async def delete_file_index(file_id: int, db: Session = Depends(get_db)):
    """
    删除文件的索引
    
    Args:
        file_id: 文件ID
        
    Returns:
        删除结果
    """
    try:
        # 验证文件存在
        file_meta = db.query(FileMetadata).filter(
            FileMetadata.id == file_id
        ).first()
        
        if not file_meta:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        logger.info(f"删除文件索引: ID={file_id}")
        
        # 删除索引
        indexing_service = get_indexing_service()
        success = indexing_service.delete_index(file_id, db)
        
        if not success:
            raise HTTPException(status_code=500, detail="删除索引失败")
        
        return {
            "success": True,
            "message": "索引删除成功",
            "file_id": file_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除索引失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/rebuild")
async def rebuild_all_indices(db: Session = Depends(get_db)):
    """
    重建所有索引
    
    返回:
        构建结果统计
    """
    try:
        logger.info("开始重建所有索引")
        
        # 清空向量库
        vector_store = get_vector_store()
        vector_store.clear()
        logger.info("向量库已清空")
        
        # 重新索引所有文件
        indexing_service = get_indexing_service()
        stats = indexing_service.index_pending_files(db)
        
        return {
            "success": stats["failed"] == 0,
            "message": f"重建完成: 成功 {stats['success']} 个, 失败 {stats['failed']} 个",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"重建索引失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"重建失败: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_similar_documents(
    query: str,
    top_k: int = 3,
    db: Session = Depends(get_db)
):
    """
    语义相似性搜索
    
    Args:
        query: 搜索查询文本
        top_k: 返回结果数量
        
    Returns:
        相似文档列表
    """
    try:
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="查询文本不能为空")
        
        logger.info(f"搜索相似文档: query='{query}', top_k={top_k}")
        
        # 对查询进行向量化
        embedding_service = get_indexing_service().embedding_service
        query_embedding = embedding_service.embed_text(query, normalize=True)
        
        # 从向量库查询
        vector_store = get_vector_store()
        documents, similarities, metadatas = vector_store.query(
            query_embedding,
            n_results=top_k
        )
        
        # 构建返回结果
        results = []
        for doc, sim, meta in zip(documents, similarities, metadatas):
            try:
                file_id = int(meta.get("file_id")) if meta.get("file_id") else None
            except (ValueError, TypeError):
                file_id = None
            
            try:
                chunk_index = int(meta.get("chunk_index")) if meta.get("chunk_index") else None
            except (ValueError, TypeError):
                chunk_index = None
            
            result = SearchResult(
                content=doc,
                similarity=float(sim),
                file_id=file_id,
                file_path=meta.get("file_path"),
                chunk_index=chunk_index,
                metadata={k: v for k, v in meta.items() 
                         if k not in ["file_id", "file_path", "chunk_index"]}
            )
            results.append(result)
        
        logger.info(f"搜索完成: 找到 {len(results)} 个相关文档")
        
        return SearchResponse(
            query=query,
            results=results,
            total_results=len(results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/files/{file_id}/info")
async def get_file_index_info(file_id: int, db: Session = Depends(get_db)):
    """
    获取文件的索引详细信息
    
    Args:
        file_id: 文件ID
        
    Returns:
        文件索引信息
    """
    try:
        file_meta = db.query(FileMetadata).filter(
            FileMetadata.id == file_id
        ).first()
        
        if not file_meta:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 获取向量库中该文件的向量数
        vector_store = get_vector_store()
        all_vectors = vector_store.get_all_documents()
        
        vector_count = 0
        if all_vectors.get("metadatas"):
            vector_count = sum(1 for meta in all_vectors["metadatas"]
                              if meta.get("file_id") == str(file_id))
        
        return {
            "file_id": file_id,
            "filename": file_meta.filename,
            "original_filename": file_meta.original_filename,
            "file_type": file_meta.file_type,
            "file_size": file_meta.file_size,
            "index_status": file_meta.index_status,
            "index_time": file_meta.index_time.isoformat() if file_meta.index_time else None,
            "chunk_count": file_meta.chunk_count or 0,
            "vector_count": vector_count,
            "error_message": file_meta.error_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文件信息失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取信息失败: {str(e)}")
