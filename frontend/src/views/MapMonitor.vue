<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchMapPoints } from '../api/dashboard'
import LeafletMap from '../components/LeafletMap.vue'
import PanelCard from '../components/PanelCard.vue'
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
        <div class="page-desc">按污染等级在地图上展示所有检测点位，可联动查看任务摘要。</div>
      </div>
    </div>

    <div class="stats-grid">
      <div class="metric-box">
        <div class="metric-label">监测点总数</div>
        <div class="metric-value">{{ summary.total }}</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">高风险点位</div>
        <div class="metric-value">{{ summary.high }}</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">中等级风险点位</div>
        <div class="metric-value">{{ summary.medium }}</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">地图交互</div>
        <div class="metric-value">Leaflet</div>
      </div>
    </div>

    <PanelCard title="监测点位地图">
      <div class="legend-row" style="margin-bottom: 16px;">
        <div v-for="(color, level) in levelColorMap" :key="level" class="legend-item">
          <span class="legend-dot" :style="{ background: color }"></span>
          <span>{{ level }}</span>
        </div>
      </div>
      <LeafletMap :points="mapPoints" height="460px" />
    </PanelCard>

    <PanelCard title="点位摘要列表">
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
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="goDetail(row.task_id)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </PanelCard>
  </div>
</template>
