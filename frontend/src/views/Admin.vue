<template>
  <div class="page-container">
    <h2 class="admin-title">管理员功能</h2>
    <el-card class="user-card">
      <div class="user-header">
        <span class="user-title">用户管理</span>
        <div class="user-actions">
          <el-input v-model="search" placeholder="搜索用户名/邮箱/姓名" size="small" class="search-input" clearable @keyup.enter="handleSearch" />
          <el-button type="primary" size="small" @click="handleSearch" :loading="loading">搜索</el-button>
          <el-button type="success" size="small" @click="showAddDialog=true">添加用户</el-button>
          <el-button type="danger" size="small" :disabled="!multipleSelection.length" @click="handleBatchDelete">批量删除</el-button>
          <el-button type="warning" size="small" @click="handleResetSort" :loading="loading">一键重置排序</el-button>
          <el-button size="small" @click="fetchUsers" :loading="loading">刷新</el-button>
        </div>
      </div>
      <UserTableDraggable :users="users" @updateOrder="handleUpdateOrder" @selectionChange="handleSelectionChange">
        <template #actions="{ row }">
          <el-button size="small" @click="goToProfile(row)">编辑</el-button>
          <el-button size="small" type="warning" @click="goToChangePassword(row)">重置密码</el-button>
          <el-button size="small" :type="row.is_active ? 'info' : 'success'" @click="toggleActive(row)">
            {{ row.is_active ? '禁用' : '启用' }}
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </UserTableDraggable>
      <div class="pagination-bar">
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

    <!-- 编辑用户弹窗（移到根级，避免作用域异常） -->
    <el-dialog v-model="showEditDialog" title="编辑用户" width="400px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="ID">
          <el-input v-model.number="editForm.id" :disabled="editForm.username === 'admin'" autocomplete="off" />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" autocomplete="off" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" autocomplete="off" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="editForm.full_name" autocomplete="off" />
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="editForm.is_admin" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="editForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog=false">取消</el-button>
        <el-button type="primary" @click="handleEditUser">保存</el-button>
      </template>
    </el-dialog>
    <!-- 重置密码弹窗（移到根级） -->
    <el-dialog v-model="showResetPwdDialog" title="重置密码" width="400px">
      <el-form :model="resetPwdForm" label-width="80px">
        <el-form-item label="新密码">
          <el-input v-model="resetPwdForm.new_password" type="password" autocomplete="off" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showResetPwdDialog=false">取消</el-button>
        <el-button type="primary" @click="handleResetPwd">重置</el-button>
      </template>
    </el-dialog>
      <!-- 只保留一份分页和卡片结构，移除多余部分 -->

    <!-- 添加用户弹窗 -->
    <el-dialog v-model="showAddDialog" title="添加用户" width="400px">
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="addForm.username" autocomplete="off" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="addForm.email" autocomplete="off" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="addForm.full_name" autocomplete="off" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="addForm.password" type="password" autocomplete="off" />
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="addForm.is_admin" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="addForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog=false">取消</el-button>
        <el-button type="primary" @click="handleAddUser">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllUsers } from '../services/api.js'
import authClient from '../services/auth.js'
import UserTableDraggable from '../components/UserTableDraggable.vue'
import { sortUsers, resetUserSort } from '../services/api.js'

