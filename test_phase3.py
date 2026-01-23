"""
Phase 3 索引系统测试脚本
测试文本处理、向量化、存储和索引功能
"""
import os
import sys
import time
import tempfile
from pathlib import Path

# 添加后端路径到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.config import settings
from backend.processors.text_processor import processor
from backend.services.embedding_service import get_embedding_service
from backend.services.vector_store import get_vector_store
from backend.logger_config import get_logger

logger = get_logger(__name__)


def create_test_files():
    """创建测试文件"""
    test_dir = tempfile.mkdtemp(prefix="kb_test_")
    
    # 创建测试文本文件
    test_files = {}
    
    # 1. 简单文本文件
    txt_file = os.path.join(test_dir, "test.txt")
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("这是一个测试文本文件。\n\n")
        f.write("它包含了多个段落。\n\n")
        f.write("我们可以用它来测试文本处理和分块功能。\n\n")
        f.write("这应该被分成多个块。")
    test_files["txt"] = txt_file
    
    # 2. Markdown 文件
    md_file = os.path.join(test_dir, "test.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# 测试 Markdown 文件\n\n")
        f.write("## 第一部分\n")
        f.write("这是第一部分的内容。\n\n")
        f.write("## 第二部分\n")
        f.write("这是第二部分的内容。")
    test_files["md"] = md_file
    
    # 3. HTML 文件
    html_file = os.path.join(test_dir, "test.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write("<html><body>")
        f.write("<h1>测试 HTML 文件</h1>")
        f.write("<p>这是一段 HTML 内容。</p>")
        f.write("<p>包含多个段落和标签。</p>")
        f.write("</body></html>")
    test_files["html"] = html_file
    
    return test_dir, test_files


def test_text_processor():
    """测试文本处理器"""
    logger.info("=" * 60)
    logger.info("Test 1: 文本处理器测试")
    logger.info("=" * 60)
    
    test_dir, test_files = create_test_files()
    
    try:
        for file_type, file_path in test_files.items():
            logger.info(f"\n处理 {file_type} 文件: {file_path}")
            
            chunks = processor.process_file(file_path)
            
            logger.info(f"分块数: {len(chunks)}")
            logger.info(f"分块大小配置 - size: {settings.CHUNK_SIZE}, overlap: {settings.CHUNK_OVERLAP}")
            
            for i, chunk in enumerate(chunks):
                logger.debug(f"  分块 {i}: 长度={len(chunk.content)}, 内容={chunk.content[:50]}...")
            
            # 验证分块
            assert len(chunks) > 0, f"{file_type} 文件分块失败"
            for chunk in chunks:
                assert len(chunk.content) > 0, "分块内容为空"
                assert chunk.content is not None, "分块内容为None"
            
            logger.info(f"✅ {file_type} 文件处理成功")
        
        logger.info("\n✅ 所有文本处理测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 文本处理测试失败: {str(e)}", exc_info=True)
        return False
    
    finally:
        # 清理测试文件
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)


