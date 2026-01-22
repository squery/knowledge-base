@echo off
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

REM 安装依赖
echo [!] 检查依赖...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo [✓] 依赖安装/更新完成

REM 启动前端服务
echo.
echo [+] 启动前端服务: http://localhost:8501
echo [+] 请在浏览器中打开上述地址
echo.
echo 按 Ctrl+C 停止服务
echo.

timeout /t 2 /nobreak
start http://localhost:8501
streamlit run frontend\app.py

pause
