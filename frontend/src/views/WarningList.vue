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
  ElMessage.success('预警状态更新成功')
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
        <div class="page-desc">展示中高风险与高风险任务，可标记已处理或未处理。</div>
      </div>
    </div>

    <div class="stats-grid">
      <StatCard title="预警总数" :value="statistics.total" description="进入预警池的任务总量" accent="#2563eb" />
      <StatCard title="高风险任务" :value="statistics.critical" description="综合评分较高，建议重点复核" accent="#ef4444" />
      <StatCard title="待处理" :value="statistics.pending" description="尚未闭环处理的预警任务" accent="#f59e0b" />
      <StatCard title="已处理" :value="statistics.processed" description="已完成治理跟进或人工复核" accent="#10b981" />
    </div>

    <PanelCard title="预警任务表">
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
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="goDetail(row.task_id)">详情</el-button>
            <el-button type="warning" link @click="toggleStatus(row)">
              {{ row.process_status === '已处理' ? '标记未处理' : '标记已处理' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </PanelCard>
  </div>
</template>
