<script setup>
import { ref } from 'vue'
import api from '../services/api.js'
import { logout } from '../services/auth.js'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

const store = useStore()

const form = ref({ old_password: '', new_password: '', confirm_password: '' })

const submit = async () => {
  if (!form.value.old_password || !form.value.new_password) {
    ElMessage.error('请填写完整的旧密码和新密码')
    return
  }
  if (form.value.new_password.length < 6) {
    ElMessage.error('新密码长度不能少于6位')
    return
  }
  if (form.value.new_password !== form.value.confirm_password) {
    ElMessage.error('两次输入的新密码不一致')
    return
  }

  try {
    const res = await api.changePassword({ old_password: form.value.old_password, new_password: form.value.new_password })
    if (res.data && res.data.success) {
      ElMessage.success('密码修改成功，请重新登录')
      // 强制登出
      store.dispatch('logout')
      logout()
    } else {
      ElMessage.error(res.data?.error || res.data?.message || '修改失败')
    }
  } catch (err) {
    console.error(err)
    ElMessage.error(err.response?.data?.error || err.response?.data?.detail || '修改失败')
  }
}
</script>

<template>
  <div class="change-password-page">
    <el-card>
      <h3>修改密码</h3>
      <el-form :model="form" label-width="120px">
        <el-form-item label="旧密码">
          <el-input v-model="form.old_password" type="password" placeholder="请输入旧密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="form.new_password" type="password" placeholder="请输入新密码（至少6位）" />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="form.confirm_password" type="password" placeholder="请再次输入新密码" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submit">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.change-password-page { max-width: 600px; margin: 0 auto; }
</style>
<!-- 已移除修改密码页面 -->
