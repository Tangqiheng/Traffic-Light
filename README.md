# 智能交通灯控制系统

## 项目简介

这是一个基于Vue.js + FastAPI的智能交通灯控制系统，实现了现代化的Web界面和RESTful API服务。

## 系统特点

- 🚦 实时交通状态监控
- 📊 数据可视化展示
- 🔐 用户认证与权限管理
- 🎨 响应式Web界面
- ⚡ 高性能API服务

## 技术栈

### 前端
- Vue 3 + Composition API
- Element Plus UI组件库
- Vue Router 路由管理
- Vuex 状态管理
- Axios HTTP客户端
- ECharts 数据可视化

### 后端
- FastAPI Web框架
- SQLAlchemy ORM
- SQLite 数据库
- JWT Token认证
- Uvicorn ASGI服务器

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- 现代浏览器

### 安装依赖

使用国内镜像源快速安装：

```bash
# Windows
python install_deps_china.py

# 或手动安装
pip install -r requirements.txt
cd frontend && npm install
```

### 启动服务

#### 方法一：使用启动脚本（推荐）

```bash
# 启动后端服务
start_backend_simple.bat

# 启动前端服务（另开终端）
start_frontend_simple.bat
```

#### 方法二：手动启动

```bash
# 启动后端（端口8001）
cd backend
python simple_server.py

# 启动前端（端口5174）
cd frontend
npm run dev
```

### 访问系统

- 前端界面: http://localhost:5174
- API文档: http://localhost:8001/docs
- 默认账号: admin/admin123

## 项目结构

```
Traffic Light/
├── backend/                 # 后端服务
│   ├── simple_server.py    # 主服务文件
│   └── traffic_users.db    # SQLite数据库
├── frontend/               # 前端应用
│   ├── src/               # 源代码
│   │   ├── views/         # 页面组件
│   │   ├── services/      # API服务
│   │   ├── store/         # 状态管理
│   │   └── router/        # 路由配置
│   └── vite.config.js     # 构建配置
├── requirements.txt        # Python依赖
└── README.md              # 项目说明
```

## 功能模块

### 用户管理
- 用户登录/登出
- 权限认证
- 个人信息管理

### 交通监控
- 实时交通数据展示
- 路口状态监控
- 历史数据查询

### 系统管理
- 系统状态查看
- 日志管理
- 配置管理

## API接口

主要API端点：

```
POST   /api/auth/login        # 用户登录
GET    /api/system/status     # 系统状态
GET    /api/traffic/data      # 交通数据
POST   /api/traffic/update    # 更新交通数据
GET    /api/user/profile      # 用户信息
```

## 开发说明

### 前端开发
```bash
cd frontend
npm run dev     # 开发模式
npm run build   # 生产构建
```

### 后端开发
```bash
cd backend
python simple_server.py  # 启动开发服务器
```

## 部署说明

### 生产环境部署
1. 构建前端: `cd frontend && npm run build`
2. 配置反向代理(Nginx/Apache)
3. 部署后端服务
4. 配置域名和SSL证书

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # Windows查看端口占用
   netstat -ano | findstr :8001
   ```

2. **依赖安装失败**
   ```bash
   # 使用国内镜像源
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
   ```

3. **数据库连接问题**
   - 检查数据库文件权限
   - 确认SQLite版本兼容性

## 许可证

MIT License

## 联系方式

如有问题请提交Issue或联系项目维护者。