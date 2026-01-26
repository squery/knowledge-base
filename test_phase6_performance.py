"""
Phase 6 Task 6.2 性能测试
测试文件上传、索引创建和问答响应时间
"""
import os
import sys
import time
import json
import tempfile
import requests
from datetime import datetime
from statistics import mean, stdev

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.logger_config import get_logger

logger = get_logger(__name__)

BACKEND_URL = "http://localhost:8000"

# 性能指标
performance_metrics = {
    "测试时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "性能指标": {},
    "测试结果": {}
}

# 性能目标
PERF_TARGETS = {
    "文件上传响应时间": "< 5秒",
    "索引创建速度": "> 1000字符/秒",
    "问答响应时间": "< 10秒",
}


def test_upload_performance():
    """测试文件上传性能"""
    logger.info("\n" + "=" * 70)
    logger.info("Test 6.2.1: 文件上传性能测试")
    logger.info("=" * 70)
    
    temp_dir = tempfile.mkdtemp()
    upload_times = []
    
    # 创建不同大小的测试文件
    test_sizes = [
        ("small", "这是一个小文件。" * 10),      # ~160 字节
        ("medium", "这是一个中等大小的文件。" * 100),  # ~1600 字节
        ("large", "这是一个较大的文件。" * 500),      # ~8000 字节
    ]
    
    for name, content in test_sizes:
        test_file = os.path.join(temp_dir, f"perf_test_{name}.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        file_size = len(content.encode('utf-8'))
        
        logger.info(f"\n上传测试 - {name} ({file_size} 字节)...")
        
        start_time = time.time()
        try:
            with open(test_file, "rb") as f:
                files = {"file": f}
                response = requests.post(f"{BACKEND_URL}/api/files/upload", files=files, timeout=15)
            
            upload_time = time.time() - start_time
            upload_times.append(upload_time)
            
            if response.status_code == 200:
                logger.info(f"  ✅ 上传成功 - 耗时: {upload_time:.2f}秒")
            else:
                logger.error(f"  ❌ 上传失败 - 状态码: {response.status_code}")
        except Exception as e:
            logger.error(f"  ❌ 上传异常: {e}")
    
    # 统计结果
    if upload_times:
        avg_upload_time = mean(upload_times)
        logger.info(f"\n上传性能统计：")
        logger.info(f"  平均响应时间: {avg_upload_time:.2f}秒")
        logger.info(f"  最小值: {min(upload_times):.2f}秒")
        logger.info(f"  最大值: {max(upload_times):.2f}秒")
        
        # 检查是否满足目标
        if avg_upload_time < 5:
            logger.info(f"  ✅ 达成目标：{PERF_TARGETS['文件上传响应时间']}")
            performance_metrics["性能指标"]["文件上传"] = f"✅ {avg_upload_time:.2f}秒 (目标 < 5秒)"
        else:
            logger.warning(f"  ⚠️ 未达成目标：平均 {avg_upload_time:.2f}秒，目标 < 5秒")
            performance_metrics["性能指标"]["文件上传"] = f"⚠️ {avg_upload_time:.2f}秒 (目标 < 5秒)"
    
    # 清理
    import shutil
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass


def test_indexing_performance():
    """测试索引创建速度"""
    logger.info("\n" + "=" * 70)
    logger.info("Test 6.2.2: 索引创建速度测试")
    logger.info("=" * 70)
    
    logger.info("\n创建测试内容...")
    
    # 创建包含不同大小内容的文件
    test_contents = [
        ("small", "这是测试文本。\n" * 50),           # ~600 字符
        ("medium", "这是测试文本。\n" * 200),         # ~2400 字符
        ("large", "这是测试文本。\n" * 500),          # ~6000 字符
    ]
    
    temp_dir = tempfile.mkdtemp()
    indexing_results = []
    
    for name, content in test_contents:
        test_file = os.path.join(temp_dir, f"index_test_{name}.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        char_count = len(content)
        
        logger.info(f"\n索引测试 - {name} ({char_count} 字符)...")
        
        start_time = time.time()
        try:
            with open(test_file, "rb") as f:
                files = {"file": f}
                response = requests.post(f"{BACKEND_URL}/api/files/upload", files=files, timeout=15)
            
            index_time = time.time() - start_time
            
            if response.status_code == 200:
                # 估算索引速度（字符/秒）
                speed = char_count / index_time if index_time > 0 else 0
                logger.info(f"  ✅ 索引成功 - 耗时: {index_time:.2f}秒, 速度: {speed:.0f} 字符/秒")
                indexing_results.append(speed)
            else:
                logger.error(f"  ❌ 索引失败")
        except Exception as e:
            logger.error(f"  ❌ 索引异常: {e}")
    
    # 统计结果
    if indexing_results:
        avg_speed = mean(indexing_results)
        logger.info(f"\n索引性能统计：")
        logger.info(f"  平均速度: {avg_speed:.0f} 字符/秒")
        logger.info(f"  最小值: {min(indexing_results):.0f} 字符/秒")
        logger.info(f"  最大值: {max(indexing_results):.0f} 字符/秒")
        
        # 检查是否满足目标
        if avg_speed > 1000:
            logger.info(f"  ✅ 达成目标：{PERF_TARGETS['索引创建速度']}")
            performance_metrics["性能指标"]["索引速度"] = f"✅ {avg_speed:.0f} 字符/秒 (目标 > 1000)"
        else:
            logger.warning(f"  ⚠️ 未达成目标：平均 {avg_speed:.0f} 字符/秒，目标 > 1000")
            performance_metrics["性能指标"]["索引速度"] = f"⚠️ {avg_speed:.0f} 字符/秒 (目标 > 1000)"
    
    # 清理
    import shutil
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass


def test_qa_response_time():
    """测试问答响应时间"""
    logger.info("\n" + "=" * 70)
    logger.info("Test 6.2.3: 问答响应时间测试")
    logger.info("=" * 70)
    
    questions = [
        "什么是人工智能",
        "如何使用这个系统",
        "系统支持哪些功能",
        "文件上传的限制是什么",
        "问答功能如何工作",
    ]
    
    response_times = []
    
    for i, question in enumerate(questions, 1):
        logger.info(f"\n问答 {i}: '{question}'")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/qa/ask",
                json={"question": question},
                timeout=20
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                logger.info(f"  ✅ 成功 - 响应时间: {response_time:.2f}秒 (回答长度: {len(answer)}字)")
                response_times.append(response_time)
            else:
                logger.warning(f"  ⚠️ 返回状态码: {response.status_code}")
        except Exception as e:
            logger.error(f"  ❌ 异常: {str(e)[:50]}")
    
    # 统计结果
    if response_times:
        avg_response_time = mean(response_times)
        logger.info(f"\n问答性能统计：")
        logger.info(f"  平均响应时间: {avg_response_time:.2f}秒")
        logger.info(f"  最小值: {min(response_times):.2f}秒")
        logger.info(f"  最大值: {max(response_times):.2f}秒")
        
        # 检查是否满足目标
        if avg_response_time < 10:
            logger.info(f"  ✅ 达成目标：{PERF_TARGETS['问答响应时间']}")
            performance_metrics["性能指标"]["问答响应"] = f"✅ {avg_response_time:.2f}秒 (目标 < 10秒)"
        else:
            logger.warning(f"  ⚠️ 未达成目标：平均 {avg_response_time:.2f}秒，目标 < 10秒")
            performance_metrics["性能指标"]["问答响应"] = f"⚠️ {avg_response_time:.2f}秒 (目标 < 10秒)"
    else:
        logger.warning("⚠️ 无有效问答测试数据")


def generate_performance_report():
    """生成性能报告"""
    logger.info("\n" + "=" * 70)
    logger.info("性能测试报告")
    logger.info("=" * 70)
    
    logger.info("\n性能目标:")
    for metric, target in PERF_TARGETS.items():
        logger.info(f"  {metric}: {target}")
    
    logger.info("\n测试结果:")
    for metric, result in performance_metrics["性能指标"].items():
        logger.info(f"  {metric}: {result}")
    
    # 统计达成情况
    achieved = sum(1 for v in performance_metrics["性能指标"].values() if "✅" in str(v))
    total = len(PERF_TARGETS)
    
    performance_metrics["测试结果"]["总目标数"] = total
    performance_metrics["测试结果"]["达成数"] = achieved
    performance_metrics["测试结果"]["达成率"] = f"{achieved/total*100:.0f}%"
    performance_metrics["测试结果"]["状态"] = "✅ 全部通过" if achieved == total else f"⚠️ {achieved}/{total} 通过"
    
    logger.info(f"\n总体评价: {performance_metrics['测试结果']['状态']}")
    
    # 保存报告
    report_file = "test_phase6_performance_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(performance_metrics, f, ensure_ascii=False, indent=2)
    logger.info(f"性能报告已保存：{report_file}")
    
    logger.info("\n" + "=" * 70)
    logger.info("Phase 6 Task 6.2 性能测试完成！")
    logger.info("=" * 70)


def main():
    logger.info("╔" + "=" * 68 + "╗")
    logger.info("║  Phase 6 Task 6.2: 性能测试                                    ║")
    logger.info("║  测试时间：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "                       ║")
    logger.info("╚" + "=" * 68 + "╝")
    
    # 检查服务
    logger.info("\n检查后端服务...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code != 200:
            logger.error("❌ 后端服务异常")
            return
        logger.info("✅ 后端服务就绪")
    except Exception as e:
        logger.error(f"❌ 无法连接后端：{e}")
        logger.info("请运行：start_all.bat (Windows) 或 ./start_all.sh")
        return
    
    # 执行性能测试
    test_upload_performance()
    test_indexing_performance()
    test_qa_response_time()
    
    # 生成报告
    generate_performance_report()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n性能测试被中断")
    except Exception as e:
        logger.error(f"\n性能测试异常：{e}")
        import traceback
        traceback.print_exc()
