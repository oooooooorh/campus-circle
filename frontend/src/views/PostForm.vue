<template>
  <div class="post-form">
    <h3>发布新动态</h3>
    <input v-model="title" placeholder="请输入标题" />
    <textarea v-model="content" placeholder="说点什么吧..."></textarea>
    <button @click="submitPost">发布</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const title = ref('')
const content = ref('')

// 定义一个“自定义事件”，发帖成功后通知父组件刷新列表
const emit = defineEmits(['post-success'])

const submitPost = async () => {
  if (!title.value || !content.value) return alert('请填写完整')

  const response = await fetch('https://campus-api-bkfua8a9gdcfaff3.eastasia-01.azurewebsites.net/api/posts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: title.value, content: content.value })
  })

  if (response.ok) {
    title.value = ''
    content.value = ''
    emit('post-success') // 触发事件
  }
}
</script>