<template>
  <div class="gshell gpage" :class="{ 'g-dark': isDark }">
    <!-- 终端条 -->
    <div class="gbar">
      <span class="gglyph"><Glyph name="terminal" :size="15" /> GLaDOS</span>
      <span class="gtitle">CHECK-IN <span class="gdim">// TERMINAL</span></span>
      <span class="gspacer" />
      <Glyph
        :name="session.logged_in ? 'wifi' : 'wifiOff'"
        :size="14"
        :class="session.logged_in ? 'gok' : 'gbad'"
      />
      <span class="gmono">{{ session.logged_in ? 'SESSION ACTIVE' : 'NO SESSION' }}</span>
      <button class="gbtn" :disabled="loading" @click="loadAll">
        <Glyph :name="loading ? 'loader' : 'refresh'" :size="13" :class="{ gspin: loading }" />刷新
      </button>
    </div>

    <!-- 主视觉 -->
    <div class="ghero">
      <div class="ghero-main">
        <div class="ghero-kicker">GLADOS NETWORK · PROTOCOL 07</div>
        <div class="ghero-title">签到控制台 <span>/ DAILY SYNC</span></div>
        <div class="gboot">
          <span class="gprompt">glados@moviepilot:~$</span>
          {{ bootText }}
          <span class="gcursor">▌</span>
        </div>
      </div>
      <div class="gsignal" :class="session.logged_in ? 'is-on' : 'is-off'" aria-hidden="true">
        <span class="gsignal-ring" />
        <span class="gsignal-ring gsignal-ring--2" />
        <span class="gsignal-core" />
        <span class="gsignal-label">{{ session.logged_in ? 'LINK UP' : 'OFFLINE' }}</span>
      </div>
    </div>

    <!-- 状态提示 -->
    <div v-if="error" class="gnote bad gnote--pad">
      <Glyph name="alert" :size="14" class="gbad" />{{ error }}
    </div>
    <div v-else-if="message" class="gnote gnote--pad" :class="{ bad: messageType === 'error' }">
      <Glyph
        :name="messageType === 'error' ? 'alert' : 'checkCircle'"
        :size="14"
        :class="messageType === 'error' ? 'gbad' : 'gok'"
      />
      {{ message }}
    </div>

    <!-- 读数面板 -->
    <div class="gmetrics ganim">
      <div class="gcell">
        <div class="gk">Points</div>
        <div class="gv is-accent">{{ displayPoints ?? '--' }}</div>
        <div class="gs">当前点数</div>
      </div>
      <div class="gcell">
        <div class="gk">Days left</div>
        <div class="gv is-cyan">{{ displayDays ?? '--' }}</div>
        <div class="gs">已用 {{ summary.days ?? '--' }} 天</div>
      </div>
      <div class="gcell">
        <div class="gk">Last run</div>
        <div class="gv gv--sm">{{ lastRun.status || '--' }}</div>
        <div class="gs">{{ lastRun.date || '尚未运行' }}</div>
      </div>
      <div class="gcell">
        <div class="gk">Device</div>
        <div class="gv gv--sm">{{ device.platform || '--' }}</div>
        <div class="gs">{{ device.screen || '--' }}</div>
      </div>
    </div>

    <!-- 会话信息带 -->
    <div class="gstrip">
      <span class="gmono gmeta"><Glyph name="mail" :size="12" />{{ session.email || '—' }}</span>
      <span class="gmono gmeta"><Glyph name="clock" :size="12" />{{ session.login_at || '—' }}</span>
      <span class="gmono gmeta"><Glyph name="monitor" :size="12" />{{ device.platform || '—' }} · {{ device.screen || '—' }}</span>
      <span class="gmono gtrunc gmeta"><Glyph name="fingerprint" :size="12" />{{ device.fingerprint || '—' }}</span>
    </div>

    <!-- 操作区 -->
    <div class="gact ganim ganim-2">
      <button
        class="gbtn primary"
        :disabled="!session.logged_in || checkinLoading"
        @click="checkin"
      >
        <Glyph
          :name="checkinLoading ? 'loader' : lastOk ? 'check' : 'play'"
          :size="13"
          :class="{ gspin: checkinLoading }"
        />
        {{ checkinLoading ? '执行中…' : '执行签到' }}
      </button>
      <button class="gbtn" @click="$emit('switch')">
        <Glyph name="settings" :size="13" />配置 / 登录
      </button>
      <span class="gmono gact-note">
        {{ session.logged_in ? 'AUTO SCHEDULE ARMED' : 'WAITING FOR AUTH' }}
      </span>
    </div>

    <div v-if="!session.logged_in" class="gnote warn gnote--pad">
      <Glyph name="alert" :size="14" class="gdimtxt" />
      <span>尚未登录。<a class="glink" @click="$emit('switch')">用邮箱验证码登录</a>后即可自动签到，登录状态会持久化保存。</span>
    </div>

    <!-- 7 日点数 -->
    <section class="gsec">
      <div class="gsechead">
        <span class="gnum">SIG</span>
        <span class="glabel gmeta"><Glyph name="activity" :size="12" />最近 7 日点数</span>
        <span class="gline" />
        <span class="gmono">TOTAL {{ chartTotal }}</span>
      </div>
      <div class="gchart">
        <div
          v-for="day in chart"
          :key="day.key"
          class="gchartbar"
          :class="{ 'is-today': day.isToday }"
          :title="`${day.key} · ${day.value} 点`"
        >
          <span class="gchartbar-val">{{ day.value || '' }}</span>
          <span class="gchartbar-track">
            <span class="gchartbar-fill" :style="{ height: day.height + '%' }" />
          </span>
          <span class="gchartbar-label">{{ day.label }}</span>
        </div>
      </div>
    </section>

    <!-- 记录 -->
    <section class="gsec">
      <div class="gsechead">
        <span class="gnum">LOG</span>
        <span class="glabel gmeta"><Glyph name="history" :size="12" />最近记录</span>
        <span class="gline" />
      </div>

      <div v-if="logRows.length" class="glog">
        <div class="gloghead">
          <span>时间</span><span>状态</span><span>点数</span><span>说明</span>
        </div>
        <div v-for="(row, index) in logRows" :key="index" class="glogrow">
          <span class="gd">{{ row.date }}</span>
          <span>
            <span class="gtag" :class="tagClass(row)">
              <Glyph :name="Number(row.points_gain) > 0 ? 'check' : 'alert'" :size="10" />{{ row.status }}
            </span>
          </span>
          <span class="gmono">{{ row.points_gain }}</span>
          <span class="gm" :title="row.message">{{ row.message }}</span>
        </div>
      </div>
      <div v-else class="gempty">
        <Glyph name="inbox" :size="16" /> NO RECORDS // 运行一次签到后这里会出现记录
      </div>
    </section>

    <!-- 页脚 -->
    <div class="gfoot">
      <span class="gmono">GLaDOS CHECK-IN · MOVIEPILOT PLUGIN</span>
      <a
        class="gaff"
        :href="AFF_LINK"
        target="_blank"
        rel="noopener"
        @mouseenter="affHover = true"
        @mouseleave="affHover = false"
      >
        <Glyph :name="affHover ? 'externalLink' : 'arrowRight'" :size="12" />
        还没有账号？注册体验
      </a>
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
  sourcePluginId: { type: String, default: '' },
  nativeSubscribe: { type: Function, default: null },
})
const emit = defineEmits(['switch', 'action', 'close'])

