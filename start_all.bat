@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
REM 一键启动脚本 (Windows)

echo ======================================
echo 本地知识库系统 - 一键启动
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

REM 安装依赖 (只在venv中安装)
echo [!] 检查并安装依赖...
if not exist "venv\Lib\site-packages\fastapi" (
    echo [*] 首次安装，可能需要几分钟...
    .\venv\Scripts\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
) else (
    echo [✓] 依赖已安装
)
echo.

REM 启动后端
echo [+] 启动后端服务...
start "后端服务-FastAPI" cmd /k call venv\Scripts\activate.bat ^& python backend\main.py

REM 等待后端启动
timeout /t 4 /nobreak

REM 启动前端
echo [+] 启动前端服务...
start "前端服务-Streamlit" cmd /k call venv\Scripts\activate.bat ^& streamlit run frontend\app.py

REM 等待前端启动
timeout /t 3 /nobreak

REM 打开浏览器
echo [+] 打开浏览器...
start http://localhost:8501

echo.
echo ======================================
echo [✓] 服务启动完成！
echo 后端地址: http://localhost:8000
echo 后端文档: http://localhost:8000/docs
echo 前端地址: http://localhost:8501
echo.
echo 各个服务窗口已单独启动，可独立关闭
echo ======================================
timeout /t 5 /nobreak
