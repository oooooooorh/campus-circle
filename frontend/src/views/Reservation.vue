<template>
  <div class="booking-container">
    <header class="page-header">
      <h1>按摩预约</h1>
      <p>放松身心，为您提供专业的校园理疗服务</p>
    </header>

    <!-- 日期选择横轴 -->
    <div class="date-tabs glass-panel">
      <button 
        v-for="d in dates" :key="d.full"
        :class="['date-pill', { active: selectedDate === d.full }]"
        @click="selectDate(d.full)"
      >
        <span class="week">{{ d.week }}</span>
        <span class="day">{{ d.day }}</span>
      </button>
    </div>

    <!-- 时间段网格 -->
    <div class="time-grid">
      <button 
        v-for="slot in allTimeSlots" :key="slot"
        :class="['time-slot glass-panel', { 
          'is-full': bookedSlots.includes(slot), 
          'is-selected': selectedSlot === slot 
        }]"
        :disabled="bookedSlots.includes(slot)"
        @click="selectedSlot = slot"
      >
        <div class="slot-content">
          <span class="time">{{ slot }}</span>
          <span v-if="bookedSlots.includes(slot)" class="status full">
            <span class="icon">🔒</span> 已满
          </span>
          <span v-else class="status available">
            可预约
          </span>
        </div>
      </button>
    </div>

    <!-- 底部悬浮操作区 -->
    <transition name="slide-up">
      <div v-if="selectedSlot" class="floating-action glass-panel">
        <div class="selection-info">
          <span class="label">已选时段:</span>
          <span class="value">{{ selectedDate }} {{ selectedSlot }}</span>
        </div>
        <button class="btn btn-primary" @click="handleReserve" :disabled="submitting">
          {{ submitting ? '预约中...' : '确认预约' }}
        </button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { API_BASE } from '../config.js'

const allTimeSlots = ['10:00~10:30', '10:30~11:00', '14:30~15:00', '15:00~15:30']

const dates = ref([
  { week: '周六', day: '04/18', full: '2026-04-18' },
  { week: '周日', day: '04/19', full: '2026-04-19' },
  { week: '周一', day: '04/20', full: '2026-04-20' }
])

const selectedDate = ref('2026-04-18')
const bookedSlots = ref([])
const selectedSlot = ref('')
const submitting = ref(false)

const selectDate = async (date) => {
  selectedDate.value = date
  selectedSlot.value = '' // 切换日期时清空选中
  try {
    const res = await fetch(`${API_BASE}/api/appointments/status/${date}`)
    bookedSlots.value = await res.json()
  } catch (e) {
    console.error('获取预约状态失败', e)
  }
}

const handleReserve = async () => {
  submitting.value = true
  try {
    const res = await fetch(`${API_BASE}/api/appointments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        date: selectedDate.value,
        time_slot: selectedSlot.value,
        user_name: '同学'
      })
    })
    
    if (!res.ok) {
      const err = await res.json()
      alert(`预约失败: ${err.detail}`)
    } else {
      alert('🎉 预约成功！请准时到达。')
      selectDate(selectedDate.value)
    }
  } catch (e) {
    alert('网络错误，请稍后再试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => selectDate(selectedDate.value))
</script>

<style scoped>
.booking-container {
  max-width: 800px;
  margin: 0 auto;
  padding-bottom: 100px; /* 为底部悬浮按钮留出空间 */
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

/* Date Pickers */
.date-tabs {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  margin-bottom: 2rem;
  overflow-x: auto;
  justify-content: center;
}

.date-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.8rem 1.5rem;
  border-radius: var(--radius-pill);
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 100px;
}

.date-pill:hover:not(.active) {
  background: rgba(99, 102, 241, 0.05);
}

.date-pill.active {
  background: var(--primary-color);
  color: white;
  box-shadow: var(--shadow-md), var(--shadow-glow);
}

.date-pill .week {
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.2rem;
}

.date-pill .day {
  font-size: 1.2rem;
  font-weight: 700;
}

/* Time Grid */
.time-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}

.time-slot {
  padding: 1.5rem;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
}

.time-slot:not(.is-full):hover {
  transform: translateY(-2px);
  border-color: rgba(99, 102, 241, 0.3);
  box-shadow: var(--shadow-md);
}

.time-slot.is-selected {
  border-color: var(--primary-color);
  background: rgba(99, 102, 241, 0.05);
  box-shadow: var(--shadow-md), 0 0 0 1px var(--primary-color);
}

.time-slot.is-full {
  background: rgba(226, 232, 240, 0.5);
  opacity: 0.7;
  cursor: not-allowed;
  filter: grayscale(1);
}

.slot-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.time {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.status {
  font-size: 0.85rem;
  font-weight: 500;
}

.status.available {
  color: var(--success);
}

.status.full {
  color: var(--text-light);
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

/* Floating CTA */
.floating-action {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  width: 90%;
  max-width: 600px;
  border-radius: var(--radius-pill);
  z-index: 100;
}

.selection-info {
  display: flex;
  flex-direction: column;
}

.selection-info .label {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.selection-info .value {
  font-weight: 600;
  color: var(--primary-color);
  font-size: 1.1rem;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translate(-50%, 100%);
}

@media (max-width: 640px) {
  .date-tabs {
    justify-content: flex-start;
  }
  .time-grid {
    grid-template-columns: 1fr;
  }
  .floating-action {
    flex-direction: column;
    gap: 1rem;
    border-radius: var(--radius-lg);
  }
  .floating-action .btn {
    width: 100%;
  }
}
</style>