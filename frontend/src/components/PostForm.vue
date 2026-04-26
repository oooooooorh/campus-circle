<template>
  <div class="post-form glass-panel">
    <div class="form-header">
      <span class="icon">✨</span>
      <h3>发布新动态</h3>
    </div>
    
    <!-- 错误提示 -->
    <transition name="fade">
      <div v-if="error" class="alert alert-error">
        <span class="alert-icon">❌</span> {{ error }}
      </div>
    </transition>
    
    <!-- 成功提示 -->
    <transition name="fade">
      <div v-if="successMsg" class="alert alert-success">
        <span class="alert-icon">✅</span> {{ successMsg }}
      </div>
    </transition>
    
    <form @submit.prevent="submitPost" class="modern-form">
      <div class="input-group">
        <input 
          v-model="form.title" 
          type="text" 
          placeholder="给你的动态起个响亮的标题吧..."
          class="modern-input"
          required
        >
      </div>
      <div class="input-group">
        <textarea 
          v-model="form.content" 
          placeholder="此刻你在想什么？"
          class="modern-input textarea"
          rows="4"
          required
        ></textarea>
      </div>
      <div class="form-actions">
        <button type="submit" class="btn btn-primary publish-btn" :disabled="loading">
          <span class="btn-icon" v-if="!loading">🚀</span>
          <span class="btn-icon spinner" v-else>⏳</span>
          {{ loading ? '正在发送电波...' : '立即发布' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { API_BASE } from '../config.js'

const emit = defineEmits(['post-created'])

const form = ref({
  title: '',
  content: ''
})

const error = ref('')
const successMsg = ref('')
const loading = ref(false)

const isValid = computed(() => {
  return form.value.title.trim() !== '' && form.value.content.trim() !== ''
})

const submitPost = async () => {
  if (!isValid.value) return
  
  isSubmitting.value = true
  try {
    const response = await fetch(`${API_BASE}/api/posts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form.value)
    })
    
    const data = await response.json()

    if (response.ok) {
      form.value = { title: '', content: '' }
      successMsg.value = '发布成功！你的声音已被世界听到。'
      setTimeout(() => { successMsg.value = '' }, 3000)
      emit('post-created')
    } else {
      error.value = `发布失败: ${data.detail || '未知错误，请稍后再试'}`
    }
  } catch (err) {
    error.value = `网络似乎开小差了: ${err.message}`
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.post-form {
  padding: 1.5rem;
  margin-bottom: 2rem;
  transition: transform 0.3s ease;
}

.post-form:hover {
  transform: translateY(-2px);
}

.form-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.form-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--primary-color);
}

.icon {
  font-size: 1.5rem;
}

.modern-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.input-group {
  position: relative;
}

.textarea {
  resize: vertical;
  min-height: 100px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.5rem;
}

.publish-btn {
  padding: 0.75rem 2rem;
  font-size: 1rem;
  border-radius: var(--radius-pill);
}

.btn-icon {
  margin-right: 0.5rem;
}

.spinner {
  display: inline-block;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

/* Alerts */
.alert {
  padding: 1rem;
  border-radius: var(--radius-md);
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.alert-error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.alert-success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