const AFF_LINK = 'https://glados.space/landing/1F8CJ-TKYWO-KHOV3-PN7X2'
const pluginId = computed(() => props.pluginId || 'gladossign')

let theme = null
try { theme = useTheme() } catch (e) { theme = null }
const isDark = computed(() => Boolean(theme && theme.current && theme.current.value && theme.current.value.dark))

const loading = ref(false)
const loaded = ref(false)
const checkinLoading = ref(false)
const error = ref('')
const message = ref('')
const messageType = ref('success')
const history = ref([])
const lastOk = ref(false)
const affHover = ref(false)
const bootedAt = ref('')

const displayPoints = ref(null)
const displayDays = ref(null)

const session = reactive({ logged_in: false, email: '', login_at: '', cookie_items: 0 })
const summary = reactive({ email: '', user_id: null, days: null, leftDays: null, points: null })
const device = reactive({ platform: '', screen: '', ua: '', fingerprint: '' })
const state = reactive({ last_checkin: null })

const lastRun = computed(() => state.last_checkin || {})
const logRows = computed(() => history.value.slice(0, 8))
const bootText = computed(() => {
  if (!bootedAt.value) return 'booting terminal…'
  return session.logged_in
    ? `uplink established · session ${session.login_at || 'active'} · ${bootedAt.value}`
    : `awaiting authentication · ${bootedAt.value}`
})

