<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { fetchTaskDetail } from '../api/tasks'
import EChartPanel from '../components/EChartPanel.vue'
import PanelCard from '../components/PanelCard.vue'
import {
  formatDateTime,
  formatDirection,
  formatImageUrl,
  formatType,
  levelTagMap
} from '../utils/dicts'

const route = useRoute()
const loading = ref(false)
const detail = ref(null)

const directionOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 28, right: 16, top: 30, bottom: 26 },
  xAxis: {
    type: 'category',
    data: (detail.value?.charts?.direction_scores || []).map((item) => formatDirection(item.direction)),
    axisLine: { lineStyle: { color: '#b6c2d1' } }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#edf2f7' } }
  },
  series: [
    {
      type: 'bar',
      barWidth: 32,
      data: (detail.value?.charts?.direction_scores || []).map((item) => item.score),
      itemStyle: {
        color: '#2563eb',
        borderRadius: [8, 8, 0, 0]
      }
    }
  ]
}))

const typeOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [
    {
      type: 'pie',
      radius: ['46%', '72%'],
      center: ['50%', '42%'],
      data: (detail.value?.charts?.type_distribution || []).map((item) => ({
        name: formatType(item.name),
        value: item.value
      })),
      label: { formatter: '{b}: {d}%' }
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

onMounted(loadDetail)
watch(() => route.params.id, loadDetail)
</script>

<template>
  <div class="page-view" v-loading="loading">
    <div class="page-head">
      <div>
        <div class="page-title">检测结果详情</div>
        <div class="page-desc">查看任务基本信息、四向识别摘要、综合评分和治理建议。</div>
      </div>
      <div v-if="detail" class="score-highlight">
        <span>{{ detail.total_score }}</span>
        <el-tag size="large" :type="levelTagMap[detail.level] || 'info'">{{ detail.level }}</el-tag>
      </div>
    </div>

    <template v-if="detail">
      <div class="metric-row">
        <div class="metric-box">
          <div class="metric-label">综合总分</div>
          <div class="metric-value">{{ detail.total_score }}</div>
        </div>
        <div class="metric-box">
          <div class="metric-label">蓝光风险</div>
          <div class="metric-value">{{ detail.blue_risk ? '存在' : '无明显风险' }}</div>
        </div>
        <div class="metric-box">
          <div class="metric-label">预警状态</div>
          <div class="metric-value">{{ detail.warning?.warning_level || '正常' }}</div>
        </div>
      </div>

      <PanelCard title="任务基本信息">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="任务 ID">{{ detail.id }}</el-descriptions-item>
          <el-descriptions-item label="任务编号">{{ detail.task_no }}</el-descriptions-item>
          <el-descriptions-item label="任务状态">{{ detail.status }}</el-descriptions-item>
          <el-descriptions-item label="地点名称">{{ detail.location_name }}</el-descriptions-item>
          <el-descriptions-item label="经纬度">{{ detail.longitude }}, {{ detail.latitude }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(detail.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="卫星评分">{{ detail.satellite_score }}</el-descriptions-item>
          <el-descriptions-item label="生态评分">{{ detail.ecology_score }}</el-descriptions-item>
          <el-descriptions-item label="图像评分">{{ detail.image_score }}</el-descriptions-item>
          <el-descriptions-item label="区域识别">{{ detail.geo_info?.region_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="土地利用">{{ detail.ecology_info?.land_use_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="卫星亮度">{{ detail.satellite_info?.brightness_value || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注信息" :span="3">{{ detail.remark || '-' }}</el-descriptions-item>
        </el-descriptions>
      </PanelCard>

      <PanelCard title="四方向原图预览">
        <div class="image-grid">
          <div v-for="item in detail.images" :key="item.id" class="image-card">
            <el-image
              :src="formatImageUrl(item.file_url)"
              fit="cover"
              style="width: 100%; height: 220px;"
              :preview-src-list="detail.images.map((img) => formatImageUrl(img.file_url))"
            />
            <div class="image-caption">
              <span>{{ formatDirection(item.direction) }}</span>
              <span>{{ item.original_name }}</span>
            </div>
          </div>
        </div>
      </PanelCard>

      <PanelCard title="四方向识别摘要">
        <el-row :gutter="16">
          <el-col v-for="item in detail.direction_summaries" :key="item.direction" :md="12" :sm="24" style="margin-bottom: 16px;">
            <div class="panel-card" style="border-radius: 16px;">
              <div class="panel-body">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                  <div style="font-size: 16px; font-weight: 700;">{{ formatDirection(item.direction) }}</div>
                  <el-tag :type="item.blue_risk ? 'danger' : 'success'">
                    {{ item.blue_risk ? '蓝光风险' : '风险较低' }}
                  </el-tag>
                </div>
                <div style="margin-bottom: 14px; color: #5d6e86;">方向评分：{{ item.score }}</div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                  <el-tag v-for="obj in item.objects" :key="`${item.direction}-${obj.label}-${obj.confidence}`" effect="plain">
                    {{ formatType(obj.label) }} {{ obj.confidence }}
                  </el-tag>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </PanelCard>

      <div class="two-col-grid">
        <PanelCard title="四方向评分对比">
          <EChartPanel :option="directionOption" />
        </PanelCard>
        <PanelCard title="污染类型占比">
          <EChartPanel :option="typeOption" />
        </PanelCard>
      </div>

      <PanelCard title="治理建议">
        <ul class="info-list">
          <li v-for="item in detail.suggestions" :key="item">{{ item }}</li>
        </ul>
      </PanelCard>
    </template>
  </div>
</template>
