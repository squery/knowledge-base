#!/bin/bash
# 后端启动脚本 (Linux/Mac)

# 强制使用UTF-8，避免中文乱码
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export PYTHONIOENCODING=utf-8

echo "======================================"
echo "本地知识库系统 - 后端启动"
echo "======================================"
echo

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "[错误] Python3未安装"
    exit 1
fi

echo "[✓] Python环境检查通过"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[!] 虚拟环境不存在，正在创建..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "[!] 检查依赖..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    exit 1
fi

echo "[✓] 依赖安装/更新完成"

# 启动后端服务
echo
echo "[+] 启动后端服务: http://localhost:8000"
echo "[+] 文档地址: http://localhost:8000/docs"
echo
echo "按 Ctrl+C 停止服务"
echo

python backend/main.py
