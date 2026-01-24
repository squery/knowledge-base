"""
问答 API 路由
基于向量检索的轻量RAG问答
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from logger_config import get_logger
from database import SessionLocal
from services.indexing_service import get_indexing_service
from services.vector_store import get_vector_store

logger = get_logger(__name__)

router = APIRouter(prefix="/api/qa", tags=["QA"])


class QARequest(BaseModel):
    question: str
    top_k: int = 3
    max_tokens: int = 256


class QASource(BaseModel):
    file_id: Optional[int]
    file_path: Optional[str]
    chunk_index: Optional[int]
    similarity: float
    content_preview: str


class QAResponse(BaseModel):
    question: str
    answer: str
    sources: List[QASource]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _generate_answer_template(question: str, contexts: List[str]) -> str:
    """模板式汇总生成回答，避免重模型依赖"""
    if not contexts:
        return "抱歉，未检索到相关内容。请尝试上传或调整问题。"
    # 简单摘要：取前若干段落拼接，附带主题
    joined = "\n\n".join([c.strip()[:500] for c in contexts[:3]])
    answer = (
        f"问题：{question}\n\n" 
        f"根据检索到的内容，综合摘要如下：\n" 
        f"{joined}\n\n"
        f"注：此为检索摘要，建议根据来源进一步核实。"
    )
    return answer


@router.post("/ask", response_model=QAResponse)
async def ask_question(req: QARequest, db: Session = Depends(get_db)):
    """
    提问问答接口：先向量检索，再进行轻量摘要生成
    """
    try:
        question = req.question.strip() if req.question else ""
        if not question:
            raise HTTPException(status_code=400, detail="问题不能为空")

        # 1) 获取嵌入与向量库
        indexing_service = get_indexing_service()
        embedding_service = indexing_service.embedding_service
        vector_store = get_vector_store()

        # 2) 对问题进行向量化
        query_emb = embedding_service.embed_text(question, normalize=True)

        # 3) 召回相关文档
        documents, similarities, metadatas = vector_store.query(
            query_embedding=query_emb,
            n_results=max(1, min(req.top_k, 10))
        )

        sources: List[QASource] = []
        contexts: List[str] = []
        for doc, sim, meta in zip(documents, similarities, metadatas):
            # 提取元数据
            file_id = None
            chunk_index = None
            try:
                if meta.get("file_id") is not None:
                    file_id = int(meta.get("file_id"))
            except Exception:
                pass
            try:
                if meta.get("chunk_index") is not None:
                    chunk_index = int(meta.get("chunk_index"))
            except Exception:
                pass

            sources.append(QASource(
                file_id=file_id,
                file_path=meta.get("file_path"),
                chunk_index=chunk_index,
                similarity=float(sim),
                content_preview=doc[:200]
            ))
            contexts.append(doc)

        # 4) 生成回答（模板式）
        answer = _generate_answer_template(question, contexts)

        return QAResponse(
            question=question,
            answer=answer,
            sources=sources
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"问答失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")
