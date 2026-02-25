#!/usr/bin/env python3
"""
系统状态检查脚本
验证前后端服务运行状态和连接性
"""

import requests
import time
import subprocess
import sys
from pathlib import Path

def check_backend_service():
    """检查后端服务状态"""
    print("🔍 检查后端服务...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 后端服务运行正常")
            print(f"   版本: {data.get('version', '未知')}")
            print(f"   状态: {data.get('status', '未知')}")
            return True
        else:
            print(f"❌ 后端服务异常 (状态码: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ 后端服务未运行: {e}")
        return False

def check_frontend_service():
    """检查前端服务状态"""
    print("\n🔍 检查前端服务...")
    try:
        response = requests.get("http://localhost:5173/", timeout=5)
        if response.status_code < 500:  # 接受2xx和4xx状态码
            print("✅ 前端服务运行正常")
            return True
        else:
            print(f"❌ 前端服务异常 (状态码: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ 前端服务未运行: {e}")
        return False

def test_login_api():
    """测试登录API功能"""
    print("\n🔐 测试登录API...")
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
            print(f"   用户名: {result.get('user', {}).get('username')}")
            print(f"   访问令牌: {result.get('access_token', '')[:20]}...")
            return True
        else:
            print(f"❌ 登录API测试失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 登录API测试异常: {e}")
        return False

def test_traffic_api():
    """测试交通数据API"""
    print("\n🚦 测试交通数据API...")
    try:
        response = requests.get(
            "http://localhost:8000/api/traffic/overview/intersection_001",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 交通数据API测试成功!")
            print(f"   数据字段: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
            return True
        else:
            print(f"❌ 交通数据API测试失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 交通数据API测试异常: {e}")
        return False

def start_backend_if_needed():
    """如果后端未运行则启动"""
    print("\n🚀 检查并启动后端服务...")
    
    if check_backend_service():
        print("后端服务已在运行")
        return True
    
    # 启动后端服务
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        print("正在启动后端服务...")
        env = {"KMP_DUPLICATE_LIB_OK": "TRUE"}
        process = subprocess.Popen([
            sys.executable, "app.py"
        ], cwd=backend_dir, env=env, 
           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 等待服务启动
        time.sleep(3)
        
        if check_backend_service():
            print("✅ 后端服务启动成功!")
            return process
        else:
            print("❌ 后端服务启动失败")
            return None
            
    except Exception as e:
        print(f"❌ 启动后端服务异常: {e}")
        return None

def main():
    print("=" * 50)
    print("智能交通灯系统 - 状态检查")
    print("=" * 50)
    
    # 检查各服务状态
    backend_ok = check_backend_service()
    frontend_ok = check_frontend_service()
    
    # 测试核心功能
    login_ok = test_login_api() if backend_ok else False
    traffic_ok = test_traffic_api() if backend_ok else False
    
    print("\n" + "=" * 50)
    print("📊 系统状态汇总:")
    print(f"   后端服务: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"   前端服务: {'✅ 正常' if frontend_ok else '❌ 异常'}")
    print(f"   登录功能: {'✅ 正常' if login_ok else '❌ 异常'}")
    print(f"   交通API:  {'✅ 正常' if traffic_ok else '❌ 异常'}")
    
    if all([backend_ok, frontend_ok, login_ok, traffic_ok]):
        print("\n🎉 系统完全正常运行!")
        print("\n🌐 访问地址:")
        print("   前端界面: http://localhost:5173")
        print("   后端API:  http://localhost:8000")
        print("   登录账户: admin / admin123")
    else:
        print("\n⚠️  系统存在问题，请检查上述错误信息")
        
        # 尝试启动后端服务
        if not backend_ok:
            print("\n🔧 尝试启动后端服务...")
            backend_process = start_backend_if_needed()
            if backend_process:
                print("后端服务已启动，请重新运行此脚本检查状态")

if __name__ == "__main__":
    main()