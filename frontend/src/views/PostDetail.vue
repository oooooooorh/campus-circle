<template>
  <div class="detail">
    <div class="card glass-panel" v-if="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div class="card glass-panel" v-else-if="error">
      <p class="err">{{ error }}</p>
    </div>

    <div class="card glass-panel" v-else>
      <div class="top">
        <router-link to="/forum" class="back">← 返回论坛</router-link>
        <div class="meta">
          <router-link
            v-if="post.author && post.user_id"
            :to="`/user/${post.user_id}`"
            class="author"
          >
            {{ post.author.display_name || post.author.username }}
          </router-link>
          <span v-else class="author">匿名</span>
          <span class="dot">·</span>
          <span class="time">{{ formatDate(post.created_at) }}</span>
        </div>
      </div>

      <h1 class="title">{{ post.title }}</h1>
      <div v-if="post.tags && post.tags.length" class="tag-row">
        <span v-for="t in post.tags" :key="t" class="tag-pill">{{ t }}</span>
      </div>
      <div class="content">{{ post.content }}</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { API_BASE } from '../config.js'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const post = ref(null)

function formatDate(dateString) {
  if (!dateString) return '-'
  const d = new Date(dateString)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const id = route.params.id
    const res = await fetch(`${API_BASE}/api/posts/${id}`)
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || '加载失败')
    post.value = data
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail { max-width: 900px; margin: 0 auto; }
.card { padding: 1.5rem; border-radius: 16px; }
.top { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.back { text-decoration: none; color: var(--text-secondary); font-weight: 600; }
.back:hover { color: var(--primary-color); }
.meta { color: var(--text-light); display: flex; align-items: center; gap: 8px; }
.author { color: var(--text-secondary); text-decoration: none; font-weight: 700; }
.author:hover { color: var(--primary-color); text-decoration: underline; }
.dot { opacity: 0.6; }
.title { margin: 14px 0 10px; font-size: 1.8rem; color: var(--text-primary); }
.tag-row{ display:flex; flex-wrap:wrap; gap:6px; margin: 4px 0 14px; }
.tag-pill{ font-size:0.78rem; padding:0.18rem 0.55rem; border-radius:999px; border:1px solid rgba(124,58,237,0.18); background: rgba(124,58,237,0.10); color:#6d28d9; font-weight:800; }
.content { color: var(--text-secondary); line-height: 1.8; white-space: pre-wrap; }
.err { color: var(--error); }
.spinner { width: 40px; height: 40px; border: 4px solid rgba(99, 102, 241, 0.1); border-left-color: var(--primary-color); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 12px; }
@keyframes spin { 100% { transform: rotate(360deg); } }
</style>