def test_embedding_service():
    """测试向量化服务"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: 向量化服务测试")
    logger.info("=" * 60)
    
    try:
        embedding_service = get_embedding_service()
        
        # 测试文本
        test_texts = [
            "这是一个测试句子。",
            "这是另一个测试句子。",
            "Python 是一种编程语言。",
            "机器学习很有趣。",
            "知识库系统帮助组织信息。"
        ]
        
        # Test 1: 单个文本向量化
        logger.info("\n单个文本向量化测试:")
        embedding = embedding_service.embed_text(test_texts[0])
        logger.info(f"  向量维度: {len(embedding)}")
        logger.info(f"  向量范数: {(embedding**2).sum()**0.5:.4f}")  # 应该接近1(已归一化)
        assert isinstance(embedding, (list, object)), "向量类型错误"
        assert len(embedding) > 0, "向量为空"
        logger.info("  ✅ 单个向量化成功")
        
        # Test 2: 批量向量化
        logger.info("\n批量向量化测试:")
        embeddings = embedding_service.embed_texts(test_texts, batch_size=2)
        logger.info(f"  向量数: {len(embeddings)}")
        logger.info(f"  每个向量维度: {len(embeddings[0])}")
        assert len(embeddings) == len(test_texts), "向量数不匹配"
        for emb in embeddings:
            assert len(emb) > 0, "向量为空"
        logger.info("  ✅ 批量向量化成功")
        
        # Test 3: 相似度计算
        logger.info("\n相似度计算测试:")
        sim1 = embedding_service.similarity(embeddings[0], embeddings[1])
        logger.info(f"  句子0 vs 句子1 相似度: {sim1:.4f}")
        
        sim2 = embedding_service.similarity(embeddings[0], embeddings[0])
        logger.info(f"  句子0 vs 句子0 相似度: {sim2:.4f}")
        
        assert 0 <= sim1 <= 1, "相似度范围错误"
        assert 0.99 <= sim2 <= 1.01, "相同句子相似度应接近1"
        logger.info("  ✅ 相似度计算成功")
        
        # Test 4: 批量相似度
        logger.info("\n批量相似度计算测试:")
        similarities = embedding_service.batch_similarity(embeddings[0], embeddings[1:])
        logger.info(f"  相似度: {similarities}")
        assert len(similarities) == len(embeddings) - 1, "相似度数不匹配"
        logger.info("  ✅ 批量相似度计算成功")
        
        logger.info("\n✅ 所有向量化测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 向量化服务测试失败: {str(e)}", exc_info=True)
        return False


def test_vector_store():
    """测试向量存储"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: 向量数据库测试")
    logger.info("=" * 60)
    
    try:
        vector_store = get_vector_store()
        
        # 准备测试数据
        test_docs = [
            "这是关于机器学习的文档",
            "这是关于深度学习的文档",
            "这是关于数据科学的文档",
            "这是关于计算机视觉的文档",
            "这是关于自然语言处理的文档"
        ]
        
        # 获取向量化服务
        embedding_service = get_embedding_service()
        embeddings = embedding_service.embed_texts(test_docs, batch_size=2)
        
        # Test 1: 添加文档
        logger.info("\n添加文档测试:")
        metadatas = [
            {"doc_id": str(i), "category": "AI"}
            for i in range(len(test_docs))
        ]
        
        ids = vector_store.add_documents(test_docs, embeddings, metadatas)
        logger.info(f"  添加了 {len(ids)} 个文档")
        logger.info(f"  文档ID: {ids[:3]}...")
        assert len(ids) == len(test_docs), "添加的文档数不匹配"
        logger.info("  ✅ 添加文档成功")
        
        # Test 2: 查询相似文档
        logger.info("\n查询相似文档测试:")
        query = "机器学习和深度学习"
        query_embedding = embedding_service.embed_text(query)
        
        results, similarities, result_metadatas = vector_store.query(query_embedding, n_results=3)
        logger.info(f"  查询: '{query}'")
        logger.info(f"  找到 {len(results)} 个相关文档:")
        for i, (doc, sim) in enumerate(zip(results, similarities)):
            logger.info(f"    {i+1}. 相似度: {sim:.4f}, 内容: {doc[:30]}...")
        
        assert len(results) > 0, "未找到相关文档"
        assert similarities[0] >= similarities[-1] if len(similarities) > 1 else True, "相似度排序错误"
        logger.info("  ✅ 查询相似文档成功")
        
        # Test 3: 获取文档
        logger.info("\n获取文档测试:")
        retrieved = vector_store.get_documents(ids[:2])
        logger.info(f"  获取了 {len(retrieved.get('ids', []))} 个文档")
        assert len(retrieved.get('ids', [])) == 2, "获取文档数错误"
        logger.info("  ✅ 获取文档成功")
        
        # Test 4: 统计
        logger.info("\n统计信息测试:")
        count = vector_store.count()
        logger.info(f"  向量库中共有 {count} 个文档")
        assert count == len(test_docs), "文档数统计错误"
        logger.info("  ✅ 统计成功")
        
        # Test 5: 删除文档
        logger.info("\n删除文档测试:")
        deleted = vector_store.delete_documents(ids[:2])
        logger.info(f"  删除操作成功: {deleted}")
        remaining = vector_store.count()
        logger.info(f"  删除后剩余 {remaining} 个文档")
        assert remaining == count - 2, "删除文档数错误"
        logger.info("  ✅ 删除文档成功")
        
        logger.info("\n✅ 所有向量存储测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 向量存储测试失败: {str(e)}", exc_info=True)
        return False


