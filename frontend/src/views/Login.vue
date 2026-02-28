<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="login-title">智能交通灯控制系统</h2>
      <p class="login-subtitle">请登录以访问系统</p>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-position="top"
        class="login-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p>默认管理员账户: admin / admin123</p>
        <p class="warning-text">请及时修改默认密码</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { login } from '../services/auth.js'

const router = useRouter()
const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  try {
    await loginFormRef.value.validate()
    loading.value = true

    // 自动裁剪密码长度，避免超过72字节
    let safePassword = loginForm.password
    // 先去除首尾空格
    safePassword = safePassword.trim()
    // 超过72字节自动截断（utf-8编码下多字节字符也能处理）
    let encoder = new TextEncoder()
    let bytes = encoder.encode(safePassword)
    if (bytes.length > 72) {
      // 截断到72字节
      let truncated = ''
      let total = 0
      for (let ch of safePassword) {
        let chBytes = encoder.encode(ch)
        if (total + chBytes.length > 72) break
        truncated += ch
        total += chBytes.length
      }
      safePassword = truncated
    }

    const response = await login(loginForm.username, safePassword)

    // 检查是否有安全警告
    if (response.code === 'DEFAULT_PASSWORD_WARNING') {
      ElMessageBox.confirm(
        '检测到您正在使用默认密码，为了账户安全建议立即修改密码。是否继续登录？',
        '安全提醒',
        {
          confirmButtonText: '继续登录',
          cancelButtonText: '前往修改密码',
          type: 'warning',
          distinguishCancelAndClose: true
        }
      ).then(() => {
        // 用户选择继续登录
        storeTokensAndRedirect(response)
      }).catch((action) => {
        // 用户选择修改密码或关闭对话框
        if (action === 'cancel') {
          // 跳转前再次确认 access_token 已保存
          if (response.access_token) {
            localStorage.setItem('access_token', response.access_token)
            console.log('跳转前再次保存 access_token:', response.access_token)
          }
          router.push('/change-password') // 使用 SPA 路由跳转，保证 token 不丢失
        }
      })
    } else if (response.access_token) {
      // 正常登录流程
      storeTokensAndRedirect(response)
    } else {
      ElMessage.error(response.error || '登录响应异常')
    }
  } catch (error) {
    console.error('登录失败:', error)
    handleError(error)
  } finally {
    loading.value = false
  }
}

// 存储token并跳转
import { useStore } from 'vuex'
const store = useStore()

const storeTokensAndRedirect = async (data) => {
  // 自动修复：每次登录都保存 access_token，并输出调试信息
  if (data.access_token) {
    localStorage.setItem('access_token', data.access_token)
    console.log('access_token 已保存:', data.access_token)
  } else {
    console.warn('登录响应未包含 access_token:', data)
  }
  localStorage.setItem('refresh_token', data.refresh_token || '')
  // 登录后立即拉取用户信息，只有拉取成功才跳转主页，保证右上角有个人信息
  try {
    const { getCurrentUser } = await import('../services/auth.js')
    const res = await getCurrentUser()
    store.dispatch('setUser', res.data)
    ElMessage.success(data.message || '登录成功')
    router.push('/')
  } catch (e) {
    ElMessage.error('登录成功但获取用户信息失败，请重试')
    store.dispatch('setUser', null)
  }
}

// 统一错误处理函数
const handleError = (error) => {
  // 网络错误
  if (!error.response) {
    ElMessage.error({
      message: '网络连接失败，请检查网络设置',
      duration: 5000,
      grouping: true
    })
    return
  }

  const status = error.response.status
  const errorData = error.response.data
  
  // 根据错误码提供具体提示
  switch (status) {
    case 400:
      handleBadRequest(errorData)
      break
    case 401:
      handleUnauthorized(errorData)
      break
    case 403:
      ElMessage.error({
        message: '访问被拒绝：' + (errorData.error || '权限不足'),
        duration: 5000,
        grouping: true
      })
      break
    case 404:
      ElMessage.error({
        message: '服务不可用：登录接口未找到，请联系管理员',
        duration: 5000,
        grouping: true
      })
      break
    case 500:
      ElMessage.error({
        message: '服务器内部错误：' + (errorData.error || '请稍后重试'),
        duration: 5000,
        grouping: true
      })
      break
    case 502:
    case 503:
    case 504:
      ElMessage.error({
        message: '服务暂时不可用，请稍后重试',
        duration: 5000,
        grouping: true
      })
      break
    default:
      ElMessage.error({
        message: `登录失败 (${status})：${errorData.error || '未知错误'}`,
        duration: 5000,
        grouping: true
      })
  }
}

// 处理400错误（客户端错误）
const handleBadRequest = (errorData) => {
  let message = '请求参数错误'
  
  if (errorData.code === 'USERNAME_REQUIRED') {
    message = '请输入用户名'
  } else if (errorData.code === 'PASSWORD_REQUIRED') {
    message = '请输入密码'
  } else if (errorData.code === 'INVALID_REQUEST_DATA') {
    message = '请求数据格式错误'
  } else if (errorData.error) {
    message = errorData.error
  }
  
  ElMessage.error({
    message: message,
    duration: 4000,
    grouping: true
  })
}

// 处理401错误（认证错误）
const handleUnauthorized = (errorData) => {
  let message = '认证失败'
  let duration = 5000
  
  if (errorData.code === 'USER_NOT_FOUND') {
    message = '用户名不存在，请检查输入'
  } else if (errorData.code === 'INVALID_PASSWORD') {
    message = '密码错误，请重新输入'
  } else if (errorData.code === 'ACCOUNT_DISABLED') {
    message = '账户已被禁用，请联系管理员'
    duration = 8000
  } else if (errorData.error) {
    message = errorData.error
  }
  
  ElMessage.error({
    message: message,
    duration: duration,
    grouping: true
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-title {
  text-align: center;
  color: #333;
  margin-bottom: 8px;
  font-size: 24px;
  font-weight: 600;
}

.login-subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 32px;
  font-size: 14px;
}

.login-form {
  margin-bottom: 24px;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
}

.login-footer {
  text-align: center;
  color: #999;
  font-size: 12px;
}

.warning-text {
  color: #e6a23c;
  margin-top: 4px;
}

/* 错误提示相关样式 */
:deep(.el-message--error) {
  background-color: #fef0f0;
  border-color: #fde2e2;
  color: #f56c6c;
}

:deep(.el-message--warning) {
  background-color: #fdf6ec;
  border-color: #faecd8;
  color: #e6a23c;
}

:deep(.el-message__content) {
  font-weight: 500;
}

/* 表单错误状态样式 */
:deep(.el-form-item.is-error .el-input__wrapper) {
  box-shadow: 0 0 0 1px #f56c6c inset;
}

/* 加载状态按钮样式 */
.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
    margin: 10px;
  }
  
  .login-title {
    font-size: 20px;
  }
}
</style>
<!-- 已移除登录页面 -->
