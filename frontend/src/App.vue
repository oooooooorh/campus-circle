<template>
  <div id="app-container">
    <!-- 导航栏：用户点击这里切换 URL -->
    <nav class="navbar">
      <router-link to="/forum">校园论坛</router-link>
      <router-link to="/schedule">课表同步</router-link>
      <router-link to="/reservation">按摩预约</router-link>
    </nav>

    <!-- 核心：路由出口 -->
    <main class="content">
      <router-view></router-view>
    </main>
  </div>
</template>

<style>
/* 简单的全局样式，让导航好看点 */
.navbar { background: #42b983; padding: 1rem; display: flex; gap: 20px; }
.navbar a { color: white; text-decoration: none; font-weight: bold; }
.navbar a.router-link-active { text-decoration: underline; color: #2c3e50; }
.content { padding: 20px; }
</style>