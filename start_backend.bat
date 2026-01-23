@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
REM 后端启动脚本 (Windows)

echo ======================================
echo 本地知识库系统 - 后端启动
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
if not exist "venv\Lib\site-packages\fastapi" (
    echo [*] 首次安装，可能需要几分钟...
    .\venv\Scripts\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
) else (
    echo [✓] 依赖已安装
)

echo.
echo ======================================
echo [✓] 依赖检查完成
echo.
echo [+] 启动后端服务: http://localhost:8000
echo [+] API文档: http://localhost:8000/docs
echo [+] 交互式文档: http://localhost:8000/redoc
echo.
echo 按 Ctrl+C 停止服务
echo ======================================
echo.

python backend\main.py

pause
