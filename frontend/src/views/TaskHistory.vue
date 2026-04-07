<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchTaskList } from '../api/tasks'
import PanelCard from '../components/PanelCard.vue'
import { formatDateTime, levelTagMap } from '../utils/dicts'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const total = ref(0)

const filters = reactive({
  keyword: '',
  level: '',
  dateRange: []
})

const pagination = reactive({
  page: 1,
  page_size: 10
})

async function loadTasks() {
  loading.value = true
  try {
    const [startTime, endTime] = filters.dateRange || []
    const data = await fetchTaskList({
      page: pagination.page,
      page_size: pagination.page_size,
      keyword: filters.keyword || undefined,
      level: filters.level || undefined,
      start_time: startTime || undefined,
      end_time: endTime || undefined
    })
    tableData.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadTasks()
}

function handleReset() {
  filters.keyword = ''
  filters.level = ''
  filters.dateRange = []
  pagination.page = 1
  loadTasks()
}

function handleSizeChange(size) {
  pagination.page_size = size
  pagination.page = 1
  loadTasks()
}

function handleCurrentChange(page) {
  pagination.page = page
  loadTasks()
}

function goDetail(id) {
  router.push(`/tasks/${id}`)
}

onMounted(loadTasks)
</script>

<template>
  <div class="page-view">
    <div class="page-head">
      <div>
        <div class="page-title">历史记录</div>
        <div class="page-desc">支持按时间、等级、地点关键字筛选检测任务，并分页查看。</div>
      </div>
    </div>

    <PanelCard title="筛选条件">
      <el-row :gutter="16">
        <el-col :md="8" :sm="24">
          <el-input v-model="filters.keyword" placeholder="请输入地点名称关键字" clearable />
        </el-col>
        <el-col :md="6" :sm="24">
          <el-select v-model="filters.level" placeholder="请选择评级" clearable style="width: 100%;">
            <el-option label="优" value="优" />
            <el-option label="良" value="良" />
            <el-option label="中" value="中" />
            <el-option label="较差" value="较差" />
            <el-option label="差" value="差" />
          </el-select>
        </el-col>
        <el-col :md="7" :sm="24">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%;"
          />
        </el-col>
        <el-col :md="3" :sm="24" style="display: flex; gap: 8px;">
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-col>
      </el-row>
    </PanelCard>

    <PanelCard title="任务列表">
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="task_no" label="任务编号" min-width="180" />
        <el-table-column prop="location_name" label="地点名称" min-width="170" />
        <el-table-column label="经纬度" min-width="180">
          <template #default="{ row }">
            {{ row.longitude }}, {{ row.latitude }}
          </template>
        </el-table-column>
        <el-table-column label="评分" width="100">
          <template #default="{ row }">
            {{ row.total_score ?? '-' }}
          </template>
        </el-table-column>
        <el-table-column label="评级" width="100">
          <template #default="{ row }">
            <el-tag :type="levelTagMap[row.level] || 'info'">{{ row.level || '-' }}</el-tag>
          </template>
        </el-table-column>
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
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="goDetail(row.id)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 18px; display: flex; justify-content: flex-end;">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next"
          :current-page="pagination.page"
          :page-size="pagination.page_size"
          :page-sizes="[10, 20, 30]"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </PanelCard>
  </div>
</template>
