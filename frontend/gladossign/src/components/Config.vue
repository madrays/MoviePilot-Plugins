<template>
  <div class="gshell gconfig" :class="{ 'g-dark': isDark }">
    <!-- 终端条 -->
    <div class="gbar">
      <span class="gglyph"><Glyph name="terminal" :size="15" /> GLaDOS</span>
      <span class="gtitle">CONFIG <span class="gdim">// AUTH &amp; RUNNER</span></span>
      <span class="gspacer" />
      <span class="gled" :class="session.logged_in ? 'ok' : 'bad'" />
      <span class="gmono">{{ session.logged_in ? 'AUTH OK' : 'NO SESSION' }}</span>
      <button class="gbtn" @click="$emit('switch')">
        <Glyph name="chevronLeft" :size="13" />返回
      </button>
    </div>

    <!-- 提示 -->
    <div v-if="error" class="gnote bad gnote--pad">{{ error }}</div>
    <div v-else-if="message" class="gnote gnote--pad" :class="{ bad: messageType === 'error' }">
      {{ message }}
    </div>

    <!-- 01 认证 -->
    <section class="gsec" @mouseenter="hoverSec = 'auth'" @mouseleave="hoverSec = ''">
      <div class="gsechead">
        <span class="gnum">01</span>
        <span class="glabel gmeta"><Glyph :name="hoverSec === 'auth' ? 'check' : 'shield'" :size="12" />Authentication</span>
        <span class="gline" />
      </div>

      <p class="gdesc">
        登录由 MoviePilot 服务器直接完成，设备身份每套安装独立生成，无需从浏览器复制 Cookie。
        登录状态持久化保存，MP 重启后无需重复登录；仅当 GlaDOS 主动失效会话时才需重新认证。
      </p>

      <div class="gform">
        <v-text-field
          v-model="email"
          label="GlaDOS 登录邮箱"
          placeholder="you@example.com"
          density="compact"
          variant="outlined"
          autocomplete="off"
          hide-details="auto"
          :disabled="session.logged_in"
        >
          <template #prepend-inner>
            <Glyph name="mail" :size="15" class="gdimtxt" />
          </template>
        </v-text-field>
        <button
          class="gbtn"
          :disabled="!email || session.logged_in || sending || cooldown > 0"
          @click="sendCode"
        >
          <Glyph :name="cooldown > 0 ? 'check' : sending ? 'loader' : 'send'" :size="13" :class="{ gspin: sending }" />
          {{ cooldown > 0 ? `重发 ${cooldown}s` : sending ? '发送中…' : '发送验证码' }}
        </button>

        <v-text-field
          v-model="code"
          label="邮箱验证码"
          placeholder="6 位验证码"
          density="compact"
          variant="outlined"
          autocomplete="one-time-code"
          hide-details="auto"
          :disabled="session.logged_in"
          @keyup.enter="login"
        >
          <template #prepend-inner>
            <Glyph name="key" :size="15" class="gdimtxt" />
          </template>
        </v-text-field>
        <button
          class="gbtn primary"
          :disabled="!email || !code || session.logged_in || loggingIn"
          @click="login"
        >
          <Glyph :name="loggingIn ? 'loader' : 'login'" :size="13" :class="{ gspin: loggingIn }" />
          {{ loggingIn ? '登录中…' : '登录' }}
        </button>
      </div>

      <div class="greadout">
        <span class="gtag" :class="session.logged_in ? 'ok' : 'bad'">
          {{ session.logged_in ? 'SESSION ACTIVE' : 'NO SESSION' }}
        </span>
        <span class="gmono gmeta"><Glyph name="mail" :size="11" />{{ session.email || '—' }}</span>
        <span class="gmono gmeta"><Glyph name="shield" :size="11" />COOKIE {{ session.cookie_items || 0 }}</span>
        <span class="gmono gmeta"><Glyph name="clock" :size="11" />{{ session.login_at ? 'AT ' + session.login_at : '—' }}</span>
        <span class="gmono gmeta"><Glyph name="monitor" :size="11" />{{ device.platform || '—' }} · {{ device.screen || '—' }}</span>
        <button v-if="session.logged_in" class="gbtn gbtn--mini" @click="logout"><Glyph name="logout" :size="11" />退出</button>
      </div>
    </section>

    <!-- 02 调度 -->
    <section class="gsec" @mouseenter="hoverSec = 'schedule'" @mouseleave="hoverSec = ''">
      <div class="gsechead">
        <span class="gnum">02</span>
        <span class="glabel gmeta"><Glyph :name="hoverSec === 'schedule' ? 'clock' : 'calendar'" :size="12" />Schedule &amp; Rewards</span>
        <span class="gline" />
      </div>

      <div class="gform gform--4">
        <v-switch v-model="config.enabled" label="启用插件" color="success" density="compact" hide-details />
        <v-switch v-model="config.notify" label="发送通知" color="success" density="compact" hide-details />
        <v-text-field
          v-model="config.cron"
          label="签到周期（Cron）"
          placeholder="0 9 * * *"
          density="compact"
          variant="outlined"
          hide-details="auto"
          hint="默认每天 09:00"
          persistent-hint
        />
        <v-text-field
          v-model.number="config.history_days"
          label="历史保留（天）"
          type="number"
          density="compact"
          variant="outlined"
          hide-details
        />
      </div>

      <div class="gform gform--3">
        <v-select
          v-model="config.auto_exchange"
          label="自动兑换"
          :items="exchangePlans"
          density="compact"
          variant="outlined"
          hide-details="auto"
          hint="达到门槛后每日最多兑换一次"
          persistent-hint
        />
        <v-text-field
          v-model.number="config.timeout_seconds"
          label="超时（秒）"
          type="number"
          density="compact"
          variant="outlined"
          hide-details
        />
        <v-text-field
          v-model.number="config.max_attempts"
          label="重试次数"
          type="number"
          density="compact"
          variant="outlined"
          hide-details
        />
      </div>
    </section>

    <!-- 03 传输 -->
    <section class="gsec" @mouseenter="hoverSec = 'transport'" @mouseleave="hoverSec = ''">
      <div class="gsechead">
        <span class="gnum">03</span>
        <span class="glabel gmeta"><Glyph :name="hoverSec === 'transport' ? 'wifi' : 'plug'" :size="12" />Transport</span>
        <span class="gline" />
      </div>

      <div class="gform gform--3">
        <v-select
          v-model="config.device_platform"
          label="设备平台"
          :items="platformItems"
          density="compact"
          variant="outlined"
          hide-details="auto"
          hint="每套安装独立随机；修改后需重新登录"
          persistent-hint
        />
        <v-text-field
          v-model="config.base_url"
          label="Base URL"
          placeholder="https://glados.cloud"
          density="compact"
          variant="outlined"
          hide-details="auto"
          hint="账号在 glados.space 则改成对应域名"
          persistent-hint
        />
        <v-text-field
          v-model.number="config.retry_interval_seconds"
          label="重试间隔（秒）"
          type="number"
          density="compact"
          variant="outlined"
          hide-details
        />
      </div>

      <div class="gform gform--2">
        <v-switch
          v-model="config.proxy_enabled"
          label="使用 MP 全局代理"
          color="success"
          density="compact"
          hide-details
        />
        <v-switch
          v-model="config.retry_no_proxy_fallback"
          label="失败后直连重试"
          color="success"
          density="compact"
          hide-details
        />
      </div>
    </section>

    <!-- 04 AFF -->
    <section class="gsec gsec--aff" @mouseenter="hoverSec = 'aff'" @mouseleave="hoverSec = ''">
      <div class="gsechead">
        <span class="gnum">04</span>
        <span class="glabel gmeta"><Glyph :name="hoverSec === 'aff' ? 'check' : 'gift'" :size="12" />Referral / AFF</span>
        <span class="gline" />
      </div>

      <div class="gaffbox">
        <div class="gaffmedia">
          <img :src="gladosLogo" alt="GlaDOS" />
        </div>
        <div class="gafftext">
          <div class="gafftitle">注册与福利</div>
          <p class="gdesc">
            GlaDOS 比较佛系，靠每日签到可以长期使用，有需要可以点右侧注册体验。
            签到点数可兑换套餐：100 点 = 10 天 / 200 点 = 30 天 / 500 点 = 100 天。
          </p>
        </div>
        <a
          class="gbtn primary gaffico"
          :href="AFF_LINK"
          target="_blank"
          rel="noopener"
          @mouseenter="affHover = true"
          @mouseleave="affHover = false"
        >
          <Glyph :name="affHover ? 'externalLink' : 'gift'" :size="14" />
          立即注册
        </a>
      </div>
    </section>

    <!-- 保存栏 -->
    <div class="gfoot gfoot--sticky">
      <button class="gbtn primary" :disabled="saving" @click="save(false)">
        <Glyph :name="saving ? 'loader' : 'save'" :size="13" :class="{ gspin: saving }" />
        {{ saving ? '保存中…' : '保存设置' }}
      </button>
      <button class="gbtn" :disabled="saving" @click="save(true)">
        <Glyph name="play" :size="13" />保存并运行一次
      </button>
      <span class="gmono gfoot-note">CHANGES APPLY ON SAVE</span>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useTheme } from 'vuetify'
