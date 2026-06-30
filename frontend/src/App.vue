<template>
  <a-layout class="app-shell">
    <a-layout-header class="app-header">
      <button class="brand" type="button" @click="router.push('/')">
        <GlobalOutlined />
        <span>智能旅行助手</span>
      </button>

      <nav class="app-nav" aria-label="主导航">
        <a-button
          :type="activePage === 'plan' ? 'primary' : 'text'"
          :ghost="activePage === 'plan'"
          @click="router.push('/')"
        >
          <template #icon><HomeOutlined /></template>
          规划行程
        </a-button>
        <a-button
          :type="activePage === 'history' ? 'primary' : 'text'"
          :ghost="activePage === 'history'"
          @click="router.push('/history')"
        >
          <template #icon><HistoryOutlined /></template>
          历史记录
        </a-button>
      </nav>
    </a-layout-header>

    <a-layout-content class="app-content">
      <router-view />
    </a-layout-content>

    <a-layout-footer class="app-footer">
      智能旅行助手 ©{{ currentYear }}
    </a-layout-footer>
  </a-layout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { GlobalOutlined, HistoryOutlined, HomeOutlined } from '@ant-design/icons-vue'

const route = useRoute()
const router = useRouter()
const currentYear = new Date().getFullYear()
const activePage = computed(() => route.path.startsWith('/history') ? 'history' : 'plan')
</script>

<style>
html,
body,
#app {
  min-height: 100%;
  margin: 0;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif;
}

.app-shell {
  width: 100%;
  min-height: 100vh;
  overflow-x: hidden;
}

.app-header {
  height: 64px;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  background: #172033;
}

.brand {
  min-width: 0;
  padding: 0;
  border: 0;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: transparent;
  color: #fff;
  font-size: 21px;
  font-weight: 700;
  cursor: pointer;
}

.app-nav {
  display: flex;
  gap: 8px;
}

.app-nav .ant-btn-text {
  color: rgba(255, 255, 255, 0.82);
}

.app-nav .ant-btn-text:hover {
  color: #fff !important;
  background: rgba(255, 255, 255, 0.1) !important;
}

.app-content {
  width: 100%;
  min-width: 0;
  min-height: 0;
}

.app-footer {
  padding: 18px 24px;
  text-align: center;
  color: #64748b;
  background: #f8fafc;
  border-top: 1px solid #e5e7eb;
}

@media (max-width: 640px) {
  .app-header {
    height: auto;
    min-height: 112px;
    padding: 10px 16px;
    gap: 12px;
    flex-wrap: wrap;
    align-content: center;
    line-height: normal;
  }

  .brand {
    width: 100%;
    font-size: 18px;
  }

  .app-nav {
    width: 100%;
    gap: 2px;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .app-nav .ant-btn {
    min-width: 0;
    width: 100%;
    padding-inline: 9px;
  }
}
</style>
