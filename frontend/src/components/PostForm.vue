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

      <div class="input-group">
        <div class="tag-header">
          <span class="tag-title">分区标签（最多 7 个）</span>
          <span class="tag-count">{{ form.tags.length }}/7</span>
        </div>
        <div class="tag-pick">
          <button
            v-for="t in presetTags"
            :key="t"
            type="button"
            class="tag-pick-btn"
            :disabled="loading || form.tags.length >= 7"
            @click="addTagValue(t)"
          >
            + {{ t }}
          </button>
          <button
            type="button"
            class="tag-pick-btn tag-pick-btn-primary"
            :disabled="loading || form.tags.length >= 7"
            @click="promptTag"
          >
            + 自定义标签
          </button>
        </div>
        <div class="tag-chips">
          <button
            v-for="(t, idx) in form.tags"
            :key="t + idx"
            class="tag-chip"
            type="button"
            @click="removeTag(idx)"
            :disabled="loading"
            title="点击移除"
          >
            {{ t }} ×
          </button>
        </div>
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
import { API_BASE, getAuthToken } from '../config.js'

const emit = defineEmits(['post-success'])

const form = ref({
  title: '',
  content: '',
  tags: []
})

const presetTags = [
  '学习', '二手', '社团', '求助', '失物招领', '考试', '生活', '美食', '拼车', '实习'
]

const error = ref('')
const successMsg = ref('')
const loading = ref(false)

const isValid = computed(() => {
  return form.value.title.trim() !== '' && form.value.content.trim() !== ''
})

function normalizeTag(t) {
  return (t || '').trim().replace(/\s+/g, ' ')
}

function addTagValue(value) {
  const t = normalizeTag(value)
  if (!t) return
  if (t.length > 20) {
    error.value = '单个分区标签最多20个字符'
    return
  }
  if (form.value.tags.length >= 7) return
  if (form.value.tags.includes(t)) {
    return
  }
  form.value.tags.push(t)
}

function removeTag(idx) {
  form.value.tags.splice(idx, 1)
}

function promptTag() {
  const v = window.prompt('请输入分区标签（最多20字）')
  if (v === null) return
  addTagValue(v)
}

const submitPost = async () => {
  if (!isValid.value) return
  
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    const token = getAuthToken()
    if (!token) {
      throw new Error('请先登录后再发布')
    }
    const response = await fetch(`${API_BASE}/api/posts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(form.value)
    })
    
    const data = await response.json()

    if (response.ok) {
      form.value = { title: '', content: '', tags: [] }
      successMsg.value = '发布成功！你的声音已被世界听到。'
      setTimeout(() => { successMsg.value = '' }, 3000)
      emit('post-success')
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

.tag-header{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.tag-title{
  font-weight: 700;
  color: var(--text-primary);
}
.tag-count{
  color: var(--text-light);
  font-size: 0.9rem;
}
.tag-chips{
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.6rem;
}

.tag-pick{
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.6rem;
}

.tag-pick-btn{
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(148, 163, 184, 0.10);
  color: var(--text-secondary);
  font-weight: 700;
  padding: 0.35rem 0.6rem;
  border-radius: 999px;
  cursor: pointer;
}

.tag-pick-btn:hover:enabled{
  background: rgba(148, 163, 184, 0.16);
}

.tag-pick-btn-primary{
  border-color: rgba(124, 58, 237, 0.22);
  background: rgba(124, 58, 237, 0.10);
  color: #6d28d9;
}

.tag-pick-btn-primary:hover:enabled{
  background: rgba(124, 58, 237, 0.16);
}

.tag-pick-btn:disabled{
  opacity: 0.6;
  cursor: not-allowed;
}
.tag-chip{
  border: 1px solid rgba(124, 58, 237, 0.22);
  background: rgba(124, 58, 237, 0.10);
  color: #6d28d9;
  font-weight: 700;
  padding: 0.35rem 0.6rem;
  border-radius: 999px;
  cursor: pointer;
}
.tag-chip:disabled{
  opacity: 0.6;
  cursor: not-allowed;
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
