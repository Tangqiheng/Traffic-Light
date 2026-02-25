#!/usr/bin/env python3
"""
后端专用启动脚本 - 专注启动和测试后端服务
跳过前端依赖检查，直接启动后端并验证功能
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def start_backend_service():
    """启动后端服务并验证"""
    print("🚀 启动后端服务...")
    
    # 切换到backend目录
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # 设置环境变量避免OpenMP冲突
    env = os.environ.copy()
    env['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    
    try:
        # 启动后端服务
        print("正在启动Flask后端服务...")
        backend_process = subprocess.Popen([
            sys.executable, "app.py"
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("等待服务启动...")
        time.sleep(3)  # 等待服务启动
        
        # 检查服务是否正常运行
        try:
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code == 200:
                print("✅ 后端服务启动成功!")
                print(f"服务信息: {response.json()}")
                return backend_process
            else:
                print(f"❌ 后端服务异常: {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ 无法连接到后端服务: {e}")
            
    except Exception as e:
        print(f"❌ 后端服务启动失败: {e}")
    
    return None

def test_backend_apis():
    """测试后端核心API功能"""
    print("\n🧪 测试后端API功能...")
    
    # 测试根路径
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ 根路径访问正常")
        else:
            print(f"❌ 根路径异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 根路径测试失败: {e}")
    
    # 测试登录API
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
            print(f"   访问令牌: {result.get('access_token', '')[:30]}...")
        else:
            print(f"❌ 登录API测试失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 登录API测试异常: {e}")
    
    # 测试交通数据API
    try:
        response = requests.get(
            "http://localhost:8000/api/traffic/overview/intersection_001",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 交通数据API测试成功!")
            print(f"   数据字段: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        else:
            print(f"❌ 交通数据API测试失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 交通数据API测试异常: {e}")

def main():
    print("=" * 50)
    print("智能交通灯系统 - 后端专用启动")
    print("=" * 50)
    
    # 启动后端服务
    backend_process = start_backend_service()
    
    if backend_process:
        # 测试API功能
        test_backend_apis()
        
        print("\n" + "=" * 50)
        print("🎉 后端服务启动完成!")
        print("=" * 50)
        print("后端服务信息:")
        print("  🔧 API地址: http://localhost:8000")
        print("  📚 API文档: http://localhost:8000/")
        print("  👤 默认账户: admin / admin123")
        print("\nAPI测试端点:")
        print("  POST /api/auth/login - 用户登录")
        print("  GET  /api/traffic/overview/{id} - 交通概况")
        print("  GET  /api/traffic/status/{id} - 交通状态")
        print("\n按 Ctrl+C 停止服务")
        
        try:
            # 保持服务运行
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 正在停止后端服务...")
            backend_process.terminate()
            print("✅ 后端服务已停止")
    else:
        print("\n❌ 后端服务启动失败，请检查错误信息")

if __name__ == "__main__":
    main()