const users = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const search = ref('')
const loading = ref(false)
const multipleSelection = ref([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showResetPwdDialog = ref(false)
const addForm = ref({ username: '', email: '', full_name: '', password: '', is_admin: false, is_active: true })
const editForm = ref({ id: null, username: '', email: '', full_name: '', is_admin: false, is_active: true })
const resetPwdForm = ref({ id: null, new_password: '' })
const userTableRef = ref(null)
const router = useRouter()

// 编辑按钮：弹窗回显目标用户信息
const goToProfile = (row) => {
  authClient.get(`/admin/users/${row.id}`).then(res => {
    const user = res.data.user
    Object.assign(editForm.value, {
      id: user.id,
      username: user.username,
      email: user.email,
      full_name: user.full_name,
      is_admin: user.is_admin,
      is_active: user.is_active
    })
    showEditDialog.value = true
  }).catch(() => {
    ElMessage.error('获取用户信息失败')
  })
}
// 重置密码按钮：直接重置为123456
const goToChangePassword = (row) => {
  ElMessageBox.confirm(`确定将用户【${row.username}】的密码重置为123456吗？`, '重置密码', { type: 'warning' })
    .then(async () => {
      await authClient.post(`/admin/users/${row.id}/reset_password`, { new_password: '123456' })
      ElMessage.success('密码已重置为123456')
    })
    .catch(() => {})
}
// 打开编辑弹窗
const openEditDialog = (row) => {
  Object.assign(editForm.value, row)
  showEditDialog.value = true
}
// 编辑用户保存
const handleEditUser = async () => {
  try {
    const { id, ...payload } = editForm.value
    await authClient.put(`/admin/users/${id}`, payload)
    ElMessage.success('修改成功')
    showEditDialog.value = false
    fetchUsers()
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || '修改失败')
  }
}
// 打开重置密码弹窗
const openResetPwdDialog = (row) => {
  resetPwdForm.value.id = row.id
  resetPwdForm.value.new_password = ''
  showResetPwdDialog.value = true
}
// 重置密码
const handleResetPwd = async () => {
  try {
    await authClient.post(`/admin/users/${resetPwdForm.value.id}/reset_password`, { new_password: resetPwdForm.value.new_password })
    ElMessage.success('密码重置成功')
    showResetPwdDialog.value = false
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || '重置失败')
  }
}
// 启用/禁用切换
const toggleActive = async (row) => {
  try {
    await authClient.patch(`/admin/users/${row.id}/toggle_active`)
    ElMessage.success(row.is_active ? '已禁用' : '已启用')
    fetchUsers()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value, q: search.value }
    const res = await authClient.get('/admin/users', { params })
    users.value = res.data.users || []
    total.value = res.data.total || 0
  } catch (e) {
    ElMessage.error('获取用户列表失败')
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
const handleSearch = () => {
  page.value = 1
  fetchUsers()
}
const handleSelectionChange = (val) => {
  multipleSelection.value = val
}
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除用户【${row.username}】吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await authClient.delete(`/admin/users/${row.id}`)
      ElMessage.success('删除成功')
      fetchUsers()
    })
    .catch(() => {})
}
const handleBatchDelete = () => {
  if (!multipleSelection.value.length) return
  ElMessageBox.confirm(`确定要批量删除选中的${multipleSelection.value.length}个用户吗？`, '警告', { type: 'warning' })
    .then(async () => {
      const ids = multipleSelection.value.map(u => u.id)
      await authClient.post('/admin/users/batch_delete', { ids })
      ElMessage.success('批量删除成功')
      fetchUsers()
      if (userTableRef.value) userTableRef.value.clearSelection()
    })
    .catch(() => {})
}
const handleAddUser = async () => {
  try {
    await authClient.post('/admin/users', addForm.value)
    ElMessage.success('添加成功')
    showAddDialog.value = false
    Object.assign(addForm.value, { username: '', email: '', full_name: '', password: '', is_admin: false, is_active: true })
    fetchUsers()
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || '添加失败')
  }
}

const handleUpdateOrder = async (newUsers) => {
  // 生成批量排序数据
  const sortList = newUsers.map((u, idx) => ({ id: u.id, sort_order: idx }))
  try {
    await sortUsers(sortList)
    ElMessage.success('用户排序已更新')
    fetchUsers()
  } catch (e) {
    ElMessage.error('排序更新失败')
  }
}

const handleResetSort = () => {
  ElMessageBox.confirm('确定要重置排序吗？将按ID从小到大排序，admin默认排第一。', '重置排序', { type: 'warning' })
    .then(async () => {
      await resetUserSort()
      ElMessage.success('排序已重置')
      fetchUsers()
    })
    .catch(() => {})
}

onMounted(() => {
  fetchUsers()
})
</script>
<style scoped>
.page-container {
  padding: 32px 0 32px 0;
  background: #f6f8fa;
  min-height: 100vh;
}
.admin-title {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 18px;
  color: #222;
  letter-spacing: 1px;
}
.user-card {
  border-radius: 16px;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.07);
  padding: 24px 24px 12px 24px;
  background: #fff;
  border: none;
}
.user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.user-title {
  font-size: 18px;
  font-weight: 600;
  color: #1976d2;
  letter-spacing: 1px;
}
.user-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
.search-input {
  width: 220px;
}
.user-table {
  border-radius: 12px;
  font-size: 15px;
  background: #fff;
  box-shadow: 0 2px 8px 0 rgba(0,0,0,0.03);
}
.user-table .el-table__header th {
  background: #f3f6fa;
  color: #333;
  font-weight: 600;
  font-size: 15px;
}
.user-table .el-table__row {
  transition: background 0.2s;
}
.user-table .el-table__row:hover {
  background: #e3f2fd !important;
}
.user-table .el-button {
  margin-right: 6px;
  border-radius: 6px;
  font-size: 13px;
}
.user-table .el-button:last-child {
  margin-right: 0;
}
.user-table .el-tag {
  border-radius: 6px;
  font-size: 13px;
  padding: 0 10px;
}
.pagination-bar {
  margin-top: 18px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.action-btns-horizontal {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  min-width: 220px;
}
.user-table .el-table__column--actions {
  min-width: 120px;
  max-width: 180px;
}
</style>
