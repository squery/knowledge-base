"""
嵌入向量化模块
使用 Sentence-Transformers 进行文本向量化
"""
from typing import List, Union
import numpy as np

try:
    from backend.logger_config import get_logger
except Exception:
    from logger_config import get_logger
try:
    from backend.config import settings
except Exception:
    from config import settings

logger = get_logger(__name__)


class EmbeddingService:
    """嵌入向量化服务"""
    
    def __init__(self, model_name: str = None, device: str = None):
        """
        初始化嵌入服务
        
        Args:
            model_name: 模型名称
            device: 设备 (cpu/cuda)
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.device = device or settings.EMBEDDING_DEVICE
        self.model = None
        self._init_model()
    
    def _init_model(self):
        """初始化嵌入模型"""
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"加载嵌入模型: {self.model_name} (device={self.device})")
            
            self.model = SentenceTransformer(self.model_name)
            self.model.to(self.device)
            
            # 获取向量维度
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"模型加载成功, 向量维度: {self.embedding_dim}")
            
        except ImportError:
            logger.error("sentence-transformers 未安装, 请执行: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}", exc_info=True)
            raise
    
    def embed_text(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        生成单个文本的嵌入向量
        
        Args:
            text: 输入文本
            normalize: 是否归一化向量
            
        Returns:
            嵌入向量 (np.ndarray)
        """
        if not self.model:
            raise RuntimeError("模型未初始化")
        
        try:
            embeddings = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=normalize,
                show_progress_bar=False
            )
            return embeddings
        except Exception as e:
            logger.error(f"文本嵌入失败: {str(e)}", exc_info=True)
            raise
    
    def embed_texts(
        self, 
        texts: List[str], 
        batch_size: int = 32,
        normalize: bool = True,
        show_progress: bool = False
    ) -> List[np.ndarray]:
        """
        批量生成文本嵌入向量
        
        Args:
            texts: 文本列表
            batch_size: 批量大小
            normalize: 是否归一化向量
            show_progress: 是否显示进度
            
        Returns:
            嵌入向量列表
        """
        if not self.model:
            raise RuntimeError("模型未初始化")
        
        if not texts:
            return []
        
        try:
            logger.info(f"开始批量嵌入: {len(texts)} 条文本, batch_size={batch_size}")
            
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=normalize,
                show_progress_bar=show_progress
            )
            
            logger.info(f"批量嵌入完成: 生成 {len(embeddings)} 个向量")
            
            # 如果是单个文本,转换为列表
            if len(embeddings.shape) == 1:
                embeddings = [embeddings]
            else:
                embeddings = [e for e in embeddings]
            
            return embeddings
            
        except Exception as e:
            logger.error(f"批量嵌入失败: {str(e)}", exc_info=True)
            raise
    
    def similarity(
        self, 
        embedding1: Union[np.ndarray, List[float]], 
        embedding2: Union[np.ndarray, List[float]]
    ) -> float:
        """
        计算两个向量的余弦相似度
        
        Args:
            embedding1: 第一个向量
            embedding2: 第二个向量
            
        Returns:
            相似度得分 (0-1)
        """
        try:
            if isinstance(embedding1, list):
                embedding1 = np.array(embedding1)
            if isinstance(embedding2, list):
                embedding2 = np.array(embedding2)
            
            # 计算余弦相似度
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"相似度计算失败: {str(e)}", exc_info=True)
            return 0.0
    
    def batch_similarity(
        self,
        query_embedding: Union[np.ndarray, List[float]],
        candidate_embeddings: List[Union[np.ndarray, List[float]]]
    ) -> List[float]:
        """
        批量计算查询向量与候选向量的相似度
        
        Args:
            query_embedding: 查询向量
            candidate_embeddings: 候选向量列表
            
        Returns:
            相似度列表
        """
        similarities = []
        for candidate in candidate_embeddings:
            sim = self.similarity(query_embedding, candidate)
            similarities.append(sim)
        return similarities


# 全局嵌入服务实例
embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """获取嵌入服务实例(延迟初始化)"""
    global embedding_service
    if embedding_service is None:
        embedding_service = EmbeddingService()
    return embedding_service
