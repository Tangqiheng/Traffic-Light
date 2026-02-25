# 前端开发说明

## 项目结构
```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/           # 静态资源
│   ├── components/       # 公共组件
│   ├── router/          # 路由配置
│   ├── services/        # API服务
│   ├── stores/          # Vuex状态管理
│   ├── utils/           # 工具函数
│   ├── views/           # 页面组件
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── index.html
├── package.json
└── vite.config.js
```

## 开发环境搭建

### 安装依赖
```bash
cd frontend
npm install
```

### 启动开发服务器
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

## 技术栈
- **框架**: Vue 3 + Vite
- **UI库**: Element Plus
- **状态管理**: Vuex 4
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **图标**: Element Plus Icons

## 路由配置

### 主要路由
- `/` - 系统概览（首页）
- `/login` - 登录页面
- `/monitor` - 实时监控
- `/control` - 信号控制
- `/history` - 历史数据
- `/reports` - 统计报告
- `/settings` - 系统设置
- `/profile` - 个人中心
- `/change-password` - 修改密码

### 路由守卫
- 自动检查用户登录状态
- 未登录用户访问受保护页面自动跳转到登录页
- 已登录用户访问登录页自动跳转到首页

## 组件开发规范

### 命名约定
- 组件文件名使用 PascalCase
- 组件内使用 kebab-case 引用
- 单文件组件 (.vue)

### 代码组织
```vue
<template>
  <!-- 模板内容 -->
</template>

<script setup>
// 组合式 API
import { ref, computed } from 'vue'
// 组件逻辑
</script>

<style scoped>
/* 样式代码 */
</style>
```

## 状态管理

### Vuex Store 结构
```javascript
store/
├── index.js          # Store 配置
├── modules/
│   ├── user.js      # 用户模块
│   └── traffic.js   # 交通数据模块
└── getters.js       # 全局 getter
```

### 用户状态
- `user`: 当前用户信息
- `isAuthenticated`: 登录状态
- `permissions`: 用户权限

## API 服务

### 服务封装
```javascript
// services/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
```

### 认证服务
```javascript
// services/auth.js
import api from './api'

export const login = (username, password) => {
  return api.post('/auth/login', { username, password })
}

export const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export const getCurrentUser = () => {
  return api.get('/auth/user')
}
```

## 样式规范

### CSS 类命名
- 使用 BEM 命名规范
- 组件样式使用 scoped
- 全局样式放在 assets/css/

### 响应式设计
- 移动端优先
- 使用 Element Plus 响应式断点
- Flexbox 布局为主

## 最近更新

### 2024-02-24 登录路由修复
- 修复登录成功后跳转到实时监控页面的问题
- 修改为跳转到系统概览页面 (`/`)
- 添加路由监听机制，确保菜单激活状态与路由同步
- 详细说明见 [login-route-fix.md](./login-route-fix.md)

### 2024-02-24 系统概览页面完善
- 补充缺失的图表组件引用
- 修复数据更新逻辑中的错误
- 完善实时数据轮询机制
- 添加完整的系统状态展示

## 开发注意事项

### 性能优化
- 合理使用 keep-alive 缓存组件
- 图片资源压缩优化
- 避免不必要的重新渲染

### 安全考虑
- 敏感信息不存储在 localStorage
- CSRF 防护
- XSS 防护

### 浏览器兼容性
- 支持现代浏览器
- IE11 需要 polyfill

## 调试技巧

### Vue DevTools
- 安装 Vue DevTools 浏览器扩展
- 查看组件树和状态
- 调试 Vuex 状态变化

### 网络请求调试
- 使用浏览器开发者工具 Network 面板
- 查看 API 请求和响应
- 检查认证头信息

## 部署说明

### 生产环境构建
```bash
npm run build
```

### 部署配置
- 静态文件部署到 Web 服务器
- 配置反向代理到后端 API
- 设置正确的 base URL

### 环境变量
```bash
# .env.production
VITE_API_BASE_URL=https://your-api-domain.com
```