<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { fetchTaskDetail } from '../api/tasks'
import EChartPanel from '../components/EChartPanel.vue'
import PanelCard from '../components/PanelCard.vue'
import {
  chartPalette,
  formatCoordinateDisplay,
  formatDateTime,
  formatDirection,
  formatImageUrl,
  formatType,
  levelTagMap
} from '../utils/dicts'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const detail = ref(null)

const previewImages = computed(() =>
  (detail.value?.images || []).map((item) => formatImageUrl(item.file_url))
)

const typeEntries = computed(() =>
  Object.entries(detail.value?.type_count || {})
    .map(([key, value]) => ({
      key,
      label: formatType(key),
      value
    }))
    .sort((a, b) => b.value - a.value)
)

const typeOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    backgroundColor: '#242b34',
    borderColor: '#313945',
    textStyle: { color: '#f5f7fa' }
  },
  legend: {
    bottom: 0,
    textStyle: { color: '#d6dde6' }
  },
  color: [
    chartPalette.bright,
    chartPalette.light,
    chartPalette.warning,
    chartPalette.danger
  ],
  series: [
    {
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
      data: (detail.value?.charts?.type_distribution || []).map((item) => ({
        name: formatType(item.name),
        value: item.value
      }))
    }
  ]
}))

const summaryBullets = computed(() => {
  const bullets = []
  const totalTypes = typeEntries.value.reduce((sum, item) => sum + item.value, 0)
  const imageCount = detail.value?.images?.length || 0

  if (imageCount) {
    bullets.push(`本次任务共纳入 ${imageCount} 张夜景样本图片参与综合分析。`)
  }

  if (typeEntries.value.length) {
    const topType = typeEntries.value[0]
    bullets.push(`本次任务共识别到 ${totalTypes} 个主要光源目标，其中 ${topType.label} 最为集中。`)
    if (typeEntries.value.length > 1) {
      bullets.push(`主要类型集中在 ${typeEntries.value.slice(0, 3).map((item) => item.label).join('、')}。`)
    }
  } else {
    bullets.push('当前样本未形成明显的类型聚类，可结合原图进一步核查。')
  }

  bullets.push(
    detail.value?.blue_risk
      ? '检测结果提示存在蓝光风险，建议优先关注高亮广告面、上射光源与夜间色温控制。'
      : '当前样本未发现明显蓝光风险，可继续结合现场巡查确认局部高亮区域。'
  )

  if (detail.value?.level) {
    bullets.push(`综合评级结果为“${detail.value.level}”，建议结合总得分与治理建议进行答辩讲解。`)
  }

  return bullets
})

async function loadDetail() {
  loading.value = true
  try {
    detail.value = await fetchTaskDetail(route.params.id)
  } finally {
    loading.value = false
  }
}

function goHistory() {
  router.push('/tasks/history')
}

onMounted(loadDetail)
watch(() => route.params.id, loadDetail)
</script>

