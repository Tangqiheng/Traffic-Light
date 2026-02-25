#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Flask导入是否正常工作的脚本
"""

try:
    from flask import Flask, jsonify, request
    print("✅ Flask导入成功!")
    print(f"Flask版本: {__import__('flask').__version__}")
    
    # 测试基本功能
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return jsonify({"message": "Hello World!", "status": "success"})
    
    print("✅ Flask应用创建成功!")
    print("✅ 所有导入和基本功能测试通过!")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装Flask: pip install flask")
    
except Exception as e:
    print(f"❌ 其他错误: {e}")

print("\n测试完成!")