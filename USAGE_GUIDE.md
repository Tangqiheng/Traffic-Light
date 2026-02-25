# 智能交通灯控制系统使用指南

## 系统概述

这是一个基于AI的智能交通灯控制系统，具有以下主要功能：
- 实时交通状态监测
- 自适应信号灯控制
- 多模态传感器数据融合
- 深度强化学习优化
- Web管理界面

## 快速启动

### 方法一：全自动启动（推荐）
```bash
# 运行完整自动化脚本
python system_startup.py
```

### 方法二：快速修复启动
```bash
# 运行快速修复脚本
python quick_fix.py
```

### 方法三：手动启动

#### 1. 启动后端服务
```bash
cd backend
# Windows PowerShell
$env:KMP_DUPLICATE_LIB_OK="TRUE"
python simple_server.py

# 或者使用命令提示符
set KMP_DUPLICATE_LIB_OK=TRUE && python simple_server.py
```

> **重要说明**：当前系统推荐使用 `simple_server.py` 作为后端主服务（运行在端口 8001），它已修复所有数据库和ORM相关问题。`app.py`（端口 8000）为历史兼容版本，可能存在兼容性问题。

#### 2. 启动前端服务
```bash
cd frontend
npm run dev
```

## 系统访问

启动成功后，可以通过以下地址访问系统：

- **前端界面**: http://localhost:5173 (如果5173被占用，Vite会自动选择其他端口如5174)
- **后端API**: http://localhost:8001 (simple_server.py) 或 http://localhost:8000 (app.py)
- **默认登录**: admin / admin123

## 功能模块

### 1. 系统概览 (Dashboard)
- 显示整体交通状况
- 关键指标统计
- 系统运行状态

### 2. 实时监控 (Monitor)
- 实时交通流量数据
- 信号灯状态显示
- 传感器数据可视化

### 3. 信号控制 (Control)
- 手动控制信号灯
- 控制策略选择
- 参数调整

### 4. 历史数据 (History)
- 历史交通数据查询
- 统计报表生成
- 数据导出功能

### 5. 系统设置 (Settings)
- 用户管理
- 系统配置
- 权限设置

## API接口

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/refresh` - 刷新令牌
- `GET /api/auth/me` - 获取当前用户信息

### 交通数据接口
- `GET /api/traffic/status/<intersection_id>` - 获取交通状态
- `GET /api/traffic/light-status/<intersection_id>` - 获取信号灯状态
- `POST /api/traffic/control/<intersection_id>` - 控制信号灯
- `GET /api/traffic/overview/<intersection_id>` - 获取交通概况

## 故障排除

### 常见问题

#### 1. 后端服务无法启动
```bash
# 检查依赖安装
pip install -r requirements.txt

# 检查端口占用
netstat -an | findstr :8000
```

#### 2. 前端服务无法启动
```bash
# 重新安装前端依赖
cd frontend
rm -rf node_modules
npm install
```

#### 3. 登录失败 404 错误
- 确认后端服务正常运行
- 检查Vite代理配置
- 验证API端点是否存在

#### 4. 数据库连接问题
```bash
# 检查数据库文件
ls backend/*.db

# 重新初始化数据库
cd backend
python init_db.py
```

### 系统检查命令

```bash
# 运行系统状态检查
python system_check.py

# 运行快速诊断
python quick_fix.py --diagnose
```

## 开发环境配置

### 后端开发
```bash
cd backend
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行单元测试
python -m pytest tests/

# 运行集成测试
python test_integration.py
```

### 前端开发
```bash
cd frontend
# 安装开发工具
npm install --save-dev

# 运行测试
npm run test

# 构建生产版本
npm run build
```

## 生产部署

### Docker部署
```bash
# 构建镜像
docker build -t traffic-light-system .

# 运行容器
docker run -p 8000:8000 traffic-light-system
```

### 传统部署
```bash
# 后端使用Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# 前端构建后使用Nginx
npm run build
# 配置Nginx指向dist目录
```

## 系统维护

### 日常维护任务
- 定期备份数据库文件
- 监控系统日志
- 检查磁盘空间使用
- 更新安全补丁

### 性能优化
- 定期清理历史数据
- 优化数据库索引
- 调整缓存策略
- 监控资源使用情况

## 技术支持

如遇到技术问题，请：
1. 查看系统日志文件
2. 运行诊断脚本
3. 检查环境配置
4. 联系技术支持团队

---
*最后更新: 2024年*