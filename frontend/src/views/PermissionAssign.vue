<template>
  <div class="page-container">
    <h2>权限分配</h2>
    <el-card>
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span style="font-size:18px;font-weight:600;">用户权限管理</span>
        <div>
          <el-input v-model="search" placeholder="搜索用户名" size="small" style="width:200px;margin-right:8px;" clearable @keyup.enter="fetchUsers" />
          <el-button type="primary" size="small" @click="fetchUsers" :loading="loading">搜索</el-button>
          <el-button size="small" @click="fetchUsers" :loading="loading">刷新</el-button>
        </div>
      </div>
      <el-table
        :data="users"
        style="margin-top:16px;"
        border
        stripe
      >
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="full_name" label="姓名" width="120" />
        <el-table-column label="权限" min-width="300">
          <template #default="scope">
            <el-tag v-for="perm in scope.row.permissions" :key="perm" type="info" style="margin-right:4px;">{{ perm }}</el-tag>
            <el-button size="small" @click="openPermDialog(scope.row)">分配权限</el-button>
          </template>
        </el-table-column>
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
    <!-- 权限分配弹窗 -->
    <el-dialog v-model="showPermDialog" title="分配权限" width="400px">
      <el-form>
        <el-form-item label="权限列表">
          <el-select v-model="permForm.permissions" multiple filterable placeholder="请选择权限">
            <el-option v-for="item in allPermissions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPermDialog=false">取消</el-button>
        <el-button type="primary" @click="handleSetPermissions">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import authClient from '../services/auth.js'

const users = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const search = ref('')
const loading = ref(false)
const showPermDialog = ref(false)
const permForm = ref({ user_id: null, permissions: [] })
const allPermissions = ref([
  'user_manage', 'log_view', 'traffic_control', 'system_config', 'report_view', 'other'
])

const fetchUsers = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value, q: search.value }
    const res = await authClient.get('/admin/users', { params })
    const userList = res.data.users || []
    // 查询每个用户的权限
    for (const user of userList) {
      const permRes = await authClient.get(`/admin/permissions/${user.id}`)
      user.permissions = permRes.data.permissions || []
    }
    users.value = userList
    total.value = res.data.total || 0
  } catch (e) {
    ElMessage.error('获取用户或权限失败')
  } finally {
    loading.value = false
  }
}
const handlePageChange = (val) => {
  page.value = val
  fetchUsers()
}
const handleSizeChange = (val) => {
  pageSize.value = val
  page.value = 1
  fetchUsers()
}
const openPermDialog = (row) => {
  permForm.value.user_id = row.id
  permForm.value.permissions = [...(row.permissions || [])]
  showPermDialog.value = true
}
const handleSetPermissions = async () => {
  try {
    await authClient.post(`/admin/permissions/${permForm.value.user_id}`, { permissions: permForm.value.permissions })
    ElMessage.success('权限分配成功')
    showPermDialog.value = false
    fetchUsers()
  } catch (e) {
    ElMessage.error('权限分配失败')
  }
}
onMounted(() => {
  fetchUsers()
})
</script>
<style scoped>
.page-container { padding: 24px; }
</style>
