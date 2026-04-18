<template>
  <div class="post-form">
    <h3>发布新帖子</h3>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error-msg">
      ❌ {{ error }}
    </div>
    
    <!-- 成功提示 -->
    <div v-if="successMsg" class="success-msg">
      ✓ {{ successMsg }}
    </div>
    
    <form @submit.prevent="submitPost">
      <input 
        v-model="form.title" 
        type="text" 
        placeholder="请输入帖子标题"
        required
      >
      <textarea 
        v-model="form.content" 
        placeholder="请输入帖子内容"
        rows="5"
        required
      ></textarea>
      <button type="submit" :disabled="loading">
        {{ loading ? '发布中...' : '发布' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const form = ref({
  title: '',
  content: ''
})

const error = ref('')
const successMsg = ref('')
const loading = ref(false)

const emit = defineEmits(['post-success'])

const submitPost = async () => {
  // 清除之前的提示
  error.value = ''
  successMsg.value = ''
  loading.value = true

  try {
    console.log('发送请求到:', 'http://127.0.0.1:8000/api/posts')
    console.log('请求体:', form.value)

    const response = await fetch('http://127.0.0.1:8000/api/posts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form.value)
    })
    
    console.log('响应状态:', response.status)
    const data = await response.json()
    console.log('响应数据:', data)

    if (response.ok) {
      form.value = { title: '', content: '' }
      successMsg.value = '发帖成功！'
      // 2秒后清除提示
      setTimeout(() => { successMsg.value = '' }, 2000)
      emit('post-success')
    } else {
      error.value = `发帖失败: ${data.detail || '服务器错误'}`
    }
  } catch (err) {
    console.error('发帖异常:', err)
    error.value = `网络错误: ${err.message}`
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.post-form {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
  margin-block-end: 20px;
}

.post-form h3 {
  margin-block-start: 0;
  margin-block-end: 10px;
}

.post-form form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.post-form input,
.post-form textarea {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
}

.post-form button {
  padding: 10px 20px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.post-form button:hover:not(:disabled) {
  background: #369970;
}

.post-form button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error-msg {
  background: #fee;
  color: #c33;
  padding: 10px;
  border-radius: 4px;
  margin-block-end: 10px;
  border: 1px solid #fcc;
}

.success-msg {
  background: #efe;
  color: #3c3;
  padding: 10px;
  border-radius: 4px;
  margin-block-end: 10px;
  border: 1px solid #cfc;
}
</style>
