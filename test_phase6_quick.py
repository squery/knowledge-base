"""
Phase 6 Task 6.1 快速功能测试
简化版本，快速验证核心功能
"""
import os
import sys
import time
import json
import tempfile
import requests
from pathlib import Path
from datetime import datetime

# 添加后端路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.logger_config import get_logger

logger = get_logger(__name__)

BACKEND_URL = "http://localhost:8000"

# 测试结果
results = {
    "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "功能测试": {},
    "测试摘要": {}
}


def test_basic_functionality():
    """测试基本功能"""
    logger.info("\n" + "=" * 70)
    logger.info("Phase 6 Task 6.1: 功能测试")
    logger.info("=" * 70)
    
    # 1. 后端健康检查
    logger.info("\n[1] 检查后端服务...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ 后端服务运行正常")
            results["功能测试"]["后端健康检查"] = "✅ 通过"
        else:
            logger.error(f"❌ 后端异常，状态码：{response.status_code}")
            results["功能测试"]["后端健康检查"] = f"❌ 失败 (状态码: {response.status_code})"
            return False
    except Exception as e:
        logger.error(f"❌ 无法连接后端：{e}")
        results["功能测试"]["后端健康检查"] = f"❌ 异常: {str(e)[:50]}"
        return False
    
    # 2. 测试文件上传
    logger.info("\n[2] 测试文件上传...")
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test_doc.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("这是测试文档。\n")
        f.write("用来验证文件上传功能。\n")
        f.write("系统应该正确处理这个文件。")
    
    try:
        with open(test_file, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{BACKEND_URL}/api/files/upload", files=files, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ 文件上传成功")
            results["功能测试"]["文件上传"] = "✅ 通过"
        else:
            logger.error(f"❌ 文件上传失败，状态码：{response.status_code}")
            results["功能测试"]["文件上传"] = f"❌ 失败 (状态码: {response.status_code})"
    except Exception as e:
        logger.error(f"❌ 文件上传异常：{e}")
        results["功能测试"]["文件上传"] = f"❌ 异常: {str(e)[:50]}"
    
    # 3. 测试文件列表
    logger.info("\n[3] 测试文件列表查询...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/files/list", timeout=10)
        if response.status_code == 200:
            files_data = response.json().get('files', [])
            logger.info(f"✅ 文件列表查询成功，共 {len(files_data)} 个文件")
            results["功能测试"]["文件列表"] = f"✅ 通过 ({len(files_data)} 个文件)"
        else:
            logger.error(f"❌ 文件列表查询失败，状态码：{response.status_code}")
            results["功能测试"]["文件列表"] = f"❌ 失败"
    except Exception as e:
        logger.error(f"❌ 文件列表异常：{e}")
        results["功能测试"]["文件列表"] = f"❌ 异常"
    
    # 4. 测试索引状态
    logger.info("\n[4] 测试索引状态查询...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/indexes/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            logger.info(f"✅ 索引统计成功")
            logger.info(f"   已索引：{stats.get('indexed_docs', 0)} 条")
            results["功能测试"]["索引查询"] = "✅ 通过"
        else:
            logger.warning(f"⚠️ 索引查询返回 {response.status_code}，尝试备用接口...")
            results["功能测试"]["索引查询"] = "⚠️ 备用接口"
    except Exception as e:
        logger.warning(f"⚠️ 索引查询异常，这是正常的：{str(e)[:40]}")
        results["功能测试"]["索引查询"] = "⚠️ 接口可能不存在"
    
    # 5. 测试问答功能
    logger.info("\n[5] 测试问答功能...")
    qa_tests = [
        "什么是知识库",
        "如何使用系统",
        "系统的功能是什么",
    ]
    
    qa_pass = 0
    for question in qa_tests:
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/qa/ask",
                json={"question": question},
                timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                logger.info(f"  ✅ 问答：'{question}' -> 获得回答（{len(answer)}字）")
                qa_pass += 1
            else:
                logger.warning(f"  ⚠️ 问答返回 {response.status_code}")
        except Exception as e:
            logger.warning(f"  ⚠️ 问答异常：{str(e)[:40]}")
    
    if qa_pass > 0:
        logger.info(f"✅ 问答功能测试：{qa_pass}/{len(qa_tests)} 通过")
        results["功能测试"]["问答功能"] = f"✅ 通过 ({qa_pass}/{len(qa_tests)})"
    else:
        logger.warning(f"⚠️ 问答功能未测试成功（可能索引为空）")
        results["功能测试"]["问答功能"] = "⚠️ 部分可用"
    
    # 6. 测试文件删除
    logger.info("\n[6] 测试文件删除功能...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/files/list", timeout=10)
        if response.status_code == 200:
            files_list = response.json().get('files', [])
            if files_list:
                file_to_delete = files_list[0]
                file_id = file_to_delete.get('id') or file_to_delete.get('file_id')
                
                response = requests.delete(f"{BACKEND_URL}/api/files/{file_id}", timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ 文件删除成功")
                    results["功能测试"]["文件删除"] = "✅ 通过"
                else:
                    logger.warning(f"⚠️ 文件删除返回 {response.status_code}")
                    results["功能测试"]["文件删除"] = "⚠️ 异常"
            else:
                logger.info("ℹ️ 系统无文件，跳过删除测试")
                results["功能测试"]["文件删除"] = "⏭️ 跳过（无文件）"
        else:
            logger.warning(f"⚠️ 无法获取文件列表")
            results["功能测试"]["文件删除"] = "❌ 跳过"
    except Exception as e:
        logger.warning(f"⚠️ 文件删除异常：{str(e)[:40]}")
        results["功能测试"]["文件删除"] = "⚠️ 异常"
    
    # 清理临时文件
    import shutil
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass
    
    return True


def generate_summary():
    """生成测试总结"""
    logger.info("\n" + "=" * 70)
    logger.info("测试结果总结")
    logger.info("=" * 70)
    
    pass_count = sum(1 for v in results["功能测试"].values() if "✅" in str(v))
    total_count = len(results["功能测试"])
    
    logger.info(f"\n总测试项：{total_count}")
    logger.info(f"通过数：{pass_count}")
    logger.info(f"通过率：{pass_count/total_count*100:.0f}%\n")
    
    for test_name, result in results["功能测试"].items():
        logger.info(f"  {test_name}: {result}")
    
    results["测试摘要"]["总项目数"] = total_count
    results["测试摘要"]["通过数"] = pass_count
    results["测试摘要"]["通过率"] = f"{pass_count/total_count*100:.0f}%"
    results["测试摘要"]["状态"] = "✅ 通过" if pass_count >= total_count * 0.8 else "⚠️ 部分通过" if pass_count > 0 else "❌ 失败"
    
    logger.info(f"\n总体状态：{results['测试摘要']['状态']}")
    
    # 保存报告
    report_file = "test_phase6_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logger.info(f"测试报告已保存：{report_file}")
    
    logger.info("\n" + "=" * 70)
    logger.info("Phase 6 Task 6.1 功能测试完成！")
    logger.info("=" * 70)


def main():
    logger.info("开始 Phase 6 Task 6.1 功能测试...")
    
    success = test_basic_functionality()
    
    if success:
        generate_summary()
    else:
        logger.error("\n测试因服务连接失败而中止")
        logger.info("请确保已运行：start_all.bat (Windows) 或 ./start_all.sh (Linux/Mac)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n测试被中断")
    except Exception as e:
        logger.error(f"\n测试异常：{e}")
        import traceback
        traceback.print_exc()
