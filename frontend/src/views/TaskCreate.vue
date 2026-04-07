<script setup>
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { createTask } from '../api/tasks'
import PanelCard from '../components/PanelCard.vue'
import { formatDirection, imageSlotOptions } from '../utils/dicts'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  location_name: '',
  longitude: 112.9388,
  latitude: 28.2282,
  remark: ''
})

const fileStore = reactive({
  east: null,
  south: null,
  west: null,
  north: null
})

function handleFileChange(direction, file) {
  fileStore[direction] = file.raw
}

function handleFileRemove(direction) {
  fileStore[direction] = null
}

function handleExceed() {
  ElMessage.warning('每个上传位只需要 1 张图片')
}

async function submitTask() {
  if (!form.longitude || !form.latitude) {
    ElMessage.warning('请填写完整的经纬度信息')
    return
  }

  const missing = imageSlotOptions.filter((item) => !fileStore[item.key])
  if (missing.length) {
    ElMessage.warning(`请补齐 4 张图片，当前缺少：${missing.map((item) => formatDirection(item.key)).join('、')}`)
    return
  }

  const payload = new FormData()
  payload.append('longitude', String(form.longitude))
  payload.append('latitude', String(form.latitude))
  if (form.location_name) payload.append('location_name', form.location_name)
  if (form.remark) payload.append('remark', form.remark)
  imageSlotOptions.forEach((item) => {
    payload.append(`${item.key}_image`, fileStore[item.key])
  })

  loading.value = true
  try {
    const data = await createTask(payload)
    ElMessage.success('检测任务已提交，正在进入报告页')
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
        <div class="page-title">上传检测</div>
        <div class="page-desc">
          上传 4 张夜景样本图并录入监测点基础信息，系统将调用 mock AI 与环境数据服务，
          生成一份适合答辩展示的检测报告。
        </div>
      </div>
      <div class="page-actions">
        <el-button type="primary" :loading="loading" @click="submitTask">提交并生成报告</el-button>
      </div>
    </div>

    <PanelCard title="监测点信息" subtitle="建议优先录入地点名称与精准经纬度，便于地图展示和报告表达。">
      <el-form label-width="96px">
        <div class="create-form-grid">
          <el-form-item label="地点名称" class="create-form-grid__wide">
            <el-input v-model="form.location_name" placeholder="例如：五一广场商圈、湘江观景平台" />
          </el-form-item>

          <el-form-item label="经度">
            <el-input-number
              v-model="form.longitude"
              :precision="6"
              :step="0.001"
              :controls="false"
              class="full-width"
            />
          </el-form-item>

          <el-form-item label="纬度">
            <el-input-number
              v-model="form.latitude"
              :precision="6"
              :step="0.001"
              :controls="false"
              class="full-width"
            />
          </el-form-item>

          <el-form-item label="备注信息" class="create-form-grid__wide">
            <el-input
              v-model="form.remark"
              type="textarea"
              :rows="4"
              placeholder="可补充监测背景、采集说明或巡检重点。"
            />
          </el-form-item>
        </div>
      </el-form>
    </PanelCard>

    <PanelCard title="图片样本上传" subtitle="请依次上传 4 张夜景图片。支持 jpg / jpeg / png，后端字段仍兼容原 east/south/west/north 接口。">
      <div class="upload-grid">
        <div v-for="item in imageSlotOptions" :key="item.key" class="upload-slot">
          <div class="upload-slot__head">
            <div class="upload-slot__title">{{ item.title }}</div>
            <div class="upload-slot__hint">支持 jpg / jpeg / png</div>
          </div>

          <el-upload
            action="#"
            :auto-upload="false"
            list-type="picture-card"
            accept=".jpg,.jpeg,.png,image/jpeg,image/png"
            :limit="1"
            :on-exceed="handleExceed"
            :on-change="(file) => handleFileChange(item.key, file)"
            :on-remove="() => handleFileRemove(item.key)"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </div>
      </div>

      <el-alert
        title="当前 AI 分析、卫星亮度与生态脆弱度均为 mock 服务，已预留独立接口层，便于后续替换为真实模型与 GIS 数据源。"
        type="info"
        :closable="false"
      />
    </PanelCard>
  </div>
</template>

<style scoped>
.create-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 18px;
}

.create-form-grid__wide {
  grid-column: 1 / -1;
}

.upload-slot {
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.upload-slot__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.upload-slot__title {
  font-size: 16px;
  font-weight: 700;
}

.upload-slot__hint {
  color: var(--text-muted);
  font-size: 12px;
}

@media (max-width: 768px) {
  .create-form-grid {
    grid-template-columns: 1fr;
  }

  .create-form-grid__wide {
    grid-column: auto;
  }

  .upload-slot__head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
