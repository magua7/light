<script setup>
import { Delete, Picture, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed, onBeforeUnmount, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { createTask } from '../api/tasks'
import PanelCard from '../components/PanelCard.vue'
import { normalizeCoordinateInput } from '../utils/dicts'

const router = useRouter()
const loading = ref(false)
const fileInputRef = ref(null)
const dragActive = ref(false)
const formRef = ref(null)
let uploadSeed = 0

const form = reactive({
  location_name: '',
  longitude: '',
  latitude: '',
  remark: ''
})

const uploadFiles = ref([])

const hasEnoughImages = computed(() => uploadFiles.value.length >= 4)

function buildCoordinateValidator(fieldName, minValue, maxValue) {
  return (_rule, value, callback) => {
    const normalized = normalizeCoordinateInput(value)
    if (!normalized) {
      callback(new Error(`${fieldName}必须为小数点后恰好 4 位`))
      return
    }
    const numeric = Number(normalized)
    if (numeric < minValue || numeric > maxValue) {
      callback(new Error(`${fieldName}超出范围，应位于 ${minValue} 到 ${maxValue} 之间`))
      return
    }
    callback()
  }
}

const rules = {
  longitude: [
    { required: true, message: '请输入经度', trigger: 'blur' },
    { validator: buildCoordinateValidator('经度', -180, 180), trigger: ['blur', 'change'] }
  ],
  latitude: [
    { required: true, message: '请输入纬度', trigger: 'blur' },
    { validator: buildCoordinateValidator('纬度', -90, 90), trigger: ['blur', 'change'] }
  ]
}

function selectAllInput(event) {
  event?.target?.select?.()
}

function openFileDialog() {
  fileInputRef.value?.click()
}

function createPreviewItem(file) {
  return {
    id: `sample-${Date.now()}-${uploadSeed++}`,
    name: file.name,
    size: file.size,
    raw: file,
    preview: URL.createObjectURL(file)
  }
}

function appendFiles(fileList) {
  const files = Array.from(fileList || []).filter((file) => file.type.startsWith('image/'))
  if (!files.length) return

  const remaining = 12 - uploadFiles.value.length
  const accepted = files.slice(0, remaining)
  if (accepted.length < files.length) {
    ElMessage.warning('最多保留 12 张夜景样本图片')
  }

  uploadFiles.value = [...uploadFiles.value, ...accepted.map(createPreviewItem)]
}

function handleInputChange(event) {
  appendFiles(event.target.files)
  event.target.value = ''
}

function handleDrop(event) {
  event.preventDefault()
  dragActive.value = false
  appendFiles(event.dataTransfer?.files)
}

function removeUpload(id) {
  const target = uploadFiles.value.find((item) => item.id === id)
  if (target?.preview) {
    URL.revokeObjectURL(target.preview)
  }
  uploadFiles.value = uploadFiles.value.filter((item) => item.id !== id)
}

function normalizeCoordinateField(field) {
  const normalized = normalizeCoordinateInput(form[field])
  if (normalized) {
    form[field] = normalized
  }
}

async function submitTask() {
  const isValid = await formRef.value?.validate?.().catch(() => false)
  if (!isValid) {
    ElMessage.warning('请按要求填写经纬度，且必须保留 4 位小数')
    return
  }

  if (!hasEnoughImages.value) {
    ElMessage.warning('请最少上传四张夜景图片')
    return
  }

  const longitude = normalizeCoordinateInput(form.longitude)
  const latitude = normalizeCoordinateInput(form.latitude)
  if (!longitude || !latitude) {
    ElMessage.warning('经纬度必须为小数点后恰好 4 位')
    return
  }

  const payload = new FormData()
  payload.append('longitude', longitude)
  payload.append('latitude', latitude)
  if (form.location_name.trim()) payload.append('location_name', form.location_name.trim())
  if (form.remark.trim()) payload.append('remark', form.remark.trim())

  uploadFiles.value.forEach((item) => {
    payload.append('images', item.raw)
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

onBeforeUnmount(() => {
  uploadFiles.value.forEach((item) => {
    if (item.preview) URL.revokeObjectURL(item.preview)
  })
})
</script>

<template>
  <div class="page-view">
    <div class="page-head">
      <div>
        <div class="page-title">上传检测</div>
        <div class="page-desc">上传夜景样本并补充点位信息，系统将基于全部样本生成检测报告。</div>
      </div>
      <div class="page-actions">
        <el-button type="primary" :loading="loading" @click="submitTask">提交并生成报告</el-button>
      </div>
    </div>

    <PanelCard title="监测点信息">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="96px">
        <div class="create-form-grid">
          <el-form-item label="地点名称" class="create-form-grid__wide">
            <el-input v-model="form.location_name" placeholder="例如：五一广场商圈、湘江观景长廊" />
          </el-form-item>

          <el-form-item label="经度" prop="longitude">
            <el-input
              v-model="form.longitude"
              placeholder="请输入经度"
              @focus="selectAllInput"
              @blur="normalizeCoordinateField('longitude')"
            />
          </el-form-item>

          <el-form-item label="纬度" prop="latitude">
            <el-input
              v-model="form.latitude"
              placeholder="请输入纬度"
              @focus="selectAllInput"
              @blur="normalizeCoordinateField('latitude')"
            />
          </el-form-item>

          <div class="coordinate-hint">默认东经和北纬</div>

          <el-form-item label="备注信息" class="create-form-grid__wide">
            <el-input
              v-model="form.remark"
              type="textarea"
              :rows="4"
              placeholder="可补充监测背景、采集说明或现场关注点"
            />
          </el-form-item>
        </div>
      </el-form>
    </PanelCard>

    <PanelCard title="夜景样本上传">
      <div class="upload-headline">请最少上传四张夜景图片</div>
      <div
        class="unified-upload"
        :class="{ 'is-drag-active': dragActive }"
        @dragover.prevent="dragActive = true"
        @dragleave.prevent="dragActive = false"
        @drop="handleDrop"
      >
        <input
          ref="fileInputRef"
          class="unified-upload__input"
          type="file"
          accept=".jpg,.jpeg,.png,image/jpeg,image/png"
          multiple
          @change="handleInputChange"
        />
        <div class="unified-upload__icon">
          <el-icon><UploadFilled /></el-icon>
        </div>
        <div class="unified-upload__title">点击或拖拽上传夜景样本图片</div>
        <div class="unified-upload__desc">支持 jpg / jpeg / png，可连续上传多张图片，系统将基于全部上传样本完成分析。</div>
        <el-button class="unified-upload__button" @click="openFileDialog">选择图片</el-button>
      </div>

      <div v-if="uploadFiles.length" class="sample-list">
        <div class="sample-list__head">
          <div class="sample-list__title">已选样本</div>
          <div class="sample-list__hint">当前已上传 {{ uploadFiles.length }} 张，所有样本都会参与本次分析。</div>
        </div>

        <div class="sample-grid">
          <article v-for="(item, index) in uploadFiles" :key="item.id" class="sample-card">
            <el-image :src="item.preview" fit="cover" class="sample-card__media" />
            <div class="sample-card__body">
              <div class="sample-card__title">
                <span>{{ `图片${index + 1}` }}</span>
                <el-tag v-if="index < 4" size="small" type="warning">核心样本</el-tag>
              </div>
              <div class="sample-card__name">{{ item.name }}</div>
            </div>
            <el-button class="sample-card__remove" circle @click="removeUpload(item.id)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </article>
        </div>
      </div>

      <div v-else class="empty-state">
        <el-icon><Picture /></el-icon>
        <span>暂未选择样本图片</span>
      </div>
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

.coordinate-hint {
  grid-column: 1 / -1;
  margin: -8px 0 14px 96px;
  color: var(--text-muted);
  font-size: 12px;
}

:deep(.el-form-item.is-error .el-input__wrapper) {
  box-shadow: 0 0 0 1px rgba(241, 102, 102, 0.88) inset;
}

.upload-headline {
  margin-bottom: 14px;
  color: var(--text-sub);
  font-size: 14px;
}

.unified-upload {
  position: relative;
  display: grid;
  justify-items: center;
  gap: 10px;
  padding: 34px 24px;
  border-radius: 24px;
  border: 1px dashed rgba(236, 231, 223, 0.2);
  background: rgba(17, 21, 28, 0.46);
  text-align: center;
  transition: border-color 0.2s ease, background 0.2s ease, transform 0.2s ease;
}

.unified-upload.is-drag-active {
  border-color: rgba(236, 231, 223, 0.38);
  background: rgba(23, 29, 37, 0.62);
  transform: translateY(-1px);
}

.unified-upload__input {
  display: none;
}

.unified-upload__icon {
  width: 58px;
  height: 58px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
  background: rgba(236, 231, 223, 0.08);
  color: var(--accent-main);
  font-size: 26px;
}

.unified-upload__title {
  font-size: 20px;
  font-weight: 700;
}

.unified-upload__desc {
  max-width: 560px;
  color: var(--text-sub);
  font-size: 14px;
  line-height: 1.8;
}

.unified-upload__button {
  min-width: 124px;
  margin-top: 8px;
}

.sample-list {
  margin-top: 22px;
}

.sample-list__head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.sample-list__title {
  font-size: 18px;
  font-weight: 700;
}

.sample-list__hint {
  color: var(--text-muted);
  font-size: 13px;
}

.sample-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.sample-card {
  position: relative;
  overflow: hidden;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(22, 27, 35, 0.68);
}

.sample-card__media {
  width: 100%;
  height: 220px;
  display: block;
}

.sample-card__body {
  padding: 14px 16px 16px;
}

.sample-card__title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  font-weight: 700;
}

.sample-card__name {
  margin-top: 8px;
  color: var(--text-sub);
  font-size: 13px;
  line-height: 1.7;
  word-break: break-all;
}

.sample-card__remove {
  position: absolute;
  top: 12px;
  right: 12px;
}

.empty-state {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 18px;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .create-form-grid,
  .sample-grid {
    grid-template-columns: 1fr;
  }

  .create-form-grid__wide {
    grid-column: auto;
  }

  .coordinate-hint {
    margin-left: 0;
  }

  .sample-list__head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
