<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { fetchWarningList, updateWarningStatus } from '../api/warnings'
import PanelCard from '../components/PanelCard.vue'
import { formatDateTime, levelTagMap } from '../utils/dicts'

const router = useRouter()
const loading = ref(false)
const warnings = ref([])

async function loadWarnings() {
  loading.value = true
  try {
    warnings.value = await fetchWarningList()
  } finally {
    loading.value = false
  }
}

async function toggleStatus(row) {
  const nextStatus = row.process_status === '已处理' ? '未处理' : '已处理'
  await updateWarningStatus(row.id, nextStatus)
  ElMessage.success(nextStatus === '已处理' ? '已标记为处理完成' : '已恢复为待处理')
  await loadWarnings()
}

function goDetail(taskId) {
  router.push(`/tasks/${taskId}`)
}

onMounted(loadWarnings)
</script>

<template>
  <div class="page-view" v-loading="loading">
    <div class="page-head">
      <div>
        <div class="page-title">预警列表</div>
        <div class="page-desc">聚焦中高风险与高风险样本，展示当前预警台账。</div>
      </div>
    </div>

    <PanelCard title="预警台账">
      <template #extra>
        <span class="panel-note">{{ warnings.length }} 条预警</span>
      </template>

      <el-table :data="warnings">
        <el-table-column prop="location_name" label="地点名称" min-width="160" align="center" header-align="center" />
        <el-table-column prop="task_no" label="任务编号" min-width="180" align="center" header-align="center">
          <template #default="{ row }">
            <span class="task-no">{{ row.task_no }}</span>
          </template>
        </el-table-column>
        <el-table-column label="时间" min-width="180" align="center" header-align="center">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="评分" width="100" align="center" header-align="center" />
        <el-table-column label="等级" width="100" align="center" header-align="center">
          <template #default="{ row }">
            <el-tag :type="levelTagMap[row.level] || 'info'">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="预警级别" width="120" align="center" header-align="center">
          <template #default="{ row }">
            <el-tag :type="row.warning_level === '高风险' ? 'danger' : 'warning'">{{ row.warning_level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="蓝光风险" width="110" align="center" header-align="center">
          <template #default="{ row }">
            <el-tag :type="row.blue_risk ? 'danger' : 'success'">{{ row.blue_risk ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="276" align="center" header-align="center">
          <template #default="{ row }">
            <div class="warning-actions">
              <el-button class="table-action-btn" @click="goDetail(row.task_id)">查看报告</el-button>
              <el-button class="table-secondary-btn" @click="toggleStatus(row)">
                {{ row.process_status === '已处理' ? '恢复待处理' : '标记已处理' }}
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </PanelCard>
  </div>
</template>

<style scoped>
.warning-actions {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  white-space: nowrap;
}

.warning-actions :deep(.el-button) {
  min-width: 96px;
  padding-left: 14px;
  padding-right: 14px;
  font-weight: 600;
  line-height: 1;
  letter-spacing: 0;
  text-shadow: none;
  white-space: nowrap;
}

.warning-actions :deep(.table-secondary-btn.el-button) {
  min-width: 118px;
}

.warning-actions :deep(.el-button > span) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
}

.task-no {
  color: var(--text-main);
  font-weight: 600;
}
</style>
