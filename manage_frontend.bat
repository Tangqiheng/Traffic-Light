@echo off
title 前端服务管理器

echo ========================================
echo   智能交通灯系统 - 前端服务管理器
echo ========================================
echo.

:menu
echo 请选择操作:
echo 1. 检查前端服务状态
echo 2. 启动前端服务
echo 3. 停止前端服务
echo 4. 退出
echo.

set /p choice=请输入选项 (1-4): 

if "%choice%"=="1" goto check_status
if "%choice%"=="2" goto start_service
if "%choice%"=="3" goto stop_service
if "%choice%"=="4" goto exit_script
goto menu

:check_status
echo.
echo 🔍 检查端口占用情况...
echo.

rem 检查常见前端端口
echo 检查端口 5173:
netstat -an | findstr :5173
if %errorlevel% == 0 (
    echo ✅ 端口 5173 正在使用
    echo 测试服务访问...
    powershell -Command "try { $resp = Invoke-WebRequest -Uri 'http://localhost:5173' -TimeoutSec 3; Write-Host '✅ 服务正常运行' } catch { Write-Host '❌ 服务异常或无法访问' }"
) else (
    echo ❌ 端口 5173 未被使用
)

echo.
echo 检查端口 5174:
netstat -an | findstr :5174
if %errorlevel% == 0 (
    echo ✅ 端口 5174 正在使用
    echo 测试服务访问...
    powershell -Command "try { $resp = Invoke-WebRequest -Uri 'http://localhost:5174' -TimeoutSec 3; Write-Host '✅ 服务正常运行' } catch { Write-Host '❌ 服务异常或无法访问' }"
) else (
    echo ❌ 端口 5174 未被使用
)

echo.
echo 检查端口 5175:
netstat -an | findstr :5175
if %errorlevel% == 0 (
    echo ✅ 端口 5175 正在使用
    echo 测试服务访问...
    powershell -Command "try { $resp = Invoke-WebRequest -Uri 'http://localhost:5175' -TimeoutSec 3; Write-Host '✅ 服务正常运行' } catch { Write-Host '❌ 服务异常或无法访问' }"
) else (
    echo ❌ 端口 5175 未被使用
)

echo.
goto menu

:start_service
echo.
echo 🚀 启动前端服务...
echo.

cd frontend

rem 检查端口5173是否被占用
netstat -an | findstr :5173 >nul
if %errorlevel% == 0 (
    echo 端口5173已被占用，检查端口5174...
    netstat -an | findstr :5174 >nul
    if %errorlevel% == 0 (
        echo 端口5174也被占用，使用端口5175...
        npm run dev -- --port 5175
    ) else (
        echo 使用端口5174...
        npm run dev -- --port 5174
    )
) else (
    echo 使用端口5173...
    npm run dev
)

goto menu

:stop_service
echo.
echo 🛑 停止前端服务...
echo.

echo 查找并终止Node.js进程...
taskkill /f /im node.exe 2>nul
if %errorlevel% == 0 (
    echo ✅ Node.js进程已终止
) else (
    echo ❌ 未找到Node.js进程
)

echo.
goto menu

:exit_script
echo.
echo 感谢使用前端服务管理器!
pause
exit