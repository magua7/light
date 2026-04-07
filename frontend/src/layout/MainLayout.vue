<script setup>
import {
  DataAnalysis,
  Location,
  Opportunity,
  UploadFilled,
  Warning
} from '@element-plus/icons-vue'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const activeMenu = computed(() => {
  if (route.path.startsWith('/tasks/create')) return '/tasks/create'
  if (route.path.startsWith('/tasks/history') || /^\/tasks\/\d+/.test(route.path)) return '/tasks/history'
  if (route.path.startsWith('/map-monitor')) return '/map-monitor'
  if (route.path.startsWith('/warnings')) return '/warnings'
  return '/dashboard'
})
</script>

<template>
  <el-container class="app-shell">
    <el-aside class="app-aside" width="240px">
      <div class="brand-wrap">
        <div class="brand-badge">LI</div>
        <div>
          <div class="brand-title">Light Inspector</div>
          <div class="brand-subtitle">城市光污染监测平台</div>
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
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <div>
          <div class="header-title">城市光污染监测与智能评级系统</div>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
