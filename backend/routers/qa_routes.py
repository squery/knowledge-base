"""
问答 API 路由
基于向量检索的轻量RAG问答
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

try:
    from backend.logger_config import get_logger
except Exception:
    from logger_config import get_logger
try:
    from backend.database import SessionLocal
except Exception:
    from database import SessionLocal
try:
    from backend.services.indexing_service import get_indexing_service
    from backend.services.vector_store import get_vector_store
except Exception:
    from services.indexing_service import get_indexing_service
    from services.vector_store import get_vector_store
try:
    from backend.config import settings
except Exception:
    from config import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/api/qa", tags=["QA"])


class QARequest(BaseModel):
    question: str
    top_k: int = 3
    max_tokens: int = 256
    use_llm: bool = False


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
    """模板式汇总生成回答，避免重模型依赖；支持自然中文表达"""
    if not contexts:
        return "抱歉，我在知识库中未找到相关内容。您可以尝试上传相关文档或换一个问题重新提问。"
    # 取最相关的段落，拼接成上下文，生成自然回答
    key_contexts = [c.strip() for c in contexts[:3]]
    main_content = key_contexts[0][:300] if key_contexts else ""
    
    # 用更自然的中文回答模板
    answer = f"根据知识库内容：\n\n{main_content}\n\n" \
             f"总的来说，{question}。" \
             f"更详细的信息请查看相关来源文档。"
    return answer


def _generate_answer_llm(question: str, contexts: List[str]) -> Optional[str]:
    """可选LLM生成回答，失败则返回None以便回退；优化中文提示词"""
    try:
        from transformers import pipeline
        device = 0 if settings.LLM_DEVICE.lower() == "cuda" else -1
        
        # 为summarization和text2text-generation分别优化提示词
        if settings.LLM_PIPELINE == "summarization":
            # mT5-XLSum：直接输入要摘要的内容
            text = "\n\n".join([c[:800] for c in contexts[:3]])
        else:
            # text2text-generation：带任务指示的输入
            text = f"问答: {question}\n参考资料:\n" + "\n".join([c[:300] for c in contexts[:3]])
        
        pipe = pipeline(settings.LLM_PIPELINE, model=settings.LLM_MODEL_NAME, device=device)
        result = pipe(text, max_length=min(settings.MAX_TOKENS, 256))
        if isinstance(result, list) and result:
            # summarization 返回 'summary_text'；text2text-generation 返回 'generated_text'
            item = result[0]
            return item.get("summary_text") or item.get("generated_text")
        return None
    except Exception:
        return None


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

        # 4) 生成回答：如开启LLM则尝试模型，否则模板
        answer = None
        if req.use_llm or settings.USE_LLM_QA:
            answer = _generate_answer_llm(question, contexts)
        if not answer:
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
