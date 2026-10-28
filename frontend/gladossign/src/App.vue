<template>
  <v-app>
    <v-app-bar color="primary" density="compact">
      <v-app-bar-title class="text-body-1">GlaDOS 签到 · 本地预览</v-app-bar-title>
    </v-app-bar>
    <v-main>
      <v-container>
        <v-alert type="info" variant="tonal" density="compact" class="mb-3 text-caption">
          这是本地开发预览壳。在 MoviePilot 中运行时，宿主会直接把 api / pluginId /
          initialConfig 作为 props 传给 Page、Config、Dashboard 组件，本文件不参与宿主渲染。
        </v-alert>
        <v-tabs v-model="tab" bg-color="surface" density="compact">
          <v-tab value="page">详情</v-tab>
          <v-tab value="config">配置</v-tab>
          <v-tab value="dashboard">仪表板</v-tab>
        </v-tabs>
        <v-window v-model="tab" class="mt-3">
          <v-window-item value="page">
            <Page :api="api" plugin-id="gladossign" @switch="tab = 'config'" />
          </v-window-item>
          <v-window-item value="config">
            <Config :api="api" :initial-config="initialConfig" plugin-id="gladossign" @switch="tab = 'page'" @save="onSave" />
          </v-window-item>
          <v-window-item value="dashboard">
            <Dashboard :api="api" plugin-id="gladossign" :config="{ attrs: {} }" />
          </v-window-item>
        </v-window>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import Page from './components/Page.vue'
import Config from './components/Config.vue'
import Dashboard from './components/Dashboard.vue'

const tab = ref('page')
const api = ref(null)
const initialConfig = {
  enabled: false,
  notify: true,
  cron: '0 9 * * *',
  base_url: 'https://glados.cloud',
  email: '',
  auto_exchange: '',
  proxy_enabled: false,
  timeout_seconds: 30,
  max_attempts: 2,
  retry_no_proxy_fallback: true,
  retry_interval_seconds: 300,
  history_days: 30,
}

function onSave(config) {
  console.log('[本地预览] 保存配置:', config)
}
</script>

<style>
body {
  margin: 0;
}
</style>
