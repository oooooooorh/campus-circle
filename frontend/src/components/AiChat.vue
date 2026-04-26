<template>
  <div class="ai-chat-box">
    <div class="chat-header" @click="toggleChat">
      <h3>🎓 校园圈 AI 助手 - 小圈</h3>
      <span class="toggle-btn">{{ isExpanded ? '▼' : '▲' }}</span>
    </div>
    
    <div v-show="isExpanded" class="chat-body">
      <!-- 聊天记录展示区 -->
      <div class="chat-history" ref="chatHistoryRef">
        <div v-for="(msg, index) in messageList" :key="index" :class="['message', msg.role]">
          <strong>{{ msg.role === 'user' ? '你' : '小圈' }}:</strong>
          <p>{{ msg.content }}</p>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="input-area">
        <input 
          v-model="inputText" 
          @keyup.enter="sendMessage"
          placeholder="问问小圈学长/学姐吧，比如：怎么复习高数？" 
          :disabled="isLoading"
        />
        <button @click="sendMessage" :disabled="isLoading">
          {{ isLoading ? '思考中...' : '发送' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { API_BASE } from '../config.js'

const isExpanded = ref(false)
const toggleChat = () => {
  isExpanded.value = !isExpanded.value
}

const inputText = ref('')
const messageList = ref([
  { role: 'ai', content: '哈喽！我是校园圈助手小圈，校园生活有啥不懂的，随时问我哦！✨' }
])
const isLoading = ref(false)
const chatHistoryRef = ref(null)

const sendMessage = async () => {
  if (!inputText.value.trim()) return

  // 1. 把用户的问题加入列表并清空输入框
  const userQuestion = inputText.value
  messageList.value.push({ role: 'user', content: userQuestion })
  inputText.value = ''
  isLoading.value = true

  // 滚动到底部
  await nextTick()
  if (chatHistoryRef.value) {
    chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
  }

  try {
    // 2. 请求后端 API (使用 fetch 替代 axios 减少依赖)
    const res = await fetch(`${API_BASE}/api/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_message: userQuestion })
    })
    
    const data = await res.json()
    
    // 3. 把 AI 的回答加入列表
    if (data.success) {
      messageList.value.push({ role: 'ai', content: data.reply })
    } else {
      messageList.value.push({ role: 'ai', content: data.detail || '发生了一点小错误~' })
    }
  } catch (error) {
    messageList.value.push({ role: 'ai', content: '哎呀，网络好像有点开小差，稍后再试一下吧~ 😥' })
  } finally {
    isLoading.value = false
    
    // 滚动到底部
    await nextTick()
    if (chatHistoryRef.value) {
      chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
    }
  }
}
</script>

<style scoped>
.ai-chat-box { 
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 350px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.15);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.chat-header {
  background: var(--primary-color, #4facfe);
  color: white;
  padding: 12px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.chat-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.toggle-btn {
  font-size: 12px;
}

.chat-body {
  display: flex;
  flex-direction: column;
}

.chat-history { 
  height: 350px; 
  overflow-y: auto; 
  padding: 15px;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message { 
  max-width: 85%;
  padding: 10px 14px; 
  border-radius: 12px; 
  font-size: 14px;
  line-height: 1.4;
  word-break: break-word;
}

.message p {
  margin: 5px 0 0 0;
}

.message strong {
  font-size: 12px;
  opacity: 0.8;
}

.message.user { 
  background-color: var(--primary-color, #4facfe); 
  color: white;
  align-self: flex-end;
  border-bottom-right-radius: 2px;
}

.message.ai { 
  background-color: white; 
  color: #333;
  align-self: flex-start;
  border-bottom-left-radius: 2px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.input-area { 
  display: flex; 
  padding: 12px;
  background: white;
  border-top: 1px solid #eee;
  gap: 8px; 
}

.input-area input { 
  flex: 1; 
  padding: 10px 14px; 
  border-radius: 20px; 
  border: 1px solid #ddd; 
  outline: none;
  font-size: 14px;
  transition: border-color 0.2s;
}

.input-area input:focus {
  border-color: var(--primary-color, #4facfe);
}

.input-area button { 
  padding: 8px 16px; 
  border-radius: 20px;
  background: var(--primary-color, #4facfe);
  color: white;
  border: none;
  cursor: pointer; 
  font-weight: 500;
  transition: background 0.2s;
}

.input-area button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.input-area button:hover:not(:disabled) {
  opacity: 0.9;
}
</style>
