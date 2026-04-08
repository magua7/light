<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchMapPoints } from '../api/dashboard'
import LeafletMap from '../components/LeafletMap.vue'
import PanelCard from '../components/PanelCard.vue'
import StatCard from '../components/StatCard.vue'
import { formatCoordinateDisplay, formatDateTime, levelColorMap, levelTagMap } from '../utils/dicts'

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
        <div class="page-desc">从空间分布角度查看长沙样本点位与任务结果。</div>
      </div>
    </div>

    <div class="stats-grid">
      <StatCard title="监测点总数" :value="summary.total" description="当前地图已加载的样本点位" accent="#ece7df" />
      <StatCard title="高风险点位" :value="summary.high" description="评级偏高的重点关注点位" accent="#bb735c" />
      <StatCard title="中等级点位" :value="summary.medium" description="评级处于中档的样本点位" accent="#c29b63" />
      <StatCard title="展示区域" value="长沙" description="地图默认视野位于湖南长沙" accent="#d6dde6" />
    </div>

    <PanelCard title="监测点位地图">
      <template #extra>
        <span class="panel-note">{{ mapPoints.length }} 个点位</span>
      </template>

      <div class="legend-row map-legend">
        <div v-for="(color, level) in levelColorMap" :key="level" class="legend-item">
          <span class="legend-dot" :style="{ background: color }"></span>
          <span>{{ level }}</span>
        </div>
      </div>
      <LeafletMap :points="mapPoints" height="520px" />
    </PanelCard>

    <PanelCard title="点位摘要列表">
      <el-table :data="mapPoints">
        <el-table-column prop="task_no" label="任务编号" min-width="180" align="center" header-align="center">
          <template #default="{ row }">
            <span class="task-no">{{ row.task_no }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="location_name" label="地点名称" min-width="180" align="center" header-align="center" />
        <el-table-column label="经纬度" min-width="200" align="center" header-align="center">
          <template #default="{ row }">
            <span class="coordinate-text">{{ formatCoordinateDisplay(row.longitude, row.latitude, { compact: true }) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="评级" width="100" align="center" header-align="center">
          <template #default="{ row }">
            <el-tag :type="levelTagMap[row.level] || 'info'">{{ row.level || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="评分" width="100" align="center" header-align="center" />
        <el-table-column label="创建时间" min-width="180" align="center" header-align="center">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130" align="center" header-align="center">
          <template #default="{ row }">
            <el-button class="table-action-btn" @click="goDetail(row.task_id)">查看报告</el-button>
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

.task-no,
.coordinate-text {
  color: var(--text-main);
  font-weight: 600;
}
</style>
