#!/usr/bin/env python3
"""
快速API修复脚本
自动检测并修复登录接口不可用的问题
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_backend_running():
    """检查后端是否正在运行"""
    try:
        response = requests.get("http://localhost:8000/", timeout=3)
        return response.status_code == 200
    except:
        return False

def start_backend_service():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # 设置环境变量
    env = os.environ.copy()
    env['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    
    try:
        # 启动后端进程
        process = subprocess.Popen([
            sys.executable, "app.py"
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("等待服务启动...")
        time.sleep(3)
        
        # 验证服务是否启动成功
        if check_backend_running():
            print("✅ 后端服务启动成功!")
            print("API地址: http://localhost:8000")
            return process
        else:
            print("❌ 后端服务启动失败")
            # 尝试读取错误信息
            try:
                stderr = process.stderr.read().decode('utf-8', errors='ignore')
                if stderr:
                    print(f"错误信息: {stderr[:200]}")
            except:
                pass
            return None
            
    except Exception as e:
        print(f"❌ 启动后端服务异常: {e}")
        return None

def test_login_endpoint():
    """测试登录端点"""
    print("\n🧪 测试登录接口...")
    
    try:
        # 发送空数据测试登录接口是否存在
        response = requests.post(
            "http://localhost:8000/api/auth/login",
            json={},
            timeout=5
        )
        
        if response.status_code in [400, 401]:  # 空数据应该返回400或401
            print("✅ 登录接口存在且可访问")
            return True
        else:
            print(f"❌ 登录接口异常: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到登录接口")
        return False
    except Exception as e:
        print(f"❌ 测试登录接口异常: {e}")
        return False

def main():
    print("=" * 50)
    print("快速API修复程序")
    print("=" * 50)
    
    # 检查后端服务状态
    if check_backend_running():
        print("✅ 后端服务已在运行")
    else:
        print("❌ 后端服务未运行")
        # 尝试启动后端服务
        backend_process = start_backend_service()
        if not backend_process:
            print("\n❌ 无法启动后端服务")
            print("请手动检查:")
            print("1. 确保在项目根目录运行")
            print("2. 检查backend/app.py文件是否存在")
            print("3. 确认Python环境正常")
            return
    
    # 测试登录接口
    if test_login_endpoint():
        print("\n🎉 登录接口正常工作!")
        print("\n现在可以正常登录系统:")
        print("🌐 前端地址: http://localhost:5173")
        print("🔧 后端API: http://localhost:8000")
        print("👤 默认账户: admin / admin123")
    else:
        print("\n❌ 登录接口仍有问题")
        print("建议检查:")
        print("1. backend/app.py中的路由配置")
        print("2. 数据库连接状态")
        print("3. 必要的依赖包是否安装")

if __name__ == "__main__":
    main()