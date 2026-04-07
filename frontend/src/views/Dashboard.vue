<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchMapPoints, fetchOverview, fetchTrend, fetchTypeDistribution } from '../api/dashboard'
import EChartPanel from '../components/EChartPanel.vue'
import LeafletMap from '../components/LeafletMap.vue'
import PanelCard from '../components/PanelCard.vue'
import StatCard from '../components/StatCard.vue'
import { chartPalette, formatDateTime, formatType, levelColorMap, levelTagMap } from '../utils/dicts'

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
    trigger: 'axis',
    backgroundColor: 'rgba(12, 13, 16, 0.96)',
    borderColor: 'rgba(255,255,255,0.08)',
    textStyle: { color: '#f1ede6' }
  },
  legend: {
    top: 0,
    textStyle: {
      color: '#bbb3a8'
    }
  },
  grid: {
    left: 24,
    right: 16,
    top: 48,
    bottom: 24,
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: trendList.value.map((item) => item.date),
    axisLine: { lineStyle: { color: 'rgba(255,255,255,0.12)' } },
    axisLabel: { color: '#8f8a81' }
  },
  yAxis: [
    {
      type: 'value',
      name: '任务数',
      nameTextStyle: { color: '#7e7971' },
      axisLabel: { color: '#8f8a81' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }
    },
    {
      type: 'value',
      name: '平均分',
      nameTextStyle: { color: '#7e7971' },
      axisLabel: { color: '#8f8a81' },
      splitLine: { show: false }
    }
  ],
  series: [
    {
      name: '检测任务数',
      type: 'line',
      smooth: true,
      symbolSize: 8,
      data: trendList.value.map((item) => item.count),
      lineStyle: { color: chartPalette.bright, width: 2 },
      itemStyle: { color: chartPalette.bright },
      areaStyle: { color: 'rgba(241, 237, 230, 0.08)' }
    },
    {
      name: '平均评分',
      type: 'bar',
      yAxisIndex: 1,
      barWidth: 16,
      data: trendList.value.map((item) => item.average_score),
      itemStyle: { color: chartPalette.warning, borderRadius: [8, 8, 0, 0] }
    }
  ]
}))

const typeOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(12, 13, 16, 0.96)',
    borderColor: 'rgba(255,255,255,0.08)',
    textStyle: { color: '#f1ede6' }
  },
  legend: {
    bottom: 0,
    textStyle: { color: '#bbb3a8' }
  },
  color: [
    chartPalette.bright,
    chartPalette.light,
    chartPalette.warning,
    chartPalette.danger
  ],
  series: [
    {
      name: '污染类型占比',
      type: 'pie',
      radius: ['48%', '72%'],
      center: ['50%', '42%'],
      label: {
        color: '#d2ccc1',
        formatter: '{b}: {d}%'
      },
      labelLine: {
        lineStyle: { color: 'rgba(255,255,255,0.18)' }
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
        <div class="page-desc">
          用更克制的方式呈现任务总量、最近趋势、污染结构与点位分布，
          便于在答辩现场快速讲清系统能力与监测结果。
        </div>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="$router.push('/tasks/create')">发起新检测</el-button>
      </div>
    </div>

    <div class="stats-grid">
      <StatCard
        title="检测任务总数"
        :value="overview.total_tasks"
        description="系统累计归档的夜间光环境检测任务"
        accent="#f1ede6"
      />
      <StatCard
        title="今日检测数"
        :value="overview.today_tasks"
        description="今日新完成的检测与分析任务"
        accent="#d2ccc1"
      />
      <StatCard
        title="高风险预警数"
        :value="overview.high_risk_warnings"
        description="进入重点复核清单的高风险任务"
        accent="#a86558"
      />
      <StatCard
        title="平均评分"
        :value="overview.average_score"
        description="当前样本任务的综合平均评分"
        accent="#b59572"
      />
    </div>

    <div class="two-col-grid">
      <PanelCard title="最近 7 天检测趋势" subtitle="结合每日任务数与平均评分，观察样本变化趋势。">
        <EChartPanel :option="trendOption" />
      </PanelCard>

      <PanelCard title="光污染类型占比" subtitle="对近期任务中的主要光源类型进行结构化统计。">
        <EChartPanel :option="typeOption" />
      </PanelCard>
    </div>

    <div class="two-col-grid">
      <PanelCard title="评级分布" subtitle="当前样本任务在五档评级中的分布情况。">
        <div class="distribution-list">
          <div v-for="item in overview.level_distribution" :key="item.name" class="distribution-row">
            <div class="distribution-row__tag">
              <el-tag :type="levelTagMap[item.name] || 'info'">{{ item.name }}</el-tag>
            </div>
            <el-progress
              :percentage="distributionTotal ? Number(((item.value / distributionTotal) * 100).toFixed(2)) : 0"
              :color="levelColorMap[item.name] || '#d2ccc1'"
              :show-text="false"
            />
            <div class="distribution-row__count">{{ item.value }} 条</div>
          </div>
        </div>
      </PanelCard>

      <PanelCard title="地图点位分布" subtitle="以湖南长沙区域为示例展示监测点空间分布。">
        <LeafletMap :points="mapPoints" />
      </PanelCard>
    </div>

    <PanelCard title="最近任务列表" subtitle="用于演示从首页快速跳转至检测报告。">
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
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="goDetail(row.id)">查看报告</el-button>
          </template>
        </el-table-column>
      </el-table>
    </PanelCard>
  </div>
</template>

<style scoped>
.distribution-list {
  display: grid;
  gap: 16px;
}

.distribution-row {
  display: grid;
  grid-template-columns: 68px 1fr 64px;
  align-items: center;
  gap: 14px;
}

.distribution-row__count {
  color: var(--text-muted);
  text-align: right;
  font-size: 13px;
}
</style>
