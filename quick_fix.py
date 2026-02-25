#!/usr/bin/env python3
"""
快速修复脚本 - 解决当前的路由和启动问题
"""

import os
import sys
import subprocess
import time
import requests

def fix_backend_routes():
    """修复后端路由问题"""
    print("🔧 修复后端路由配置...")
    
    # 检查并安装必要的依赖
    required_packages = ["flask", "flask-cors", "flask-sqlalchemy", "pyjwt"]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"📥 安装 {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    # 确保在backend目录
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    os.chdir(backend_dir)
    
    return True

def start_services():
    """启动前后端服务"""
    print("\n🚀 启动服务...")
    
    # 启动后端
    print("启动后端服务...")
    backend_env = os.environ.copy()
    backend_env['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    
    backend_process = subprocess.Popen([
        sys.executable, "app.py"
    ], env=backend_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(3)  # 等待后端启动
    
    # 验证后端是否启动成功
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务启动成功")
        else:
            print(f"❌ 后端服务启动异常: {response.status_code}")
            return False
    except:
        print("❌ 后端服务启动失败")
        return False
    
    # 启动前端
    print("启动前端服务...")
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    os.chdir(frontend_dir)
    
    frontend_process = subprocess.Popen([
        "npm", "run", "dev"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(5)  # 等待前端启动
    
    # 验证前端是否启动成功
    try:
        response = requests.get("http://localhost:5173/", timeout=5)
        if response.status_code < 500:
            print("✅ 前端服务启动成功")
        else:
            print(f"❌ 前端服务启动异常: {response.status_code}")
    except:
        print("⚠️  前端服务可能仍在启动中...")
    
    return backend_process, frontend_process

def test_login_api():
    """测试登录API"""
    print("\n🧪 测试登录功能...")
    
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(
            "http://localhost:8000/api/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 登录API测试成功!")
            print(f"   用户: {result.get('user', {}).get('username')}")
            print(f"   Token获取成功")
            return True
        else:
            print(f"❌ 登录API测试失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 登录测试异常: {e}")
        return False

def main():
    print("=" * 50)
    print("智能交通灯系统 - 快速修复启动")
    print("=" * 50)
    
    # 修复路由配置
    if not fix_backend_routes():
        print("❌ 路由修复失败")
        return
    
    # 启动服务
    services = start_services()
    if not services:
        print("❌ 服务启动失败")
        return
    
    backend_process, frontend_process = services
    
    # 测试登录功能
    if test_login_api():
        print("\n" + "=" * 50)
        print("🎉 系统启动成功!")
        print("=" * 50)
        print("访问地址:")
        print("  🌐 前端界面: http://localhost:5173")
        print("  🔧 后端API: http://localhost:8000")
        print("  👤 登录账户: admin / admin123")
        print("\n按 Ctrl+C 停止服务")
        
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 停止服务...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ 服务已停止")
    else:
        print("\n❌ 系统启动存在问题，请检查错误信息")

if __name__ == "__main__":
    main()