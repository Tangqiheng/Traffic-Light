#!/usr/bin/env python3
"""
Node.js 自动下载安装脚本
使用国内镜像源快速安装Node.js
"""

import os
import sys
import subprocess
import platform
import requests
from pathlib import Path

def detect_system():
    """检测系统信息"""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    print(f"系统信息: {system} {arch}")
    
    # 确定下载链接
    if system == "windows":
        if "64" in arch or "amd64" in arch:
            return "win-x64"
        else:
            return "win-x86"
    elif system == "darwin":  # macOS
        return "darwin-x64"
    else:  # Linux
        if "64" in arch:
            return "linux-x64"
        else:
            return "linux-x86"

def download_nodejs(arch_type):
    """从淘宝镜像下载Node.js"""
    print("🔍 从淘宝镜像下载Node.js...")
    
    # 获取最新版本信息
    try:
        version_url = "https://npmmirror.com/mirrors/node/index.json"
        response = requests.get(version_url, timeout=10)
        versions = response.json()
        
        # 获取最新稳定版本
        latest_version = None
        for version_info in versions:
            if version_info.get('lts'):  # 获取最新的LTS版本
                latest_version = version_info['version']
                break
        
        if not latest_version:
            latest_version = versions[0]['version']  # 获取第一个版本
            
        print(f"_latest版本: {latest_version}")
        
    except Exception as e:
        print(f"获取版本信息失败: {e}")
        latest_version = "v20.10.0"  # 默认版本
        print(f"使用默认版本: {latest_version}")
    
    # 构造下载链接
    base_url = "https://npmmirror.com/mirrors/node"
    if arch_type == "win-x64":
        download_url = f"{base_url}/{latest_version}/node-{latest_version}-win-x64.zip"
        filename = f"node-{latest_version}-win-x64.zip"
    elif arch_type == "win-x86":
        download_url = f"{base_url}/{latest_version}/node-{latest_version}-win-x86.zip"
        filename = f"node-{latest_version}-win-x86.zip"
    else:
        print(f"暂不支持的架构: {arch_type}")
        return None
    
    print(f"下载地址: {download_url}")
    
    # 下载文件
    try:
        print("开始下载...")
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"\r下载进度: {progress:.1f}%", end='')
        
        print(f"\n✅ 下载完成: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None

def extract_and_install(zip_filename):
    """解压并安装Node.js"""
    print("📦 解压Node.js...")
    
    try:
        import zipfile
        
        # 解压到指定目录
        extract_dir = "nodejs"
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        print(f"✅ 解压完成到: {extract_dir}")
        
        # 获取解压后的实际目录名
        extracted_folders = [f for f in os.listdir(extract_dir) if os.path.isdir(os.path.join(extract_dir, f))]
        if extracted_folders:
            node_folder = os.path.join(extract_dir, extracted_folders[0])
            node_exe = os.path.join(node_folder, "node.exe")
            npm_exe = os.path.join(node_folder, "npm.cmd")
            
            print(f"Node.js路径: {node_exe}")
            print(f"NPM路径: {npm_exe}")
            
            # 测试安装
            test_installation(node_exe, npm_exe)
            
            # 添加到环境变量提示
            print("\n💡 安装提示:")
            print(f"请将以下路径添加到系统PATH环境变量:")
            print(f"  {node_folder}")
            print(f"\n或者临时使用:")
            print(f"  set PATH=%PATH%;{node_folder}")
            
            return node_folder
        else:
            print("❌ 解压目录为空")
            return None
            
    except Exception as e:
        print(f"❌ 解压失败: {e}")
        return None

def test_installation(node_path, npm_path):
    """测试Node.js和NPM安装"""
    print("\n🧪 测试安装...")
    
    try:
        # 测试Node.js
        result = subprocess.run([node_path, "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Node.js版本: {result.stdout.strip()}")
        else:
            print(f"❌ Node.js测试失败: {result.stderr}")
            
        # 测试NPM
        result = subprocess.run([npm_path, "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ NPM版本: {result.stdout.strip()}")
        else:
            print(f"❌ NPM测试失败: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    print("=" * 50)
    print("Node.js 自动安装程序 (国内镜像)")
    print("=" * 50)
    
    # 检测系统架构
    arch_type = detect_system()
    
    # 下载Node.js
    zip_file = download_nodejs(arch_type)
    if not zip_file:
        return
    
    # 解压安装
    install_path = extract_and_install(zip_file)
    if install_path:
        print(f"\n🎉 Node.js安装成功!")
        print(f"安装路径: {install_path}")
        print(f"现在可以运行: npm install 来安装前端依赖")
    else:
        print(f"\n❌ 安装失败")

if __name__ == "__main__":
    main()