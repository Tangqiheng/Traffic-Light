<template>
  <div class="register-container">
    <div class="register-card">
      <h2 class="register-title">注册新用户</h2>
      <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" label-position="top" class="register-form">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" size="large" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" size="large" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="registerForm.full_name" placeholder="请输入姓名" size="large" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" size="large" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" class="register-button" :loading="loading" @click="handleRegister">注册</el-button>
        </el-form-item>
      </el-form>
      <div class="register-footer">
        <el-link type="primary" @click="goLogin">已有账号？去登录</el-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../services/api.js'

const router = useRouter()
const registerFormRef = ref()
const loading = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
  confirmPassword: ''
})

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度3-20位', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 72, message: '密码长度6-72位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: (rule, value, callback) => {
      if (value !== registerForm.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  try {
    await registerFormRef.value.validate()
    loading.value = true
    const payload = {
      username: registerForm.username.trim(),
      email: registerForm.email.trim(),
      full_name: registerForm.full_name.trim(),
      password: registerForm.password
    }
    await api.register(payload)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (err) {
    if (err.response && err.response.data && err.response.data.error) {
      ElMessage.error(err.response.data.error)
    } else {
      ElMessage.error('注册失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

const goLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}
.register-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}
.register-title {
  text-align: center;
  color: #333;
  margin-bottom: 8px;
  font-size: 24px;
  font-weight: 600;
}
.register-form {
  margin-bottom: 24px;
}
.register-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
}
.register-footer {
  text-align: center;
  color: #999;
  font-size: 12px;
  margin-top: 12px;
}
</style>
