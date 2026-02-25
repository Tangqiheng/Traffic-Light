@echo off
title 智能交通灯系统 - 前端服务

echo ========================================
echo   智能交通灯系统 - 前端服务启动器
echo ========================================
echo.

cd frontend

echo 设置npm国内镜像源...
npm config set registry https://registry.npmmirror.com

echo.
echo 检查依赖...
if not exist "node_modules" (
    echo 检测到缺失依赖，正在安装...
    npm install
)

echo.
echo 检查端口占用情况...
netstat -an | findstr :5174 >nul
if %errorlevel% == 0 (
    echo 端口5174已被占用
    echo 尝试使用其他端口...
    npm run dev -- --port 5175
) else (
    echo 端口5174可用，启动前端服务...
    npm run dev
)

echo.
echo 服务已停止
pause