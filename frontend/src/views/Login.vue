<script setup>
import { Lock, MoonNight, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { loginAccount, registerAccount } from '../api/auth'
import { persistAuth } from '../utils/auth'

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

async function handleLogin() {
  if (!loginForm.username.trim() || !loginForm.password.trim()) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
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
          <el-icon><MoonNight /></el-icon>
        </div>
        <h1 class="login-title">LightInspector 城市光环境监测系统</h1>
        <p class="login-subtitle">城市夜间光环境监测与评级平台</p>
      </section>

      <section class="login-panel">
        <el-tabs v-model="activeTab" stretch class="auth-tabs">
          <el-tab-pane label="登录" name="login">
            <el-form
              :model="loginForm"
              label-position="left"
              label-width="74px"
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
              label-width="74px"
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
  filter: blur(60px);
  opacity: 0.35;
}

.login-page__glow--left {
  width: 420px;
  height: 420px;
  left: -120px;
  top: 80px;
  background: rgba(245, 239, 226, 0.08);
}

.login-page__glow--right {
  width: 360px;
  height: 360px;
  right: -80px;
  bottom: 60px;
  background: rgba(168, 101, 88, 0.12);
}

.login-shell {
  position: relative;
  z-index: 1;
  width: min(1080px, 100%);
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 24px;
}

.login-hero,
.login-panel {
  padding: 40px;
  border-radius: 28px;
  background: rgba(17, 19, 21, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 32px 72px rgba(0, 0, 0, 0.38);
  backdrop-filter: blur(18px);
}

.login-hero {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 440px;
}

.login-badge {
  width: 58px;
  height: 58px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
  background: rgba(241, 237, 230, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #f1ede6;
  font-size: 24px;
}

.login-title {
  margin: 24px 0 12px;
  font-size: 36px;
  line-height: 1.2;
  color: var(--text-main);
}

.login-subtitle {
  margin: 0;
  color: var(--text-sub);
  font-size: 15px;
  line-height: 1.8;
}

.login-panel {
  align-self: center;
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
    min-height: 260px;
  }

  .login-title {
    font-size: 32px;
  }
}
</style>
