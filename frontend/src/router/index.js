import { createRouter, createWebHistory } from 'vue-router'
import Forum from '../views/Forum.vue'
import Schedule from '../views/Schedule.vue'
import Reservation from '../views/Reservation.vue'

const routes = [
  {
    path: '/',
    redirect: '/forum'
  },
  {
    path: '/forum',
    name: 'Forum',
    component: Forum
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: Schedule
  },
  {
    path: '/reservation',
    name: 'Reservation',
    component: Reservation
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
