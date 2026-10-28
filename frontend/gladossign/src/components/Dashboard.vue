<template>
  <v-card flat>
    <v-card-text class="d-flex align-center flex-wrap ga-3 py-2">
      <v-icon
        :icon="session.logged_in ? 'mdi-account-check' : 'mdi-account-off'"
        :color="session.logged_in ? 'success' : 'warning'"
      />
      <span class="text-body-2">
        {{ session.logged_in ? (session.email || '已登录') : '未登录' }}
      </span>
      <v-divider vertical class="mx-1" />
      <span class="text-body-2">
        剩余 <strong>{{ summary.leftDays ?? '—' }}</strong> 天
      </span>
      <v-divider vertical class="mx-1" />
      <span class="text-body-2">
        <strong>{{ summary.points ?? '—' }}</strong> 点
      </span>
      <v-divider vertical class="mx-1" />
      <span class="text-caption text-medium-emphasis">
        {{ device.platform }} · {{ device.screen }}
      </span>
      <v-spacer />
      <v-btn
        size="small"
        color="primary"
        variant="tonal"
        prepend-icon="mdi-calendar-check"
        :loading="loading"
        :disabled="!session.logged_in"
        @click="checkin"
      >
        签到
      </v-btn>
      <v-btn
        v-if="allowRefresh"
        size="small"
        variant="text"
        icon="mdi-refresh"
        :loading="loading"
        @click="load"
      />
    </v-card-text>
    <v-alert
      v-if="message"
      :type="messageType"
      density="compact"
      variant="tonal"
      class="mx-3 mb-2"
      closable
      @click:close="message = ''"
    >
      {{ message }}
    </v-alert>
  </v-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { friendlyError, withTimeout } from '../utils/request'

const props = defineProps({
  api: { type: Object, default: null },
  pluginId: { type: String, default: 'gladossign' },
  config: { type: Object, default: () => ({}) },
  allowRefresh: { type: Boolean, default: true },
  sourcePluginId: { type: String, default: '' },
})
const pluginId = computed(() => props.pluginId || 'gladossign')
const loading = ref(false)
const message = ref('')
const messageType = ref('success')
const session = reactive({ logged_in: false, email: '', login_at: '' })
const summary = reactive({ email: '', leftDays: null, points: null })
const device = reactive({ platform: '', screen: '' })

async function load() {
  if (!props.api) return
  loading.value = true
  try {
    const data = await withTimeout(props.api.get(`plugin/${pluginId.value}/state`), 20000, '加载状态')
    if (data) {
      Object.assign(session, data.session || {})
      Object.assign(summary, data.summary || {})
      Object.assign(device, data.device || {})
    }
  } catch (err) {
    message.value = `加载失败：${friendlyError(err)}`
    messageType.value = 'error'
  } finally {
    loading.value = false
  }
}

async function checkin() {
  if (!props.api) return
  loading.value = true
  try {
    const result = await withTimeout(props.api.post(`plugin/${pluginId.value}/checkin`, {}), 45000, '签到')
    message.value = (result && (result.msg || result.status)) || '签到完成'
    messageType.value = result && result.code === 0 ? 'success' : 'error'
    await load()
  } catch (err) {
    message.value = `签到失败：${friendlyError(err)}`
    messageType.value = 'error'
  } finally {
    loading.value = false
  }
}

watch(() => props.api, (value) => {
  if (value) load()
})

onMounted(load)
</script>
