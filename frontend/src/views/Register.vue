<template>
  <div class="auth-page">
    <div class="auth-card glass-panel">
      <h1>注册</h1>
      <p class="sub">创建一个站内账号</p>

      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>

      <div class="form">
        <input v-model="username" class="modern-input" placeholder="用户名（≥3位）" :disabled="loading" />
        <input v-model="password" class="modern-input" type="password" placeholder="密码（≥6位）" :disabled="loading" />
        <button class="btn btn-primary" :disabled="loading || !username || !password" @click="handleRegister">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </div>

      <div class="hint">
        已有账号？
        <router-link to="/login">去登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register, login } from '../api/auth-api.js'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

async function handleRegister() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await register(username.value, password.value)
    await login(username.value, password.value)
    success.value = '注册成功，已自动登录'
    setTimeout(() => router.push('/forum'), 300)
  } catch (e) {
    error.value = e.message || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: calc(100vh - 160px);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
}
.auth-card {
  width: 100%;
  max-width: 420px;
  padding: 24px;
  border-radius: 16px;
}
.sub { color: var(--text-secondary); margin-top: 6px; }
.form { display: flex; flex-direction: column; gap: 12px; margin-top: 16px; }
.hint { margin-top: 16px; color: var(--text-secondary); text-align: center; }
.alert { padding: 10px 12px; border-radius: 10px; margin-top: 12px; }
.alert-error { background: rgba(239, 68, 68, 0.1); color: var(--error); border: 1px solid rgba(239, 68, 68, 0.2); }
.alert-success { background: rgba(16, 185, 129, 0.1); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.2); }
</style>

