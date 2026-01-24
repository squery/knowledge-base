"""
嵌入效果校验脚本
测试向量化模型的质量和相似度检索能力
"""
import sys
import os

# 添加后端目录到路径
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

from services.embedding_service import get_embedding_service
from services.vector_store import get_vector_store
import numpy as np


def test_similarity_search():
    """测试相似度检索"""
    print("=" * 60)
    print("嵌入效果校验测试")
    print("=" * 60)
    print()
    
    # 初始化服务
    print("[1/4] 初始化嵌入服务...")
    embedding_service = get_embedding_service()
    print(f"✓ 模型: {embedding_service.model_name}")
    print(f"✓ 向量维度: {embedding_service.embedding_dim}")
    print()
    
    # 准备测试数据
    print("[2/4] 准备测试数据...")
    test_docs = [
        "Python是一种高级编程语言，广泛应用于Web开发、数据分析和人工智能领域。",
        "JavaScript是一种脚本语言，主要用于网页开发和前端交互。",
        "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习。",
        "深度学习是机器学习的子领域，使用神经网络来处理复杂的模式识别任务。",
        "FastAPI是一个现代化的Python Web框架，用于构建高性能的API服务。",
        "React是一个流行的JavaScript库，用于构建用户界面。",
        "Docker是一个容器化平台，用于打包和部署应用程序。",
        "数据库是用于存储和管理数据的系统，常见的有MySQL、PostgreSQL等。"
    ]
    
    print(f"✓ 准备了 {len(test_docs)} 个测试文档")
    print()
    
    # 向量化测试文档
    print("[3/4] 向量化测试文档...")
    embeddings = embedding_service.embed_texts(test_docs, normalize=True)
    print(f"✓ 生成了 {len(embeddings)} 个向量")
    print()
    
    # 测试查询
    print("[4/4] 测试相似度检索...")
    print()
    
    queries = [
        "什么是Python编程语言？",
        "机器学习和深度学习有什么关系？",
        "如何构建Web API？"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"查询 {i}: {query}")
        print("-" * 60)
        
        # 向量化查询
        query_embedding = embedding_service.embed_text(query, normalize=True)
        
        # 计算相似度
        similarities = []
        for j, doc_embedding in enumerate(embeddings):
            similarity = embedding_service.similarity(query_embedding, doc_embedding)
            similarities.append((j, similarity, test_docs[j]))
        
        # 排序并显示Top-3
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        print("Top-3 最相关文档:")
        for rank, (doc_idx, sim, doc_text) in enumerate(similarities[:3], 1):
            print(f"  {rank}. 相似度: {sim:.4f}")
            print(f"     文档 #{doc_idx}: {doc_text[:50]}...")
        print()
    
    # 评估向量质量
    print("=" * 60)
    print("向量质量评估")
    print("=" * 60)
    
    # 计算向量的平均模长
    norms = [np.linalg.norm(emb) for emb in embeddings]
    avg_norm = np.mean(norms)
    print(f"平均向量模长: {avg_norm:.4f} (归一化后应接近1.0)")
    
    # 计算向量间的平均相似度
    all_similarities = []
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            sim = embedding_service.similarity(embeddings[i], embeddings[j])
            all_similarities.append(sim)
    
    avg_sim = np.mean(all_similarities)
    max_sim = np.max(all_similarities)
    min_sim = np.min(all_similarities)
    
    print(f"向量间平均相似度: {avg_sim:.4f}")
    print(f"最大相似度: {max_sim:.4f}")
    print(f"最小相似度: {min_sim:.4f}")
    print()
    
    # 建议
    print("建议:")
    if avg_norm < 0.95 or avg_norm > 1.05:
        print("  ⚠️ 向量模长偏离1.0，建议检查归一化设置")
    else:
        print("  ✓ 向量归一化正常")
    
    if avg_sim > 0.7:
        print("  ⚠️ 平均相似度较高，可能需要更强的区分能力")
    elif avg_sim < 0.2:
        print("  ⚠️ 平均相似度较低，可能模型表达能力不足")
    else:
        print("  ✓ 向量区分度适中")
    
    print()
    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_similarity_search()
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