import { friendlyError, withTimeout } from '../utils/request'
import Glyph from './Glyph.vue'
import gladosLogo from '../assets/gladosLogo'
import '../styles/terminal.css'

const props = defineProps({
  api: { type: Object, default: null },
  initialConfig: { type: Object, default: () => ({}) },
  pluginId: { type: String, default: 'gladossign' },
  sourcePluginId: { type: String, default: '' },
  nativeSubscribe: { type: Function, default: null },
})
const emit = defineEmits(['save', 'switch', 'close'])

const AFF_LINK = 'https://glados.space/landing/1F8CJ-TKYWO-KHOV3-PN7X2'


const pluginId = computed(() => props.pluginId || 'gladossign')
let theme = null
try { theme = useTheme() } catch (e) { theme = null }
const isDark = computed(() => Boolean(theme && theme.current && theme.current.value && theme.current.value.dark))

const error = ref('')
const message = ref('')
const messageType = ref('success')
const sending = ref(false)
const loggingIn = ref(false)
const saving = ref(false)
const cooldown = ref(0)
const affHover = ref(false)
const hoverSec = ref('')
let cooldownTimer = null

const email = ref('')
const code = ref('')
const session = reactive({ logged_in: false, email: '', login_at: '', cookie_items: 0 })
const device = reactive({ platform: '', screen: '', ua: '', fingerprint: '' })

