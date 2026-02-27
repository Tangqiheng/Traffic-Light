<script setup>
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import api from '../services/api.js'
import { getCurrentUser } from '../services/auth.js'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'

const store = useStore()


const formRef = ref(null)
const form = ref({ username: '', email: '', full_name: '' })
const route = useRoute()
const userId = computed(() => route.params.userId)

const loadUser = async () => {
  try {
    let data
    if (userId.value) {
      // 管理员查看/编辑其他用户
      const res = await api.getUserById(userId.value)
      data = res.data
    } else {
      // 当前用户
      const res = await getCurrentUser()
      data = res.data
    }
    form.value.username = data.username
    form.value.email = data.email || ''
    form.value.full_name = data.full_name || ''
  } catch (err) {
    console.error('加载用户失败', err)
    ElMessage.error('加载用户信息失败')
  }
}


const submit = async () => {
  try {
    if (!form.value.username) {
      ElMessage.error('用户名不能为空')
      return
    }
    const payload = {
      username: form.value.username,
      email: form.value.email,
      full_name: form.value.full_name
    }
    let res
    if (userId.value) {
      // 管理员编辑其他用户
      res = await api.updateUserById(userId.value, payload)
    } else {
      // 当前用户
      res = await api.updateProfile(payload)
      store.dispatch('setUser', res.data)
    }
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
          <el-input v-model="form.username" placeholder="请输入用户名" />
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
