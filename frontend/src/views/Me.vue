<template>
  <div class="me-container">
    <header class="page-header">
      <h1>个人中心</h1>
      <p>管理你的账号与个人资料</p>
    </header>

    <div v-if="loading" class="state glass-panel">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else class="grid">
      <section class="card glass-panel">
        <h3>账号信息</h3>
        <div class="kv">
          <div class="k">用户名</div>
          <div class="v">{{ me?.username }}</div>
        </div>
        <div class="kv">
          <div class="k">注册时间</div>
          <div class="v">{{ formatDate(me?.created_at) }}</div>
        </div>
      </section>

      <section class="card glass-panel">
        <h3>个人资料（可编辑）</h3>
        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>

        <div class="form">
          <label class="label">昵称</label>
          <input v-model="form.display_name" class="modern-input" placeholder="例如：小明" />

          <label class="label">头像链接</label>
          <input v-model="form.avatar_url" class="modern-input" placeholder="https://..." />

          <label class="label">个人简介</label>
          <textarea v-model="form.bio" class="modern-input textarea" rows="4" placeholder="写点什么..." />

          <button class="btn btn-primary" :disabled="saving" @click="save">
            {{ saving ? '保存中...' : '保存资料' }}
          </button>
        </div>
      </section>

      <section class="card glass-panel span-2">
        <div class="row">
          <h3>我发布的帖子</h3>
          <button class="btn btn-secondary" @click="loadMyPosts" :disabled="postsLoading">
            {{ postsLoading ? '刷新中...' : '刷新' }}
          </button>
        </div>

        <div v-if="postsLoading" class="state">
          <div class="spinner"></div>
          <p>正在加载帖子...</p>
        </div>

        <div v-else-if="myPosts.length === 0" class="empty">
          你还没有发布过帖子
        </div>

        <div v-else class="post-list">
          <div v-for="p in myPosts" :key="p.id" class="post-item">
            <div class="title">{{ p.title }}</div>
            <div class="meta">{{ formatDate(p.created_at) }}</div>
            <div class="content">{{ p.content }}</div>
          </div>
        </div>
      </section>

      <section class="card glass-panel span-2">
        <div class="row">
          <h3>我的收藏</h3>
          <button class="btn btn-secondary" @click="loadMyFavorites" :disabled="favLoading">
            {{ favLoading ? '刷新中...' : '刷新' }}
          </button>
        </div>

        <div v-if="favLoading" class="state">
          <div class="spinner"></div>
          <p>正在加载收藏...</p>
        </div>

        <div v-else-if="favorites.length === 0" class="empty">
          你还没有收藏过帖子
        </div>

        <div v-else class="post-list">
          <div v-for="p in favorites" :key="p.id" class="post-item">
            <div class="title">{{ p.title }}</div>
            <div class="meta">
              <span v-if="p.author">{{ p.author.display_name || p.author.username }}</span>
              <span v-else>匿名</span>
              · {{ formatDate(p.created_at) }}
            </div>
            <div class="content">{{ p.content }}</div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { API_BASE, getAuthToken } from '../config.js'
import { getMe, logout as doLogout } from '../api/auth-api.js'

const router = useRouter()
const loading = ref(true)
const saving = ref(false)
const postsLoading = ref(false)
const favLoading = ref(false)
const error = ref('')
const success = ref('')

const me = ref(null)
const myPosts = ref([])
const favorites = ref([])

const form = ref({
  display_name: '',
  bio: '',
  avatar_url: '',
})

function formatDate(dateString) {
  if (!dateString) return '-'
  const d = new Date(dateString)
  return d.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function loadMe() {
  const token = getAuthToken()
  if (!token) {
    doLogout()
    router.push('/login')
    return
  }

  const data = await getMe()
  if (!data) {
    doLogout()
    router.push('/login')
    return
  }
  me.value = data
  form.value.display_name = data.display_name || ''
  form.value.bio = data.bio || ''
  form.value.avatar_url = data.avatar_url || ''
}

async function loadMyPosts() {
  postsLoading.value = true
  try {
    const token = getAuthToken()
    const res = await fetch(`${API_BASE}/api/me/posts`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || '加载失败')
    myPosts.value = Array.isArray(data) ? data : []
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    postsLoading.value = false
  }
}

async function loadMyFavorites() {
  favLoading.value = true
  try {
    const token = getAuthToken()
    const res = await fetch(`${API_BASE}/api/me/favorites`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || '加载失败')
    favorites.value = Array.isArray(data) ? data : []
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    favLoading.value = false
  }
}

async function save() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    const token = getAuthToken()
    const res = await fetch(`${API_BASE}/api/me`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        display_name: form.value.display_name,
        bio: form.value.bio,
        avatar_url: form.value.avatar_url,
      }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || '保存失败')
    me.value = data
    success.value = '保存成功'
    setTimeout(() => (success.value = ''), 2000)
  } catch (e) {
    error.value = e.message || '保存失败'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    await loadMe()
    await loadMyPosts()
    await loadMyFavorites()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.me-container { max-width: 1000px; margin: 0 auto; }
.page-header { text-align: center; margin-bottom: 2rem; }
.page-header h1 { font-size: 2.2rem; color: var(--primary-color); margin-bottom: 0.5rem; }
.page-header p { color: var(--text-secondary); }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1.5rem; }
.span-2 { grid-column: span 2; }
.card { padding: 1.5rem; border-radius: 16px; }
.kv { display: grid; grid-template-columns: 90px 1fr; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--border-color); }
.kv:last-child { border-bottom: none; }
.k { color: var(--text-secondary); }
.v { color: var(--text-primary); font-weight: 600; }
.form { display: flex; flex-direction: column; gap: 10px; margin-top: 10px; }
.label { font-size: 0.9rem; color: var(--text-secondary); }
.textarea { resize: vertical; min-height: 90px; }
.row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.post-list { display: flex; flex-direction: column; gap: 12px; margin-top: 12px; }
.post-item { padding: 12px; border-radius: 12px; border: 1px solid var(--border-color); background: rgba(255,255,255,0.6); }
.title { font-weight: 700; color: var(--text-primary); }
.meta { color: var(--text-light); font-size: 0.85rem; margin: 4px 0 8px; }
.content { color: var(--text-secondary); line-height: 1.6; white-space: pre-wrap; }
.state { padding: 2rem; text-align: center; }
.spinner { width: 40px; height: 40px; border: 4px solid rgba(99, 102, 241, 0.1); border-left-color: var(--primary-color); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 12px; }
.empty { margin-top: 12px; color: var(--text-secondary); text-align: center; padding: 20px; }
.alert { padding: 10px 12px; border-radius: 10px; margin-top: 10px; }
.alert-error { background: rgba(239, 68, 68, 0.1); color: var(--error); border: 1px solid rgba(239, 68, 68, 0.2); }
.alert-success { background: rgba(16, 185, 129, 0.1); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.2); }
@keyframes spin { 100% { transform: rotate(360deg); } }
@media (max-width: 900px) {
  .grid { grid-template-columns: 1fr; }
  .span-2 { grid-column: span 1; }
}
</style>

