<script setup>
import { Plus } from '@element-plus/icons-vue'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { createTask } from '../api/tasks'
import PanelCard from '../components/PanelCard.vue'
import { formatDirection } from '../utils/dicts'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  location_name: '',
  longitude: 121.487,
  latitude: 31.238,
  remark: ''
})

const fileStore = reactive({
  east: null,
  south: null,
  west: null,
  north: null
})

const directions = [
  { key: 'east', title: '东向图片' },
  { key: 'south', title: '南向图片' },
  { key: 'west', title: '西向图片' },
  { key: 'north', title: '北向图片' }
]

function handleFileChange(direction, file) {
  fileStore[direction] = file.raw
}

function handleFileRemove(direction) {
  fileStore[direction] = null
}

async function submitTask() {
  if (!form.longitude || !form.latitude) {
    ElMessage.warning('请填写经纬度')
    return
  }

  const missing = directions.filter((item) => !fileStore[item.key])
  if (missing.length) {
    ElMessage.warning(`请上传完整的四个方向图片，缺少：${missing.map((item) => formatDirection(item.key)).join('、')}`)
    return
  }

  const payload = new FormData()
  payload.append('longitude', String(form.longitude))
  payload.append('latitude', String(form.latitude))
  if (form.location_name) payload.append('location_name', form.location_name)
  if (form.remark) payload.append('remark', form.remark)
  directions.forEach((item) => {
    payload.append(`${item.key}_image`, fileStore[item.key])
  })

  loading.value = true
  try {
    const data = await createTask(payload)
    ElMessage.success('检测任务创建成功')
    router.push(`/tasks/${data.id}`)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page-view">
    <div class="page-head">
      <div>
        <div class="page-title">上传检测任务</div>
        <div class="page-desc">上传东南西北四个方向夜景图片，并录入检测点基础信息。</div>
      </div>
      <el-button type="primary" :loading="loading" @click="submitTask">开始检测</el-button>
    </div>

    <PanelCard title="任务信息">
      <el-form label-width="100px">
        <el-row :gutter="18">
          <el-col :md="12" :sm="24">
            <el-form-item label="地点名称">
              <el-input v-model="form.location_name" placeholder="可选，例如：解放广场商圈" />
            </el-form-item>
          </el-col>
          <el-col :md="6" :sm="24">
            <el-form-item label="经度">
              <el-input-number v-model="form.longitude" :precision="6" :step="0.001" :controls="false" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :md="6" :sm="24">
            <el-form-item label="纬度">
              <el-input-number v-model="form.latitude" :precision="6" :step="0.001" :controls="false" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注信息">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="可选，填写巡检背景、监测说明等" />
        </el-form-item>
      </el-form>
    </PanelCard>

    <PanelCard title="四方向夜景图片">
      <div class="upload-grid">
        <div v-for="item in directions" :key="item.key">
          <div style="margin-bottom: 10px; font-weight: 600;">{{ item.title }}</div>
          <el-upload
            action="#"
            :auto-upload="false"
            list-type="picture-card"
            accept="image/*"
            :limit="1"
            :on-change="(file) => handleFileChange(item.key, file)"
            :on-remove="() => handleFileRemove(item.key)"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </div>
      </div>
      <el-alert
        title="当前 AI 检测为 mock 接口，后续可直接替换为真实模型服务，不影响前端提交流程。"
        type="info"
        :closable="false"
        style="margin-top: 16px;"
      />
    </PanelCard>
  </div>
</template>
