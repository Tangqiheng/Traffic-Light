@echo off
title Node.js 下载器

echo ========================================
echo   Node.js 国内镜像下载器
echo ========================================
echo.

echo 正在从淘宝镜像下载Node.js...
echo.

REM 下载Node.js LTS版本
powershell -Command "Invoke-WebRequest -Uri 'https://npmmirror.com/mirrors/node/v20.10.0/node-v20.10.0-win-x64.zip' -OutFile 'node-v20.10.0-win-x64.zip'"

if exist "node-v20.10.0-win-x64.zip" (
    echo.
    echo ✅ 下载完成!
    echo.
    echo 解压文件...
    powershell -Command "Expand-Archive -Path 'node-v20.10.0-win-x64.zip' -DestinationPath '.'"
    
    echo.
    echo ✅ 解压完成!
    echo.
    echo 测试安装...
    node-v20.10.0-win-x64\node.exe --version
    node-v20.10.0-win-x64\npm.cmd --version
    
    echo.
    echo 🎉 Node.js安装成功!
    echo 安装路径: %CD%\node-v20.10.0-win-x64
    echo.
    echo 要使用npm，请运行:
    echo set PATH=%%PATH%%;%CD%\node-v20.10.0-win-x64
    echo.
) else (
    echo ❌ 下载失败，请检查网络连接
)

pause