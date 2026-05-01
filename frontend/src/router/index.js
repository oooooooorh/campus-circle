import { createRouter, createWebHistory } from 'vue-router'
import Forum from '../views/Forum.vue'
import Schedule from '../views/Schedule.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Me from '../views/Me.vue'
import UserPublic from '../views/UserPublic.vue'
import PostDetail from '../views/PostDetail.vue'
import { getAuthToken } from '../config.js'

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
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/me',
    name: 'Me',
    component: Me,
    meta: { requiresAuth: true }
  },
  {
    path: '/user/:id',
    name: 'UserPublic',
    component: UserPublic
  },
  {
    path: '/post/:id',
    name: 'PostDetail',
    component: PostDetail
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  if (to.meta?.requiresAuth && !getAuthToken()) {
    return { path: '/login' }
  }
})

export default router
