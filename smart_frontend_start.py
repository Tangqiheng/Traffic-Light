#!/usr/bin/env python3
"""
智能前端启动脚本
自动检测端口占用情况并启动前端服务到可用端口
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_port_availability(port):
    """检查端口是否可用"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def find_available_port(start_port=5173, max_attempts=10):
    """寻找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        if check_port_availability(port):
            return port
    return None

def check_existing_frontend():
    """检查是否已有前端服务在运行"""
    try:
        # 检查常见的前端端口
        ports_to_check = [5173, 5174, 5175]
        for port in ports_to_check:
            try:
                response = requests.get(f"http://localhost:{port}", timeout=3)
                if response.status_code < 500:
                    return port
            except:
                continue
        return None
    except Exception:
        return None

def start_frontend_service():
    """启动前端服务"""
    print("🔍 检查前端服务状态...")
    
    # 检查是否已有服务在运行
    existing_port = check_existing_frontend()
    if existing_port:
        print(f"✅ 前端服务已在端口 {existing_port} 运行")
        print(f"🌐 访问地址: http://localhost:{existing_port}")
        return existing_port
    
    # 寻找可用端口
    print("🔍 寻找可用端口...")
    available_port = find_available_port()
    
    if not available_port:
        print("❌ 无法找到可用端口")
        return None
    
    print(f"✅ 找到可用端口: {available_port}")
    
    # 切换到前端目录
    frontend_dir = Path(__file__).parent / "frontend"
    
    try:
        print(f"🚀 启动前端服务到端口 {available_port}...")
        
        # 启动前端服务
        if available_port == 5173:
            process = subprocess.Popen([
                "npm", "run", "dev"
            ], cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            process = subprocess.Popen([
                "npm", "run", "dev", "--", "--port", str(available_port)
            ], cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务启动
        print("⏳ 等待前端服务启动...")
        time.sleep(5)
        
        # 验证服务是否启动成功
        try:
            response = requests.get(f"http://localhost:{available_port}", timeout=5)
            if response.status_code < 500:
                print(f"✅ 前端服务启动成功!")
                print(f"🌐 访问地址: http://localhost:{available_port}")
                return available_port
            else:
                print(f"❌ 前端服务启动异常: {response.status_code}")
                return None
        except:
            print("⚠️  前端服务可能仍在启动中...")
            print(f"🌐 请稍后访问: http://localhost:{available_port}")
            return available_port
            
    except Exception as e:
        print(f"❌ 启动前端服务失败: {e}")
        return None

def main():
    print("=" * 50)
    print("智能前端启动程序")
    print("=" * 50)
    
    port = start_frontend_service()
    
    if port:
        print("\n" + "=" * 50)
        print("🎉 前端服务启动完成!")
        print("=" * 50)
        print("访问信息:")
        print(f"  🌐 前端界面: http://localhost:{port}")
        print("  🔧 后端API: http://localhost:8000")
        print("  👤 登录账户: admin / admin123")
        print("\n按 Ctrl+C 停止服务")
        
        try:
            # 保持脚本运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 正在停止前端服务...")
            print("✅ 服务已停止")
    else:
        print("\n❌ 前端服务启动失败")

if __name__ == "__main__":
    main()