<template>
  <div class="schedule-page">
    <div class="schedule-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>📚 我的课表</h1>
        <p class="subtitle">点击按钮同步学校官网课表</p>
      </div>

      <!-- 登录表单卡片 -->
      <div class="login-card">
        <h2>🔐 教务系统登录</h2>
        
        <div class="form-group">
          <label for="username">学号：</label>
          <input
            id="username"
            v-model="credentials.username"
            type="text"
            placeholder="请输入学号"
            :disabled="loading"
            @keyup.enter="fetchSchedule"
          />
        </div>

        <div class="form-group">
          <label for="password">密码：</label>
          <input
            id="password"
            v-model="credentials.password"
            type="password"
            placeholder="请输入教务系统密码"
            :disabled="loading"
            @keyup.enter="fetchSchedule"
          />
        </div>

        <div class="button-group">
          <button 
            @click="fetchSchedule" 
            class="btn-primary"
            :disabled="loading || !credentials.username || !credentials.password"
          >
            <span v-if="!loading">🔄 获取课表</span>
            <span v-else>⏳ 正在加载...</span>
          </button>
          
          <button 
            v-if="schedule.length > 0"
            @click="downloadJSON"
            class="btn-secondary"
            :disabled="loading"
          >
            💾 下载 JSON
          </button>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="alert alert-error">
          <span class="alert-icon">❌</span>
          <span class="alert-text">{{ error }}</span>
          <button class="alert-close" @click="error = null">×</button>
        </div>

        <!-- 成功提示 -->
        <div v-if="successMessage" class="alert alert-success">
          <span class="alert-icon">✅</span>
          <span class="alert-text">{{ successMessage }}</span>
          <button class="alert-close" @click="successMessage = null">×</button>
        </div>
      </div>

      <!-- 课表显示区域 -->
      <div v-if="schedule.length > 0" class="schedule-content">
        <h2>📖 课表信息</h2>
        
        <!-- 统计信息 -->
        <div class="schedule-stats">
          <div class="stat-item">
            <span class="stat-label">总课程数：</span>
            <span class="stat-value">{{ schedule.length }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">周次跨度：</span>
            <span class="stat-value">{{ weekRange }}</span>
          </div>
        </div>

        <!-- 课程表格 -->
        <div class="table-wrapper">
          <table class="schedule-table">
            <thead>
              <tr>
                <th>课程代码</th>
                <th>课程名称</th>
                <th>学分</th>
                <th>班级</th>
                <th>周次</th>
                <th>星期</th>
                <th>节次</th>
                <th>教师</th>
                <th>地点</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(course, index) in schedule" :key="index" class="table-row">
                <td class="code">{{ course.kh }}</td>
                <td class="name">{{ course.kcmc }}</td>
                <td class="credit">{{ course.xf }}</td>
                <td class="class">{{ course.jxb }}</td>
                <td class="weeks">{{ course.zc }}</td>
                <td class="day">{{ course.xq }}</td>
                <td class="time">{{ course.jc }}</td>
                <td class="teacher">{{ course.kcjs || '-' }}</td>
                <td class="location">{{ course.skdd || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 周次日程表（可视化） -->
        <h2>📅 周次日程</h2>
        <div class="weekly-schedule">
          <div class="week-grid">
            <div 
              v-for="(day, dayIndex) in weekDays" 
              :key="dayIndex"
              class="day-column"
            >
              <div class="day-header">{{ day }}</div>
              <div class="courses">
                <div 
                  v-for="(course, courseIndex) in getCoursesForDay(day)"
                  :key="courseIndex"
                  class="course-block"
                  :style="{ backgroundColor: getCourseColor(courseIndex) }"
                >
                  <div class="course-title">{{ course.kcmc }}</div>
                  <div class="course-time">{{ course.jc }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态提示 -->
      <div v-else-if="!loading" class="empty-state">
        <div class="empty-icon">📋</div>
        <p>还没有加载课表</p>
        <p class="empty-hint">输入学号和密码，点击"获取课表"开始</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getSchedule } from '../api/schedule-api.js'

// 状态管理
const credentials = ref({
  username: '',
  password: ''
})

const schedule = ref([])
const loading = ref(false)
const error = ref(null)
const successMessage = ref(null)

// 周一到周日
const weekDays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']

// 课程颜色列表
const colors = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
  '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#A8E6CF'
]

/**
 * 获取周次范围
 */
const weekRange = computed(() => {
  if (schedule.value.length === 0) return '-'
  const weeks = new Set()
  schedule.value.forEach(course => {
    if (course.zc) {
      weeks.add(course.zc)
    }
  })
  return Array.from(weeks).join('; ')
})

/**
 * 获取某天的课程
 */
function getCoursesForDay(day) {
  return schedule.value.filter(course => course.xq === day)
}

/**
 * 获取课程的随机颜色
 */
function getCourseColor(index) {
  return colors[index % colors.length]
}

/**
 * 获取课表
 */
async function fetchSchedule() {
  // 验证输入
  if (!credentials.value.username || !credentials.value.password) {
    error.value = '请输入学号和密码'
    return
  }

  loading.value = true
  error.value = null
  successMessage.value = null

  try {
    const result = await getSchedule(
      credentials.value.username,
      credentials.value.password
    )

    if (result.status === 'success' && result.data) {
      schedule.value = result.data
      successMessage.value = `✅ 成功加载 ${result.count} 门课程！`
      
      // 3秒后自动关闭成功提示
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
    } else {
      error.value = '未获取到课表数据'
    }
  } catch (err) {
    error.value = err.message || '获取课表失败，请检查账号密码'
    console.error('爬虫错误:', err)
  } finally {
    loading.value = false
  }
}

/**
 * 下载 JSON 文件
 */
function downloadJSON() {
  try {
    const dataStr = JSON.stringify(schedule.value, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json;charset=utf-8' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `课表_${new Date().toISOString().slice(0, 10)}.json`
    link.click()
    URL.revokeObjectURL(url)
    successMessage.value = '✅ 课表已下载'
    setTimeout(() => {
      successMessage.value = null
    }, 2000)
  } catch (err) {
    error.value = '下载失败: ' + err.message
  }
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.schedule-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.schedule-container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  color: white;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 2.5em;
  margin: 0 0 10px 0;
  font-weight: 700;
}

.subtitle {
  font-size: 1.1em;
  opacity: 0.9;
  margin: 0;
}

/* 登录卡片 */
.login-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.login-card h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  font-size: 1.5em;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1em;
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 25px;
  flex-wrap: wrap;
}

/* 按钮样式 */
.btn-primary,
.btn-secondary {
  padding: 12px 30px;
  border: none;
  border-radius: 8px;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 150px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
  border: 2px solid #e0e0e0;
}

.btn-secondary:hover:not(:disabled) {
  background: #e0e0e0;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 提示框 */
.alert {
  padding: 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 20px;
  font-weight: 500;
}

.alert-icon {
  font-size: 1.3em;
  flex-shrink: 0;
}

.alert-text {
  flex: 1;
}

.alert-close {
  background: none;
  border: none;
  font-size: 1.5em;
  cursor: pointer;
  padding: 0;
  color: inherit;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.alert-close:hover {
  opacity: 1;
}

.alert-error {
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ef5350;
}

.alert-success {
  background-color: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #66bb6a;
}

/* 课表内容 */
.schedule-content {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.schedule-content h2 {
  color: #333;
  margin-top: 0;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #667eea;
  font-size: 1.3em;
}

/* 统计信息 */
.schedule-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.stat-item {
  background: #f5f7fa;
  padding: 15px 20px;
  border-radius: 8px;
  display: flex;
  gap: 10px;
  align-items: center;
  flex: 1;
  min-width: 200px;
}

.stat-label {
  color: #666;
  font-weight: 600;
}

.stat-value {
  color: #667eea;
  font-weight: 700;
  font-size: 1.2em;
}

/* 表格 */
.table-wrapper {
  overflow-x: auto;
  margin: 20px 0;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.schedule-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9em;
}

.schedule-table thead {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  position: sticky;
  top: 0;
  z-index: 10;
}

.schedule-table th {
  padding: 15px;
  text-align: left;
  font-weight: 600;
  white-space: nowrap;
}

.schedule-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.schedule-table tbody tr:hover {
  background-color: #f0f0f0;
}

.schedule-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #e0e0e0;
}

.table-row:last-child td {
  border-bottom: none;
}

.code {
  color: #667eea;
  font-weight: 600;
  font-family: 'Monaco', 'Courier New', monospace;
}

.name {
  font-weight: 500;
}

.credit {
  text-align: center;
  color: #FF6B6B;
  font-weight: 600;
}

/* 周次日程 */
.weekly-schedule {
  margin-top: 30px;
}

.week-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.day-column {
  background: #f9f9f9;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.day-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 10px;
  text-align: center;
  font-weight: 600;
}

.courses {
  padding: 10px;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.course-block {
  padding: 10px;
  border-radius: 6px;
  color: white;
  font-size: 0.85em;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.course-block:hover {
  transform: translateY(-2px);
}

.course-title {
  font-weight: 600;
  margin-bottom: 4px;
  line-height: 1.2;
}

.course-time {
  font-size: 0.75em;
  opacity: 0.9;
}

/* 空状态 */
.empty-state {
  background: white;
  border-radius: 12px;
  padding: 60px 30px;
  text-align: center;
  color: #999;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.empty-icon {
  font-size: 3em;
  margin-bottom: 20px;
}

.empty-state p {
  margin: 10px 0;
  font-size: 1.1em;
}

.empty-hint {
  font-size: 0.95em;
  color: #bbb;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header h1 {
    font-size: 1.8em;
  }

  .schedule-stats {
    flex-direction: column;
  }

  .stat-item {
    min-width: 100%;
  }

  .schedule-table {
    font-size: 0.8em;
  }

  .schedule-table th,
  .schedule-table td {
    padding: 8px;
  }

  .button-group {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }

  .week-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }
}
</style>