<script setup>
import {
  DataAnalysis,
  Location,
  Opportunity,
  StarFilled,
  SwitchButton,
  UploadFilled,
  Warning
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { logoutAccount } from '../api/auth'
import { clearAuth, getLoginUser } from '../utils/auth'
import { BRAND_FULL_NAME, BRAND_NAV_NAME, BRAND_SHORT_NAME } from '../utils/dicts'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => {
  if (route.path.startsWith('/tasks/create')) return '/tasks/create'
  if (route.path.startsWith('/tasks/history') || /^\/tasks\/\d+/.test(route.path)) return '/tasks/history'
  if (route.path.startsWith('/map-monitor')) return '/map-monitor'
  if (route.path.startsWith('/warnings')) return '/warnings'
  return '/dashboard'
})

const loginUser = computed(() => getLoginUser() || '未命名用户')

async function handleLogout() {
  try {
    await logoutAccount()
  } catch {
    // 即使后端登出失败，也要保证本地登录态被清理
  } finally {
    clearAuth()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}
</script>

<template>
  <el-container class="app-shell">
    <el-aside class="app-aside" width="252px">
      <div class="brand-wrap">
        <div class="brand-badge">
          <el-icon><StarFilled /></el-icon>
        </div>
        <div>
          <div class="brand-title">{{ BRAND_SHORT_NAME }}</div>
          <div class="brand-subtitle">{{ BRAND_NAV_NAME }}</div>
        </div>
      </div>

      <el-menu :default-active="activeMenu" router class="app-menu">
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>首页大屏</span>
        </el-menu-item>
        <el-menu-item index="/tasks/create">
          <el-icon><UploadFilled /></el-icon>
          <span>上传检测</span>
        </el-menu-item>
        <el-menu-item index="/tasks/history">
          <el-icon><Opportunity /></el-icon>
          <span>历史记录</span>
        </el-menu-item>
        <el-menu-item index="/map-monitor">
          <el-icon><Location /></el-icon>
          <span>地图监测</span>
        </el-menu-item>
        <el-menu-item index="/warnings">
          <el-icon><Warning /></el-icon>
          <span>预警列表</span>
        </el-menu-item>
      </el-menu>

      <div class="aside-footer">
        <div class="aside-footer__label">示例区域</div>
        <div class="aside-footer__value">湖南 · 长沙夜间光环境</div>
      </div>
    </el-aside>

    <el-container class="app-stage">
      <el-header class="app-header">
        <div class="header-content">
          <div class="header-kicker">{{ BRAND_FULL_NAME }}</div>
        </div>
        <div class="header-actions">
          <div class="header-userbox">
            <div class="header-userlabel">当前账号</div>
            <div class="header-user">{{ loginUser }}</div>
          </div>
          <el-button class="header-logout" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </el-button>
        </div>
      </el-header>

      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