const chart = computed(() => {
  const days = []
  const now = new Date()
  for (let i = 6; i >= 0; i -= 1) {
    const day = new Date(now)
    day.setDate(now.getDate() - i)
    days.push({
      key: `${day.getFullYear()}-${String(day.getMonth() + 1).padStart(2, '0')}-${String(day.getDate()).padStart(2, '0')}`,
      label: `${day.getMonth() + 1}/${day.getDate()}`,
      isToday: i === 0,
      value: 0,
    })
  }
  for (const row of history.value) {
    const key = String(row.date || '').slice(0, 10)
    const bucket = days.find((day) => day.key === key)
    if (bucket) bucket.value += Number(row.points_gain) || 0
  }
  const max = Math.max(1, ...days.map((day) => day.value))
  return days.map((day) => ({ ...day, height: Math.round((day.value / max) * 100) }))
})
const chartTotal = computed(() => chart.value.reduce((sum, day) => sum + day.value, 0))

function animateNumber(target, value) {
  const to = Number(value)
  if (value === null || value === undefined || Number.isNaN(to)) {
    target.value = null
    return
  }
  const reduce = typeof window !== 'undefined'
    && window.matchMedia
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reduce) {
    target.value = to
    return
  }
  const from = Number(target.value) || 0
  const start = performance.now()
  const duration = 620
  const step = (now) => {
    const progress = Math.min(1, (now - start) / duration)
    const eased = 1 - Math.pow(1 - progress, 3)
    target.value = Math.round(from + (to - from) * eased)
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

function showMessage(text, type = 'success') {
  message.value = text
  messageType.value = type
}

function tagClass(row) {
  const status = String(row.status || '')
  if (status.includes('成功') || status.includes('签到')) return 'ok'
  if (status.includes('失败') || status.includes('失效') || status.includes('不一致')) return 'bad'
  return ''
}

async function loadState() {
  if (!props.api) return
  const data = await withTimeout(
    props.api.get(`plugin/${pluginId.value}/state`),
    20000,
    '加载状态',
  )
  if (!data) return
  Object.assign(session, data.session || {})
  Object.assign(summary, data.summary || {})
  Object.assign(device, data.device || {})
  state.last_checkin = data.last_checkin || null
  animateNumber(displayPoints, summary.points)
  animateNumber(displayDays, summary.leftDays)
}

async function loadHistory() {
  if (!props.api) return
  const rows = await withTimeout(
    props.api.get(`plugin/${pluginId.value}/history`),
    20000,
    '加载历史',
  )
  history.value = Array.isArray(rows) ? rows : []
}

async function loadAll() {
  if (!props.api) {
    loaded.value = true
    return
  }
  loading.value = true
  error.value = ''
  try {
    await loadState()
    await loadHistory()
    loaded.value = true
  } catch (err) {
    error.value = `加载状态失败：${friendlyError(err)}`
  } finally {
    loading.value = false
  }
}

async function checkin() {
  if (!props.api) return
  checkinLoading.value = true
  error.value = ''
  try {
    const result = await withTimeout(
      props.api.post(`plugin/${pluginId.value}/checkin`, {}),
      45000,
      '签到',
    )
    if (result && result.code === 0) {
      lastOk.value = true
      showMessage(result.msg || '签到成功')
    } else {
      lastOk.value = false
      showMessage((result && (result.msg || result.status)) || '签到失败', 'error')
    }
    await loadAll()
    emit('action')
  } catch (err) {
    lastOk.value = false
    error.value = `签到失败：${friendlyError(err)}`
  } finally {
    checkinLoading.value = false
  }
}

watch(() => props.api, (value) => {
  if (value) loadAll()
})

watch(() => summary.points, (value) => animateNumber(displayPoints, value))
watch(() => summary.leftDays, (value) => animateNumber(displayDays, value))

onMounted(() => {
  bootedAt.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
  loadAll()
})
</script>

<style scoped>
.gpage {
  display: flex;
  flex-direction: column;
}
.gnote--pad {
  margin: 12px 14px 0;
}
.gstrip {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  padding: 8px 16px;
  border-bottom: 1px solid var(--g-line);
  background: var(--g-panel-2);
}
.gtrunc {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 260px;
}
.gact {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding: 14px 16px;
  border-bottom: 1px solid var(--g-line);
}
.gact-note {
  margin-left: auto;
}
.gv--sm {
  font-size: 18px;
  line-height: 1.3;
  letter-spacing: 0.02em;
}
.glink {
  color: var(--g-accent);
  cursor: pointer;
  border-bottom: 1px solid color-mix(in oklab, var(--g-accent) 50%, transparent);
}
.gfoot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
  padding: 10px 16px;
  color: var(--g-dim);
}
.gaff {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: 'Share Tech Mono', ui-monospace, monospace;
  font-size: 11.5px;
  color: var(--g-accent-2);
  text-decoration: none;
  border-bottom: 1px solid color-mix(in oklab, var(--g-accent-2) 40%, transparent);
}
.gaff:hover {
  color: var(--g-accent);
  border-bottom-color: var(--g-accent);
}
</style>
