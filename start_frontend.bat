@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
REM 前端启动脚本 (Windows)

echo ======================================
echo 本地知识库系统 - 前端启动
echo ======================================
echo.

REM 检查Python版本
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装或不在PATH中
    pause
    exit /b 1
)

echo [✓] Python环境检查通过

REM 检查虚拟环境
if not exist "venv" (
    echo [!] 虚拟环境不存在，正在创建...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖 (只在venv中)
echo [!] 检查依赖...
if not exist "venv\Lib\site-packages\streamlit" (
    echo [*] 首次安装，可能需要几分钟...
    .\venv\Scripts\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
) else (
    echo [✓] 依赖已安装
)

echo.
echo ======================================
echo [✓] 依赖检查完成
echo.
echo [+] 启动前端服务: http://localhost:8501
echo [+] 请在浏览器中打开上述地址
echo.
echo 后端服务应该已启动（http://localhost:8000）
echo 按 Ctrl+C 停止服务
echo ======================================
echo.

timeout /t 2 /nobreak >nul

REM 固定端口并启动前端
streamlit run frontend\app.py --server.port 8501 --server.address 0.0.0.0

pause
