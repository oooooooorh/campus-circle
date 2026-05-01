<template>
  <div class="forum-container">
    <div v-if="toast" class="toast">{{ toast }}</div>
    <!-- Header -->
    <header class="page-header">
      <h1>校园交流圈</h1>
      <p>分享你的校园生活，遇见有趣的灵魂</p>

      <!-- Global Search -->
      <div class="search-bar glass-panel">
        <input
          v-model="search"
          class="search-input"
          placeholder="搜索帖子标题/内容/作者..."
        />
        <button v-if="search" class="search-btn" @click="clearSearch">清空</button>
      </div>
    </header>

    <!-- 引入发帖零件 -->
    <PostForm @post-success="fetchPosts" />

    <!-- 状态区域 -->
    <transition name="fade" mode="out-in">
      <!-- 加载状态 -->
      <div v-if="loading" class="state-container loading-state glass-panel">
        <div class="spinner"></div>
        <p>正在努力获取新鲜事...</p>
      </div>

      <!-- 错误信息 -->
      <div v-else-if="error" class="state-container error-state glass-panel">
        <span class="icon">💔</span>
        <p>{{ error }}</p>
        <button class="btn btn-primary" @click="fetchPosts">重试</button>
      </div>

      <!-- 空状态 -->
      <div v-else-if="posts.length === 0" class="state-container empty-state glass-panel">
        <span class="icon">🌱</span>
        <p>{{ search ? '没有搜到相关内容' : '这里还是一片荒芜' }}</p>
        <span v-if="!search">快来发布第一条动态，抢占沙发！</span>
      </div>

      <!-- 帖子列表 -->
      <div v-else class="post-list">
        <transition-group name="list">
          <div v-for="post in posts" :key="post.id" class="post-card glass-panel">
            <div class="post-header">
              <router-link
                v-if="post.author && post.user_id"
                class="avatar-placeholder"
                :to="`/user/${post.user_id}`"
                :title="authorName(post)"
              >
                {{ authorInitial(post) }}
              </router-link>
              <div v-else class="avatar-placeholder">
                {{ authorInitial(post) }}
              </div>
              <div class="post-meta">
                <h4 class="post-title">{{ post.title }}</h4>
                <div class="post-author" v-if="post.author && post.user_id">
                  <router-link :to="`/user/${post.user_id}`" class="author-link">
                    {{ authorName(post) }}
                  </router-link>
                </div>
                <div class="post-time">
                  <span class="time-icon">🕒</span> {{ formatDate(post.created_at) }}
                </div>
              </div>
            </div>
            <div class="post-content">
              <p>{{ post.content }}</p>
            </div>
            <div class="post-footer">
              <button class="action-btn" title="点赞（占位）" @click.prevent>
                <svg class="icon-mini" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M7 22V10M7 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h3M7 10l4-7a2 2 0 0 1 3 2v5h5a2 2 0 0 1 2 2l-2 8a2 2 0 0 1-2 2H7" />
                </svg>
              </button>
              <button class="action-btn" title="评论（占位）" @click.prevent>
                <svg class="icon-mini" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" />
                </svg>
              </button>
              <button class="action-btn" title="转发（复制链接）" @click="copyPostLink(post.id)">
                <svg class="icon-mini" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M16 3h5v5" />
                  <path d="M21 3l-7.5 7.5" />
                  <path d="M13.5 10.5H9a6 6 0 0 0 0 12h3" />
                </svg>
              </button>
              <button
                class="action-btn"
                :class="{ 'fav-active': isFavorited(post.id) }"
                title="收藏"
                @click="toggleFavorite(post.id)"
              >
                <svg class="icon-mini" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M12 17.3l-6.18 3.7 1.64-7.03L2 8.97l7.19-.61L12 2l2.81 6.36 7.19.61-5.46 4.99 1.64 7.03z" />
                </svg>
              </button>
            </div>
          </div>
        </transition-group>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import PostForm from '../components/PostForm.vue'
import { API_BASE, getAuthToken } from '../config.js'

const posts = ref([])
const loading = ref(false)
const error = ref('')
const search = ref('')
let searchTimer = null
const favoriteIds = ref(new Set())
const router = useRouter()
const toast = ref('')
let toastTimer = null

// 获取帖子列表的函数
const fetchPosts = async () => {
  loading.value = true
  error.value = ''
  try {
    const q = search.value.trim()
    const url = q ? `${API_BASE}/api/posts?q=${encodeURIComponent(q)}` : `${API_BASE}/api/posts`
    const response = await fetch(url)
    if (response.ok) {
      posts.value = await response.json()
    } else {
      throw new Error(`连接小分队走丢了 (HTTP ${response.status})`)
    }
  } catch (err) {
    error.value = `获取动态失败: ${err.message}`
  } finally {
    loading.value = false
  }
}

