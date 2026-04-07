import { createRouter, createWebHashHistory } from 'vue-router'

import { fetchCurrentUser } from '../api/auth'
import MainLayout from '../layout/MainLayout.vue'
import { clearAuth, getCurrentUser, getToken, isLoggedIn, setCurrentUser } from '../utils/auth'
import Dashboard from '../views/Dashboard.vue'
import Login from '../views/Login.vue'
import MapMonitor from '../views/MapMonitor.vue'
import TaskCreate from '../views/TaskCreate.vue'
import TaskDetail from '../views/TaskDetail.vue'
import TaskHistory from '../views/TaskHistory.vue'
import WarningList from '../views/WarningList.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: {
        title: '登录',
        public: true
      }
    },
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
          meta: { title: '检测报告' }
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

let verifiedToken = ''
let authCheckTask = null

async function ensureAuthenticated() {
  const token = getToken()
  if (!token) return false

  if (verifiedToken === token && getCurrentUser()) {
    return true
  }

  if (!authCheckTask) {
    authCheckTask = fetchCurrentUser({ silentError: true, skipAuthCleanup: true })
      .then((user) => {
        setCurrentUser(user)
        verifiedToken = token
        return true
      })
      .catch(() => {
        clearAuth()
        verifiedToken = ''
        return false
      })
      .finally(() => {
        authCheckTask = null
      })
  }

  return authCheckTask
}

router.beforeEach(async (to) => {
  const publicPage = to.meta.public === true
  if (!publicPage && !isLoggedIn()) {
    return {
      path: '/login',
      query: { redirect: to.fullPath }
    }
  }

  if (publicPage) {
    if (!isLoggedIn()) return true
    const authenticated = await ensureAuthenticated()
    if (authenticated && to.path === '/login') {
      return '/dashboard'
    }
    return true
  }

  const authenticated = await ensureAuthenticated()
  if (!authenticated) {
    return {
      path: '/login',
      query: { redirect: to.fullPath }
    }
  }

  return true
})

export default router
