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
    backgroundColor: '#242b34',
    borderColor: '#313945',
    textStyle: { color: '#f5f7fa' }
  },
  legend: {
    top: 4,
    itemGap: 16,
    textStyle: {
      color: '#d6dde6'
    }
  },
  grid: {
    left: 28,
    right: 20,
    top: 52,
    bottom: 28,
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: trendList.value.map((item) => item.date),
    axisLine: { lineStyle: { color: '#47515f' } },
    axisTick: { show: false },
    axisLabel: { color: '#c5cdd7' }
  },
  yAxis: [
    {
      type: 'value',
      name: '任务数',
      nameTextStyle: { color: '#aab3bf' },
      axisLabel: { color: '#c5cdd7' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } }
    },
    {
      type: 'value',
      name: '平均分',
      nameTextStyle: { color: '#aab3bf' },
      axisLabel: { color: '#c5cdd7' },
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
      lineStyle: { color: chartPalette.light, width: 2.5 },
      itemStyle: { color: chartPalette.light },
      areaStyle: { color: 'rgba(214, 221, 230, 0.1)' }
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
    backgroundColor: '#242b34',
    borderColor: '#313945',
    textStyle: { color: '#f5f7fa' }
  },
  legend: {
    bottom: 0,
    icon: 'circle',
    textStyle: { color: '#d6dde6' }
  },
  color: [
    chartPalette.light,
    chartPalette.mid,
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
        color: '#dfe4eb',
        formatter: '{b}: {d}%'
      },
      labelLine: {
        lineStyle: { color: '#576271' }
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

function goCreate() {
  router.push('/tasks/create')
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
        <div class="page-desc">查看任务规模、近期趋势、光源结构与长沙样本点位。</div>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="goCreate">新建检测任务</el-button>
      </div>
    </div>

    <div class="stats-grid">
      <StatCard
        title="检测任务总数"
        :value="overview.total_tasks"
        description="系统累计归档的夜间光环境检测任务"
        accent="#ece7df"
      />
      <StatCard
        title="今日检测数"
        :value="overview.today_tasks"
        description="今日新完成的检测与综合分析任务"
        accent="#d6dde6"
      />
      <StatCard
        title="高风险预警数"
        :value="overview.high_risk_warnings"
        description="建议优先复核的高风险样本任务"
        accent="#bb735c"
      />
      <StatCard
        title="平均评分"
        :value="overview.average_score"
        description="当前样本任务的综合平均评分"
        accent="#c29b63"
      />
    </div>

    <div class="two-col-grid">
      <PanelCard title="最近 7 天检测趋势">
        <EChartPanel :option="trendOption" />
      </PanelCard>

      <PanelCard title="污染类型占比">
        <EChartPanel :option="typeOption" />
      </PanelCard>
    </div>

    <div class="two-col-grid">
      <PanelCard title="评级分布">
        <div class="distribution-list">
          <div v-for="item in overview.level_distribution" :key="item.name" class="distribution-row">
            <div class="distribution-row__tag">
              <el-tag :type="levelTagMap[item.name] || 'info'">{{ item.name }}</el-tag>
            </div>
            <el-progress
              :percentage="distributionTotal ? Number(((item.value / distributionTotal) * 100).toFixed(2)) : 0"
              :color="levelColorMap[item.name] || '#d6dde6'"
              :show-text="false"
            />
            <div class="distribution-row__count">{{ item.value }} 条</div>
          </div>
        </div>
      </PanelCard>

      <PanelCard title="地图点位分布">
        <LeafletMap :points="mapPoints" height="360px" />
      </PanelCard>
    </div>

    <PanelCard title="最近任务列表">
      <template #extra>
        <span class="panel-note">最近 {{ overview.recent_tasks.length }} 条</span>
      </template>

      <el-table :data="overview.recent_tasks">
        <el-table-column prop="task_no" label="任务编号" min-width="170">
          <template #default="{ row }">
            <span class="task-no">{{ row.task_no }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="location_name" label="地点名称" min-width="170" />
        <el-table-column label="评级" width="110">
          <template #default="{ row }">
            <el-tag :type="levelTagMap[row.level] || 'info'">{{ row.level || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="评分" width="110">
          <template #default="{ row }">
            <span class="score-text">{{ row.total_score ?? '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130">
          <template #default="{ row }">
            <el-button class="table-action-btn" @click="goDetail(row.id)">查看报告</el-button>
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
  color: var(--text-sub);
  text-align: right;
  font-size: 13px;
}

.task-no {
  color: var(--text-main);
  font-weight: 600;
  letter-spacing: 0.02em;
}

.score-text {
  color: var(--text-main);
  font-weight: 600;
}
</style>
