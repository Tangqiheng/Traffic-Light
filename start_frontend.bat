@echo off
title 前端服务启动器

echo ========================================
echo   智能交通灯系统 - 前端服务启动器
echo ========================================
echo.

cd frontend

echo 检查端口占用情况...
netstat -an | findstr :5173 >nul
if %errorlevel% == 0 (
    echo 端口5173已被占用，尝试使用端口5174...
    echo.
    npm run dev -- --port 5174
) else (
    echo 端口5173可用，启动前端服务...
    echo.
    npm run dev
)

echo.
echo 服务已停止
pause