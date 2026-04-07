<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { fetchTaskDetail } from '../api/tasks'
import EChartPanel from '../components/EChartPanel.vue'
import PanelCard from '../components/PanelCard.vue'
import {
  chartPalette,
  formatCoordinate,
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

const directionOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(12, 13, 16, 0.96)',
    borderColor: 'rgba(255,255,255,0.08)',
    textStyle: { color: '#f1ede6' }
  },
  grid: { left: 20, right: 16, top: 28, bottom: 24, containLabel: true },
  xAxis: {
    type: 'category',
    data: (detail.value?.charts?.direction_scores || []).map((item) => formatDirection(item.direction)),
    axisLine: { lineStyle: { color: 'rgba(255,255,255,0.12)' } },
    axisLabel: { color: '#8f8a81' }
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#8f8a81' },
    splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }
  },
  series: [
    {
      type: 'bar',
      barWidth: 32,
      data: (detail.value?.charts?.direction_scores || []).map((item) => item.score),
      itemStyle: {
        color: chartPalette.bright,
        borderRadius: [10, 10, 0, 0]
      }
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
        <div class="page-desc">
          将任务信息、图像识别摘要、环境评分与治理建议整合为一页式报告，
          便于在答辩现场完整展示检测流程与分析结果。
        </div>
      </div>
      <div class="page-actions">
        <el-button @click="goHistory">返回历史记录</el-button>
      </div>
    </div>

    <template v-if="detail">
      <div class="report-hero">
        <div class="report-hero__main">
          <div class="report-hero__kicker">任务编号 {{ detail.task_no }}</div>
          <div class="report-hero__title">{{ detail.location_name }}</div>
          <div class="report-hero__meta">
            <span>经纬度 {{ formatCoordinate(detail.longitude, detail.latitude) }}</span>
            <span>创建时间 {{ formatDateTime(detail.created_at) }}</span>
            <span>状态 {{ detail.status }}</span>
          </div>
        </div>

        <div class="report-score">
          <div class="report-score__label">综合评分</div>
          <div class="report-score__value">{{ detail.total_score }}</div>
          <el-tag size="large" :type="levelTagMap[detail.level] || 'info'">{{ detail.level }}</el-tag>
        </div>
      </div>

      <div class="metric-row">
        <div class="metric-box">
          <div class="metric-label">蓝光风险</div>
          <div class="metric-value">{{ detail.blue_risk ? '存在' : '风险较低' }}</div>
        </div>
        <div class="metric-box">
          <div class="metric-label">预警状态</div>
          <div class="metric-value">{{ detail.warning?.warning_level || '正常' }}</div>
        </div>
        <div class="metric-box">
          <div class="metric-label">图像评分</div>
          <div class="metric-value">{{ detail.image_score }}</div>
        </div>
      </div>

      <PanelCard title="任务基本信息" subtitle="保留点位信息、环境评分与任务状态，方便作为报告摘要直接讲解。">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="任务 ID">{{ detail.id }}</el-descriptions-item>
          <el-descriptions-item label="任务编号">{{ detail.task_no }}</el-descriptions-item>
          <el-descriptions-item label="任务状态">{{ detail.status }}</el-descriptions-item>
          <el-descriptions-item label="地点名称">{{ detail.location_name }}</el-descriptions-item>
          <el-descriptions-item label="经纬度">{{ formatCoordinate(detail.longitude, detail.latitude) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(detail.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="卫星评分">{{ detail.satellite_score }}</el-descriptions-item>
          <el-descriptions-item label="生态评分">{{ detail.ecology_score }}</el-descriptions-item>
          <el-descriptions-item label="区域识别">{{ detail.geo_info?.region_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="土地利用">{{ detail.ecology_info?.land_use_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="卫星亮度">{{ detail.satellite_info?.brightness_value || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注信息" :span="3">{{ detail.remark || '-' }}</el-descriptions-item>
        </el-descriptions>
      </PanelCard>

      <PanelCard title="图像样本预览" subtitle="报告统一按 图片1~图片4 展示样本顺序，便于现场讲解与截图展示。">
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

      <PanelCard title="单图识别摘要" subtitle="分别展示每张样本图的分值、蓝光风险与主要光源识别结果。">
        <div class="summary-grid">
          <article v-for="item in detail.direction_summaries" :key="item.direction" class="summary-card">
            <div class="summary-card__head">
              <div>
                <div class="summary-card__title">{{ formatDirection(item.direction) }}</div>
                <div class="summary-card__score">评分 {{ item.score }}</div>
              </div>
              <el-tag :type="item.blue_risk ? 'danger' : 'success'">
                {{ item.blue_risk ? '存在蓝光风险' : '风险较低' }}
              </el-tag>
            </div>

            <div class="tag-cloud">
              <el-tag
                v-for="obj in item.objects"
                :key="`${item.direction}-${obj.label}-${obj.confidence}`"
                effect="plain"
                class="tag-cloud__item"
              >
                {{ formatType(obj.label) }} {{ obj.confidence }}
              </el-tag>
            </div>
          </article>
        </div>
      </PanelCard>

      <div class="two-col-grid">
        <PanelCard title="四图评分对比" subtitle="比较 4 张样本图在图像分析阶段的评分差异。">
          <EChartPanel :option="directionOption" />
        </PanelCard>

        <PanelCard title="污染类型结构" subtitle="汇总本次任务中不同光源类型的占比。">
          <EChartPanel :option="typeOption" />
        </PanelCard>
      </div>

      <PanelCard title="治理建议" subtitle="基于光源类型、等级和蓝光风险生成简要治理建议。">
        <ul class="info-list">
          <li v-for="item in detail.suggestions" :key="item">{{ item }}</li>
        </ul>
      </PanelCard>
    </template>
  </div>
</template>

<style scoped>
.report-hero {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 18px;
  padding: 28px;
  border-radius: 26px;
  background:
    linear-gradient(180deg, rgba(18, 20, 24, 0.96) 0%, rgba(12, 13, 16, 0.98) 100%);
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

.report-score {
  min-width: 190px;
  padding: 22px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.report-score__label {
  color: var(--text-muted);
  font-size: 13px;
}

.report-score__value {
  margin: 14px 0 18px;
  font-size: 52px;
  font-weight: 700;
  line-height: 1;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.summary-card {
  padding: 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.summary-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.summary-card__title {
  font-size: 18px;
  font-weight: 700;
}

.summary-card__score {
  margin-top: 8px;
  color: var(--text-muted);
  font-size: 13px;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.tag-cloud__item {
  margin: 0;
}

@media (max-width: 960px) {
  .report-hero,
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .report-score {
    min-width: 0;
  }
}
</style>