const config = reactive({
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
  retry_interval_seconds: 10,
  history_days: 30,
  device_platform: 'auto',
})

if (props.initialConfig && Object.keys(props.initialConfig).length) {
  Object.assign(config, props.initialConfig)
  email.value = props.initialConfig.email || ''
}

const exchangePlans = [
  { title: '不自动兑换', value: '' },
  { title: '10 天（100 积分）', value: '10' },
  { title: '30 天（200 积分）', value: '30' },
  { title: '100 天（500 积分）', value: '100' },
]
const platformItems = [
  { title: '自动（跟随 MP 宿主机）', value: 'auto' },
  { title: 'Windows', value: 'windows' },
  { title: 'macOS', value: 'macos' },
  { title: 'Linux', value: 'linux' },
]

function showMessage(text, type = 'success') {
  message.value = text
  messageType.value = type
}

function startCooldown(seconds = 60) {
  cooldown.value = seconds
  if (cooldownTimer) clearInterval(cooldownTimer)
  cooldownTimer = setInterval(() => {
    cooldown.value -= 1
    if (cooldown.value <= 0) {
      clearInterval(cooldownTimer)
      cooldownTimer = null
    }
  }, 1000)
}

async function loadState() {
  if (!props.api) return
  const data = await withTimeout(
    props.api.get(`plugin/${pluginId.value}/state`),
    20000,
    '加载状态',
  )
  if (!data) return
  if (data.config) {
    Object.assign(config, data.config)
    email.value = data.config.email || email.value
  }
  Object.assign(session, data.session || {})
  Object.assign(device, data.device || {})
}

async function sendCode() {
  if (!props.api || cooldown.value > 0) return
  sending.value = true
  error.value = ''
  try {
    const result = await withTimeout(
      props.api.post(`plugin/${pluginId.value}/send_code`, { email: email.value }),
      25000,
      '发送验证码',
    )
    if (result && result.code === 0) {
      showMessage(result.msg || '验证码已发送')
      startCooldown(60)
    } else {
      showMessage((result && result.msg) || '发送失败', 'error')
    }
  } catch (err) {
    error.value = `发送验证码失败：${friendlyError(err)}`
  } finally {
    sending.value = false
  }
}

