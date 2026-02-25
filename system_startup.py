#!/usr/bin/env python3
"""
智能交通灯控制系统 - 完整启动和检查脚本
自动检测环境、安装依赖、启动服务并验证系统状态
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

class SystemManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
    def check_python_environment(self):
        """检查Python环境"""
        print("🔍 检查Python环境...")
        print(f"Python版本: {sys.version}")
        print(f"项目路径: {self.project_root}")
        return True
    
    def install_backend_dependencies(self):
        """安装后端依赖"""
        print("\n📦 安装后端依赖...")
        os.chdir(self.backend_dir)
        
        required_packages = [
            "flask",
            "flask-cors", 
            "flask-sqlalchemy",
            "pyjwt",
            "passlib",
            "python-jose[cryptography]",
            "pymysql",
            "requests"
        ]
        
        for package in required_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} 安装成功")
            except subprocess.CalledProcessError:
                print(f"❌ {package} 安装失败")
                return False
        
        return True
    
    def install_frontend_dependencies(self):
        """安装前端依赖"""
        print("\n📦 安装前端依赖...")
        os.chdir(self.frontend_dir)
        
        try:
            # 检查npm是否可用
            subprocess.check_call(["npm", "--version"])
            print("✅ npm 可用")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ npm 未找到，请安装Node.js")
            return False
        
        try:
            # 安装前端依赖
            subprocess.check_call(["npm", "install"])
            print("✅ 前端依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ 前端依赖安装失败")
            return False
    
    def start_backend_service(self):
        """启动后端服务"""
        print("\n🚀 启动后端服务...")
        os.chdir(self.backend_dir)
        
        # 设置环境变量避免OpenMP冲突
        env = os.environ.copy()
        env['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
        
        try:
            # 启动后端服务
            backend_process = subprocess.Popen([
                sys.executable, "app.py"
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print("✅ 后端服务启动中...")
            time.sleep(3)  # 等待服务启动
            
            # 检查服务是否正常运行
            try:
                response = requests.get("http://localhost:8000/", timeout=5)
                if response.status_code == 200:
                    print("✅ 后端服务运行正常")
                    return backend_process
                else:
                    print(f"❌ 后端服务异常: {response.status_code}")
            except requests.RequestException:
                print("❌ 无法连接到后端服务")
                
        except Exception as e:
            print(f"❌ 后端服务启动失败: {e}")
        
        return None
    
    def start_frontend_service(self):
        """启动前端服务"""
        print("\n🚀 启动前端服务...")
        os.chdir(self.frontend_dir)
        
        try:
            # 启动前端开发服务器
            frontend_process = subprocess.Popen([
                "npm", "run", "dev"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print("✅ 前端服务启动中...")
            time.sleep(5)  # 等待服务启动
            
            # 检查服务是否正常运行
            try:
                response = requests.get("http://localhost:5173/", timeout=5)
                if response.status_code < 500:  # 接受2xx和4xx状态码
                    print("✅ 前端服务运行正常")
                    return frontend_process
                else:
                    print(f"❌ 前端服务异常: {response.status_code}")
            except requests.RequestException:
                print("❌ 无法连接到前端服务")
                
        except Exception as e:
            print(f"❌ 前端服务启动失败: {e}")
        
        return None
    
    def test_system_functionality(self):
        """测试系统核心功能"""
        print("\n🧪 测试系统核心功能...")
        
        # 测试后端API
        try:
            # 测试根路径
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code == 200:
                print("✅ 后端根路径访问正常")
            else:
                print(f"❌ 后端根路径异常: {response.status_code}")
            
            # 测试登录API
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
                print("✅ 登录API测试成功")
                print(f"   用户: {result.get('user', {}).get('username')}")
                print(f"   Token: {result.get('access_token', '')[:20]}...")
            else:
                print(f"❌ 登录API测试失败: {response.status_code}")
                print(f"   错误: {response.text}")
                
        except Exception as e:
            print(f"❌ 后端API测试失败: {e}")
        
        # 测试前端访问
        try:
            response = requests.get("http://localhost:5173/", timeout=5)
            if response.status_code < 500:
                print("✅ 前端页面访问正常")
            else:
                print(f"❌ 前端页面访问异常: {response.status_code}")
        except Exception as e:
            print(f"❌ 前端访问测试失败: {e}")
    
    def run_complete_setup(self):
        """运行完整的系统设置"""
        print("=" * 60)
        print("智能交通灯控制系统 - 自动化启动程序")
        print("=" * 60)
        
        # 检查环境
        if not self.check_python_environment():
            return False
        
        # 安装依赖
        if not self.install_backend_dependencies():
            print("❌ 后端依赖安装失败")
            return False
        
        if not self.install_frontend_dependencies():
            print("❌ 前端依赖安装失败")
            return False
        
        # 启动服务
        backend_process = self.start_backend_service()
        if not backend_process:
            print("❌ 后端服务启动失败")
            return False
        
        frontend_process = self.start_frontend_service()
        if not frontend_process:
            print("❌ 前端服务启动失败")
            return False
        
        # 测试功能
        self.test_system_functionality()
        
        print("\n" + "=" * 60)
        print("🎉 系统启动完成!")
        print("=" * 60)
        print("系统信息:")
        print("  🌐 前端地址: http://localhost:5173")
        print("  🔧 后端API: http://localhost:8000")
        print("  👤 默认账户: admin / admin123")
        print("\n按 Ctrl+C 停止所有服务")
        
        try:
            # 保持服务运行
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 正在停止服务...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ 服务已停止")

def main():
    manager = SystemManager()
    manager.run_complete_setup()

if __name__ == "__main__":
    main()