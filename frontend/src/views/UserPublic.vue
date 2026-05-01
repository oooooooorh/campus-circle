<template>
  <div class="user-page">
    <div class="card glass-panel" v-if="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div class="card glass-panel" v-else-if="error">
      <p class="err">{{ error }}</p>
    </div>

    <div class="card glass-panel" v-else>
      <div class="header">
        <div class="avatar">
          {{ initial }}
        </div>
        <div class="meta">
          <div class="name">{{ name }}</div>
          <div class="username">@{{ user.username }}</div>
        </div>
      </div>
      <div class="bio" v-if="user.bio">{{ user.bio }}</div>
      <div class="bio empty" v-else>这个用户还没有填写简介</div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { API_BASE } from '../config.js'

const route = useRoute()
const user = ref(null)
const loading = ref(true)
const error = ref('')

const name = computed(() => user.value?.display_name || user.value?.username || '用户')
const initial = computed(() => String(name.value).charAt(0).toUpperCase())

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const id = route.params.id
    const res = await fetch(`${API_BASE}/api/users/${id}`)
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || '加载失败')
    user.value = data
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.user-page { max-width: 720px; margin: 0 auto; }
.card { padding: 1.5rem; border-radius: 16px; }
.header { display: flex; align-items: center; gap: 14px; }
.avatar {
  width: 56px; height: 56px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.6rem; font-weight: 800;
}
.name { font-size: 1.2rem; font-weight: 800; color: var(--text-primary); }
.username { color: var(--text-secondary); margin-top: 2px; }
.bio { margin-top: 14px; color: var(--text-secondary); line-height: 1.7; white-space: pre-wrap; }
.bio.empty { opacity: 0.85; }
.err { color: var(--error); }
.spinner { width: 40px; height: 40px; border: 4px solid rgba(99, 102, 241, 0.1); border-left-color: var(--primary-color); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 12px; }
@keyframes spin { 100% { transform: rotate(360deg); } }
</style>

