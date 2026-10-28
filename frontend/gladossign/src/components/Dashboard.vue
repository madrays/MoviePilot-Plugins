<template>
  <div class="gshell gdash" :class="{ 'g-dark': isDark }">
    <div class="gbar">
      <span class="gglyph"><Glyph name="terminal" :size="14" /> GLaDOS</span>
      <span class="gtitle">CHECK-IN</span>
      <Glyph :name="session.logged_in ? 'wifi' : 'wifiOff'" :size="13" :class="session.logged_in ? 'gok' : 'gbad'" />
      <span class="gmono gtrunc">{{ session.logged_in ? session.email || 'SESSION ACTIVE' : 'NO SESSION' }}</span>
      <span class="gspacer" />
      <span class="gmono gstat"><b>{{ summary.points ?? '--' }}</b> pts</span>
      <span class="gmono gstat"><b>{{ summary.leftDays ?? '--' }}</b> d</span>
      <button
        class="gbtn primary"
        :disabled="!session.logged_in || loading"
        @click="checkin"
      >
        <Glyph :name="loading ? 'loader' : (lastOk ? 'check' : 'play')" :size="12" :class="{ gspin: loading }" />
        {{ loading ? '…' : '签到' }}
      </button>
      <button
        v-if="allowRefresh"
        class="gbtn"
        :disabled="loading"
        title="刷新"
        @click="load"
      >
        <Glyph :name="loading ? 'loader' : 'refresh'" :size="12" :class="{ gspin: loading }" />
      </button>
    </div>
    <div v-if="message" class="gnote gnote--in" :class="{ bad: messageType === 'error' }">
      <Glyph :name="messageType === 'error' ? 'alert' : 'checkCircle'" :size="13" :class="messageType === 'error' ? 'gbad' : 'gok'" />
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useTheme } from 'vuetify'
import { friendlyError, withTimeout } from '../utils/request'
import Glyph from './Glyph.vue'
import '../styles/terminal.css'

const props = defineProps({
  api: { type: Object, default: null },
  pluginId: { type: String, default: 'gladossign' },
  config: { type: Object, default: () => ({}) },
  allowRefresh: { type: Boolean, default: true },
  sourcePluginId: { type: String, default: '' },
})
const pluginId = computed(() => props.pluginId || 'gladossign')
let theme = null
try { theme = useTheme() } catch (e) { theme = null }
const isDark = computed(() => Boolean(theme && theme.current && theme.current.value && theme.current.value.dark))

const loading = ref(false)
const message = ref('')
const messageType = ref('success')
const lastOk = ref(false)
const session = reactive({ logged_in: false, email: '', login_at: '' })
const summary = reactive({ email: '', leftDays: null, points: null })

async function load() {
  if (!props.api) return
  loading.value = true
  try {
    const data = await withTimeout(
      props.api.get(`plugin/${pluginId.value}/state`),
      20000,
      '加载状态',
    )
    if (data) {
      Object.assign(session, data.session || {})
      Object.assign(summary, data.summary || {})
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
    const result = await withTimeout(
      props.api.post(`plugin/${pluginId.value}/checkin`, {}),
      45000,
      '签到',
    )
    message.value = (result && (result.msg || result.status)) || '签到完成'
    messageType.value = result && result.code === 0 ? 'success' : 'error'
    lastOk.value = Boolean(result && result.code === 0)
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

<style scoped>
.gdash {
  border: 1px solid var(--g-line);
}
.gtrunc {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.gstat b {
  color: var(--g-ink);
  font-weight: 700;
}
.gnote--in {
  border: 0;
  border-top: 1px solid var(--g-line);
  background: var(--g-panel);
}
</style>
