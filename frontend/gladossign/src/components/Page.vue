<template>
  <div class="plugin-page">
    <v-card flat class="mb-3">
      <v-card-title class="d-flex align-center py-2">
        <v-icon icon="mdi-shield-check" color="primary" class="mr-2" />
        <span class="text-subtitle-1 font-weight-medium">GlaDOS 签到</span>
        <v-spacer />
        <v-btn
          icon="mdi-refresh"
          size="small"
          variant="text"
          :loading="loading"
          @click="loadAll"
        />
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

        <v-skeleton-loader v-if="loading && !loaded" type="article" />

        <template v-else>
          <v-row dense>
            <v-col cols="12" sm="6" md="3">
              <v-card variant="tonal" color="surface" class="pa-3 h-100">
                <div class="text-caption text-medium-emphasis">登录状态</div>
                <div class="d-flex align-center mt-1">
                  <v-icon
                    :icon="state.session.logged_in ? 'mdi-account-check' : 'mdi-account-off'"
                    :color="state.session.logged_in ? 'success' : 'warning'"
                    size="18"
                    class="mr-1"
                  />
                  <span class="text-body-2 font-weight-medium">
                    {{ state.session.logged_in ? '已登录' : '未登录' }}
                  </span>
                </div>
                <div class="text-caption text-medium-emphasis mt-1 text-truncate">
                  {{ state.session.email || '—' }}
                </div>
              </v-card>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-card variant="tonal" color="surface" class="pa-3 h-100">
                <div class="text-caption text-medium-emphasis">剩余天数</div>
                <div class="text-h6 font-weight-medium mt-1">
                  {{ state.summary.leftDays ?? '—' }}
                </div>
                <div class="text-caption text-medium-emphasis mt-1">
                  已用 {{ state.summary.days ?? '—' }} 天
                </div>
              </v-card>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-card variant="tonal" color="surface" class="pa-3 h-100">
                <div class="text-caption text-medium-emphasis">当前点数</div>
                <div class="text-h6 font-weight-medium mt-1">
                  {{ state.summary.points ?? '—' }}
                </div>
                <div class="text-caption text-medium-emphasis mt-1">
                  {{ state.session.login_at ? '登录于 ' + state.session.login_at : '—' }}
                </div>
              </v-card>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-card variant="tonal" color="surface" class="pa-3 h-100">
                <div class="text-caption text-medium-emphasis">设备身份（固定）</div>
                <div class="text-body-2 font-weight-medium mt-1">
                  {{ state.device.platform || '—' }} · {{ state.device.screen || '—' }}
                </div>
                <div class="text-caption text-medium-emphasis mt-1 text-truncate">
                  {{ state.device.fingerprint || '—' }}
                </div>
              </v-card>
            </v-col>
          </v-row>

          <div class="d-flex align-center mt-4 flex-wrap ga-2">
            <v-btn
              color="primary"
              prepend-icon="mdi-calendar-check"
              :loading="checkinLoading"
              :disabled="!state.session.logged_in"
              @click="checkin"
            >
              立即签到
            </v-btn>
            <v-btn
              variant="tonal"
              prepend-icon="mdi-cog"
              @click="$emit('switch')"
            >
              配置 / 登录
            </v-btn>
            <span v-if="state.last_checkin" class="text-caption text-medium-emphasis ml-2">
              最近一次：{{ state.last_checkin.date }} · {{ state.last_checkin.status }}
            </span>
          </div>

          <v-alert
            v-if="!state.session.logged_in"
            type="info"
            variant="tonal"
            density="compact"
            class="mt-4"
          >
            尚未登录。点「配置 / 登录」填写邮箱并获取验证码，登录在 MoviePilot 服务器端完成，之后即可自动签到。
          </v-alert>

          <v-card v-if="history.length" variant="outlined" class="mt-4">
            <v-card-title class="text-subtitle-2 py-2">最近记录</v-card-title>
            <v-table density="compact" hover>
              <thead>
                <tr>
                  <th class="text-caption">时间</th>
                  <th class="text-caption">状态</th>
                  <th class="text-caption">点数</th>
                  <th class="text-caption">说明</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in history" :key="index">
                  <td class="text-caption">{{ row.date }}</td>
                  <td>
                    <v-chip size="x-small" variant="tonal">{{ row.status }}</v-chip>
                  </td>
                  <td class="text-caption">{{ row.points_gain }}</td>
                  <td class="text-caption text-medium-emphasis">{{ row.message }}</td>
                </tr>
              </tbody>
            </v-table>
          </v-card>
        </template>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'

const props = defineProps({
  api: { type: Object, default: null },
  pluginId: { type: String, default: 'gladossign' },
  sourcePluginId: { type: String, default: '' },
  nativeSubscribe: { type: Function, default: null },
})
const emit = defineEmits(['switch', 'action', 'close'])

const pluginId = computed(() => props.pluginId || 'gladossign')
const PLUGIN_ID = pluginId  // 兼容原有调用写法
const loading = ref(false)
const loaded = ref(false)
const checkinLoading = ref(false)
const error = ref('')
const message = ref('')
const messageType = ref('success')
const history = ref([])

const state = reactive({
  session: { logged_in: false, email: '', login_at: '', cookie_items: 0 },
  summary: { email: '', user_id: null, days: null, leftDays: null, points: null },
  device: { platform: '', screen: '', ua: '', fingerprint: '' },
  last_checkin: null,
})

function showMessage(text, type = 'success') {
  message.value = text
  messageType.value = type
}

async function loadState() {
  if (!props.api) return
  const data = await props.api.get(`plugin/${pluginId.value}/state`)
  if (!data) return
  Object.assign(state.session, data.session || {})
  Object.assign(state.summary, data.summary || {})
  Object.assign(state.device, data.device || {})
  state.last_checkin = data.last_checkin || null
}

async function loadHistory() {
  if (!props.api) return
  const rows = await props.api.get(`plugin/${pluginId.value}/history`)
  history.value = Array.isArray(rows) ? rows.slice(0, 8) : []
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
    emit('action')
  } catch (err) {
    error.value = `加载状态失败：${err}`
  } finally {
    loading.value = false
  }
}

async function checkin() {
  if (!props.api) return
  checkinLoading.value = true
  error.value = ''
  try {
    const result = await props.api.post(`plugin/${pluginId.value}/checkin`, {})
    if (result && result.code === 0) {
      showMessage(result.msg || '签到成功')
    } else {
      showMessage((result && (result.msg || result.status)) || '签到失败', 'error')
    }
    await loadAll()
  } catch (err) {
    error.value = `签到失败：${err}`
  } finally {
    checkinLoading.value = false
  }
}

watch(() => props.api, (value) => {
  if (value) loadAll()
})

onMounted(loadAll)
</script>

<style scoped>
.plugin-page {
  padding: 4px;
}
.h-100 {
  height: 100%;
}
</style>
