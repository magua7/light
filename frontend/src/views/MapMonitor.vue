<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchMapPoints } from '../api/dashboard'
import LeafletMap from '../components/LeafletMap.vue'
import PanelCard from '../components/PanelCard.vue'
import StatCard from '../components/StatCard.vue'
import { formatDateTime, levelColorMap, levelTagMap } from '../utils/dicts'

const router = useRouter()
const loading = ref(false)
const mapPoints = ref([])

const summary = computed(() => {
  const result = { total: mapPoints.value.length, high: 0, medium: 0 }
  mapPoints.value.forEach((item) => {
    if (item.level === '差' || item.level === '较差') result.high += 1
    if (item.level === '中') result.medium += 1
  })
  return result
})

async function loadMapPoints() {
  loading.value = true
  try {
    mapPoints.value = await fetchMapPoints()
  } finally {
    loading.value = false
  }
}

function goDetail(id) {
  router.push(`/tasks/${id}`)
}

onMounted(loadMapPoints)
</script>

<template>
  <div class="page-view" v-loading="loading">
    <div class="page-head">
      <div>
        <div class="page-title">地图监测</div>
        <div class="page-desc">
          基于湖南长沙范围内的演示点位展示监测结果，
          适合从空间角度说明系统如何管理多点位光污染检测任务。
        </div>
      </div>
    </div>

    <div class="stats-grid">
      <StatCard title="监测点总数" :value="summary.total" description="地图中已加载的样本点位" accent="#f1ede6" />
      <StatCard title="高风险点位" :value="summary.high" description="评级为较差或差的重点点位" accent="#a86558" />
      <StatCard title="中等级点位" :value="summary.medium" description="评级处于中档的样本点位" accent="#b59572" />
      <StatCard title="展示区域" value="长沙" description="默认视野已调整至湖南长沙附近" accent="#d2ccc1" />
    </div>

    <PanelCard title="监测点位地图" subtitle="不同评级对应不同颜色标记，点击点位可快速进入检测报告。">
      <div class="legend-row map-legend">
        <div v-for="(color, level) in levelColorMap" :key="level" class="legend-item">
          <span class="legend-dot" :style="{ background: color }"></span>
          <span>{{ level }}</span>
        </div>
      </div>
      <LeafletMap :points="mapPoints" height="500px" />
    </PanelCard>

    <PanelCard title="点位摘要列表" subtitle="地图下方保留表格，方便答辩时切换列表讲解。">
      <el-table :data="mapPoints" stripe>
        <el-table-column prop="task_no" label="任务编号" min-width="170" />
        <el-table-column prop="location_name" label="地点名称" min-width="160" />
        <el-table-column label="评级" width="100">
          <template #default="{ row }">
            <el-tag :type="levelTagMap[row.level] || 'info'">{{ row.level || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="评分" width="100" />
        <el-table-column label="蓝光风险" width="110">
          <template #default="{ row }">
            <el-tag :type="row.blue_risk ? 'danger' : 'success'">{{ row.blue_risk ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="goDetail(row.task_id)">查看报告</el-button>
          </template>
        </el-table-column>
      </el-table>
    </PanelCard>
  </div>
</template>

<style scoped>
.map-legend {
  margin-bottom: 16px;
}
</style>
