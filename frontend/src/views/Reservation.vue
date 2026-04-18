<template>
  <div class="booking-container">
    <!-- 1. 日期选择横轴 -->
    <div class="date-tabs">
      <div 
        v-for="d in dates" :key="d.full"
        :class="['date-item', { active: selectedDate === d.full }]"
        @click="selectDate(d.full)"
      >
        <span>{{ d.week }}</span>
        <span>{{ d.day }}</span>
      </div>
    </div>

    <!-- 2. 时间段网格 -->
    <div class="time-grid">
      <button 
        v-for="slot in allTimeSlots" :key="slot"
        :class="['slot-btn', { 
          'full': bookedSlots.includes(slot), 
          'selected': selectedSlot === slot 
        }]"
        :disabled="bookedSlots.includes(slot)"
        @click="selectedSlot = slot"
      >
        {{ slot }}
        <span class="status-tag">{{ bookedSlots.includes(slot) ? '已满' : '剩余1' }}</span>
      </button>
    </div>

    <button class="submit-btn" @click="handleReserve">立即预约</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 所有的可选时间段（写死在前端，也可以从后端获取）
const allTimeSlots = ['10:00~10:30', '10:30~11:00', '14:30~15:00', '15:00~15:30']

// 响应式数据
const dates = ref([
  { week: '周六', day: '04/18', full: '2026-04-18' },
  { week: '周日', day: '04/19', full: '2026-04-19' },
  { week: '周一', day: '04/20', full: '2026-04-20' }
])
const selectedDate = ref('2026-04-18') // 当前选中的日期
const bookedSlots = ref([])           // 当前日期已被占用的段
const selectedSlot = ref('')          // 用户当前选中的段

// 逻辑：切换日期时，去后端抓取该日期的占用情况
const selectDate = async (date) => {
  selectedDate.value = date
  const res = await fetch(`http://127.0.0.1:8000/api/appointments/status/${date}`)
  bookedSlots.value = await res.json() // 后端返回如：["10:00~10:30"]
}

// 逻辑：提交预约
const handleReserve = async () => {
  const res = await fetch('http://127.0.0.1:8000/api/appointments', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      date: selectedDate.value,
      time_slot: selectedSlot.value,
      user_name: 'nb'
    })
  })
  if (!res.ok) {
    const err = await res.json()
    alert(err.detail) // 弹出“被人抢先了”
  } else {
    alert('预约成功！')
    selectDate(selectedDate.value) // 刷新状态
  }
}

onMounted(() => selectDate(selectedDate.value))
</script>

<style scoped>
/* 核心样式：模拟图片中的视觉效果 */
.date-tabs { display: flex; overflow-x: auto; gap: 10px; margin-bottom: 20px; }
.date-item { 
  border: 1px solid #ddd; padding: 10px; border-radius: 8px; 
  display: flex; flex-direction: column; align-items: center; min-width: 60px;
}
.date-item.active { border-color: #42b983; color: #42b983; background: #e6f7f0; }

.time-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.slot-btn { 
  border: 1px solid #eee; background: white; padding: 15px; border-radius: 8px;
  position: relative; text-align: left;
}
.slot-btn.full { background: #f5f5f5; color: #ccc; cursor: not-allowed; }
.slot-btn.selected { border-color: #42b983; background: #e6f7f0; }
.status-tag { font-size: 10px; color: #999; margin-left: 5px; }
</style>