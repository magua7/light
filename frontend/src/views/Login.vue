<script setup>
import { Lock, StarFilled, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { checkBackendHealth, loginAccount, registerAccount } from '../api/auth'
import { persistAuth } from '../utils/auth'
import { BRAND_FORMAL_NAME, BRAND_SHORT_NAME, BRAND_SLOGAN } from '../utils/dicts'

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
    <div class="login-shell">
      <section class="login-hero">
        <div class="login-badge">
          <el-icon><StarFilled /></el-icon>
        </div>

        <div class="login-copy">
          <div class="login-kicker">系统入口</div>
          <h1 class="login-wordmark">{{ BRAND_SHORT_NAME }}</h1>
          <p class="login-title-detail">{{ BRAND_FORMAL_NAME }}</p>
          <p class="login-subtitle">{{ BRAND_SLOGAN }}</p>
        </div>
      </section>

      <section class="login-panel">
        <div class="login-panel__head">
          <div class="login-panel__eyebrow">欢迎使用</div>
          <div class="login-panel__title">登录系统</div>
        </div>

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
  padding: 40px 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-shell {
  position: relative;
  z-index: 1;
  width: min(1128px, 100%);
  display: grid;
  grid-template-columns: minmax(0, 0.98fr) minmax(392px, 440px);
  gap: 36px;
  align-items: center;
}

.login-hero,
.login-panel {
  padding: 40px 38px;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  box-shadow: 0 28px 72px rgba(0, 0, 0, 0.28);
  backdrop-filter: blur(18px);
}

.login-hero {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 500px;
  background:
    linear-gradient(160deg, rgba(14, 19, 26, 0.72) 0%, rgba(11, 16, 22, 0.58) 100%);
}

.login-hero::after {
  content: '';
  position: absolute;
  inset: auto 44px 42px auto;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(196, 157, 103, 0.18) 0%, rgba(196, 157, 103, 0) 72%);
  pointer-events: none;
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

.login-copy {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 500px;
  margin-top: 28px;
}

.login-kicker {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--text-sub);
  font-size: 12px;
  letter-spacing: 0.12em;
}

.login-wordmark {
  margin: 0;
  color: var(--text-main);
  font-size: clamp(2.25rem, 1.7vw + 1rem, 3.35rem);
  font-weight: 700;
  line-height: 1.08;
  letter-spacing: 0.015em;
}

.login-title-detail {
  margin: 0;
  max-width: 17em;
  color: #edf2f8;
  font-size: clamp(1rem, 0.42vw + 0.94rem, 1.22rem);
  font-weight: 600;
  line-height: 1.76;
  text-wrap: pretty;
}

.login-subtitle {
  margin: 0;
  max-width: 25em;
  color: var(--text-sub);
  font-size: 14px;
  line-height: 1.92;
}

.login-panel {
  width: 100%;
  justify-self: end;
  background:
    linear-gradient(180deg, rgba(11, 15, 22, 0.88) 0%, rgba(12, 16, 22, 0.8) 100%);
}

.login-panel__head {
  margin-bottom: 24px;
}

.login-panel__eyebrow {
  color: var(--text-muted);
  font-size: 12px;
  letter-spacing: 0.1em;
}

.login-panel__title {
  margin-top: 10px;
  color: var(--text-main);
  font-size: 26px;
  font-weight: 700;
}

.auth-form {
  margin-top: 8px;
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
  margin-bottom: 18px;
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
    gap: 20px;
  }

  .login-hero,
  .login-panel {
    padding: 30px 28px;
  }

  .login-hero {
    min-height: 320px;
  }

  .login-copy,
  .login-title-detail,
  .login-subtitle {
    max-width: none;
  }
}
</style>
