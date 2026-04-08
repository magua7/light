<script setup>
import { Lock, StarFilled, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { checkBackendHealth, loginAccount, registerAccount } from '../api/auth'
import { persistAuth } from '../utils/auth'
import { BRAND_FULL_NAME, BRAND_SLOGAN } from '../utils/dicts'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const activeTab = ref('login')

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const redirectPath = computed(() => route.query.redirect || '/dashboard')

async function ensureBackendAvailable() {
  try {
    await checkBackendHealth()
    return true
  } catch {
    ElMessage.error('后端当前未正常响应，请先确认后端已启动；如果 8000 端口被旧 Python 进程占用，请先结束旧进程后再重试。')
    return false
  }
}

async function handleLogin() {
  if (!loginForm.username.trim() || !loginForm.password.trim()) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    const backendReady = await ensureBackendAvailable()
    if (!backendReady) return

    if (import.meta.env.DEV) {
      console.info('[auth] POST /api/auth/login')
    }

    const data = await loginAccount({
      username: loginForm.username.trim(),
      password: loginForm.password
    })
    persistAuth(data.access_token, data.user)
    ElMessage.success('登录成功')
    router.push(redirectPath.value)
  } catch (error) {
    if (import.meta.env.DEV) {
      console.warn('[auth] login request failed', error)
    }
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!registerForm.username.trim() || !registerForm.password.trim() || !registerForm.confirmPassword.trim()) {
    ElMessage.warning('请完整填写注册信息')
    return
  }

  if (registerForm.password.length < 6) {
    ElMessage.warning('密码长度至少为 6 位')
    return
  }

  if (registerForm.password !== registerForm.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  loading.value = true
  try {
    const backendReady = await ensureBackendAvailable()
    if (!backendReady) return

    if (import.meta.env.DEV) {
      console.info('[auth] POST /api/auth/register')
    }

    await registerAccount({
      username: registerForm.username.trim(),
      password: registerForm.password
    })
    ElMessage.success('注册成功，请登录')
    loginForm.username = registerForm.username.trim()
    loginForm.password = ''
    registerForm.username = ''
    registerForm.password = ''
    registerForm.confirmPassword = ''
    activeTab.value = 'login'
  } catch (error) {
    if (import.meta.env.DEV) {
      console.warn('[auth] register request failed', error)
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-page__glow login-page__glow--left"></div>
    <div class="login-page__glow login-page__glow--right"></div>

    <div class="login-shell">
      <section class="login-hero">
        <div class="login-badge">
          <el-icon><StarFilled /></el-icon>
        </div>
        <h1 class="login-title">{{ BRAND_FULL_NAME }}</h1>
        <p class="login-subtitle">{{ BRAND_SLOGAN }}</p>
      </section>

      <section class="login-panel">
        <el-tabs v-model="activeTab" stretch class="auth-tabs">
          <el-tab-pane label="登录" name="login">
            <el-form
              :model="loginForm"
              label-position="left"
              label-width="76px"
              class="auth-form"
              @submit.prevent="handleLogin"
            >
              <el-form-item label="用户名" class="auth-form__item">
                <el-input
                  v-model="loginForm.username"
                  placeholder="请输入用户名"
                  class="auth-input"
                >
                  <template #prefix>
                    <el-icon><User /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item label="密码" class="auth-form__item">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  show-password
                  placeholder="请输入密码"
                  class="auth-input"
                  @keyup.enter="handleLogin"
                >
                  <template #prefix>
                    <el-icon><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-button type="primary" class="login-submit" :loading="loading" @click="handleLogin">
                登录
              </el-button>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="注册" name="register">
            <el-form
              :model="registerForm"
              label-position="left"
              label-width="76px"
              class="auth-form"
              @submit.prevent="handleRegister"
            >
              <el-form-item label="用户名" class="auth-form__item">
                <el-input
                  v-model="registerForm.username"
                  placeholder="请设置用户名"
                  class="auth-input"
                >
                  <template #prefix>
                    <el-icon><User /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item label="密码" class="auth-form__item">
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  show-password
                  placeholder="请设置至少 6 位密码"
                  class="auth-input"
                >
                  <template #prefix>
                    <el-icon><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item label="确认密码" class="auth-form__item">
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  show-password
                  placeholder="请再次输入密码"
                  class="auth-input"
                  @keyup.enter="handleRegister"
                >
                  <template #prefix>
                    <el-icon><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-button type="primary" class="login-submit" :loading="loading" @click="handleRegister">
                注册账号
              </el-button>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </section>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  padding: 48px 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.login-page__glow {
  position: absolute;
  border-radius: 999px;
  filter: blur(72px);
  opacity: 0.32;
}

.login-page__glow--left {
  width: 440px;
  height: 440px;
  left: -120px;
  top: 80px;
  background: rgba(226, 232, 244, 0.08);
}

.login-page__glow--right {
  width: 360px;
  height: 360px;
  right: -80px;
  bottom: 40px;
  background: rgba(196, 157, 103, 0.12);
}

.login-shell {
  position: relative;
  z-index: 1;
  width: min(1120px, 100%);
  display: grid;
  grid-template-columns: 1.15fr 420px;
  gap: 24px;
}

.login-hero,
.login-panel {
  padding: 40px;
  border-radius: 30px;
  background: rgba(12, 16, 22, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.32);
  backdrop-filter: blur(16px);
}

.login-hero {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 520px;
}

.login-badge {
  width: 62px;
  height: 62px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 20px;
  background: rgba(241, 237, 230, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #f1ede6;
  font-size: 24px;
}

.login-title {
  margin: 26px 0 14px;
  max-width: 12em;
  color: var(--text-main);
  font-size: clamp(2.2rem, 3vw, 3.5rem);
  line-height: 1.22;
  letter-spacing: 0.01em;
  text-wrap: balance;
}

.login-subtitle {
  margin: 0;
  max-width: 22em;
  color: var(--text-sub);
  font-size: 16px;
  line-height: 1.9;
}

.login-panel {
  align-self: center;
}

.auth-form {
  margin-top: 10px;
}

.auth-form__item {
  margin-bottom: 18px;
}

.login-submit {
  width: 100%;
  height: 46px;
  margin-top: 10px;
}

:deep(.auth-form .el-form-item__label) {
  justify-content: flex-start;
  padding-right: 14px;
  color: var(--text-sub);
  line-height: 46px;
}

:deep(.auth-form .el-form-item__content) {
  min-width: 0;
}

:deep(.auth-form .el-input) {
  width: 100%;
}

:deep(.auth-form .el-input__wrapper) {
  min-height: 46px;
  padding-left: 12px;
  padding-right: 12px;
}

:deep(.auth-form .el-input__prefix-inner),
:deep(.auth-form .el-input__suffix-inner) {
  display: inline-flex;
  align-items: center;
}

:deep(.auth-form .el-input__suffix-inner) {
  min-width: 18px;
}

:deep(.auth-tabs .el-tabs__header) {
  margin-bottom: 22px;
}

:deep(.auth-tabs .el-tabs__nav-wrap::after) {
  background: rgba(255, 255, 255, 0.08);
}

:deep(.auth-tabs .el-tabs__item) {
  color: var(--text-muted);
  font-size: 15px;
}

:deep(.auth-tabs .el-tabs__item.is-active) {
  color: var(--text-main);
}

:deep(.auth-tabs .el-tabs__active-bar) {
  background: var(--accent-main);
}

@media (max-width: 960px) {
  .login-shell {
    grid-template-columns: 1fr;
  }

  .login-hero,
  .login-panel {
    padding: 28px;
  }

  .login-hero {
    min-height: 280px;
  }

  .login-title {
    max-width: none;
  }
}
</style>
