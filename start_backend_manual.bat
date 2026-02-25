@echo off
title 智能交通灯系统 - 后端服务启动器

echo ========================================
echo   智能交通灯控制系统后端服务启动器
echo ========================================
echo.

REM 检查是否在正确的目录
if not exist "backend\app.py" (
    echo 错误: 请在项目根目录运行此脚本
    echo 当前目录: %CD%
    pause
    exit /b 1
)

echo 1. 切换到后端目录...
cd backend

echo 2. 设置环境变量...
set KMP_DUPLICATE_LIB_OK=TRUE

echo 3. 检查Python环境...
python --version

echo 4. 启动Flask后端服务...
echo 服务将在 http://localhost:8000 上运行
echo 按 Ctrl+C 停止服务
echo.

python app.py

echo.
echo 服务已停止
pause