<template>
  <div class="forum-container">
    <!-- 引入发帖零件 -->
    <PostForm @post-success="fetchPosts" />

    <hr />

    <div class="post-list">
      <div v-for="post in posts" :key="post.id" class="post-card">
        <h4>{{ post.title }}</h4>
        <p>{{ post.content }}</p>
        <small>{{ new Date(post.created_at).toLocaleString() }}</small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import PostForm from '../components/PostForm.vue' // 引入零件

const posts = ref([])

// 获取帖子列表的函数
const fetchPosts = async () => {
  const response = await fetch('http://127.0.0.1:8000/api/posts')
  posts.value = await response.json()
}

// 页面一加载就执行
onMounted(() => {
  fetchPosts()
})
</script>