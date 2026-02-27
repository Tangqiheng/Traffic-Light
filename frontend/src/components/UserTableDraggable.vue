<template>
  <el-table :data="localUsers" class="user-table" border stripe ref="tableRef" @selection-change="emitSelection">
    <el-table-column type="selection" width="40" />
    <el-table-column prop="id" label="ID" width="60" />
    <el-table-column prop="username" label="用户名" width="120" />
    <el-table-column prop="email" label="邮箱" width="180" />
    <el-table-column prop="full_name" label="姓名" width="120" />
    <el-table-column prop="is_active" label="状态" width="80">
      <template #default="scope">
        <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
          {{ scope.row.is_active ? '正常' : '禁用' }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="is_admin" label="管理员" width="80">
      <template #default="scope">
        <el-tag :type="scope.row.is_admin ? 'warning' : 'info'">
          {{ scope.row.is_admin ? '是' : '否' }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="created_at" label="注册时间" width="180" />
    <el-table-column prop="updated_at" label="更新时间" width="180" />
    <el-table-column label="排序" width="120">
      <template #default="scope">
        <el-button size="small" @click="moveUp(scope.$index)" :disabled="scope.$index === 0">上移</el-button>
        <el-button size="small" @click="moveDown(scope.$index)" :disabled="scope.$index === localUsers.length - 1">下移</el-button>
      </template>
    </el-table-column>
    <el-table-column label="操作" width="260">
      <template #default="scope">
        <slot name="actions" :row="scope.row" />
      </template>
    </el-table-column>
    <template #body>
      <draggable :list="localUsers" @end="onDragEnd" tag="tbody">
        <template #item="{element, index}">
          <tr>
            <!-- 这里可自定义拖拽行内容 -->
          </tr>
        </template>
      </draggable>
    </template>
  </el-table>
</template>
<script setup>
import { ref, watch } from 'vue'
import draggable from 'vuedraggable'
const props = defineProps({
  users: Array,
})
const emit = defineEmits(['updateOrder', 'selectionChange'])
const tableRef = ref(null)
const localUsers = ref([...props.users])

watch(() => props.users, (val) => {
  localUsers.value = [...val]
})

const moveUp = (idx) => {
  if (idx > 0) {
    const temp = localUsers.value[idx]
    localUsers.value.splice(idx, 1)
    localUsers.value.splice(idx - 1, 0, temp)
    emit('updateOrder', localUsers.value)
  }
}
const moveDown = (idx) => {
  if (idx < localUsers.value.length - 1) {
    const temp = localUsers.value[idx]
    localUsers.value.splice(idx, 1)
    localUsers.value.splice(idx + 1, 0, temp)
    emit('updateOrder', localUsers.value)
  }
}
const onDragEnd = () => {
  emit('updateOrder', localUsers.value)
}
const emitSelection = (val) => {
  emit('selectionChange', val)
}
</script>
<style scoped>
.user-table {
  margin-bottom: 12px;
}
</style>
