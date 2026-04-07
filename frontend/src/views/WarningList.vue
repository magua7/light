<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { fetchWarningList, updateWarningStatus } from '../api/warnings'
import PanelCard from '../components/PanelCard.vue'
import StatCard from '../components/StatCard.vue'
import { formatDateTime, levelTagMap } from '../utils/dicts'

const router = useRouter()
const loading = ref(false)
const warnings = ref([])

const statistics = computed(() => {
  const total = warnings.value.length
  const processed = warnings.value.filter((item) => item.process_status === '已处理').length
  const pending = total - processed
  const critical = warnings.value.filter((item) => item.warning_level === '高风险').length
  return { total, processed, pending, critical }
})

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
  ElMessage.success(nextStatus === '已处理' ? '已标记为处理完成' : '已重新标记为待处理')
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
        <div class="page-desc">
          用于展示中高风险与高风险任务，并记录处理状态，
          适合在比赛演示时说明系统的预警闭环能力。
        </div>
      </div>
    </div>

    <div class="stats-grid">
      <StatCard title="预警总数" :value="statistics.total" description="进入预警池的任务总量" accent="#f1ede6" />
      <StatCard title="高风险任务" :value="statistics.critical" description="建议优先安排复核的样本点位" accent="#a86558" />
      <StatCard title="待处理" :value="statistics.pending" description="尚未完成闭环跟进的预警任务" accent="#b59572" />
      <StatCard title="已处理" :value="statistics.processed" description="已完成人工复核或治理跟进" accent="#87917e" />
    </div>

    <PanelCard title="预警台账" subtitle="保留处理状态切换能力，便于展示从发现到跟进的完整链路。">
      <el-table :data="warnings" stripe>
        <el-table-column prop="location_name" label="地点名称" min-width="160" />
        <el-table-column prop="task_no" label="任务编号" min-width="170" />
        <el-table-column label="时间" min-width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="评分" width="100" />
        <el-table-column label="等级" width="100">
          <template #default="{ row }">
            <el-tag :type="levelTagMap[row.level] || 'info'">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="预警级别" width="110">
          <template #default="{ row }">
            <el-tag :type="row.warning_level === '高风险' ? 'danger' : 'warning'">{{ row.warning_level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="蓝光风险" width="110">
          <template #default="{ row }">
            <el-tag :type="row.blue_risk ? 'danger' : 'success'">{{ row.blue_risk ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="处理状态" width="110">
          <template #default="{ row }">
            <el-tag :type="row.process_status === '已处理' ? 'success' : 'info'">{{ row.process_status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <div class="warning-actions">
              <el-button type="primary" link @click="goDetail(row.task_id)">查看报告</el-button>
              <el-button type="warning" link @click="toggleStatus(row)">
                {{ row.process_status === '已处理' ? '重新标记待处理' : '标记为已处理' }}
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
  display: inline-flex;
  align-items: center;
  gap: 12px;
}
</style>