async function loadFavoriteIds() {
  try {
    const token = getAuthToken()
    if (!token) {
      favoriteIds.value = new Set()
      return
    }
    const res = await fetch(`${API_BASE}/api/me/favorites/ids`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) {
      favoriteIds.value = new Set()
      return
    }
    const data = await res.json()
    favoriteIds.value = new Set(Array.isArray(data) ? data : [])
  } catch {
    favoriteIds.value = new Set()
  }
}

// 格式化日期：相对时间或美化后的绝对时间
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date

  // 1分钟内
  if (diff < 60000) return '刚刚'
  // 1小时内
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  // 24小时内
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  
  return date.toLocaleDateString('zh-CN', { 
    month: 'short', 
    day: 'numeric', 
    hour: '2-digit', 
    minute: '2-digit'
  })
}

// 页面一加载就执行
onMounted(() => {
  fetchPosts()
  loadFavoriteIds()
})

watch(search, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    fetchPosts()
  }, 300)
})

const clearSearch = () => {
  search.value = ''
}

const authorName = (post) => {
  if (post?.author?.display_name) return post.author.display_name
  if (post?.author?.username) return post.author.username
  return '匿名'
}

const authorInitial = (post) => {
  const name = authorName(post)
  return String(name).charAt(0).toUpperCase()
}

const isFavorited = (postId) => {
  return favoriteIds.value.has(postId)
}

async function toggleFavorite(postId) {
  const token = getAuthToken()
  if (!token) {
    router.push('/login')
    return
  }
  const fav = isFavorited(postId)
  const method = fav ? 'DELETE' : 'POST'
  const res = await fetch(`${API_BASE}/api/posts/${postId}/favorite`, {
    method,
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    error.value = data.detail || '操作失败'
    return
  }
  const next = new Set(favoriteIds.value)
  if (fav) next.delete(postId)
  else next.add(postId)
  favoriteIds.value = next
}

async function copyPostLink(postId) {
  try {
    const url = `${window.location.origin}/post/${postId}`
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(url)
    } else {
      const input = document.createElement('input')
      input.value = url
      document.body.appendChild(input)
      input.select()
      document.execCommand('copy')
      document.body.removeChild(input)
    }
    toast.value = '已复制链接'
  } catch (e) {
    toast.value = '复制失败，请手动复制地址栏链接'
  } finally {
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = setTimeout(() => (toast.value = ''), 1800)
  }
}
</script>

<style scoped>
.forum-container {
  max-width: 800px;
  margin: 0 auto;
}

.toast {
  position: fixed;
  top: 90px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(15, 23, 42, 0.88);
  color: white;
  padding: 10px 14px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.9rem;
  z-index: 9999;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

/* Page Header */
.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2.5rem;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.page-header p {
  background: linear-gradient(90deg, #8b5cf6 0%, #a855f7 45%, #6366f1 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-size: 1.1rem;
}

/* Search */
.search-bar {
  margin: 1rem auto 0;
  max-width: 520px;
  padding: 0.6rem;
  border-radius: var(--radius-pill);
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 0.6rem 0.8rem;
  font-size: 1rem;
  color: var(--text-primary);
}

.search-btn {
  border: none;
  cursor: pointer;
  padding: 0.5rem 0.9rem;
  border-radius: var(--radius-pill);
  background: rgba(99, 102, 241, 0.12);
  color: var(--primary-color);
  font-weight: 700;
}

.search-btn:hover {
  background: rgba(99, 102, 241, 0.18);
}

/* States */
.state-container {
  padding: 3rem 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.state-container .icon {
  font-size: 3rem;
}

.state-container p {
  font-size: 1.2rem;
  color: var(--text-primary);
  font-weight: 500;
}

.state-container span {
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(99, 102, 241, 0.1);
  border-left-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Post List & Cards */
.post-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.post-card {
  padding: 1.5rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.post-card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
}

.post-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.avatar-placeholder {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-pill);
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  box-shadow: var(--shadow-sm);
}

.post-meta {
  flex: 1;
}

.post-author {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 0.2rem;
}

.author-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 600;
}

.author-link:hover {
  color: var(--primary-color);
  text-decoration: underline;
}

.post-title {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.post-time {
  font-size: 0.85rem;
  color: var(--text-light);
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.post-content {
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 1.5rem;
  word-break: break-word;
}

.post-footer {
  display: flex;
  gap: 0.25rem;
  border-top: 1px solid var(--border-color);
  padding-top: 1rem;
}

.action-btn {
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-secondary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  font-size: 0.95rem;
  cursor: pointer;
  padding: 0.45rem 0.6rem;
  border-radius: 999px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
}

.icon-mini {
  width: 18px;
  height: 18px;
  stroke: currentColor;
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.fav-active {
  color: #7c3aed;
  background: rgba(124, 58, 237, 0.12);
}

/* Animations */
@keyframes spin {
  100% { transform: rotate(360deg); }
}

.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.list-leave-active {
  position: absolute;
}
</style>