<template>
  <div class="page-view" v-loading="loading">
    <div class="page-head">
      <div>
        <div class="page-title">检测报告</div>
        <div class="page-desc">汇总点位信息、识别摘要与治理建议，便于答辩展示本次样本结果。</div>
      </div>
      <div class="page-actions">
        <el-button @click="goHistory">返回历史记录</el-button>
      </div>
    </div>

    <template v-if="detail">
      <div class="report-hero">
        <div class="report-hero__main">
          <div class="report-hero__kicker">任务编号 {{ detail.task_no }}</div>
          <div class="report-hero__title">{{ detail.location_name || '未命名点位' }}</div>
          <div class="report-hero__meta">
            <span>{{ formatCoordinateDisplay(detail.longitude, detail.latitude) }}</span>
            <span>创建时间 {{ formatDateTime(detail.created_at) }}</span>
            <span v-if="detail.remark">备注 {{ detail.remark }}</span>
          </div>
        </div>
      </div>

      <div class="metric-row">
        <div class="metric-box">
          <div class="metric-label">总得分</div>
          <div class="metric-value">{{ detail.total_score ?? '--' }}</div>
        </div>
        <div class="metric-box">
          <div class="metric-label">评级结果</div>
          <div class="metric-value">
            <el-tag size="large" :type="levelTagMap[detail.level] || 'info'">{{ detail.level || '-' }}</el-tag>
          </div>
        </div>
        <div class="metric-box">
          <div class="metric-label">蓝光风险</div>
          <div class="metric-value">{{ detail.blue_risk ? '存在风险' : '风险较低' }}</div>
        </div>
      </div>

      <PanelCard title="任务基本信息">
        <div class="brief-grid">
          <div class="brief-item">
            <span class="brief-item__label">任务编号</span>
            <span class="brief-item__value">{{ detail.task_no }}</span>
          </div>
          <div class="brief-item">
            <span class="brief-item__label">地点名称</span>
            <span class="brief-item__value">{{ detail.location_name || '-' }}</span>
          </div>
          <div class="brief-item">
            <span class="brief-item__label">经纬度</span>
            <span class="brief-item__value">{{ formatCoordinateDisplay(detail.longitude, detail.latitude) }}</span>
          </div>
          <div class="brief-item">
            <span class="brief-item__label">创建时间</span>
            <span class="brief-item__value">{{ formatDateTime(detail.created_at) }}</span>
          </div>
          <div v-if="detail.remark" class="brief-item brief-item--wide">
            <span class="brief-item__label">备注</span>
            <span class="brief-item__value">{{ detail.remark }}</span>
          </div>
        </div>
      </PanelCard>

      <PanelCard title="图像样本预览">
        <div class="image-grid">
          <div v-for="item in detail.images" :key="item.id" class="image-card">
            <el-image
              :src="formatImageUrl(item.file_url)"
              fit="cover"
              class="image-card__media"
              :preview-src-list="previewImages"
            />
            <div class="image-caption">
              <span>{{ formatDirection(item.direction) }}</span>
              <span>{{ item.original_name }}</span>
            </div>
          </div>
        </div>
      </PanelCard>

      <PanelCard title="识别摘要">
        <div class="summary-layout">
          <div class="summary-overview">
            <div class="summary-keywords">
              <el-tag
                v-for="item in typeEntries"
                :key="item.key"
                effect="plain"
                class="summary-keywords__tag"
              >
                {{ item.label }} · {{ item.value }}
              </el-tag>
            </div>

            <ul class="summary-bullets">
              <li v-for="item in summaryBullets" :key="item">{{ item }}</li>
            </ul>
          </div>

          <div class="summary-chart">
            <EChartPanel :option="typeOption" />
          </div>
        </div>
      </PanelCard>

      <PanelCard title="治理建议">
        <ul class="info-list">
          <li v-for="item in detail.suggestions" :key="item">{{ item }}</li>
        </ul>
      </PanelCard>
    </template>
  </div>
</template>

<style scoped>
.report-hero {
  padding: 28px;
  border-radius: 26px;
  background: linear-gradient(180deg, rgba(14, 19, 26, 0.84) 0%, rgba(10, 13, 18, 0.9) 100%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: var(--shadow-main);
}

.report-hero__kicker {
  color: var(--text-muted);
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.report-hero__title {
  margin-top: 12px;
  font-size: 34px;
  font-weight: 700;
}

.report-hero__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  margin-top: 16px;
  color: var(--text-sub);
  font-size: 14px;
}

.brief-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.brief-item {
  display: grid;
  gap: 8px;
  padding: 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.brief-item--wide {
  grid-column: 1 / -1;
}

.brief-item__label {
  color: var(--text-muted);
  font-size: 12px;
}

.brief-item__value {
  color: var(--text-main);
  font-size: 15px;
  line-height: 1.8;
}

.summary-layout {
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  gap: 18px;
  align-items: stretch;
}

.summary-overview {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.summary-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.summary-keywords__tag {
  margin: 0;
}

.summary-bullets {
  margin: 0;
  padding-left: 20px;
  color: var(--text-sub);
  line-height: 1.9;
}

.summary-bullets li + li {
  margin-top: 10px;
}

.summary-chart {
  min-height: 360px;
}

@media (max-width: 960px) {
  .brief-grid,
  .summary-layout {
    grid-template-columns: 1fr;
  }

  .brief-item--wide {
    grid-column: auto;
  }
}
</style>
