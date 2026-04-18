<template>
  <div class="forum-container">
    <!-- 引入发帖零件 -->
    <PostForm @post-success="fetchPosts" />

    <hr />

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-msg">加载中...</div>

    <!-- 错误信息 -->
    <div v-if="error" class="error-msg">
      ❌ {{ error }}
    </div>

    <!-- 帖子列表 -->
    <div v-if="posts.length === 0 && !loading" class="no-posts">
      还没有帖子，来发第一个吧！
    </div>

    <div class="post-list">
      <div v-for="post in posts" :key="post.id" class="post-card">
        <h4>{{ post.title }}</h4>
        <p>{{ post.content }}</p>
        <small>📅 {{ formatDate(post.created_at) }}</small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import PostForm from '../components/PostForm.vue'

const posts = ref([])
const loading = ref(false)
const error = ref('')

// 获取帖子列表的函数
const fetchPosts = async () => {
  loading.value = true
  error.value = ''

  try {
    console.log('获取帖子列表...')
    const response = await fetch('http://127.0.0.1:8000/api/posts')
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()
    console.log('获取帖子成功:', data)
    posts.value = data
  } catch (err) {
    console.error('获取帖子失败:', err)
    error.value = `获取帖子失败: ${err.message}`
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 页面一加载就执行
onMounted(() => {
  fetchPosts()
})
</script>

<style scoped>
.forum-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.loading-msg {
  text-align: center;
  color: #999;
  padding: 20px;
}

.error-msg {
  background: #fee;
  color: #c33;
  padding: 15px;
  border-radius: 4px;
  margin-block-end: 20px;
  border: 1px solid #fcc;
}

.no-posts {
  text-align: center;
  color: #999;
  padding: 40px 20px;
  font-size: 16px;
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.post-card {
  border: 1px solid #ddd;
  padding: 15px;
  border-radius: 4px;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.post-card h4 {
  margin-block-start: 0;
  margin-block-end: 10px;
  color: #333;
}

.post-card p {
  margin: 10px 0;
  color: #666;
  line-height: 1.5;
  word-break: break-word;
}

.post-card small {
  color: #999;
  font-size: 12px;
}

hr {
  border: none;
  border-block-start: 1px solid #eee;
  margin: 20px 0;
}
</style>