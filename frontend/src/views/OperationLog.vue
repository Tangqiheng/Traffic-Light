<template>
  <div class="page-container">
    <h2>操作日志</h2>
    <el-card>
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span style="font-size:18px;font-weight:600;">日志查询</span>
        <div>
          <el-input v-model="searchUsername" placeholder="按用户名搜索" size="small" style="width:200px;margin-right:8px;" clearable @keyup.enter="fetchLogs" />
          <el-button type="primary" size="small" @click="fetchLogs" :loading="loading">搜索</el-button>
          <el-button size="small" @click="fetchLogs" :loading="loading">刷新</el-button>
        </div>
      </div>
      <el-table
        :data="logs"
        style="margin-top:16px;"
        border
        stripe
      >
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="action" label="操作" width="180" />
        <el-table-column prop="detail" label="详情" />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
      <div style="margin-top:16px;text-align:right;">
        <el-pagination
          background
          layout="total, prev, pager, next, sizes"
          :total="total"
          :page-size="pageSize"
          :current-page="page"
          :page-sizes="[10,20,50,100]"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import authClient from '../services/auth.js'

const logs = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searchUsername = ref('')
const loading = ref(false)

const fetchLogs = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (searchUsername.value) params.username = searchUsername.value
    const res = await authClient.get('/admin/logs', { params })
    logs.value = res.data.logs || []
    total.value = res.data.total || 0
  } catch (e) {
    ElMessage.error('获取日志失败')
  } finally {
    loading.value = false
  }
}
const handlePageChange = (val) => {
  page.value = val
  fetchLogs()
}
const handleSizeChange = (val) => {
  pageSize.value = val
  page.value = 1
  fetchLogs()
}
onMounted(() => {
  fetchLogs()
})
</script>
<style scoped>
.page-container { padding: 24px; }
</style>
