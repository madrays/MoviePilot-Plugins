import { createApp, h, ref } from 'vue'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import 'vuetify/styles'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import Page from './components/Page.vue'
import Config from './components/Config.vue'
import Dashboard from './components/Dashboard.vue'

const vuetify = createVuetify({
  components,
  directives,
  icons: { defaultSet: 'mdi', aliases, sets: { mdi } },
  theme: {
    defaultTheme: 'gladosDark',
    themes: {
      gladosDark: {
        dark: true,
        colors: { primary: '#4ea1ff', success: '#3ecf8e', warning: '#ffb545', error: '#ff6b6b', background: '#121212', surface: '#1b1f24' },
      },
    },
  },
})

// ---- 模拟宿主 api（axios 风格，返回已解包数据）----
const calls = []
window.__calls = calls

const statePayload = {
  config: {
    enabled: true,
    notify: true,
    cron: '0 9 * * *',
    base_url: 'https://glados.space',
    email: 'demo@example.com',
    auto_exchange: '100',
    proxy_enabled: false,
    timeout_seconds: 30,
    max_attempts: 2,
    retry_no_proxy_fallback: true,
    retry_interval_seconds: 300,
    history_days: 30,
  },
  session: { logged_in: true, email: 'demo@example.com', login_at: '2026-10-28 09:00:00', cookie_items: 2 },
  device: { platform: 'Windows', screen: '1920x1080', ua: 'UA-demo', fingerprint: '2153399374…' },
  summary: { email: 'demo@example.com', user_id: 661475, days: 0, leftDays: 62, points: 1219 },
  last_checkin: { date: '2026-10-28 09:00:05', status: '签到成功', points_gain: 12 },
}

const historyPayload = [
  { date: '2026-10-28 09:00:05', status: '签到', points_gain: 12, message: '每日签到奖励' },
  { date: '2026-10-27 09:00:03', status: '签到', points_gain: 9, message: '每日签到奖励' },
]

let loggedIn = true
const api = {
  async get(path) {
    calls.push({ method: 'GET', path })
    if (path.endsWith('/state')) return { ...statePayload, session: { ...statePayload.session, logged_in: loggedIn } }
    if (path.endsWith('/history')) return historyPayload
    return {}
  },
  async post(path, body) {
    calls.push({ method: 'POST', path, body })
    if (path.endsWith('/checkin')) return { code: 0, status: '签到成功', msg: '签到成功！获得 12 点数' }
    if (path.endsWith('/send_code')) return { code: 0, msg: '验证码已发送，请查收邮箱' }
    if (path.endsWith('/login')) { loggedIn = true; return { code: 0, msg: '登录成功', leftDays: 62 } }
    if (path.endsWith('/logout')) { loggedIn = false; return { code: 0, msg: '已退出登录' } }
    return { code: -1, msg: 'unknown' }
  },
}

const tab = ref('page')
const saved = ref(null)
window.__saved = null

const app = createApp({
  render() {
    return h('v-app', [
      h('v-app-bar', { density: 'compact', color: 'primary' }, {
        default: () => [
          h('v-app-bar-title', { class: 'text-body-1' }, () => 'GlaDOS 测试台'),
          h('v-btn', { variant: 'text', onClick: () => (tab.value = 'page') }, () => '详情'),
          h('v-btn', { variant: 'text', onClick: () => (tab.value = 'config') }, () => '配置'),
          h('v-btn', { variant: 'text', onClick: () => (tab.value = 'dashboard') }, () => '仪表板'),
        ],
      }),
      h('v-main', [
        h('v-container', [
          tab.value === 'page'
            ? h(Page, { api, pluginId: 'gladossign', onSwitch: () => (tab.value = 'config'), onAction: () => calls.push({ method: 'EVENT', path: 'action' }) })
            : tab.value === 'config'
              ? h(Config, {
                  api,
                  pluginId: 'gladossign',
                  initialConfig: statePayload.config,
                  onSwitch: () => (tab.value = 'page'),
                  onSave: (payload) => { saved.value = payload; window.__saved = payload; calls.push({ method: 'EVENT', path: 'save', body: payload }) },
                })
              : h(Dashboard, { api, pluginId: 'gladossign', config: { attrs: {} }, allowRefresh: true }),
        ]),
      ]),
    ])
  },
})

app.use(vuetify)
app.mount('#app')