def test_end_to_end_indexing():
    """测试端到端索引流程"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: 端到端索引流程测试")
    logger.info("=" * 60)
    
    try:
        # 准备测试文件
        test_dir, test_files = create_test_files()
        
        # 创建测试索引服务
        from backend.services.indexing_service import IndexingService
        indexing_service = IndexingService()
        
        # 索引文本文件
        logger.info("\n索引测试文件:")
        txt_file = test_files["txt"]
        
        # 这里模拟文件ID为1的索引过程
        file_id = 1
        success, message, chunk_count = indexing_service.index_file(
            file_id=file_id,
            file_path=txt_file,
            file_type="document",
            db=None
        )
        
        logger.info(f"  索引成功: {success}")
        logger.info(f"  消息: {message}")
        logger.info(f"  分块数: {chunk_count}")
        
        assert success, "索引失败"
        assert chunk_count > 0, "分块数为0"
        logger.info("  ✅ 索引成功")
        
        # 验证向量库
        logger.info("\n验证向量库:")
        vector_store = get_vector_store()
        vector_count = vector_store.count()
        logger.info(f"  向量库中现有 {vector_count} 个向量")
        assert vector_count >= chunk_count, "向量数少于分块数"
        logger.info("  ✅ 向量库验证成功")
        
        logger.info("\n✅ 端到端索引流程测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 端到端索引测试失败: {str(e)}", exc_info=True)
        return False
    
    finally:
        # 清理
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)


def run_performance_test():
    """性能测试"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 5: 性能测试")
    logger.info("=" * 60)
    
    try:
        embedding_service = get_embedding_service()
        
        # 生成大量测试文本
        test_size = 100
        test_texts = [f"测试文本 {i}: " + "这是一个测试句子。" * 10 for i in range(test_size)]
        
        # 测试向量化性能
        logger.info(f"\n向量化性能测试 ({test_size} 个文本):")
        start = time.time()
        embeddings = embedding_service.embed_texts(test_texts, batch_size=32)
        elapsed = time.time() - start
        
        total_chars = sum(len(t) for t in test_texts)
        throughput = total_chars / elapsed
        
        logger.info(f"  耗时: {elapsed:.2f} 秒")
        logger.info(f"  吞吐量: {throughput:.0f} 字符/秒")
        logger.info(f"  平均: {elapsed/test_size*1000:.2f} 毫秒/文本")
        
        assert elapsed > 0, "耗时计算错误"
        assert throughput > 100, "吞吐量过低"
        logger.info("  ✅ 性能测试通过")
        
        logger.info("\n✅ 所有性能测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 性能测试失败: {str(e)}", exc_info=True)
        return False


def main():
    """主测试函数"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 58 + "║")
    logger.info("║" + "  Phase 3 索引系统完整测试".center(58) + "║")
    logger.info("║" + " " * 58 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    
    results = {}
    
    # 运行所有测试
    tests = [
        ("文本处理器", test_text_processor),
        ("向量化服务", test_embedding_service),
        ("向量数据库", test_vector_store),
        ("端到端索引", test_end_to_end_indexing),
        ("性能测试", run_performance_test),
    ]
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"测试异常: {str(e)}", exc_info=True)
            results[test_name] = False
    
    # 输出总结
    logger.info("\n" + "=" * 60)
    logger.info("测试总结")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name:20} {status}")
    
    logger.info("=" * 60)
    logger.info(f"总体: {passed}/{total} 通过")
    logger.info("=" * 60)
    
    if passed == total:
        logger.info("\n🎉 所有测试通过！Phase 3 实现完整。")
        return 0
    else:
        logger.error(f"\n⚠️  有 {total - passed} 个测试失败。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
