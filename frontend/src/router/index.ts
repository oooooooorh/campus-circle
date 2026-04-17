import { createRouter, createWebHistory } from 'vue-router'
// 1. 引入刚才创建的三个大页面
import Forum from '../views/Forum.vue'
import Schedule from '../views/Schedule.vue'
import Reservation from '../views/Reservation.vue'

// 2. 定义路由映射表（地图）
const routes = [
    { path: '/', redirect: '/forum' }, // 默认打开网页就跳到论坛
    { path: '/forum', component: Forum },
    { path: '/schedule', component: Schedule },
    { path: '/reservation', component: Reservation }
]

// 3. 创建路由实例
const router = createRouter({
    history: createWebHistory(), // 使用 HTML5 模式，网址看起来很自然（没有#号）
    routes
})

export default router //暴露出去