async function login() {
  if (!props.api) return
  loggingIn.value = true
  error.value = ''
  try {
    const result = await withTimeout(
      props.api.post(`plugin/${pluginId.value}/login`, {
        email: email.value,
        code: code.value,
      }),
      45000,
      '登录',
    )
    if (result && result.code === 0) {
      showMessage(`登录成功（剩余 ${result.leftDays ?? '—'} 天）`)
      code.value = ''
      config.email = email.value
      await loadState()
    } else {
      showMessage((result && result.msg) || '登录失败', 'error')
    }
  } catch (err) {
    error.value = `登录失败：${friendlyError(err)}`
  } finally {
    loggingIn.value = false
  }
}

async function logout() {
  if (!props.api) return
  try {
    await withTimeout(props.api.post(`plugin/${pluginId.value}/logout`, {}), 15000, '退出登录')
    showMessage('已退出登录')
    await loadState()
  } catch (err) {
    error.value = `退出失败：${friendlyError(err)}`
  }
}

function save(runNow = false) {
  saving.value = true
  error.value = ''
  const payload = {
    ...JSON.parse(JSON.stringify(config)),
    email: email.value || config.email,
    onlyonce: Boolean(runNow),
  }
  emit('save', payload)
  setTimeout(() => {
    saving.value = false
    showMessage(runNow ? '已保存，正在运行一次签到' : '设置已保存')
  }, 500)
}

watch(() => props.api, (value) => {
  if (value) loadState()
})

onMounted(loadState)
onBeforeUnmount(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})
</script>

<style scoped>
.gconfig {
  display: flex;
  flex-direction: column;
}
.gnote--pad {
  margin: 12px 14px 0;
}
.gdesc {
  margin: 0 0 12px;
  max-width: 74ch;
  font-size: 12.5px;
  line-height: 1.75;
  color: var(--g-dim);
}
.gform {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px 12px;
  align-items: start;
}
.gform--4 {
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
}
.gform--3 {
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  margin-top: 10px;
}
.gform--2 {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  margin-top: 10px;
}
.greadout {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--g-line);
}
.gbtn--mini {
  padding: 5px 10px;
  font-size: 10.5px;
}
.gsec--aff {
  border-bottom: 0;
}
.gaffbox {
  display: grid;
  grid-template-columns: 88px minmax(0, 1fr) auto;
  align-items: center;
  gap: 16px;
  padding: 14px;
  border: 1px solid var(--g-line);
  background: var(--g-panel-2);
  position: relative;
}
.gaffmedia {
  width: 88px;
  height: 88px;
  border: 1px solid var(--g-line);
  background: var(--g-panel);
  display: grid;
  place-items: center;
  overflow: hidden;
}
.gaffmedia img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 8px;
  filter: grayscale(0.35) contrast(1.05);
  transition: filter 0.25s ease, transform 0.25s ease;
}
.gaffbox:hover .gaffmedia img {
  filter: grayscale(0) contrast(1.05);
  transform: scale(1.04);
}
@media (max-width: 720px) {
  .gaffbox {
    grid-template-columns: 64px minmax(0, 1fr);
  }
  .gaffmedia {
    width: 64px;
    height: 64px;
  }
  .gaffico {
    grid-column: 1 / -1;
    justify-content: center;
  }
}
.gaffbox::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  width: 9px;
  height: 9px;
  border: 1px solid var(--g-accent);
  border-width: 1px 0 0 1px;
}
.gafftext {
  max-width: 62ch;
}
.gafftitle {
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--g-ink);
  margin-bottom: 4px;
}
.gaffbox .gdesc {
  margin: 0;
}
.gaffico {
  text-decoration: none;
  white-space: nowrap;
}
.gfoot--sticky {
  position: sticky;
  bottom: 0;
  background: var(--g-panel);
  border-top: 1px solid var(--g-line);
  padding: 12px 16px;
}
.gfoot-note {
  margin-left: auto;
}
</style>
