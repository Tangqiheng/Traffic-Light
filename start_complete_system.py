#!/usr/bin/env python3
"""
完整系统启动脚本
自动启动前后端服务并验证系统状态
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

class SystemLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_process = None
        self.frontend_process = None
        self.simulator_process = None
    
    def start_backend(self):
        """启动后端服务"""
        print("🚀 启动后端服务...")
        backend_dir = self.project_root / "backend"
        os.chdir(backend_dir)
        # 设置环境变量
        env = os.environ.copy()
        env['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, "app.py"
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("等待后端服务启动...")
            time.sleep(3)
            # 验证后端是否启动成功
            try:
                response = requests.get("http://localhost:8000/", timeout=5)
                if response.status_code == 200:
                    print("✅ 后端服务启动成功!")
                    return True
                else:
                    print(f"❌ 后端服务启动异常: {response.status_code}")
                    return False
            except:
                print("❌ 后端服务启动失败")
                return False
        except Exception as e:
            print(f"❌ 启动后端服务异常: {e}")
            return False

    def start_simulator(self):
        """启动交通数据模拟器"""
        print("\n🚦 启动交通数据模拟器...")
        simulator_path = self.project_root / "backend" / "simple_simulator.py"
        try:
            self.simulator_process = subprocess.Popen([
                sys.executable, str(simulator_path)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ 模拟器已启动!")
            return True
        except Exception as e:
            print(f"❌ 启动模拟器异常: {e}")
            return False
    
    def start_frontend(self):
        """启动前端服务"""
        print("\n🚀 启动前端服务...")
        
        frontend_dir = self.project_root / "frontend"
        os.chdir(frontend_dir)
        
        try:
            # 检查端口5173是否被占用
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 5173))
            sock.close()
            
            if result == 0:
                print("端口5173已被占用，使用端口5174...")
                self.frontend_process = subprocess.Popen([
                    "npm", "run", "dev", "--", "--port", "5174"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                frontend_url = "http://localhost:5174"
            else:
                print("使用端口5173...")
                self.frontend_process = subprocess.Popen([
                    "npm", "run", "dev"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                frontend_url = "http://localhost:5173"
            
            print("等待前端服务启动...")
            time.sleep(5)
            
            # 验证前端是否启动成功
            try:
                response = requests.get(frontend_url, timeout=5)
                if response.status_code < 500:
                    print("✅ 前端服务启动成功!")
                    return frontend_url
                else:
                    print(f"❌ 前端服务启动异常: {response.status_code}")
                    return None
            except:
                print("⚠️  前端服务可能仍在启动中...")
                return frontend_url
                
        except Exception as e:
            print(f"❌ 启动前端服务异常: {e}")
            return None
    
    def test_system_functionality(self):
        """测试系统核心功能"""
        print("\n🧪 测试系统核心功能...")
        
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
                print("✅ 登录功能正常")
                print(f"   用户: {result.get('user', {}).get('username')}")
                return True
            else:
                print(f"❌ 登录功能异常: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 登录功能测试异常: {e}")
            return False
    
    def run(self):
        """运行完整启动流程"""
        print("=" * 60)
        print("智能交通灯控制系统 - 完整启动程序")
        print("=" * 60)
        
        # 启动后端
        if not self.start_backend():
            print("❌ 后端服务启动失败，程序退出")
            return

        # 启动模拟器
        self.start_simulator()

        # 启动前端
        frontend_url = self.start_frontend()
        if not frontend_url:
            print("❌ 前端服务启动失败")

        # 测试功能
        if self.test_system_functionality():
            print("\n" + "=" * 60)
            print("🎉 系统启动完成!")
            print("=" * 60)
            print("系统访问信息:")
            print(f"  🌐 前端界面: {frontend_url or 'http://localhost:5173'}")
            print("  🔧 后端API: http://localhost:8000")
            print("  👤 登录账户: admin / admin123")
            print("\n按 Ctrl+C 停止所有服务")

            try:
                # 保持服务运行
                if self.backend_process:
                    self.backend_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 正在停止服务...")
                if self.backend_process:
                    self.backend_process.terminate()
                if self.frontend_process:
                    self.frontend_process.terminate()
                if self.simulator_process:
                    self.simulator_process.terminate()
                print("✅ 服务已停止")
        else:
            print("\n❌ 系统功能测试失败")

def main():
    launcher = SystemLauncher()
    launcher.run()

if __name__ == "__main__":
    main()