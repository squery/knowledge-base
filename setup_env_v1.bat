@echo off
setlocal
REM 切换到 v1 方案（FastAPI 0.99.x + pydantic 1.x，Chroma 0.4.x）

cd /d "%~dp0"
if not exist venv (
  python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements_v1.txt

echo [OK] v1 方案安装完成
endlocal
