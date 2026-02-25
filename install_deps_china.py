#!/usr/bin/env python3
"""
使用国内镜像源安装项目依赖
"""
import subprocess
import sys
import os

def run_command(cmd, description=""):
    """执行命令并显示结果"""
    print(f"\n{'='*50}")
    print(f"正在执行: {description}")
    print(f"命令: {cmd}")
    print('='*50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print("✅ 成功!")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ 失败!")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        return False

def main():
    print("🚀 智能交通灯系统 - 国内镜像源依赖安装")
    print("="*60)
    
    # 检查是否在虚拟环境中
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if not in_venv:
        print("⚠️  建议在虚拟环境中运行此脚本")
        print("可以先创建虚拟环境:")
        print("  python -m venv venv")
        print("  venv\\Scripts\\activate  # Windows")
        input("\n按回车键继续或Ctrl+C退出...")
    
    # 设置国内pip镜像源
    print("\n🔧 配置国内pip镜像源...")
    mirrors = [
        "https://pypi.tuna.tsinghua.edu.cn/simple/",
        "https://mirrors.aliyun.com/pypi/simple/",
        "https://pypi.douban.com/simple/"
    ]
    
    for mirror in mirrors:
        if run_command(f"pip config set global.index-url {mirror}", f"设置镜像源: {mirror}"):
            break
    
    # 升级pip
    print("\n🔄 升级pip...")
    run_command("python -m pip install --upgrade pip", "升级pip")
    
    # 安装后端依赖
    print("\n📦 安装后端依赖...")
    backend_deps = [
        "fastapi",
        "uvicorn[standard]",
        "sqlalchemy",
        "pydantic",
        "pyjwt",
        "python-multipart"
    ]
    
    for dep in backend_deps:
        run_command(f"pip install {dep}", f"安装 {dep}")
    
    # 进入前端目录安装前端依赖
    if os.path.exists("frontend"):
        print("\n🎨 安装前端依赖...")
        os.chdir("frontend")
        
        # 设置npm国内镜像
        run_command("npm config set registry https://registry.npmmirror.com", "设置npm镜像源")
        
        # 清理缓存
        run_command("npm cache clean --force", "清理npm缓存")
        
        # 安装依赖
        run_command("npm install", "安装前端依赖")
        
        os.chdir("..")
    
    print("\n🎉 依赖安装完成!")
    print("\n💡 下一步:")
    print("  1. 启动后端: python backend/simple_server.py")
    print("  2. 启动前端: cd frontend && npm run dev")
    print("  3. 访问系统: http://localhost:5174")

if __name__ == "__main__":
    main()