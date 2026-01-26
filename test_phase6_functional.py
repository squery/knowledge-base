"""
Phase 6 功能测试脚本
全面测试系统的文件上传、索引、问答、删除等核心功能
"""
import os
import sys
import time
import json
import tempfile
import requests
from pathlib import Path
from datetime import datetime

# 添加后端路径到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.logger_config import get_logger

logger = get_logger(__name__)

# API 配置
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"

# 测试结果记录
test_results = {
    "测试时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "总体状态": "进行中",
    "任务": {
        "文件上传": {"状态": "未测试", "结果": []},
        "自动索引": {"状态": "未测试", "结果": []},
        "问答功能": {"状态": "未测试", "结果": []},
        "文件删除": {"状态": "未测试", "结果": []},
    }
}


def check_backend_health():
    """检查后端健康状态"""
    logger.info("=" * 60)
    logger.info("检查后端服务健康状态...")
    logger.info("=" * 60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ 后端服务运行正常")
            return True
        else:
            logger.error(f"❌ 后端服务异常，状态码：{response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ 无法连接到后端服务，请确保后端已启动（端口8000）")
        return False
    except Exception as e:
        logger.error(f"❌ 检查后端健康状态失败：{e}")
        return False


def check_frontend_health():
    """检查前端健康状态"""
    logger.info("=" * 60)
    logger.info("检查前端服务健康状态...")
    logger.info("=" * 60)
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            logger.info("✅ 前端服务运行正常")
            return True
        else:
            logger.error(f"❌ 前端服务异常，状态码：{response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ 无法连接到前端服务，请确保前端已启动（端口8501）")
        return False
    except Exception as e:
        logger.error(f"❌ 检查前端健康状态失败：{e}")
        return False


def test_file_upload():
    """Task 6.1.1: 测试文件上传功能"""
    logger.info("\n" + "=" * 60)
    logger.info("Task 6.1.1: 测试文件上传功能")
    logger.info("=" * 60)
    
    results = []
    
    # 创建临时测试文件
    temp_dir = tempfile.mkdtemp(prefix="phase6_test_")
    logger.info(f"创建临时测试目录：{temp_dir}")
    
    test_files = {
        "test_single.txt": "这是一个测试文本文件。\n包含多个句子用于测试文件上传功能。\n系统应该正确处理这个文件。",
        "test_doc.md": "# 测试 Markdown 文件\n\n## 功能模块\n- 文件上传\n- 索引建立\n- 智能问答\n- 文件管理",
        "test_code.py": "def hello_world():\n    print('Hello, World!')\n\ndef add(a, b):\n    return a + b",
    }
    
    # 测试1: 单文件上传
    logger.info("\n[测试1] 单文件上传")
    test_file = os.path.join(temp_dir, "test_single.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_files["test_single.txt"])
    
    try:
        with open(test_file, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{BACKEND_URL}/api/files/upload", files=files, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ 单文件上传成功")
            logger.info(f"   文件ID：{data.get('file_id', 'N/A')}")
            logger.info(f"   文件名：{data.get('filename', 'N/A')}")
            results.append({"测试": "单文件上传", "状态": "✅ 通过", "细节": str(data)})
        else:
            logger.error(f"❌ 单文件上传失败，状态码：{response.status_code}")
            results.append({"测试": "单文件上传", "状态": "❌ 失败", "错误": response.text})
    except Exception as e:
        logger.error(f"❌ 单文件上传异常：{e}")
        results.append({"测试": "单文件上传", "状态": "❌ 异常", "错误": str(e)})
    
    # 测试2: 批量上传
    logger.info("\n[测试2] 批量文件上传")
    try:
        files_to_upload = []
        for filename, content in list(test_files.items())[:2]:
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            files_to_upload.append(("files", open(filepath, "rb")))
        
        response = requests.post(f"{BACKEND_URL}/api/files/upload_batch", files=files_to_upload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ 批量文件上传成功")
            logger.info(f"   上传文件数：{len(data.get('files', []))}")
            results.append({"测试": "批量文件上传", "状态": "✅ 通过", "上传数": len(data.get('files', []))})
        else:
            logger.error(f"❌ 批量文件上传失败，状态码：{response.status_code}")
            results.append({"测试": "批量文件上传", "状态": "❌ 失败", "错误": response.text})
    except Exception as e:
        logger.error(f"❌ 批量文件上传异常：{e}")
        results.append({"测试": "批量文件上传", "状态": "❌ 异常", "错误": str(e)})
    
    # 测试3: 文件列表查询
    logger.info("\n[测试3] 文件列表查询")
    try:
        response = requests.get(f"{BACKEND_URL}/api/files/list", timeout=10)
        if response.status_code == 200:
            data = response.json()
            file_count = len(data.get('files', []))
            logger.info(f"✅ 文件列表查询成功")
            logger.info(f"   当前文件总数：{file_count}")
            results.append({"测试": "文件列表查询", "状态": "✅ 通过", "文件数": file_count})
        else:
            logger.error(f"❌ 文件列表查询失败，状态码：{response.status_code}")
            results.append({"测试": "文件列表查询", "状态": "❌ 失败", "错误": response.text})
    except Exception as e:
        logger.error(f"❌ 文件列表查询异常：{e}")
        results.append({"测试": "文件列表查询", "状态": "❌ 异常", "错误": str(e)})
    
    # 清理
    import shutil
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass
    
    # 更新测试结果
    test_results["任务"]["文件上传"]["结果"] = results
    pass_count = len([r for r in results if "✅" in r["状态"]])
    test_results["任务"]["文件上传"]["状态"] = f"✅ 通过 ({pass_count}/{len(results)})" if pass_count > 0 else "❌ 失败"
    
    logger.info(f"\n文件上传测试总结：{pass_count}/{len(results)} 通过")
    return test_results["任务"]["文件上传"]["状态"]


def test_auto_indexing():
    """Task 6.1.2: 测试自动索引功能"""
    logger.info("\n" + "=" * 60)
    logger.info("Task 6.1.2: 测试自动索引功能")
    logger.info("=" * 60)
    
    results = []
    
    # 测试1: 检查索引状态
    logger.info("\n[测试1] 索引状态查询")
    try:
        response = requests.get(f"{BACKEND_URL}/api/indexes/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ 索引状态查询成功")
            logger.info(f"   已索引文件数：{data.get('indexed_files', 0)}")
            logger.info(f"   待索引文件数：{data.get('pending_files', 0)}")
            logger.info(f"   索引失败数：{data.get('failed_files', 0)}")
            results.append({"测试": "索引状态查询", "状态": "✅ 通过", "详情": data})
        else:
            logger.error(f"❌ 索引状态查询失败，状态码：{response.status_code}")
            results.append({"测试": "索引状态查询", "状态": "❌ 失败", "错误": response.text})
    except Exception as e:
        logger.error(f"❌ 索引状态查询异常：{e}")
        results.append({"测试": "索引状态查询", "状态": "❌ 异常", "错误": str(e)})
    
    # 测试2: 等待索引完成
    logger.info("\n[测试2] 等待索引完成（最多30秒）")
    max_wait = 30
    wait_start = time.time()
    
    try:
        while time.time() - wait_start < max_wait:
            response = requests.get(f"{BACKEND_URL}/api/indexes/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                pending = data.get('pending_files', 0)
                if pending == 0:
                    logger.info(f"✅ 所有文件索引完成")
                    results.append({"测试": "索引完成等待", "状态": "✅ 通过", "耗时": f"{time.time() - wait_start:.1f}秒"})
                    break
                else:
                    logger.info(f"   待索引文件数：{pending}，等待中...")
                    time.sleep(2)
            else:
                raise Exception(f"状态码：{response.status_code}")
        else:
            logger.warning(f"⚠️ 索引等待超时（30秒）")
            results.append({"测试": "索引完成等待", "状态": "⚠️ 超时", "详情": "等待超过30秒"})
    except Exception as e:
        logger.error(f"❌ 索引等待异常：{e}")
        results.append({"测试": "索引完成等待", "状态": "❌ 异常", "错误": str(e)})
    
    # 更新测试结果
    test_results["任务"]["自动索引"]["结果"] = results
    pass_count = len([r for r in results if "✅" in r["状态"]])
    test_results["任务"]["自动索引"]["状态"] = f"✅ 通过 ({pass_count}/{len(results)})" if pass_count > 0 else "❌ 失败"
    
    logger.info(f"\n自动索引测试总结：{pass_count}/{len(results)} 通过")
    return test_results["任务"]["自动索引"]["状态"]


def test_qa_functionality():
    """Task 6.1.3: 测试问答功能"""
    logger.info("\n" + "=" * 60)
    logger.info("Task 6.1.3: 测试问答功能")
    logger.info("=" * 60)
    
    results = []
    
    # 测试问题
    test_queries = [
        "什么是知识库系统",
        "如何上传文件",
        "系统支持哪些文件类型",
        "问答功能如何工作",
    ]
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n[测试{i}] 问答：'{query}'")
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/qa/ask",
                json={"question": query},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '无回答')
                sources = data.get('sources', [])
                logger.info(f"✅ 问答成功")
                logger.info(f"   问题：{query}")
                logger.info(f"   回答：{answer[:100]}..." if len(answer) > 100 else f"   回答：{answer}")
                logger.info(f"   来源数：{len(sources)}")
                results.append({
                    "测试": f"问答：{query}",
                    "状态": "✅ 通过",
                    "回答长度": len(answer),
                    "来源数": len(sources)
                })
            else:
                logger.error(f"❌ 问答失败，状态码：{response.status_code}")
                results.append({
                    "测试": f"问答：{query}",
                    "状态": "❌ 失败",
                    "错误": response.text[:100]
                })
        except Exception as e:
            logger.error(f"❌ 问答异常：{e}")
            results.append({
                "测试": f"问答：{query}",
                "状态": "❌ 异常",
                "错误": str(e)[:100]
            })
    
    # 更新测试结果
    test_results["任务"]["问答功能"]["结果"] = results
    pass_count = len([r for r in results if "✅" in r["状态"]])
    test_results["任务"]["问答功能"]["状态"] = f"✅ 通过 ({pass_count}/{len(results)})" if pass_count > 0 else "❌ 失败"
    
    logger.info(f"\n问答功能测试总结：{pass_count}/{len(results)} 通过")
    return test_results["任务"]["问答功能"]["状态"]


def test_file_deletion():
    """Task 6.1.4: 测试文件删除功能"""
    logger.info("\n" + "=" * 60)
    logger.info("Task 6.1.4: 测试文件删除功能")
    logger.info("=" * 60)
    
    results = []
    
    # 首先获取文件列表
    logger.info("\n[准备] 获取文件列表")
    try:
        response = requests.get(f"{BACKEND_URL}/api/files/list", timeout=10)
        if response.status_code != 200:
            logger.error(f"❌ 无法获取文件列表")
            results.append({"测试": "文件删除准备", "状态": "❌ 失败", "原因": "无法获取文件列表"})
            test_results["任务"]["文件删除"]["结果"] = results
            test_results["任务"]["文件删除"]["状态"] = "❌ 失败"
            return test_results["任务"]["文件删除"]["状态"]
        
        files = response.json().get('files', [])
        logger.info(f"当前系统中有 {len(files)} 个文件")
        
        if len(files) == 0:
            logger.warning("⚠️ 系统中没有文件，跳过删除测试")
            results.append({"测试": "文件删除", "状态": "⚠️ 跳过", "原因": "没有测试文件"})
        else:
            # 尝试删除第一个文件
            file_to_delete = files[0]
            file_id = file_to_delete.get('id') or file_to_delete.get('file_id')
            filename = file_to_delete.get('filename', '未知文件')
            
            logger.info(f"\n[测试] 删除文件：{filename}")
            try:
                response = requests.delete(f"{BACKEND_URL}/api/files/{file_id}", timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ 文件删除成功")
                    results.append({"测试": "单个文件删除", "状态": "✅ 通过", "文件": filename})
                else:
                    logger.error(f"❌ 文件删除失败，状态码：{response.status_code}")
                    results.append({"测试": "单个文件删除", "状态": "❌ 失败", "错误": response.text[:100]})
            except Exception as e:
                logger.error(f"❌ 文件删除异常：{e}")
                results.append({"测试": "单个文件删除", "状态": "❌ 异常", "错误": str(e)[:100]})
    
    except Exception as e:
        logger.error(f"❌ 获取文件列表异常：{e}")
        results.append({"测试": "文件删除准备", "状态": "❌ 异常", "错误": str(e)})
    
    # 更新测试结果
    test_results["任务"]["文件删除"]["结果"] = results
    pass_count = len([r for r in results if "✅" in r["状态"]])
    test_results["任务"]["文件删除"]["状态"] = f"✅ 通过 ({pass_count}/{len(results)})" if pass_count > 0 else "⚠️ 部分完成" if results else "❌ 失败"
    
    logger.info(f"\n文件删除测试总结：{pass_count}/{len(results)} 通过")
    return test_results["任务"]["文件删除"]["状态"]


def generate_test_report():
    """生成测试报告"""
    logger.info("\n" + "=" * 60)
    logger.info("测试报告总结")
    logger.info("=" * 60)
    
    # 统计总体结果
    total_tests = sum(len(task["结果"]) for task in test_results["任务"].values())
    passed_tests = sum(
        len([r for r in task["结果"] if "✅" in r["状态"]])
        for task in test_results["任务"].values()
    )
    
    test_results["总体状态"] = f"✅ 完成 ({passed_tests}/{total_tests} 通过)" if passed_tests > 0 else "❌ 失败"
    
    logger.info(f"\n总测试数：{total_tests}")
    logger.info(f"通过数：{passed_tests}")
    logger.info(f"通过率：{passed_tests/total_tests*100:.1f}%")
    
    logger.info("\n各任务状态：")
    for task_name, task_data in test_results["任务"].items():
        logger.info(f"  {task_name}：{task_data['状态']}")
    
    # 保存测试报告为JSON
    report_file = os.path.join(os.path.dirname(__file__), "test_phase6_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    logger.info(f"\n测试报告已保存到：{report_file}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Phase 6 Task 6.1 功能测试完成！")
    logger.info("=" * 60)


def main():
    """主测试流程"""
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║  Phase 6 Task 6.1: 功能测试                              ║")
    logger.info("║  测试时间：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "                         ║")
    logger.info("╚" + "=" * 58 + "╝")
    
    # 检查服务健康状态
    backend_ok = check_backend_health()
    frontend_ok = check_frontend_health()
    
    if not backend_ok or not frontend_ok:
        logger.error("\n⚠️ 后端或前端服务未运行，请先启动系统！")
        logger.info("请在终端中运行：start_all.bat (Windows) 或 ./start_all.sh (Linux/Mac)")
        return
    
    logger.info("\n✅ 所有服务就绪，开始功能测试...\n")
    
    # 执行测试
    test_file_upload()
    test_auto_indexing()
    test_qa_functionality()
    test_file_deletion()
    
    # 生成报告
    generate_test_report()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n测试被用户中断")
    except Exception as e:
        logger.error(f"\n\n测试异常：{e}")
        import traceback
        traceback.print_exc()
