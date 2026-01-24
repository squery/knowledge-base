@echo off
setlocal
REM 切换到 v2 方案（FastAPI+pydantic v2，Chroma 0.5.x）

cd /d "%~dp0"
if not exist venv (
  python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements_v2.txt

echo [OK] v2 方案安装完成
endlocal
