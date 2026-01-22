#!/bin/bash
# 一键启动脚本 (Linux/Mac)

echo "======================================"
echo "本地知识库系统 - 一键启动"
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
echo "[!] 检查并安装依赖..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    exit 1
fi

echo "[✓] 依赖安装/更新完成"
echo

# 启动后端
echo "[+] 启动后端服务..."
python backend/main.py > logs/backend.log 2>&1 &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo "[+] 启动前端服务..."
streamlit run frontend/app.py > logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# 等待前端启动
sleep 2

# 打开浏览器
echo "[+] 打开浏览器..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:8501 &
elif [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:8501 &
fi

echo
echo "======================================"
echo "[✓] 服务启动完成！"
echo "后端地址: http://localhost:8000"
echo "前端地址: http://localhost:8501"
echo "按 Ctrl+C 停止所有服务"
echo "======================================"
echo

# 等待用户中断
wait

# 清理进程
kill $BACKEND_PID 2>/dev/null
kill $FRONTEND_PID 2>/dev/null
