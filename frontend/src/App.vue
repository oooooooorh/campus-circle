<template>
  <div id="app-container">
    <!-- Glassmorphic Navigation Bar -->
    <nav class="navbar glass-panel">
      <div class="nav-brand">
        <span class="icon">🎓</span>
        <span class="brand-text">校园圈</span>
      </div>
      <div class="nav-links">
        <router-link to="/forum" class="nav-item">
          <span class="nav-icon">💬</span> 校园论坛
        </router-link>
        <router-link to="/schedule" class="nav-item">
          <span class="nav-icon">📅</span> 课表同步
        </router-link>
        <router-link to="/me" class="nav-item">
          <span class="nav-icon">👤</span> 个人中心
        </router-link>
      </div>

      <div class="nav-actions">
        <template v-if="isAuthed">
          <span class="user-pill">已登录</span>
          <button class="nav-btn" @click="handleLogout">退出登录</button>
          <button class="nav-btn nav-btn-secondary" @click="handleSwitchAccount">切换账号</button>
        </template>
        <template v-else>
          <router-link to="/login" class="nav-btn-link">登录</router-link>
          <router-link to="/register" class="nav-btn-link nav-btn-link-secondary">注册</router-link>
        </template>
      </div>
    </nav>

    <!-- Main Content Area -->
    <main class="content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
      
      <!-- AI 助手组件悬浮在整个应用层面 -->
      <AiChat />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import AiChat from './components/AiChat.vue'
import { getAuthToken } from './config.js'
import { logout } from './api/auth-api.js'

const router = useRouter()
const isAuthed = computed(() => !!getAuthToken())

function handleLogout() {
  logout()
  router.push('/login')
}

function handleSwitchAccount() {
  logout()
  router.push('/login')
}
</script>

<style>
/* App Layout */
#app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Navbar Styles */
.navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 2rem;
  margin: 1rem auto;
  width: 90%;
  max-width: 1200px;
  border-radius: var(--radius-pill);
  gap: 1rem;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary-color);
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
}

.nav-actions{
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.user-pill{
  font-size: 0.9rem;
  color: var(--text-secondary);
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border-color);
  background: rgba(255,255,255,0.6);
}

.nav-btn{
  border: none;
  cursor: pointer;
  padding: 0.45rem 0.9rem;
  border-radius: var(--radius-pill);
  background: rgba(99, 102, 241, 0.12);
  color: var(--primary-color);
  font-weight: 600;
  transition: all .2s ease;
}

.nav-btn:hover{
  background: rgba(99, 102, 241, 0.18);
}

.nav-btn-secondary{
  background: rgba(148, 163, 184, 0.18);
  color: var(--text-secondary);
}

.nav-btn-secondary:hover{
  background: rgba(148, 163, 184, 0.26);
}

.nav-btn-link{
  text-decoration: none;
  padding: 0.45rem 0.9rem;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(99, 102, 241, 0.25);
  color: var(--primary-color);
  font-weight: 600;
  transition: all .2s ease;
}

.nav-btn-link:hover{
  background: rgba(99, 102, 241, 0.08);
}

.nav-btn-link-secondary{
  border-color: rgba(16, 185, 129, 0.25);
  color: rgba(16, 185, 129, 1);
}

.nav-btn-link-secondary:hover{
  background: rgba(16, 185, 129, 0.08);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-pill);
  transition: all 0.3s ease;
}

.nav-item:hover {
  color: var(--primary-color);
  background: rgba(99, 102, 241, 0.1);
}

.nav-item.router-link-active {
  color: var(--primary-color);
  background: rgba(99, 102, 241, 0.15);
  font-weight: 600;
}

/* Content Area */
.content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* Page Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
    border-radius: var(--radius-lg);
  }
  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
  }
}
</style>