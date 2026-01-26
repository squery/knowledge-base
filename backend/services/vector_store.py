"""
向量数据库服务
使用 Chroma 作为向量存储
"""
from typing import List, Dict, Optional, Tuple
import os
from datetime import datetime

try:
    from backend.logger_config import get_logger
except Exception:
    from logger_config import get_logger
try:
    from backend.config import settings
except Exception:
    from config import settings

logger = get_logger(__name__)


class VectorStore:
    """Chroma 向量数据库封装"""
    
    def __init__(self, persist_dir: str = None):
        """
        初始化向量存储
        
        Args:
            persist_dir: 持久化存储目录
        """
        self.persist_dir = persist_dir or settings.CHROMA_DB_PATH
        self.client = None
        self.collection = None
        self._init_store()
    
    def _init_store(self):
        """初始化 Chroma 向量存储"""
        try:
            import chromadb
            
            # 确保持久化目录存在
            os.makedirs(self.persist_dir, exist_ok=True)
            
            logger.info(f"初始化 Chroma 向量存储: {self.persist_dir}")
            
            # 使用新版本 Chroma API
            self.client = chromadb.PersistentClient(
                path=self.persist_dir
            )
            
            # 获取或创建默认集合
            self.collection = self.client.get_or_create_collection(
                name="knowledge_base",
                metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
            )
            
            logger.info(f"向量存储初始化成功")
            
        except ImportError:
            logger.error("chromadb 未安装, 请执行: pip install chromadb")
            raise
        except Exception as e:
            logger.error(f"向量存储初始化失败: {str(e)}", exc_info=True)
            raise
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict] = None,
        ids: List[str] = None,
        deduplicate: bool = True
    ) -> List[str]:
        """
        添加文档到向量存储（支持去重）
        
        Args:
            documents: 文档文本列表
            embeddings: 对应的向量列表
            metadatas: 元数据列表
            ids: 文档ID列表 (自动生成如果不提供)
            deduplicate: 是否去重（基于ID）
            
        Returns:
            添加的文档ID列表
        """
        if not documents or not embeddings:
            logger.warning("文档或向量列表为空")
            return []
        
        if len(documents) != len(embeddings):
            raise ValueError("文档数和向量数不匹配")
        
        try:
            # 生成ID (如果未提供)
            if ids is None:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                ids = [f"doc_{timestamp}_{i}" for i in range(len(documents))]
            
            # 去重检查
            if deduplicate:
                existing = self.collection.get(ids=ids, include=[])
                existing_ids = set(existing.get("ids", []))
                
                if existing_ids:
                    logger.info(f"检测到 {len(existing_ids)} 个重复ID，将跳过")
                    # 过滤掉已存在的
                    filtered = [(i, d, e, m) for i, d, e, m in zip(ids, documents, embeddings, metadatas or [{}]*len(ids)) 
                                if i not in existing_ids]
                    if not filtered:
                        logger.warning("所有文档ID均已存在，跳过添加")
                        return []
                    ids, documents, embeddings, metadatas = zip(*filtered)
                    ids, documents, embeddings, metadatas = list(ids), list(documents), list(embeddings), list(metadatas)
            
            # 构建元数据
            if metadatas is None:
                metadatas = [{} for _ in documents]
            
            # 不再添加时间戳，减少元数据开销
            
            logger.info(f"添加 {len(documents)} 个文档到向量存储")
            
            # 添加到集合
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            # 注意: Chroma 0.4.x+ PersistentClient 会自动持久化，无需手动调用 persist()
            
            logger.info(f"文档添加成功: {len(ids)} 个")
            return ids
            
        except Exception as e:
            logger.error(f"添加文档失败: {str(e)}", exc_info=True)
            raise
    
    def query(
        self,
        query_embedding: List[float],
        n_results: int = 3,
        where: Dict = None
    ) -> Tuple[List[str], List[float], List[Dict]]:
        """
        查询相似文档
        
        Args:
            query_embedding: 查询向量
            n_results: 返回结果数量
            where: 元数据过滤条件
            
        Returns:
            (文档列表, 距离列表, 元数据列表)
        """
        if not self.collection:
            raise RuntimeError("向量存储未初始化")
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                include=["documents", "distances", "metadatas"]
            )
            
            if not results or not results["documents"] or not results["documents"][0]:
                return [], [], []
            
            documents = results["documents"][0]
            distances = results["distances"][0]
            metadatas = results["metadatas"][0]
            
            # 转换距离为相似度 (cosine距离 -> 相似度)
            # Chroma 返回的是距离,需要转换为相似度
            similarities = [1 - d for d in distances]
            
            return documents, similarities, metadatas
            
        except Exception as e:
            logger.error(f"查询失败: {str(e)}", exc_info=True)
            return [], [], []
    
    def delete_documents(self, ids: List[str]) -> bool:
        """
        删除文档
        
        Args:
            ids: 文档ID列表
            
        Returns:
            是否成功
        """
        if not ids:
            return True
        
        try:
            logger.info(f"删除 {len(ids)} 个文档")
            self.collection.delete(ids=ids)
            # Chroma 0.4.x+ PersistentClient 会自动持久化
            logger.info(f"文档删除成功")
            return True
        except Exception as e:
            logger.error(f"删除文档失败: {str(e)}", exc_info=True)
            return False
    
    def delete_by_metadata(self, where: Dict) -> int:
        """
        按元数据删除文档
        
        Args:
            where: 元数据过滤条件
            
        Returns:
            删除的文档数
        """
        try:
            # 获取所有匹配的文档
            results = self.collection.get(where=where, include=[])
            ids_to_delete = results.get("ids", [])
            
            if ids_to_delete:
                self.delete_documents(ids_to_delete)
            
            return len(ids_to_delete)
        except Exception as e:
            logger.error(f"删除文档失败: {str(e)}", exc_info=True)
            return 0
    
    def get_documents(self, ids: List[str]) -> Dict[str, any]:
        """
        获取指定ID的文档
        
        Args:
            ids: 文档ID列表
            
        Returns:
            文档字典
        """
        if not ids:
            return {}
        
        try:
            results = self.collection.get(
                ids=ids,
                include=["documents", "metadatas", "embeddings"]
            )
            return results
        except Exception as e:
            logger.error(f"获取文档失败: {str(e)}", exc_info=True)
            return {}
    
    def get_all_documents(self) -> Dict[str, any]:
        """
        获取所有文档
        
        Returns:
            所有文档字典
        """
        try:
            results = self.collection.get(
                include=["documents", "metadatas", "ids"]
            )
            return results
        except Exception as e:
            logger.error(f"获取所有文档失败: {str(e)}", exc_info=True)
            return {"ids": [], "documents": [], "metadatas": []}
    
    def count(self) -> int:
        """
        获取集合中的文档数
        
        Returns:
            文档总数
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"获取文档数失败: {str(e)}", exc_info=True)
            return 0
    
    def clear(self) -> bool:
        """
        清空集合
        
        Returns:
            是否成功
        """
        try:
            logger.warning("清空向量存储集合")
            self.client.delete_collection(name="knowledge_base")
            self.collection = self.client.get_or_create_collection(
                name="knowledge_base",
                metadata={"hnsw:space": "cosine"}
            )
            # Chroma 0.4.x+ PersistentClient 会自动持久化
            return True
        except Exception as e:
            logger.error(f"清空集合失败: {str(e)}", exc_info=True)
            return False


# 全局向量存储实例
vector_store = None


def get_vector_store() -> VectorStore:
    """获取向量存储实例"""
    global vector_store
    if vector_store is None:
        vector_store = VectorStore()
    return vector_store
