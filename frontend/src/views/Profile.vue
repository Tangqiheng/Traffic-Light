<script setup>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import api from '../services/api.js'
import { getCurrentUser } from '../services/auth.js'
import { ElMessage } from 'element-plus'

const store = useStore()

const formRef = ref(null)
const form = ref({ username: '', email: '', full_name: '' })

const loadUser = async () => {
  try {
    const res = await getCurrentUser()
    const data = res.data
    form.value.username = data.username
    form.value.email = data.email || ''
    form.value.full_name = data.full_name || ''
    store.dispatch('setUser', data)
  } catch (err) {
    console.error('加载用户失败', err)
  }
}

const submit = async () => {
  try {
    const payload = {
      email: form.value.email,
      full_name: form.value.full_name
    }
    const res = await api.updateProfile(payload)
    const updated = res.data
    store.dispatch('setUser', updated)
    ElMessage.success('资料更新成功')
  } catch (err) {
    console.error(err)
    ElMessage.error(err.response?.data?.detail || '更新失败')
  }
}

onMounted(() => {
  loadUser()
})
</script>

<template>
  <div class="profile-page">
    <el-card>
      <h3>个人中心</h3>
      <el-form :model="form" ref="formRef" label-width="90px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.full_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submit">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.profile-page { max-width: 720px; margin: 0 auto; }
</style>
<!-- 已移除个人中心页面 -->
