"""
快速测试脚本
"""
import requests
import json
import time
import os
import sys

def test_api():
    """测试API"""
    API_URL = "http://localhost:8000"
    
    print("\n=== 1. 测试健康检查 ===")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"✅ 状态码: {response.status_code}")
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False
    
    print("\n=== 2. 测试统计信息 ===")
    try:
        response = requests.get(f"{API_URL}/api/files/statistics", timeout=5)
        print(f"✅ 状态码: {response.status_code}")
        result = response.json()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False
    
    print("\n=== 3. 测试上传单个文件 ===")
    try:
        # 创建测试文件
        test_file = "test_doc.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("这是一个测试文档。")
        
        # 上传
        with open(test_file, "rb") as f:
            files = {"file": (test_file, f)}
            response = requests.post(f"{API_URL}/api/files/upload", files=files, timeout=10)
        
        print(f"✅ 状态码: {response.status_code}")
        result = response.json()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        os.remove(test_file)
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False
    
    print("\n=== 4. 测试获取文件列表 ===")
    try:
        response = requests.get(f"{API_URL}/api/files/list", timeout=5)
        print(f"✅ 状态码: {response.status_code}")
        result = response.json()
        print(f"文件数: {result.get('count', 0)}")
        if result.get('data'):
            print(f"第一个文件: {result['data'][0].get('original_filename')}")
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("等待API启动...")
    time.sleep(2)
    test_api()
