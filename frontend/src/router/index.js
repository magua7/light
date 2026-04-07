import { createRouter, createWebHashHistory } from 'vue-router'

import MainLayout from '../layout/MainLayout.vue'
import Dashboard from '../views/Dashboard.vue'
import MapMonitor from '../views/MapMonitor.vue'
import TaskCreate from '../views/TaskCreate.vue'
import TaskDetail from '../views/TaskDetail.vue'
import TaskHistory from '../views/TaskHistory.vue'
import WarningList from '../views/WarningList.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      redirect: '/dashboard',
      children: [
        {
          path: '/dashboard',
          name: 'dashboard',
          component: Dashboard,
          meta: { title: '首页大屏' }
        },
        {
          path: '/tasks/create',
          name: 'task-create',
          component: TaskCreate,
          meta: { title: '上传检测' }
        },
        {
          path: '/tasks/:id',
          name: 'task-detail',
          component: TaskDetail,
          meta: { title: '检测详情' }
        },
        {
          path: '/tasks/history',
          name: 'task-history',
          component: TaskHistory,
          meta: { title: '历史记录' }
        },
        {
          path: '/map-monitor',
          name: 'map-monitor',
          component: MapMonitor,
          meta: { title: '地图监测' }
        },
        {
          path: '/warnings',
          name: 'warning-list',
          component: WarningList,
          meta: { title: '预警列表' }
        }
      ]
    }
  ]
})

export default router
