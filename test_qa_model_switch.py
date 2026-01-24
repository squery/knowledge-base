#!/usr/bin/env python3
"""
测试 QA 接口模型切换和中文回答优化
- 测试 mT5-XLSum（summarization）与模板回退
- 验证中文提示词生成的回答质量
"""
import sys
import json
import requests
from pathlib import Path

# 添加后端路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from config import settings

BASE_URL = "http://127.0.0.1:8010"  # 调整为当前启动端口

def test_qa_api():
    """测试 QA API 接口"""
    print("\n========== QA API 接口测试 ==========\n")
    
    # 测试问题
    test_questions = [
        "什么是 Python？",
        "如何使用向量数据库？",
        "知识库系统有什么功能？",
    ]
    
    print(f"当前 LLM 配置:")
    print(f"  - 模型: {settings.LLM_MODEL_NAME}")
    print(f"  - 管线: {settings.LLM_PIPELINE}")
    print(f"  - 最大令牌数: {settings.MAX_TOKENS}")
    print(f"  - 默认启用 LLM: {settings.USE_LLM_QA}\n")
    
    for question in test_questions:
        print(f"\n【问题】{question}")
        print("-" * 60)
        
        # 测试1: 模板回退 (use_llm=false)
        print("✓ 测试模板回退 (use_llm=false):")
        try:
            payload = {
                "question": question,
                "top_k": 3,
                "max_tokens": 128,
                "use_llm": False
            }
            response = requests.post(f"{BASE_URL}/api/qa/ask", json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"  答案: {result['answer'][:100]}...")
                print(f"  来源数: {len(result['sources'])}")
            else:
                print(f"  错误: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  异常: {e}")
        
        # 测试2: LLM 生成 (use_llm=true)
        print("\n✓ 测试 LLM 生成 (use_llm=true):")
        try:
            payload = {
                "question": question,
                "top_k": 3,
                "max_tokens": 128,
                "use_llm": True
            }
            response = requests.post(f"{BASE_URL}/api/qa/ask", json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                print(f"  答案: {result['answer'][:100]}...")
                print(f"  来源数: {len(result['sources'])}")
            else:
                print(f"  错误: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  异常: {e}")
        
        print()

def test_health():
    """测试健康检查"""
    print("========== 健康检查 ==========\n")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 后端健康状态: {data['status']}")
            print(f"  应用: {data['app_name']}")
            print(f"  版本: {data['version']}")
        else:
            print(f"✗ 后端响应错误: {response.status_code}")
    except Exception as e:
        print(f"✗ 无法连接后端: {e}")
        print(f"  请确保后端运行在 {BASE_URL}")
        return False
    return True

if __name__ == "__main__":
    if test_health():
        test_qa_api()
    else:
        print("\n后端未运行，请先启动后端")
        sys.exit(1)
