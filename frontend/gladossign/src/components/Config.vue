<template>
  <div class="plugin-config">
    <v-card flat class="mb-3">
      <v-card-title class="d-flex align-center py-2">
        <v-icon icon="mdi-cog" color="primary" class="mr-2" />
        <span class="text-subtitle-1 font-weight-medium">GlaDOS 签到设置</span>
        <v-spacer />
        <v-btn
          variant="text"
          size="small"
          prepend-icon="mdi-arrow-left"
          @click="$emit('switch')"
        >
          返回
        </v-btn>
      </v-card-title>

      <v-card-text class="pt-0">
        <v-alert
          v-if="error"
          type="error"
          density="compact"
          variant="tonal"
          class="mb-3"
          closable
          @click:close="error = ''"
        >
          {{ error }}
        </v-alert>
        <v-alert
          v-if="message"
          :type="messageType"
          density="compact"
          variant="tonal"
          class="mb-3"
          closable
          @click:close="message = ''"
        >
          {{ message }}
        </v-alert>

        <!-- 账号登录 -->
        <v-card variant="outlined" class="mb-3">
          <v-card-title class="text-subtitle-2 py-2">
            <v-icon icon="mdi-email-lock" size="small" class="mr-1" />
            账号登录（服务器端完成）
          </v-card-title>
          <v-card-text>
            <v-alert
              type="info"
              variant="tonal"
              density="compact"
              class="mb-3 text-caption"
            >
              登录由 MoviePilot 服务器直接完成，设备身份每套安装独立生成，无需从浏览器复制 Cookie。
              登录状态会持久化保存：MoviePilot 重启后仍然有效，无需重复登录；仅当 GlaDOS 主动失效会话时才需重新登录。
            </v-alert>

            <v-row dense>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="email"
                  label="GlaDOS 登录邮箱"
                  placeholder="you@example.com"
                  prepend-inner-icon="mdi-email"
                  density="compact"
                  variant="outlined"
                  autocomplete="off"
                  hide-details="auto"
                  :disabled="session.logged_in"
                />
              </v-col>
              <v-col cols="12" md="6" class="d-flex align-center">
                <v-btn
                  variant="tonal"
                  color="primary"
                  prepend-icon="mdi-send"
                  :loading="sending"
                  :disabled="!email || session.logged_in || sending || cooldown > 0"
                  @click="sendCode"
                >
                  {{ cooldown > 0 ? `重新发送（${cooldown}s）` : '发送验证码' }}
                </v-btn>
              </v-col>
            </v-row>

            <v-row dense class="mt-1">
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="code"
                  label="邮箱收到的验证码"
                  placeholder="6 位验证码"
                  prepend-inner-icon="mdi-key"
                  density="compact"
                  variant="outlined"
                  autocomplete="one-time-code"
                  hide-details="auto"
                  :disabled="session.logged_in"
                  @keyup.enter="login"
                />
              </v-col>
              <v-col cols="12" md="6" class="d-flex align-center ga-2">
                <v-btn
                  color="primary"
                  prepend-icon="mdi-login"
                  :loading="loggingIn"
                  :disabled="!email || !code || session.logged_in || loggingIn"
                  @click="login"
                >
                  登录
                </v-btn>
                <v-btn
                  v-if="session.logged_in"
                  variant="text"
                  color="error"
                  prepend-icon="mdi-logout"
                  @click="logout"
                >
                  退出登录
                </v-btn>
              </v-col>
            </v-row>

            <v-divider class="my-3" />

            <div class="d-flex align-center flex-wrap ga-3 text-caption">
              <v-chip
                :color="session.logged_in ? 'success' : 'warning'"
                size="small"
                variant="tonal"
              >
                {{ session.logged_in ? '已登录' : '未登录' }}
              </v-chip>
              <span v-if="session.email" class="text-medium-emphasis">
                {{ session.email }}
              </span>
              <span v-if="session.login_at" class="text-medium-emphasis">
                登录于 {{ session.login_at }}
              </span>
              <span v-if="session.cookie_items" class="text-medium-emphasis">
                Cookie 项 {{ session.cookie_items }}
              </span>
              <span class="text-medium-emphasis">
                设备：{{ device.platform }} · {{ device.screen }}
              </span>
            </div>
          </v-card-text>
        </v-card>

        <!-- 基础设置 -->
        <v-card variant="outlined" class="mb-3">
          <v-card-title class="text-subtitle-2 py-2">
            <v-icon icon="mdi-tune" size="small" class="mr-1" />
            基础设置
          </v-card-title>
          <v-card-text>
            <v-row dense>
              <v-col cols="12" sm="6" md="3">
                <v-switch
                  v-model="config.enabled"
                  label="启用插件"
                  color="success"
                  density="compact"
                  hide-details
                />
              </v-col>
              <v-col cols="12" sm="6" md="3">
                <v-switch
                  v-model="config.notify"
                  label="发送通知"
                  color="success"
                  density="compact"
                  hide-details
                />
              </v-col>
              <v-col cols="12" sm="6" md="3">
                <v-switch
                  v-model="config.proxy_enabled"
                  label="使用全局代理"
                  color="success"
                  density="compact"
                  hide-details
                />
              </v-col>
              <v-col cols="12" sm="6" md="3">
                <v-text-field
                  v-model.number="config.history_days"
                  label="历史保留天数"
                  type="number"
                  density="compact"
                  variant="outlined"
                  hide-details
                />
              </v-col>
            </v-row>

            <v-row dense class="mt-2">
              <v-col cols="12" md="4">
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
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="config.auto_exchange"
                  label="自动兑换套餐"
                  :items="exchangePlans"
                  clearable
                  density="compact"
                  variant="outlined"
                  hide-details="auto"
                  hint="积分达到门槛后每日最多兑换一次"
                  persistent-hint
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="config.device_platform"
                  label="设备平台"
                  :items="platformItems"
                  density="compact"
                  variant="outlined"
                  hide-details="auto"
                  hint="每套安装独立随机生成；修改后需重新登录"
                  persistent-hint
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="config.base_url"
                  label="Base URL"
                  placeholder="https://glados.cloud"
                  density="compact"
                  variant="outlined"
                  hide-details="auto"
                  hint="默认 glados.cloud；账号在 glados.space 则改成对应域名"
                  persistent-hint
                />
              </v-col>
            </v-row>

            <v-row dense class="mt-2">
              <v-col cols="12" sm="6" md="3">
                <v-text-field
                  v-model.number="config.timeout_seconds"
                  label="超时（秒）"
                  type="number"
                  density="compact"
                  variant="outlined"
                  hide-details
                />
              </v-col>
              <v-col cols="12" sm="6" md="3">
                <v-text-field
                  v-model.number="config.max_attempts"
                  label="重试次数"
                  type="number"
                  density="compact"
                  variant="outlined"
                  hide-details
                />
              </v-col>
              <v-col cols="12" sm="6" md="3">
                <v-text-field
                  v-model.number="config.retry_interval_seconds"
                  label="重试间隔（秒）"
                  type="number"
                  density="compact"
                  variant="outlined"
                  hide-details
                />
              </v-col>
              <v-col cols="12" sm="6" md="3" class="d-flex align-center">
                <v-switch
                  v-model="config.retry_no_proxy_fallback"
                  label="失败后直连重试"
                  color="success"
                  density="compact"
                  hide-details
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <div class="d-flex align-center ga-2">
          <v-btn
            color="primary"
            prepend-icon="mdi-content-save"
            :loading="saving"
            @click="save"
          >
            保存设置
          </v-btn>
          <v-btn
            variant="tonal"
            prepend-icon="mdi-play"
            :loading="saving"
            @click="save(true)"
          >
            保存并立即运行
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { friendlyError, withTimeout } from '../utils/request'

