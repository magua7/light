<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchMapPoints, fetchOverview, fetchTrend, fetchTypeDistribution } from '../api/dashboard'
import EChartPanel from '../components/EChartPanel.vue'
import LeafletMap from '../components/LeafletMap.vue'
import PanelCard from '../components/PanelCard.vue'
import StatCard from '../components/StatCard.vue'
import { formatDateTime, formatType, levelColorMap, levelTagMap } from '../utils/dicts'

const router = useRouter()
const loading = ref(false)
const overview = ref({
  total_tasks: 0,
  today_tasks: 0,
  high_risk_warnings: 0,
  average_score: 0,
  level_distribution: [],
  recent_tasks: []
})
const trendList = ref([])
const typeDistribution = ref([])
const mapPoints = ref([])

const distributionTotal = computed(() =>
  overview.value.level_distribution.reduce((sum, item) => sum + item.value, 0)
)

const trendOption = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    textStyle: {
      color: '#5d6e86'
    }
  },
  grid: {
    left: 30,
    right: 18,
    top: 40,
    bottom: 30
  },
  xAxis: {
    type: 'category',
    data: trendList.value.map((item) => item.date),
    axisLine: { lineStyle: { color: '#b6c2d1' } }
  },
  yAxis: [
    {
      type: 'value',
      name: '任务数',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#edf2f7' } }
    },
    {
      type: 'value',
      name: '平均分',
      axisLine: { show: false },
      splitLine: { show: false }
    }
  ],
  series: [
    {
      name: '检测任务数',
      type: 'line',
      smooth: true,
      data: trendList.value.map((item) => item.count),
      itemStyle: { color: '#2563eb' },
      areaStyle: { color: 'rgba(37, 99, 235, 0.16)' }
    },
    {
      name: '平均评分',
      type: 'bar',
      yAxisIndex: 1,
      barWidth: 16,
      data: trendList.value.map((item) => item.average_score),
      itemStyle: { color: '#38bdf8', borderRadius: [6, 6, 0, 0] }
    }
  ]
}))

const typeOption = computed(() => ({
  tooltip: {
    trigger: 'item'
  },
  legend: {
    bottom: 0
  },
  series: [
    {
      name: '污染类型占比',
      type: 'pie',
      radius: ['45%', '72%'],
      center: ['50%', '44%'],
      label: {
        formatter: '{b}: {d}%'
      },
      data: typeDistribution.value.map((item) => ({
        name: formatType(item.name),
        value: item.value
      }))
    }
  ]
}))

async function loadDashboard() {
  loading.value = true
  try {
    const [overviewData, trendData, typeData, mapData] = await Promise.all([
      fetchOverview(),
      fetchTrend(),
      fetchTypeDistribution(),
      fetchMapPoints()
    ])
    overview.value = overviewData
    trendList.value = trendData
    typeDistribution.value = typeData
    mapPoints.value = mapData
  } finally {
    loading.value = false
  }
}

function goDetail(id) {
  router.push(`/tasks/${id}`)
}

onMounted(loadDashboard)
</script>

<template>
  <div class="page-view" v-loading="loading">
    <div class="page-head">
      <div>
        <div class="page-title">首页大屏</div>
        <div class="page-desc">展示全市监测任务总览、趋势分析、类型分布和点位地图。</div>
      </div>
      <el-button type="primary" @click="$router.push('/tasks/create')">新建检测任务</el-button>
    </div>

    <div class="stats-grid">
      <StatCard
        title="检测任务总数"
        :value="overview.total_tasks"
        description="系统累计创建的光污染检测任务"
        accent="#2563eb"
      />
      <StatCard
        title="今日检测数"
        :value="overview.today_tasks"
        description="今天新增并完成的检测任务"
        accent="#0ea5e9"
      />
      <StatCard
        title="高风险预警数"
        :value="overview.high_risk_warnings"
        description="进入重点治理清单的高风险任务"
        accent="#f97316"
      />
      <StatCard
        title="平均评分"
        :value="overview.average_score"
        description="当前样本任务的综合平均评分"
        accent="#14b8a6"
      />
    </div>

    <div class="two-col-grid">
      <PanelCard title="最近 7 天检测趋势">
        <EChartPanel :option="trendOption" />
      </PanelCard>

      <PanelCard title="光污染类型占比">
        <EChartPanel :option="typeOption" />
      </PanelCard>
    </div>

    <div class="two-col-grid">
      <PanelCard title="等级分布统计">
        <div class="panel-body" style="padding: 0;">
          <div
            v-for="item in overview.level_distribution"
            :key="item.name"
            style="display: grid; grid-template-columns: 60px 1fr 50px; gap: 12px; align-items: center; margin-bottom: 14px;"
          >
            <el-tag :type="levelTagMap[item.name] || 'info'">{{ item.name }}</el-tag>
            <el-progress
              :percentage="distributionTotal ? Number(((item.value / distributionTotal) * 100).toFixed(2)) : 0"
              :color="levelColorMap[item.name] || '#2563eb'"
              :show-text="false"
            />
            <div style="text-align: right; color: #5d6e86;">{{ item.value }} 条</div>
          </div>
        </div>
      </PanelCard>

      <PanelCard title="地图点位分布">
        <LeafletMap :points="mapPoints" />
      </PanelCard>
    </div>

    <PanelCard title="最近任务列表">
      <el-table :data="overview.recent_tasks" stripe>
        <el-table-column prop="task_no" label="任务编号" min-width="170" />
        <el-table-column prop="location_name" label="地点名称" min-width="160" />
        <el-table-column label="评级" width="100">
          <template #default="{ row }">
            <el-tag :type="levelTagMap[row.level] || 'info'">{{ row.level || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="评分" width="100" />
        <el-table-column label="创建时间" min-width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="goDetail(row.id)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </PanelCard>
  </div>
</template>
