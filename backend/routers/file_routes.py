"""
文件管理路由
处理文件上传、列表、删除等API端点
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import FileType, IndexStatus
from services.file_service import FileService
from logger_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/files", tags=["文件管理"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传单个文件
    
    Args:
        file: 上传的文件
        db: 数据库会话
        
    Returns:
        文件元数据
    """
    try:
        logger.info(f"开始上传文件: {file.filename}")

        # 读取文件内容
        file_content = await file.read()
        file_size = len(file_content)

        # 保存文件
        file_metadata = FileService.save_uploaded_file(
            db=db,
            filename=file.filename,
            file_content=file_content,
            file_size=file_size
        )

        return {
            "success": True,
            "message": "文件上传成功",
            "data": file_metadata.to_dict()
        }

    except ValueError as e:
        logger.warning(f"文件上传验证失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.post("/upload/batch")
async def upload_files_batch(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    批量上传文件
    
    Args:
        files: 上传的文件列表
        db: 数据库会话
        
    Returns:
        上传结果统计
    """
    try:
        logger.info(f"开始批量上传 {len(files)} 个文件")

        results = {
            "success": [],
            "failed": [],
            "skipped": []  # 已存在的文件
        }

        for file in files:
            try:
                # 读取文件内容
                file_content = await file.read()
                file_size = len(file_content)

                # 保存文件
                file_metadata = FileService.save_uploaded_file(
                    db=db,
                    filename=file.filename,
                    file_content=file_content,
                    file_size=file_size
                )

                # 检查是否是已存在的文件
                if file_metadata.filename != file.filename:
                    results["skipped"].append({
                        "filename": file.filename,
                        "reason": "文件已存在"
                    })
                else:
                    results["success"].append(file_metadata.to_dict())

            except Exception as e:
                logger.error(f"文件上传失败 {file.filename}: {str(e)}")
                results["failed"].append({
                    "filename": file.filename,
                    "error": str(e)
                })

        return {
            "success": True,
            "message": f"批量上传完成: 成功 {len(results['success'])}, 跳过 {len(results['skipped'])}, 失败 {len(results['failed'])}",
            "data": results
        }

    except Exception as e:
        logger.error(f"批量上传失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"批量上传失败: {str(e)}")


@router.get("/list")
async def get_file_list(
    file_type: Optional[str] = Query(None, description="文件类型过滤: document 或 code"),
    index_status: Optional[str] = Query(None, description="索引状态过滤: pending, indexing, indexed, failed"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db)
):
    """
    获取文件列表
    
    Args:
        file_type: 文件类型过滤
        index_status: 索引状态过滤
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话
        
    Returns:
        文件列表
    """
    try:
        # 转换参数
        file_type_enum = None
        if file_type:
            try:
                file_type_enum = FileType(file_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"无效的文件类型: {file_type}")

        index_status_enum = None
        if index_status:
            try:
                index_status_enum = IndexStatus(index_status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"无效的索引状态: {index_status}")

        # 获取文件列表
        files = FileService.get_file_list(
            db=db,
            file_type=file_type_enum,
            index_status=index_status_enum,
            skip=skip,
            limit=limit
        )

        return {
            "success": True,
            "data": [f.to_dict() for f in files],
            "count": len(files)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文件列表失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")


@router.get("/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """
    获取文件统计信息
    
    Args:
        db: 数据库会话
        
    Returns:
        统计信息
    """
    try:
        stats = FileService.get_statistics(db)
        return {
            "success": True,
            "data": stats
        }

    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/{file_id}")
async def get_file_detail(
    file_id: int,
    db: Session = Depends(get_db)
):
    """
    获取文件详细信息
    
    Args:
        file_id: 文件ID
        db: 数据库会话
        
    Returns:
        文件详细信息
    """
    try:
        file_metadata = FileService.get_file_by_id(db, file_id)
        if not file_metadata:
            raise HTTPException(status_code=404, detail="文件不存在")

        return {
            "success": True,
            "data": file_metadata.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文件详情失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取文件详情失败: {str(e)}")


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    physical_delete: bool = Query(False, description="是否物理删除文件"),
    db: Session = Depends(get_db)
):
    """
    删除单个文件
    
    Args:
        file_id: 文件ID
        physical_delete: 是否物理删除
        db: 数据库会话
        
    Returns:
        删除结果
    """
    try:
        success = FileService.delete_file(db, file_id, physical_delete)
        if not success:
            raise HTTPException(status_code=404, detail="文件不存在或删除失败")

        return {
            "success": True,
            "message": "文件删除成功"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文件失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")


@router.post("/delete/batch")
async def delete_files_batch(
    file_ids: List[int],
    physical_delete: bool = Query(False, description="是否物理删除文件"),
    db: Session = Depends(get_db)
):
    """
    批量删除文件
    
    Args:
        file_ids: 文件ID列表
        physical_delete: 是否物理删除
        db: 数据库会话
        
    Returns:
        删除结果统计
    """
    try:
        if not file_ids:
            raise HTTPException(status_code=400, detail="文件ID列表不能为空")

        success_count, fail_count = FileService.batch_delete_files(db, file_ids, physical_delete)

        return {
            "success": True,
            "message": f"批量删除完成: 成功 {success_count}, 失败 {fail_count}",
            "data": {
                "success_count": success_count,
                "fail_count": fail_count
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量删除失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"批量删除失败: {str(e)}")


@router.put("/{file_id}/index-status")
async def update_file_index_status(
    file_id: int,
    status: str,
    error_message: Optional[str] = None,
    chunk_count: int = 0,
    db: Session = Depends(get_db)
):
    """
    更新文件索引状态
    
    Args:
        file_id: 文件ID
        status: 新的索引状态
        error_message: 错误信息
        chunk_count: 分块数量
        db: 数据库会话
        
    Returns:
        更新结果
    """
    try:
        # 转换状态
        try:
            index_status = IndexStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的索引状态: {status}")

        success = FileService.update_index_status(
            db=db,
            file_id=file_id,
            status=index_status,
            error_message=error_message,
            chunk_count=chunk_count
        )

        if not success:
            raise HTTPException(status_code=404, detail="文件不存在或更新失败")

        return {
            "success": True,
            "message": "索引状态更新成功"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新索引状态失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新索引状态失败: {str(e)}")
