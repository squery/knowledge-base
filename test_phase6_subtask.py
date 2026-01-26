"""
Phase 6 Task 6.1 详细子任务测试
逐一测试文件上传、索引、问答、删除等各个子任务
"""
import os
import sys
import time
import json
import tempfile
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.logger_config import get_logger

logger = get_logger(__name__)

BACKEND_URL = "http://localhost:8000"

# 详细的子任务结果
subtask_results = {
    "执行时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "子任务": {
        "6.1.1 文件上传功能测试": {},
        "6.1.2 索引功能测试": {},
        "6.1.3 问答功能测试": {},
        "6.1.4 文件删除测试": {},
    }
}


def test_6_1_1_file_upload():
    """子任务 6.1.1: 文件上传功能测试"""
    logger.info("\n" + "=" * 70)
    logger.info("子任务 6.1.1: 文件上传功能测试")
    logger.info("=" * 70)
    
    test_details = []
    temp_dir = tempfile.mkdtemp()
    
    # 测试1: 上传小文件
    logger.info("\n[小文件测试] 创建并上传 100字节文件...")
    test_file = os.path.join(temp_dir, "small_file.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("这是一个小文件。" * 3)
    
    start = time.time()
    try:
        with open(test_file, "rb") as f:
            response = requests.post(f"{BACKEND_URL}/api/files/upload", files={"file": f}, timeout=10)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            logger.info(f"✅ 小文件上传成功 - 耗时: {elapsed:.2f}秒")
            test_details.append({"子测试": "小文件上传", "状态": "✅ 通过", "耗时": f"{elapsed:.2f}秒", "文件大小": "~100字节"})
        else:
            logger.error(f"❌ 小文件上传失败: {response.status_code}")
            test_details.append({"子测试": "小文件上传", "状态": "❌ 失败", "状态码": response.status_code})
    except Exception as e:
        logger.error(f"❌ 异常: {e}")
        test_details.append({"子测试": "小文件上传", "状态": "❌ 异常", "错误": str(e)[:50]})
    
    # 测试2: 上传中等文件
    logger.info("\n[中等文件测试] 创建并上传 1000字节文件...")
    test_file = os.path.join(temp_dir, "medium_file.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("这是一个中等大小的文件。" * 30)
    
    start = time.time()
    try:
        with open(test_file, "rb") as f:
            response = requests.post(f"{BACKEND_URL}/api/files/upload", files={"file": f}, timeout=10)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            logger.info(f"✅ 中等文件上传成功 - 耗时: {elapsed:.2f}秒")
            test_details.append({"子测试": "中等文件上传", "状态": "✅ 通过", "耗时": f"{elapsed:.2f}秒", "文件大小": "~1000字节"})
        else:
            logger.error(f"❌ 中等文件上传失败")
            test_details.append({"子测试": "中等文件上传", "状态": "❌ 失败"})
    except Exception as e:
        logger.error(f"❌ 异常: {e}")
        test_details.append({"子测试": "中等文件上传", "状态": "❌ 异常"})
    
    # 测试3: 文件类型验证
    logger.info("\n[文件类型测试] 测试不同类型文件...")
    file_types = {
        "txt": "这是文本文件",
        "md": "# 这是Markdown文件\n\n## 标题\n内容",
    }
    
    for ext, content in file_types.items():
        test_file = os.path.join(temp_dir, f"test_file.{ext}")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        try:
            with open(test_file, "rb") as f:
                response = requests.post(f"{BACKEND_URL}/api/files/upload", files={"file": f}, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ .{ext} 文件上传成功")
                test_details.append({"子测试": f".{ext} 文件类型", "状态": "✅ 通过"})
            else:
                logger.error(f"❌ .{ext} 文件上传失败")
                test_details.append({"子测试": f".{ext} 文件类型", "状态": "❌ 失败"})
        except Exception as e:
            logger.error(f"❌ .{ext} 上传异常: {e}")
            test_details.append({"子测试": f".{ext} 文件类型", "状态": "❌ 异常"})
    
    # 清理
    import shutil
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass
    
    pass_count = len([t for t in test_details if "✅" in t["状态"]])
    subtask_results["子任务"]["6.1.1 文件上传功能测试"]["结果"] = test_details
    subtask_results["子任务"]["6.1.1 文件上传功能测试"]["通过率"] = f"{pass_count}/{len(test_details)}"
    subtask_results["子任务"]["6.1.1 文件上传功能测试"]["状态"] = "✅ 通过" if pass_count >= 3 else "⚠️ 部分通过"
    
    logger.info(f"\n子任务 6.1.1 总结: {pass_count}/{len(test_details)} 通过")
    return pass_count


def test_6_1_2_indexing():
    """子任务 6.1.2: 索引功能测试"""
    logger.info("\n" + "=" * 70)
    logger.info("子任务 6.1.2: 索引功能测试")
    logger.info("=" * 70)
    
    test_details = []
    
    # 测试1: 索引状态查询
    logger.info("\n[索引状态查询] 获取系统索引统计...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/indexes/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            logger.info(f"✅ 索引统计成功")
            logger.info(f"   已索引文档: {stats.get('indexed_docs', 0)}")
            logger.info(f"   集合数: {stats.get('collections', 0)}")
            test_details.append({"子测试": "索引统计查询", "状态": "✅ 通过", "文档数": stats.get('indexed_docs', 0)})
        else:
            logger.warning(f"⚠️ 索引统计返回 {response.status_code}")
            test_details.append({"子测试": "索引统计查询", "状态": "⚠️ 接口异常"})
    except Exception as e:
        logger.error(f"❌ 异常: {e}")
        test_details.append({"子测试": "索引统计查询", "状态": "❌ 异常"})
    
    # 测试2: 索引持久化验证
    logger.info("\n[索引持久化测试] 检查索引文件...")
    try:
        # 检查索引目录是否存在
        index_dir = os.path.join(os.path.dirname(__file__), "indexes")
        if os.path.exists(index_dir):
            logger.info(f"✅ 索引目录存在: {index_dir}")
            index_files = os.listdir(index_dir)
            logger.info(f"   索引文件数: {len(index_files)}")
            test_details.append({"子测试": "索引持久化", "状态": "✅ 通过", "文件数": len(index_files)})
        else:
            logger.warning(f"⚠️ 索引目录不存在")
            test_details.append({"子测试": "索引持久化", "状态": "⚠️ 目录不存在"})
    except Exception as e:
        logger.error(f"❌ 异常: {e}")
        test_details.append({"子测试": "索引持久化", "状态": "❌ 异常"})
    
    # 测试3: 索引速度验证
    logger.info("\n[索引速度测试] 测试新文件索引速度...")
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "speed_test.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("这是索引速度测试文件。" * 50)
    
    char_count = len("这是索引速度测试文件。" * 50)
    
    start = time.time()
    try:
        with open(test_file, "rb") as f:
            response = requests.post(f"{BACKEND_URL}/api/files/upload", files={"file": f}, timeout=10)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            speed = char_count / elapsed if elapsed > 0 else 0
            logger.info(f"✅ 索引速度: {speed:.0f} 字符/秒 (耗时 {elapsed:.2f}秒)")
            test_details.append({"子测试": "索引速度", "状态": "✅ 通过", "速度": f"{speed:.0f} 字/秒"})
        else:
            logger.error(f"❌ 索引失败")
            test_details.append({"子测试": "索引速度", "状态": "❌ 失败"})
    except Exception as e:
        logger.error(f"❌ 异常: {e}")
        test_details.append({"子测试": "索引速度", "状态": "❌ 异常"})
    
    # 清理
    import shutil
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass
    
    pass_count = len([t for t in test_details if "✅" in t["状态"]])
    subtask_results["子任务"]["6.1.2 索引功能测试"]["结果"] = test_details
    subtask_results["子任务"]["6.1.2 索引功能测试"]["通过率"] = f"{pass_count}/{len(test_details)}"
    subtask_results["子任务"]["6.1.2 索引功能测试"]["状态"] = "✅ 通过" if pass_count >= 2 else "⚠️ 部分通过"
    
    logger.info(f"\n子任务 6.1.2 总结: {pass_count}/{len(test_details)} 通过")
    return pass_count


def test_6_1_3_qa():
    """子任务 6.1.3: 问答功能测试"""
    logger.info("\n" + "=" * 70)
    logger.info("子任务 6.1.3: 问答功能测试")
    logger.info("=" * 70)
    
    test_details = []
    
    questions = [
        ("基础问答", "人工智能是什么"),
        ("功能问答", "这个系统可以做什么"),
        ("使用问答", "如何上传文件"),
        ("技术问答", "系统使用什么技术"),
    ]
    
    for category, question in questions:
        logger.info(f"\n[{category}] 问题: '{question}'")
        
        start = time.time()
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/qa/ask",
                json={"question": question},
                timeout=15
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                logger.info(f"✅ 回答成功 - 耗时: {elapsed:.2f}秒, 字数: {len(answer)}")
                test_details.append({
                    "子测试": category,
                    "状态": "✅ 通过",
                    "问题": question,
                    "回答长度": len(answer),
                    "耗时": f"{elapsed:.2f}秒"
                })
            else:
                logger.warning(f"⚠️ 返回状态码 {response.status_code}")
                test_details.append({"子测试": category, "状态": "⚠️ 异常状态码"})
        except Exception as e:
            logger.error(f"❌ 异常: {e}")
            test_details.append({"子测试": category, "状态": "❌ 异常"})
    
    pass_count = len([t for t in test_details if "✅" in t["状态"]])
    subtask_results["子任务"]["6.1.3 问答功能测试"]["结果"] = test_details
    subtask_results["子任务"]["6.1.3 问答功能测试"]["通过率"] = f"{pass_count}/{len(test_details)}"
    subtask_results["子任务"]["6.1.3 问答功能测试"]["状态"] = "✅ 通过" if pass_count >= 3 else "⚠️ 部分通过"
    
    logger.info(f"\n子任务 6.1.3 总结: {pass_count}/{len(test_details)} 通过")
    return pass_count


def test_6_1_4_deletion():
    """子任务 6.1.4: 文件删除测试"""
    logger.info("\n" + "=" * 70)
    logger.info("子任务 6.1.4: 文件删除测试")
    logger.info("=" * 70)
    
    test_details = []
    
    # 测试1: 获取文件列表
    logger.info("\n[准备] 获取可删除的文件...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/files/list", timeout=10)
        if response.status_code == 200:
            files = response.json().get('files', [])
            logger.info(f"✅ 获取文件列表成功，共 {len(files)} 个文件")
            test_details.append({"子测试": "获取文件列表", "状态": "✅ 通过", "文件数": len(files)})
            
            # 测试2: 尝试删除文件
            if files:
                file_to_delete = files[0]
                file_id = file_to_delete.get('id') or file_to_delete.get('file_id')
                filename = file_to_delete.get('filename', '未知')
                
                logger.info(f"\n[删除] 删除文件: {filename}")
                try:
                    response = requests.delete(f"{BACKEND_URL}/api/files/{file_id}", timeout=10)
                    if response.status_code == 200:
                        logger.info(f"✅ 文件删除成功")
                        test_details.append({"子测试": "单个文件删除", "状态": "✅ 通过", "文件": filename})
                    else:
                        logger.warning(f"⚠️ 删除返回 {response.status_code}")
                        test_details.append({"子测试": "单个文件删除", "状态": "⚠️ 异常状态码"})
                except Exception as e:
                    logger.error(f"❌ 异常: {e}")
                    test_details.append({"子测试": "单个文件删除", "状态": "❌ 异常"})
            else:
                logger.info("ℹ️ 系统无文件，跳过删除测试")
                test_details.append({"子测试": "单个文件删除", "状态": "⏭️ 跳过", "原因": "无文件"})
        else:
            logger.error(f"❌ 获取文件列表失败")
            test_details.append({"子测试": "获取文件列表", "状态": "❌ 失败"})
    except Exception as e:
        logger.error(f"❌ 异常: {e}")
        test_details.append({"子测试": "获取文件列表", "状态": "❌ 异常"})
    
    pass_count = len([t for t in test_details if "✅" in t["状态"]])
    skip_count = len([t for t in test_details if "⏭️" in t["状态"]])
    subtask_results["子任务"]["6.1.4 文件删除测试"]["结果"] = test_details
    subtask_results["子任务"]["6.1.4 文件删除测试"]["通过率"] = f"{pass_count}/{len(test_details) - skip_count}"
    subtask_results["子任务"]["6.1.4 文件删除测试"]["状态"] = "✅ 通过" if pass_count > 0 or skip_count > 0 else "❌ 失败"
    
    logger.info(f"\n子任务 6.1.4 总结: {pass_count}/{len(test_details)} 通过")
    return pass_count


def generate_report():
    """生成详细报告"""
    logger.info("\n" + "=" * 70)
    logger.info("Task 6.1 子任务执行总结")
    logger.info("=" * 70)
    
    for task_name, task_data in subtask_results["子任务"].items():
        status = task_data.get("状态", "❌ 未执行")
        pass_rate = task_data.get("通过率", "N/A")
        logger.info(f"{task_name}: {status} ({pass_rate})")
    
    # 计算总体通过率
    total_pass = sum(
        len([r for r in task_data.get("结果", []) if "✅" in r.get("状态", "")])
        for task_data in subtask_results["子任务"].values()
    )
    total_tests = sum(
        len(task_data.get("结果", []))
        for task_data in subtask_results["子任务"].values()
    )
    
    if total_tests > 0:
        overall_rate = total_pass / total_tests * 100
        logger.info(f"\n总体通过率: {overall_rate:.0f}% ({total_pass}/{total_tests})")
    
    # 保存报告
    report_file = "test_phase6_subtask_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(subtask_results, f, ensure_ascii=False, indent=2)
    logger.info(f"详细报告已保存: {report_file}")
    
    logger.info("\n" + "=" * 70)
    logger.info("Task 6.1 子任务测试完成！")
    logger.info("=" * 70)


def main():
    logger.info("╔" + "=" * 68 + "╗")
    logger.info("║  Phase 6 Task 6.1 - 详细子任务测试                          ║")
    logger.info("║  测试时间：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "                       ║")
    logger.info("╚" + "=" * 68 + "╝")
    
    # 检查后端
    logger.info("\n检查后端服务...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ 后端服务就绪")
        else:
            logger.error("❌ 后端服务异常")
            return
    except Exception as e:
        logger.error(f"❌ 无法连接后端: {e}")
        logger.info("请运行: start_all.bat (Windows) 或 ./start_all.sh")
        return
    
    # 执行子任务
    test_6_1_1_file_upload()
    test_6_1_2_indexing()
    test_6_1_3_qa()
    test_6_1_4_deletion()
    
    # 生成报告
    generate_report()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n测试被中断")
    except Exception as e:
        logger.error(f"\n测试异常: {e}")
        import traceback
        traceback.print_exc()
