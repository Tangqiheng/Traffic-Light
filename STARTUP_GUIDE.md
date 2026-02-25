# 智能交通灯控制系统启动指南

## 系统架构
- 前端：Vue.js + Vite (端口 5173)
- 后端：FastAPI (端口 8001) - 使用 simple_server.py 作为主服务
- 数据库：SQLite (开发环境)

## 启动步骤

### 1. 启动后端服务
```bash
# 方法一：使用批处理脚本（推荐）
双击运行 start_backend.bat

# 方法二：手动启动（推荐使用 simple_server.py）
cd backend
python simple_server.py
```

后端启动成功后会显示：
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

> **注意**：由于历史兼容性问题，系统默认使用 `simple_server.py` 作为后端服务（端口 8001），而非 `app.py`（端口 8000）。`simple_server.py` 已修复所有数据库和ORM相关问题，是当前推荐的后端服务。

### 2. 启动前端服务
```bash
# 方法一：使用批处理脚本（推荐）
双击运行 start_frontend.bat

# 方法二：手动启动
cd frontend
npm install  # 首次运行需要安装依赖
npm run dev
```

前端启动成功后会显示：
```
Local: http://localhost:5173/
```

> **端口说明**：如果5173端口被占用，Vite会自动选择其他可用端口（如5174），请查看终端输出确认实际端口。

## 默认登录账户
- 用户名：admin
- 密码：admin123

## 常见问题排查

### 1. 登录404错误
**问题现象**：登录时报404错误
**解决方案**：
- 确认后端服务已在8001端口启动（不是8000）
- 检查Vite代理配置是否指向 `http://localhost:8001`
- 浏览器开发者工具中查看网络请求的实际URL

### 2. 数据库连接错误
**问题现象**：后端启动时报数据库错误
**解决方案**：
- 确保已安装所需依赖：`pip install fastapi uvicorn sqlalchemy pydantic`
- 系统会自动创建SQLite数据库文件 `traffic_users.db`

### 3. 前端白屏或加载失败
**问题现象**：访问http://localhost:5173显示空白页面
**解决方案**：
- 确认Node.js和npm已正确安装
- 删除node_modules文件夹后重新运行`npm install`
- 检查Vite配置文件中的代理设置

## API端点测试

可以直接使用curl或Postman测试API：

### 登录接口
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 交通数据接口
```bash
curl http://localhost:8001/api/traffic/overview/intersection_001
```

## 开发环境配置

### 环境变量
在`.env`文件中可以配置：
```
DATABASE_URL=sqlite:///./traffic_users.db
JWT_SECRET_KEY=your-secret-key-change-in-production
```

### 调试技巧
1. 后端：在`simple_server.py`中可以添加调试信息
2. 前端：使用浏览器开发者工具查看控制台和网络面板
3. 数据库：可以使用DB Browser for SQLite查看数据

## 生产环境部署
生产环境建议使用：
- Nginx作为反向代理
- Uvicorn运行FastAPI应用
- MySQL数据库
- SSL证书配置