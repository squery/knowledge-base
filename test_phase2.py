"""
Phase 2测试脚本
测试文件管理功能
"""
import requests
import json
import time
import os

API_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {str(e)}")
        return False


def test_upload_single_file():
    """测试上传单个文件"""
    print("\n=== 测试上传单个文件 ===")
    try:
        # 创建测试文件
        test_file_path = "test_document.txt"
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("这是一个测试文档。包含一些测试文本。\n")
            f.write("用于测试文件上传功能。\n")
            f.write("系统应该能够成功处理这个文件。\n")
        
        # 上传文件
        with open(test_file_path, "rb") as f:
            files = {"file": (test_file_path, f)}
            response = requests.post(f"{API_URL}/api/files/upload", files=files, timeout=10)
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # 清理
        os.remove(test_file_path)
        
        return response.status_code == 200 and result.get("success", False)
    except Exception as e:
        print(f"错误: {str(e)}")
        return False


def test_upload_batch_files():
    """测试批量上传文件"""
    print("\n=== 测试批量上传文件 ===")
    try:
        # 创建多个测试文件
        test_files = []
        for i in range(3):
            file_path = f"test_file_{i}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"这是测试文件 {i}\n")
                f.write(f"文件ID: {i}\n")
            test_files.append(file_path)
        
        # 批量上传
        files_data = []
        for file_path in test_files:
            with open(file_path, "rb") as f:
                files_data.append(("files", (file_path, f.read())))
        
        response = requests.post(
            f"{API_URL}/api/files/upload/batch",
            files=files_data,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # 清理
        for file_path in test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return response.status_code == 200 and result.get("success", False)
    except Exception as e:
        print(f"错误: {str(e)}")
        return False


def test_get_file_list():
    """测试获取文件列表"""
    print("\n=== 测试获取文件列表 ===")
    try:
        response = requests.get(f"{API_URL}/api/files/list", timeout=5)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"文件数量: {result.get('count', 0)}")
        
        # 打印前5个文件
        files = result.get('data', [])
        for i, file in enumerate(files[:5]):
            print(f"\n文件 {i+1}:")
            print(f"  ID: {file.get('id')}")
            print(f"  原始名称: {file.get('original_filename')}")
            print(f"  大小: {file.get('file_size')} 字节")
            print(f"  类型: {file.get('file_type')}")
            print(f"  索引状态: {file.get('index_status')}")
        
        return response.status_code == 200 and result.get("success", False)
    except Exception as e:
        print(f"错误: {str(e)}")
        return False


def test_get_statistics():
    """测试获取统计信息"""
    print("\n=== 测试获取统计信息 ===")
    try:
        response = requests.get(f"{API_URL}/api/files/statistics", timeout=5)
        print(f"状态码: {response.status_code}")
        result = response.json()
        stats = result.get('data', {})
        print(f"统计信息:")
        print(f"  总文件数: {stats.get('total_files', 0)}")
        print(f"  文档数: {stats.get('document_count', 0)}")
        print(f"  代码文件数: {stats.get('code_count', 0)}")
        print(f"  已索引: {stats.get('indexed_count', 0)}")
        print(f"  待索引: {stats.get('pending_count', 0)}")
        
        return response.status_code == 200 and result.get("success", False)
    except Exception as e:
        print(f"错误: {str(e)}")
        return False


def test_get_file_detail():
    """测试获取文件详情"""
    print("\n=== 测试获取文件详情 ===")
    try:
        # 先获取文件列表
        response = requests.get(f"{API_URL}/api/files/list", timeout=5)
        files = response.json().get('data', [])
        
        if not files:
            print("没有文件可用于测试")
            return False
        
        # 获取第一个文件的详情
        file_id = files[0]['id']
        response = requests.get(f"{API_URL}/api/files/{file_id}", timeout=5)
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        file_detail = result.get('data', {})
        print(f"文件详情:")
        print(f"  ID: {file_detail.get('id')}")
        print(f"  名称: {file_detail.get('original_filename')}")
        print(f"  大小: {file_detail.get('file_size')} 字节")
        print(f"  MD5: {file_detail.get('md5_hash')}")
        print(f"  上传时间: {file_detail.get('upload_time')}")
        
        return response.status_code == 200 and result.get("success", False)
    except Exception as e:
        print(f"错误: {str(e)}")
        return False


def test_delete_file():
    """测试删除文件"""
    print("\n=== 测试删除文件 ===")
    try:
        # 先上传一个文件用于删除
        test_file_path = "test_delete.txt"
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("这个文件将被删除")
        
        with open(test_file_path, "rb") as f:
            files = {"file": (test_file_path, f)}
            response = requests.post(f"{API_URL}/api/files/upload", files=files, timeout=10)
        
        file_id = response.json().get('data', {}).get('id')
        
        if not file_id:
            print("上传文件失败")
            return False
        
        print(f"上传的文件ID: {file_id}")
        
        # 删除文件
        response = requests.delete(f"{API_URL}/api/files/{file_id}", timeout=5)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # 清理
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        
        return response.status_code == 200 and result.get("success", False)
    except Exception as e:
        print(f"错误: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("=" * 50)
    print("Phase 2 - 文件管理模块测试")
    print("=" * 50)
    
    # 等待API启动
    print("\n等待API启动...")
    for i in range(10):
        try:
            requests.get(f"{API_URL}/health", timeout=2)
            print("API已就绪")
            break
        except:
            print(f"等待中... ({i+1}/10)")
            time.sleep(1)
    
    results = {
        "健康检查": test_health(),
        "上传单个文件": test_upload_single_file(),
        "批量上传文件": test_upload_batch_files(),
        "获取文件列表": test_get_file_list(),
        "获取统计信息": test_get_statistics(),
        "获取文件详情": test_get_file_detail(),
        "删除文件": test_delete_file(),
    }
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    print(f"\n总计: {passed_tests}/{total_tests} 通过")


if __name__ == "__main__":
    main()
