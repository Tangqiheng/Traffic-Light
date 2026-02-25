# Node.js 国内镜像安装指南

## 🚀 快速安装方法

### 方法一：使用自动化脚本（推荐）
```bash
python install_nodejs.py
```

### 方法二：手动下载安装

#### 1. 访问国内镜像站点

**淘宝NPM镜像**（最推荐）：
- 网址：https://npmmirror.com/mirrors/node/
- 特点：速度最快，更新及时

**清华大学镜像**：
- 网址：https://mirrors.tuna.tsinghua.edu.cn/nodejs-release/
- 特点：稳定可靠

**华为云镜像**：
- 网址：https://mirrors.huaweicloud.com/nodejs/
- 特点：企业级稳定

#### 2. 选择合适的版本

**Windows用户**：
- 64位系统：下载 `node-vXX.XX.X-win-x64.zip`
- 32位系统：下载 `node-vXX.XX.X-win-x86.zip`

**推荐版本**：
- LTS版本（长期支持）：更稳定
- Current版本：最新功能

#### 3. 安装步骤

1. **下载ZIP文件**
   - 从镜像站选择对应版本下载

2. **解压文件**
   - 解压到 `C:\Program Files\nodejs` 或其他目录

3. **配置环境变量**
   ```
   右键"此电脑" → 属性 → 高级系统设置 → 环境变量
   在系统变量PATH中添加Node.js安装路径
   ```

4. **验证安装**
   ```bash
   node --version
   npm --version
   ```

## 📋 常用国内镜像源配置

### NPM源配置
```bash
# 查看当前源
npm config get registry

# 设置淘宝源
npm config set registry https://registry.npmmirror.com

# 临时使用淘宝源
npm install --registry=https://registry.npmmirror.com
```

### Yarn源配置
```bash
# 设置淘宝源
yarn config set registry https://registry.npmmirror.com
```

## 🔧 项目前端依赖安装

Node.js安装完成后，在项目目录执行：

```bash
cd frontend
npm install
npm run dev
```

## 🎯 常见问题解决

### 1. npm命令找不到
- 检查环境变量是否正确配置
- 重启命令行窗口

### 2. 权限问题
```bash
# Windows管理员权限运行
npm install -g npm-windows-upgrade
```

### 3. 网络超时
```bash
# 设置npm超时时间
npm config set timeout 60000
```

## 💡 优化建议

1. **使用cnpm**（淘宝npm客户端）
   ```bash
   npm install -g cnpm --registry=https://registry.npmmirror.com
   cnpm install
   ```

2. **使用yarn**（更快的包管理器）
   ```bash
   npm install -g yarn
   yarn config set registry https://registry.npmmirror.com
   yarn install
   ```

3. **使用pnpm**（节省磁盘空间）
   ```bash
   npm install -g pnpm
   pnpm config set registry https://registry.npmmirror.com
   pnpm install
   ```

---
*建议优先使用淘宝NPM镜像，下载和安装速度最佳*