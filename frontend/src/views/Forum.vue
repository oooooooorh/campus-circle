<template>
  <div class="forum-container">
    <!-- Header -->
    <header class="page-header">
      <h1>校园交流圈</h1>
      <p>分享你的校园生活，遇见有趣的灵魂</p>
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
        <p>这里还是一片荒芜</p>
        <span>快来发布第一条动态，抢占沙发！</span>
      </div>

      <!-- 帖子列表 -->
      <div v-else class="post-list">
        <transition-group name="list">
          <div v-for="post in posts" :key="post.id" class="post-card glass-panel">
            <div class="post-header">
              <div class="avatar-placeholder">
                {{ post.title.charAt(0).toUpperCase() }}
              </div>
              <div class="post-meta">
                <h4 class="post-title">{{ post.title }}</h4>
                <div class="post-time">
                  <span class="time-icon">🕒</span> {{ formatDate(post.created_at) }}
                </div>
              </div>
            </div>
            <div class="post-content">
              <p>{{ post.content }}</p>
            </div>
            <div class="post-footer">
              <button class="action-btn"><span class="icon">👍</span> 赞</button>
              <button class="action-btn"><span class="icon">💬</span> 评论</button>
              <button class="action-btn"><span class="icon">🔁</span> 转发</button>
            </div>
          </div>
        </transition-group>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import PostForm from '../components/PostForm.vue'
import { API_BASE } from '../config.js'

const posts = ref([])
const loading = ref(false)
const error = ref('')

// 获取帖子列表的函数
const fetchPosts = async () => {
  try {
    const response = await fetch(`${API_BASE}/api/posts`)
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
})
</script>

<style scoped>
.forum-container {
  max-width: 800px;
  margin: 0 auto;
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
  color: var(--text-secondary);
  font-size: 1.1rem;
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
  gap: 1rem;
  border-top: 1px solid var(--border-color);
  padding-top: 1rem;
}

.action-btn {
  background: none;
  border: none;
  color: var(--text-light);
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0.5rem 0.8rem;
  border-radius: var(--radius-sm);
  transition: all 0.2s;
}

.action-btn:hover {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
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