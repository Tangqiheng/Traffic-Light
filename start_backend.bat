@echo off
cd /d "%~dp0"
cd backend

echo 正在启动智能交通灯控制系统后端服务...
echo ========================================

REM 激活虚拟环境（如果存在）
if exist "..\venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call ..\venv\Scripts\activate.bat
)

REM 检查并安装依赖
echo 检查必要依赖...
python -c "import fastapi, uvicorn, sqlalchemy, pydantic, jwt" 2>nul
if errorlevel 1 (
    echo 检测到缺失依赖，正在安装...
    pip install fastapi uvicorn sqlalchemy pydantic pyjwt
    if errorlevel 1 (
        echo 尝试使用完整安装脚本...
        cd ..
        python install_all_deps.py
        cd backend
    )
)

REM 启动后端服务 - 使用 simple_server.py 作为主服务
echo 启动FastAPI后端服务 (simple_server.py)...
echo 注意: 使用端口 8001
python simple_server.py

pause