<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchTaskList } from '../api/tasks'
import PanelCard from '../components/PanelCard.vue'
import { formatCoordinate, formatDateTime, levelTagMap } from '../utils/dicts'

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
        <div class="page-desc">
          回看已完成的检测任务，支持按地点、评级和时间范围筛选，
          便于在演示时快速定位代表性样本并进入报告页。
        </div>
      </div>
    </div>

    <PanelCard title="筛选条件" subtitle="输入关键词、选择评级和时间范围后即可筛选历史样本。">
      <div class="filter-grid">
        <el-input v-model="filters.keyword" placeholder="请输入地点名称或任务编号关键词" clearable />

        <el-select v-model="filters.level" placeholder="请选择评级" clearable>
          <el-option label="优" value="优" />
          <el-option label="良" value="良" />
          <el-option label="中" value="中" />
          <el-option label="较差" value="较差" />
          <el-option label="差" value="差" />
        </el-select>

        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          value-format="YYYY-MM-DD"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        />

        <div class="action-group">
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </div>
      </div>
    </PanelCard>

    <PanelCard title="任务列表" subtitle="保留经纬度、等级、蓝光风险等核心信息，适合投屏查看。">
      <template #extra>
        <span class="panel-note">共 {{ total }} 条</span>
      </template>

      <el-table :data="tableData" v-loading="loading">
        <el-table-column prop="task_no" label="任务编号" min-width="180">
          <template #default="{ row }">
            <span class="task-no">{{ row.task_no }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="location_name" label="地点名称" min-width="170" />
        <el-table-column label="经纬度" min-width="190">
          <template #default="{ row }">
            <span class="coordinate-text">{{ formatCoordinate(row.longitude, row.latitude) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="评分" width="100">
          <template #default="{ row }">
            <span class="score-text">{{ row.total_score ?? '-' }}</span>
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
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button class="table-action-btn" @click="goDetail(row.id)">查看报告</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="table-pagination">
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

<style scoped>
.filter-grid {
  display: grid;
  grid-template-columns: 1.3fr 0.9fr 1.1fr auto;
  gap: 16px;
}

.task-no,
.score-text,
.coordinate-text {
  color: var(--text-main);
  font-weight: 600;
}

.table-pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 960px) {
  .filter-grid {
    grid-template-columns: 1fr;
  }
}
</style>
