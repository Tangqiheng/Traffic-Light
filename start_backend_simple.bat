@echo off
title 智能交通灯系统 - 后端服务

echo ========================================
echo   智能交通灯系统 - 后端服务启动器
echo ========================================
echo.

cd backend

echo 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python环境
    pause
    exit /b 1
)

echo.
echo 检查必要依赖...
python -c "import fastapi, uvicorn, sqlalchemy, jwt" 2>nul
if errorlevel 1 (
    echo 检测到缺失依赖，正在安装...
    cd ..
    python install_deps_china.py
    cd backend
)

echo.
echo 启动FastAPI后端服务...
echo 地址: http://localhost:8001
echo API文档: http://localhost:8001/docs
echo.

python simple_server.py

echo.
echo 服务已停止
pause