const props = defineProps({
  api: { type: Object, default: null },
  initialConfig: { type: Object, default: () => ({}) },
  pluginId: { type: String, default: 'gladossign' },
  sourcePluginId: { type: String, default: '' },
  nativeSubscribe: { type: Function, default: null },
})
const emit = defineEmits(['save', 'switch', 'close'])

const pluginId = computed(() => props.pluginId || 'gladossign')
const error = ref('')
const message = ref('')
const messageType = ref('success')
const sending = ref(false)
const loggingIn = ref(false)
const saving = ref(false)
const cooldown = ref(0)
let cooldownTimer = null

const email = ref('')
const code = ref('')
const session = reactive({ logged_in: false, email: '', login_at: '', cookie_items: 0 })
const device = reactive({ platform: '', screen: '', ua: '', fingerprint: '' })
const platformItems = [
  { title: '自动（跟随 MP 宿主机）', value: 'auto' },
  { title: 'Windows', value: 'windows' },
  { title: 'macOS', value: 'macos' },
  { title: 'Linux', value: 'linux' },
]

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
  retry_interval_seconds: 300,
  history_days: 30,
  device_platform: 'auto',
})

// 宿主会传入 initialConfig，先落地为本地配置
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

function showMessage(text, type = 'success') {
  message.value = text
  messageType.value = type
}

async function loadState() {
  if (!props.api) return
  const data = await props.api.get(`plugin/${pluginId.value}/state`)
  if (!data) return
  if (data.config) {
    Object.assign(config, data.config)
    email.value = data.config.email || ''
  }
  Object.assign(session, data.session || {})
  Object.assign(device, data.device || {})
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
    error.value = `退出失败：${err}`
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
.plugin-config {
  padding: 4px;
}
</style>
