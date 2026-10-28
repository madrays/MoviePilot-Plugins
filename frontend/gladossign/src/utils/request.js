/**
 * 宿主 api 可能因后端阻塞迟迟不返回（反代会先回 504），
 * 这里统一加超时兜底，保证按钮不会无限转圈。
 */
export function withTimeout(promise, ms, label) {
  let timer = null
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => {
      reject(new Error(`${label}超时（${Math.round(ms / 1000)} 秒无响应）`))
    }, ms)
  })
  return Promise.race([promise, timeout]).finally(() => {
    if (timer) clearTimeout(timer)
  })
}

/** 把网关/网络错误转成更可读的提示。 */
export function friendlyError(error) {
  const text = String((error && (error.message || error)) || error || '')
  if (text.includes('504')) {
    return '网关超时（504）：MoviePilot 等待后端超时，请稍后重试并查看插件日志'
  }
  if (text.includes('502') || text.includes('503')) {
    return `服务暂不可用（${text.match(/50[23]/)?.[0] || '5xx'}）：请稍后重试`
  }
  return text || '请求失败'
}
