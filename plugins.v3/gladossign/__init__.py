import json
import time
from datetime import datetime, timedelta
from typing import Any, List, Dict, Tuple, Optional

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

try:
    from app.sdk.config import settings
except ImportError:
    from app.core.config import settings
from app.plugins import _PluginBase
try:
    from app.sdk.logging import logger
except ImportError:
    from app.log import logger
from app.schemas import NotificationType
import requests


class gladossign(_PluginBase):
    plugin_name = "GlaDOS 签到"
    plugin_desc = "每日签到获取点数；积累点数可兑换 10~100 天套餐时长"
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/glados.png"
    plugin_version = "3.6.0"
    plugin_author = "madrays"
    author_url = "https://github.com/madrays"
    plugin_config_prefix = "gladossign_"
    plugin_order = 1
    auth_level = 2

    _enabled = False
    _notify = True
    _onlyonce = False
    _cron = "0 9 * * *"
    _base_url = "https://glados.cloud"
    _cookie = ""
    _auth_bundle = ""
    _bundle_meta: Dict[str, Any] = {}
    _device_id = ""
    _auto_exchange = ""
    _proxy_enabled = False
    _timeout_seconds = 30
    _retry_interval_seconds = 300
    _max_attempts = 2
    _retry_no_proxy_fallback = True
    _history_days = 30
    _scheduler: Optional[BackgroundScheduler] = None

    _DEFAULT_UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36')

    # 兑换接口的 planType 是字符串枚举（见控制台前端：plan100 / plan200 / plan500）
    _EXCHANGE_PLANS = {
        "10": {"points": 100, "label": "10天套餐", "plan_type": "plan100"},
        "30": {"points": 200, "label": "30天套餐", "plan_type": "plan200"},
        "100": {"points": 500, "label": "100天套餐", "plan_type": "plan500"},
    }

    # 一次性提取代码（与控制台 app.bundle.js 模块 811/833/540/55 逐行等价，已在真实浏览器
    # 里与站点原始实现对照通过）。执行后自动算出设备指纹、识别登录域名、生成凭证 JSON，
    # 并在页面底部弹出中性风格的分步指引面板（含 Cookie 手动复制指引与兜底复制按钮）。
    _DEVICE_ID_HELPER = (
        "(async()=>{ function H(a,b=0){let n=3735928559^b,r=1103547991^b;for(let i=0,t;i<a.length;i++){t=a.charCodeAt(i);n=Math.imul(n^t,2654435761);r=Math.imul(r^t,1597334677)}n=Math.imul(n^n>>>16,2246822507)^Math.imul(r^r>>>13,3266489909);r=Math.imul(r^r>>>16,2246822507)^Math.imul(n^n>>>13,3266489909);return 4294967296*(2097151&r)+(n>>>0)+\"\"} function cyrb53(a,b=0){return H(a.slice(0,a.length/2|0),b)+\"\"+H(a.slice(a.length/2|0),b)} function cf(){try{const c=document.createElement(\"canvas\"),x=c.getContext(\"2d\"),t=\"abz190#$%^@\\u00a3\\u00e9\\u00faGLaDOS!6.5[-%-&*]@345876 <canvas>\";x.textBaseline=\"top\";x.font=\"32px 'Arial'\";x.textBaseline=\"alphabetic\";x.fillStyle=\"#f1680e\";x.fillRect(125,1,62,20);x.fillStyle=\"#0c6d9e\";x.fillText(t,2,15);x.fillStyle=\"rgba(102, 204, 0, 0.7)\";x.fillText(t,4,17);x.fillStyle=\"rgba(12, 24, 10, 0.2)\";x.fillText(t,10,107);x.rotate(.03);x.fillText(t,4,17);x.fillStyle=\"rgb(155,255,5)\";x.shadowBlur=8;x.shadowColor=\"red\";x.fillRect(20,12,100,5);return c.toDataURL()}catch(e){return screen.height+\"x\"+screen.width}} function af(){return new Promise((ok,no)=>{try{const O=window.OfflineAudioContext||window.webkitOfflineAudioContext,ctx=new O(1,44100,44100),t=ctx.currentTime,osc=ctx.createOscillator(),comp=ctx.createDynamicsCompressor();osc.type=\"triangle\";osc.frequency.setValueAtTime(1e4,t);const set=(k,v)=>{try{if(comp[k]&&typeof comp[k].setValueAtTime===\"function\")comp[k].setValueAtTime(v,t)}catch(e){}};set(\"threshold\",-50);set(\"knee\",40);set(\"ratio\",12);set(\"reduction\",-20);set(\"attack\",0);set(\"release\",.25);osc.connect(comp);comp.connect(ctx.destination);osc.start(0);ctx.startRendering();ctx.oncomplete=ev=>{let s=0;for(let i=4500;i<5e3;i++)s+=Math.abs(ev.renderedBuffer.getChannelData(0)[i]);ok(s.toString())}}catch(e){no(e)}})} let ab=\"\";try{ab=btoa(await af())}catch(e){} const device=cyrb53(ab+cf())+\"-\"+window.screen.height+\"-\"+window.screen.width; const cookie=document.cookie||\"\"; const host=location.host; const bundle=JSON.stringify({v:1,cookie:cookie,device:device,domain:host,screen:window.screen.width+\"x\"+window.screen.height,ua:navigator.userAgent,at:new Date().toISOString()}); const copyText=(text)=>{let done=false;try{const ta=document.createElement(\"textarea\");ta.value=text;ta.setAttribute(\"readonly\",\"\");ta.style.cssText=\"position:fixed;top:0;left:-9999px;opacity:0\";document.body.appendChild(ta);ta.select();ta.setSelectionRange(0,text.length);done=document.execCommand(\"copy\");document.body.removeChild(ta)}catch(e){}if(!done){try{navigator.clipboard.writeText(text);done=true}catch(e){}}return done}; const copied=copyText(bundle); const esc=(s)=>String(s).replace(/&/g,\"&amp;\").replace(/</g,\"&lt;\"); const old=document.getElementById(\"__glados_fp__\");if(old)old.remove(); const w=document.createElement(\"div\");w.id=\"__glados_fp__\"; w.style.cssText=\"position:fixed;z-index:2147483647;left:16px;right:16px;bottom:16px;max-width:760px;margin:0 auto;box-sizing:border-box;background:#151719;color:#e6e8eb;border:1px solid #2b2f33;border-radius:10px;box-shadow:0 12px 32px rgba(0,0,0,.45);font:14px/1.6 -apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;max-height:78vh;overflow:auto\"; const sec=\"padding:14px 18px;border-top:1px solid #24282c\"; const lbl=\"font-size:12px;letter-spacing:.4px;color:#8b9299;margin:0 0 4px\"; const mono=\"font:12.5px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace\"; w.innerHTML= \"<div style='display:flex;align-items:center;gap:10px;padding:14px 18px'>\" +\"<span style='width:7px;height:7px;border-radius:50%;background:\"+(copied?\"#4ea1ff\":\"#d9a441\")+\";flex:none'></span>\" +\"<span style='font-weight:600;font-size:15px'>\"+(copied?\"凭证已生成，已尝试复制\":\"凭证已生成，请点下方按钮复制\")+\"</span>\" +\"<span style='margin-left:auto;color:#8b9299;font-size:12.5px'>\"+esc(host)+\"</span>\" +\"</div>\" +\"<div style='\"+sec+\"'>\" +\"<div style='\"+lbl+\"'>设备指纹</div>\" +\"<div style='\"+mono+\";color:#9ecbff;word-break:break-all'>\"+esc(device)+\"</div>\" +\"<div style='\"+lbl+\";margin-top:10px'>自动读到的 Cookie</div>\" +\"<div style='\"+mono+\";color:\"+(cookie?\"#e6e8eb\":\"#d9a441\")+\"'>\"+(cookie?esc(cookie):\"（空 —— 站点使用 HttpOnly Cookie，脚本无法读取）\")+\"</div>\" +\"</div>\" +\"<div style='\"+sec+\"'>\" +\"<div style='font-weight:600;margin:0 0 8px'>还需要你手动做一次：复制 Cookie</div>\" +\"<ol style='margin:0;padding-left:20px;color:#c3c8cd'>\" +\"<li style='margin:3px 0'>F12 → <b style='color:#e6e8eb'>Application</b> → 左侧 <b style='color:#e6e8eb'>Cookies</b> → <b style='color:#e6e8eb'>\"+esc(host)+\"</b></li>\" +\"<li style='margin:3px 0'>双击 <b style='color:#e6e8eb'>koa:sess</b> 和 <b style='color:#e6e8eb'>koa:sess.sig</b> 的 Value 复制</li>\" +\"<li style='margin:3px 0'>拼成一行：<span style='\"+mono+\";color:#9ecbff'>koa:sess=&lt;值&gt;; koa:sess.sig=&lt;值&gt;</span></li>\" +\"</ol>\" +\"</div>\" +\"<div style='\"+sec+\"'>\" +\"<div style='font-weight:600;margin:0 0 8px'>填进 MoviePilot 插件</div>\" +\"<div style='color:#c3c8cd'>① <b style='color:#e6e8eb'>一次性凭证</b> → 粘贴下方 JSON（设备指纹与域名自动识别）</div>\" +\"<div style='color:#c3c8cd;margin-top:2px'>② <b style='color:#e6e8eb'>完整 Cookie</b> → 粘贴上面那行 Cookie</div>\" +\"<div style='color:#c3c8cd;margin-top:2px'>保存 → 点「立即运行一次」</div>\" +\"</div>\" +\"<div style='\"+sec+\"'>\" +\"<div style='\"+mono+\";color:#8b9299;word-break:break-all;max-height:72px;overflow:auto;background:#101214;border:1px solid #24282c;border-radius:6px;padding:9px 11px;user-select:all'>\"+esc(bundle)+\"</div>\" +\"<div style='display:flex;gap:8px;align-items:center;margin-top:12px'>\" +\"<button id='__glados_copy' style='font:600 13.5px/1 -apple-system,\\\\'PingFang SC\\\\',sans-serif;padding:9px 16px;border-radius:6px;border:1px solid #3a6ea5;background:#2f6fb3;color:#fff;cursor:pointer'>复制凭证 JSON</button>\" +\"<button id='__glados_close' style='font:600 13.5px/1 -apple-system,\\\\'PingFang SC\\\\',sans-serif;padding:9px 16px;border-radius:6px;border:1px solid #33383d;background:#1d2023;color:#c3c8cd;cursor:pointer'>关闭</button>\" +\"<span id='__glados_ok' style='font-size:12.5px;color:#6fb3f2'></span>\" +\"</div>\" +\"</div>\"; document.body.appendChild(w); const ok=w.querySelector(\"#__glados_ok\"); w.querySelector(\"#__glados_copy\").onclick=()=>{ok.textContent=copyText(bundle)?\"已复制\":\"复制失败，请手动选中上方文本\";}; w.querySelector(\"#__glados_close\").onclick=()=>w.remove(); console.log(\"凭证 JSON:\",bundle); return bundle})()"
    )

    def _device_helper_button(self) -> Dict[str, Any]:
        """生成「复制指纹提取代码」按钮，代码内嵌在 onclick 中，无需额外存储配置。"""
        snippet = json.dumps(self._DEVICE_ID_HELPER)
        onclick = (
            "(function(b){"
            "const code=" + snippet + ";"
            "const flash=(t)=>{const o=b.textContent;b.textContent=t;setTimeout(()=>{b.textContent=o},1500)};"
            "const run=()=>navigator.clipboard.writeText(code).then(()=>flash('已复制提取代码'))"
            ".catch(()=>{const a=document.createElement('textarea');a.value=code;"
            "a.style.position='fixed';a.style.left='-9999px';document.body.appendChild(a);a.select();"
            "try{document.execCommand('copy')?flash('已复制提取代码'):alert('复制失败，请手动复制');}"
            "catch(e){alert('复制失败，请手动复制')}document.body.removeChild(a)});"
            "run()})(this)"
        )
        return {
            'component': 'VBtn',
            'props': {
                'color': 'primary',
                'variant': 'tonal',
                'size': 'small',
                'class': 'mt-1',
                'onclick': onclick,
            },
            'text': '📋 复制「设备指纹」提取代码',
        }

    def init_plugin(self, config: dict = None):
        self.stop_service()
        if config:
            self._enabled = config.get("enabled", False)
            self._notify = config.get("notify", True)
            self._onlyonce = config.get("onlyonce", False)
            self._cron = config.get("cron", "0 9 * * *")
            
            # 优化 base_url 获取逻辑，防止被默认值误覆盖
            cfg_url = config.get("base_url")
            if cfg_url:
                self._base_url = str(cfg_url).strip()
            else:
                self._base_url = "https://glados.cloud"
            logger.info(f"加载配置: Base URL={self._base_url}")
            
            self._auth_bundle = config.get("auth_bundle") or ""
            self._cookie = (config.get("cookie") or "").strip()
            self._device_id = (config.get("device_id") or "").strip()
            # 一次性凭证优先：自动从中解析 Cookie 与设备指纹
            bundle = self._parse_auth_bundle(self._auth_bundle)
            if bundle:
                if bundle.get("cookie"):
                    self._cookie = bundle["cookie"]
                if bundle.get("device"):
                    self._device_id = bundle["device"]
                # 域名自动识别：凭证里的 domain 是浏览器实际登录域，优先级高于配置项，
                # 且签到 token 由该域名推导，必须一致，否则会跨域导致 Cookie 失效。
                bundle_domain = str(bundle.get("domain") or "").strip()
                if bundle_domain:
                    if bundle_domain != self._base_url.replace("https://", "").replace("http://", "").split("/")[0]:
                        logger.info(f"域名自动识别为 {bundle_domain}（凭证来源），已覆盖配置值 {self._base_url}")
                    self._base_url = "https://" + bundle_domain
                self._bundle_meta = {k: bundle.get(k) for k in ("domain", "screen", "ua", "at") if bundle.get(k)}
                cookie_items = len([x for x in self._cookie.split(";") if x.strip()]) if self._cookie else 0
                logger.info(
                    f"已解析一次性凭证: 域名={self._base_url}, Cookie项={cookie_items}, "
                    f"设备指纹={'有' if self._device_id else '无'}, 来源屏幕={bundle.get('screen') or '未知'}"
                )
                if not self._cookie:
                    logger.warning("凭证里没有 Cookie（站点 Cookie 为 HttpOnly，脚本读不到），请在「② 完整 Cookie」栏手动填写：F12 → Application → Cookies → 登录域名 → koa:sess 与 koa:sess.sig")
            else:
                self._bundle_meta = {}
                if self._auth_bundle.strip():
                    logger.warning("一次性凭证解析失败，已回退到手动填写的 Cookie / 设备指纹")
            self._auto_exchange = str(config.get("auto_exchange") or "").strip()
            if self._auto_exchange not in self._EXCHANGE_PLANS:
                self._auto_exchange = ""
            self._proxy_enabled = bool(config.get("proxy_enabled", False))
            try:
                self._timeout_seconds = int(config.get("timeout_seconds", 30))
            except Exception:
                self._timeout_seconds = 30
            try:
                self._max_attempts = int(config.get("max_attempts", 2))
            except Exception:
                self._max_attempts = 2
            self._retry_no_proxy_fallback = bool(config.get("retry_no_proxy_fallback", True))
            try:
                self._retry_interval_seconds = int(config.get("retry_interval_seconds", 2))
            except Exception:
                self._retry_interval_seconds = 2
            try:
                self._history_days = int(config.get("history_days", 30))
            except Exception:
                self._history_days = 30
        if self._onlyonce:
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            self._scheduler.add_job(func=self.sign, trigger='date', run_date=datetime.now() + timedelta(seconds=3), name="GlaDOS签到")
            self._onlyonce = False
            self.update_config({
                "enabled": self._enabled,
                "notify": self._notify,
                "cookie": self._cookie,
                "device_id": self._device_id,
                "auth_bundle": self._auth_bundle,
                "auto_exchange": self._auto_exchange,
                "cron": self._cron,
                "onlyonce": False,
                "base_url": self._base_url,
                "proxy_enabled": self._proxy_enabled,
                "timeout_seconds": self._timeout_seconds,
                "max_attempts": self._max_attempts,
                "retry_no_proxy_fallback": self._retry_no_proxy_fallback,
                "retry_interval_seconds": self._retry_interval_seconds,
                "history_days": self._history_days,
            })
            if self._scheduler.get_jobs():
                self._scheduler.start()
        if self._enabled and self._cron:
            logger.info(f"注册定时服务: {self._cron}")

    def sign(self):
        logger.info("开始 GlaDOS 签到")
        url = f"{self._base_url.rstrip('/')}/api/user/checkin"
        logger.info(f"请求地址: {url}")
        headers = self._build_headers()
        proxies = self._get_proxies()
        logger.info(f"使用代理: {'是' if (proxies is not None) else '否'}")
        logger.info(f"Cookie: {'有' if bool(self._cookie) else '无'}")
        logger.info(f"设备指纹: {'已配置' if bool(self._device_id) else '未配置(控制台将返回 device-mismatch)'}")
        # 提取域名作为 token (例如 glados.cloud 或 glados.one)
        domain = self._base_url.replace('https://', '').replace('http://', '').split('/')[0]
        body = {"token": domain}
        attempts = [None]
        if proxies:
            attempts = [proxies] + ([None] if self._retry_no_proxy_fallback else [])
        last_error = None
        for idx, px in enumerate(attempts):
            for attempt in range(1, int(self._max_attempts) + 1):
                try:
                    start_ms = int(time.time()*1000)
                    resp = requests.post(url, json=body, headers=headers, timeout=self._timeout_seconds, proxies=px)
                    cost_ms = int(time.time()*1000) - start_ms
                    text_len = len(resp.text or "")
                    ctype = resp.headers.get('Content-Type') or resp.headers.get('content-type')
                    logger.info(f"响应状态: {resp.status_code}, 耗时: {cost_ms}ms, 类型: {ctype}, 长度: {text_len}")
                    data = {}
                    try:
                        data = resp.json() or {}
                    except Exception:
                        data = {}
                    logger.info(f"解析结果: code={data.get('code')}, reason={data.get('reason')}, message={data.get('message')}")
                    raw_code = data.get('code')
                    code = int(raw_code) if raw_code is not None else -1
                    # 尝试从 root 获取 points，也可能在 list[0]
                    points_gain = int(data.get('points') or 0) 
                    msg_en = str(data.get('message') or '')
                    lst = data.get('list') or []
                    item = lst[0] if lst else {}
                    # 如果 root 没 point，尝试从 item 获取 (部分 API 变种)
                    if points_gain == 0 and item.get('points'):
                         try: points_gain = int(item.get('points'))
                         except: pass

                    uid = item.get('user_id')
                    balance = item.get('balance')
                    now_ms = int(time.time()*1000)
                    t_ms_server = int(item.get('time') or now_ms)
                    t_ms = now_ms if code == 1 else t_ms_server
                    dt = datetime.fromtimestamp(t_ms/1000.0)
                    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    status = '签到成功' if (points_gain > 0) else ('已签到' if (code == 1 or ('Repeats' in msg_en) or ('Try Tomorrow' in msg_en)) else '签到失败')
                    msg_cn = (f"签到成功！获得 {points_gain} 点数" if status == '签到成功' else ("重复签到！请明天再试" if status == '已签到' else (msg_en or '签到失败')))

                    if code == 4 and data.get('reason') == 'device-mismatch':
                        status = '签到失败'
                        msg_cn = self._describe_device_mismatch(data)
                        logger.warning(
                            f"设备校验未通过: loginDevice={data.get('loginDevice')}, "
                            f"currentDevice={data.get('currentDevice')}, 本插件指纹={self._device_id or '未配置'}"
                        )
                    
                    if status == '已签到':
                        logger.info(f"检测到重复签到 (Code={code}), API通常不返回余额/UID, 将通过 User/Points 接口获取")
                    else:
                        logger.info(f"业务摘要: 状态={status}, 本次点数={points_gain}, 余额={balance}, 用户ID={uid}")
                    
                    # 尝试拉取最新的 Points 接口数据作为权威数据
                    self._fetch_user_summary(headers, px)

                    exchange_result = ""
                    if status in ('签到成功', '已签到'):
                        exchange_result = self._try_auto_exchange(headers, px)
                        if exchange_result.startswith("自动兑换成功"):
                            # 兑换会改变点数与剩余天数，刷新后再组织通知。
                            self._fetch_user_summary(headers, px)
                    
                    # 重新读取数据用于通知
                    info_out = self.get_data('glados_user') or {}
                    last_point_info = self.get_data('glados_points_info') or {}
                    
                    # 优先使用 api/user/points 的数据
                    current_points = self._to_int(last_point_info.get('points')) 
                    if current_points is None:
                         current_points = self._to_int(balance)
                    
                    # 修正：如果是“已签到”状态，尝试从历史记录中查找今天的签到记录，以展示“今日已获点数”
                    try:
                        tz = pytz.timezone(settings.TZ)
                        today_ymd = datetime.now(tz).strftime('%Y-%m-%d')
                        history_list = self.get_data('glados_history') or []
                        # 查找 message 或 date 匹配今天的记录 (API detail: checkin:2026-01-20-...)
                        logger.info(f"正在匹配今日记录: {today_ymd}, 历史记录数: {len(history_list)}")
                        if history_list:
                            logger.info(f"第一条记录: {history_list[0]}")
                        
                        # 逻辑修正：由于 message 可能已被翻译为 "每日签到奖励"，不能仅依赖 message 中的日期
                        # 应该检查 date 字段 (YYYY-MM-DD HH:MM:SS) 是否包含今日日期
                        todays_rec = next((h for h in history_list if today_ymd in str(h.get('date','')) and ('checkin' in str(h.get('message','')).lower() or '签到' in str(h.get('message','')))), None)
                        
                        if todays_rec:
                            # 找到了今天的权威记录
                            real_gain = int(todays_rec.get('points_gain', 0))
                            if status == '已签到':
                                points_gain = real_gain
                                msg_cn = f"重复签到！今日已获 {points_gain} 点数"
                    except Exception as e:
                        logger.warning(f"匹配今日记录失败: {e}")

                    # 更新通知逻辑
                    if self._notify:
                        title = '✅ GlaDOS 签到成功' if status == '签到成功' else ('✅ 今日已签到' if status == '已签到' else '🔴 GlaDOS 签到失败')
                        emoji = '📈' if points_gain > 0 else ('➖' if points_gain == 0 else '📉')
                        
                        text_parts = [
                            f"📝 {msg_cn}",
                            f"🆔 用户ID：{uid}" if uid else "",
                            f"{emoji} 本次点数：{points_gain}",
                            f"💰 当前点数：{current_points}" if current_points is not None else "",
                            f"⏰ 时间：{dt_str}",
                            (f"📅 已用天数：{info_out.get('days')}" if info_out.get('days') is not None else ""),
                            (f"🕒 剩余天数：{info_out.get('leftDays')}" if info_out.get('leftDays') is not None else ""),
                            (f"📧 邮箱：{info_out.get('email')}" if info_out.get('email') else ""),
                            (f"🎁 {exchange_result}" if exchange_result else ""),
                        ]
                        self.post_message(mtype=NotificationType.SiteMessage, title=title, text="\n".join([x for x in text_parts if x]))
                    return {} # 历史记录统一由 _fetch_user_summary 处理
                except Exception as e:
                    last_error = e
                    logger.warning(f"请求失败(第{idx+1}组{'使用代理' if px else '不使用代理'}第{attempt}/{self._max_attempts}次): {e}")
                    if attempt < int(self._max_attempts):
                        try:
                            time.sleep(max(0, int(self._retry_interval_seconds)))
                        except Exception:
                            pass
                    continue
        d = {"date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "status": "签到失败", "message": f"请求异常: {last_error}"}
        self._save_history(d)
        if self._notify:
            self.post_message(mtype=NotificationType.SiteMessage, title="🔴 GlaDOS 签到失败", text=f"⏰ {d['date']}\n❌ {d['message']}")
        return d

    @staticmethod
    def _parse_auth_bundle(raw: Any) -> Dict[str, str]:
        """
        解析「一次性凭证」，兼容三种粘贴形式：
          1. 提取脚本产出的 JSON：{"v":1,"cookie":"...","device":"...","screen":"..."}
          2. 从浏览器复制的请求头片段：Cookie: xxx 与 Authorization: yyy
          3. 只有 Cookie 的裸串（此时设备指纹留空，由调用方回退到手动栏）
        解析失败返回空字典。
        """
        text = str(raw or "").strip()
        if not text:
            return {}
        # 形 1：JSON 凭证包
        if text.startswith("{"):
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    cookie = str(data.get("cookie") or "").strip()
                    device = str(data.get("device") or data.get("authorization") or "").strip()
                    if cookie or device:
                        return {
                            "cookie": cookie,
                            "device": device,
                            "domain": str(data.get("domain") or "").strip(),
                            "screen": str(data.get("screen") or "").strip(),
                            "ua": str(data.get("ua") or "").strip(),
                            "at": str(data.get("at") or "").strip(),
                        }
            except Exception as error:
                logger.warning(f"一次性凭证 JSON 解析失败: {error}")
        # 形 2：请求头片段
        cookie = ""
        device = ""
        for line in text.replace("\r", "\n").split("\n"):
            line = line.strip()
            lowered = line.lower()
            if lowered.startswith("cookie:"):
                cookie = line.split(":", 1)[1].strip()
            elif lowered.startswith("authorization:"):
                device = line.split(":", 1)[1].strip()
        if cookie or device:
            return {"cookie": cookie, "device": device}
        # 形 3：裸 Cookie（必须含有 = 且不含换行，避免把指纹误当 Cookie）
        if "=" in text and "\n" not in text and len(text) < 8000:
            return {"cookie": text, "device": ""}
        return {}

    def _build_headers(self) -> Dict[str, str]:
        """
        构造与 GlaDOS 控制台一致的请求头。

        控制台前端会给每个 /api 请求附带 ``Authorization: <设备指纹>``，
        值为 ``cyrb53(base64(音频指纹)+canvas指纹)-屏幕高-屏幕宽``。
        服务端会用它与登录时记录的设备指纹比对，不一致即返回
        ``{"code": 4, "reason": "device-mismatch"}``，因此 MoviePilot
        必须原样携带浏览器的指纹才能签到。
        """
        # 服务端会比对「登录设备」与「当前浏览器」的 UA 平台，必须沿用提取凭证时
        # 那台设备的 UA，否则非 macOS 登录的用户必被判 device-mismatch。
        headers = {
            'User-Agent': self._device_ua(),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/json;charset=UTF-8',
            'Sec-CH-UA-Platform': self._ua_platform(self._device_ua()),
            'Sec-CH-UA-Mobile': '?0',
            'Origin': self._base_url,
            'Referer': self._base_url.rstrip('/') + '/',
            'Cookie': self._cookie,
        }
        if self._device_id:
            headers['Authorization'] = self._device_id
        return headers

    def _device_ua(self) -> str:
        """优先使用一次性凭证里记录的 UA，缺失时回退默认。"""
        meta = self._bundle_meta if isinstance(self._bundle_meta, dict) else {}
        ua = str(meta.get("ua") or "").strip()
        return ua or self._DEFAULT_UA

    @staticmethod
    def _ua_platform(ua: str) -> str:
        """从 UA 推断 sec-ch-ua-platform 取值，与登录设备的声明保持一致。"""
        text = str(ua or "")
        if "Windows" in text:
            return '"Windows"'
        if "Android" in text:
            return '"Android"'
        if "iPhone" in text or "iPad" in text or "iOS" in text:
            return '"iOS"'
        if "Linux" in text:
            return '"Linux"'
        if "Macintosh" in text or "Mac OS X" in text:
            return '"macOS"'
        return '"macOS"'

    @staticmethod
    def _device_hint(prefix: str, raw: Any) -> str:
        """把服务端返回的设备指纹压缩成便于日志排查的片段。"""
        text = str(raw or '').strip()
        if not text:
            return f"{prefix}=未返回"
        return f"{prefix}={text[:10]}…{text[-10:]}" if len(text) > 24 else f"{prefix}={text}"

    def _describe_device_mismatch(self, data: Dict[str, Any]) -> str:
        """生成设备不一致的可执行提示，区分缺指纹 / 缺设备 UA / 设备本身换了。"""
        base = "登录设备与当前请求设备不一致"
        if not self._device_id:
            return f"{base}：本插件未配置设备指纹，请在浏览器控制台页执行提取代码后填入「设备指纹」"
        detail = "，".join([
            f"服务端登录设备={data.get('loginDevice') or '未知'}",
            f"本次请求设备={data.get('currentDevice') or '未知'}",
        ])
        # 凭证缺少 ua 时无法还原登录设备特征，最常见于旧版提取脚本产出的凭证
        meta = self._bundle_meta if isinstance(self._bundle_meta, dict) else {}
        if not meta.get("ua"):
            return (f"{base}（{detail}）：凭证里缺少设备 UA 信息，请在浏览器重新提取一次凭证"
                    f"（提取脚本会带上登录设备的 UA 与平台）")
        return (f"{base}（{detail}）：凭证记录的登录设备与本机 UA 已对齐，"
                f"若仍失败说明该账号最近在其他设备重新登录过，请用那台设备重新提取凭证")

    def _normalize_proxies(self, p: Any) -> Optional[Dict[str, str]]:
        try:
            if not p:
                return None
            if isinstance(p, str):
                return {"http": p, "https": p}
            if isinstance(p, dict):
                http = p.get('http') or p.get('HTTP')
                https = p.get('https') or p.get('HTTPS') or http
                if http or https:
                    return {"http": http or https, "https": https or http}
        except Exception:
            pass
        return None

    def _get_proxies(self) -> Optional[Dict[str, str]]:
        try:
            if not self._proxy_enabled:
                return None
            p = getattr(settings, 'PROXY', None)
            return self._normalize_proxies(p)
        except Exception:
            return None

    def _to_int(self, v: Any) -> Optional[int]:
        try:
            if v is None:
                return None
            if isinstance(v, int):
                return v
            if isinstance(v, float):
                return int(v)
            s = str(v).strip()
            if s == "":
                return None
            if "." in s:
                return int(float(s))
            return int(s)
        except Exception:
            return None

    def _try_auto_exchange(self, headers: Dict[str, str], proxies: Optional[Dict[str, str]]) -> str:
        """按可选配置兑换套餐；仅使用当前账号已登录会话，不尝试绕过认证。"""
        plan = self._EXCHANGE_PLANS.get(self._auto_exchange)
        if not plan:
            return ""

        def record(status: str, message: str, points_change: int = 0) -> None:
            self._save_history({
                "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "ts": int(time.time() * 1000),
                "status": status,
                "message": message,
                "points_gain": points_change,
            })

        timezone = pytz.timezone(settings.TZ)
        today = datetime.now(timezone).strftime('%Y-%m-%d')
        history = self.get_data('glados_history') or []
        if any(
            today in str(item.get('date', ''))
            and item.get('status') in ('兑换', '兑换成功')
            for item in history
        ):
            logger.info("今日已兑换套餐，跳过自动兑换")
            return ""

        current_points = self._to_int((self.get_data('glados_points_info') or {}).get('points'))
        required_points = plan['points']
        if current_points is None:
            result = "积分数据未就绪，跳过自动兑换"
            record("兑换跳过", result)
            return result
        if current_points < required_points:
            result = f"积分不足 ({current_points}/{required_points})，未兑换{plan['label']}"
            record("积分不足", result)
            return result

        try:
            response = requests.post(
                f"{self._base_url.rstrip('/')}/api/user/exchange",
                json={"planType": plan["plan_type"]},
                headers=headers,
                timeout=self._timeout_seconds,
                proxies=proxies,
            )
            data = response.json() or {}
        except Exception as error:
            logger.warning(f"自动兑换请求失败: {error}")
            result = f"自动兑换请求失败：{error}"
            record("兑换异常", result)
            return result

        if data.get('code') == 0:
            result = f"自动兑换成功：{plan['label']} (-{required_points}点)"
            logger.info(result)
            return result
        logger.info(f"兑换响应: code={data.get('code')}, message={data.get('message') or data.get('reason')}, planType={plan['plan_type']}")

        reason = data.get('message') or data.get('reason') or f"HTTP {response.status_code}"
        logger.warning(f"自动兑换失败: {reason}")
        result = f"自动兑换失败：{reason}"
        record("兑换失败", result)
        return result

    def _fetch_user_summary(self, headers: Dict[str, str], proxies: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """
        拉取用户信息，包括 /api/user/points (积分/历史) 和 /api/user/info (账号详情)
        """
        try:
            # 1. 获取积分和历史记录 (Source of Truth)
            url_points = f"{self._base_url.rstrip('/')}/api/user/points"
            try:
                r = requests.get(url_points, headers=headers, timeout=12, proxies=proxies)
                if r.status_code == 200:
                    d = r.json() or {}
                    if d.get('code') == 0:
                        # 保存原始 Points 数据
                        self.save_data('glados_points_info', d)
                        
                        # 同步历史记录
                        history_list = d.get('history', [])
                        self._sync_history_from_api(history_list)
            except Exception as e:
                logger.warning(f"获取 Points 失败: {e}")

            # 2. 获取账号基本信息 (days, email etc)
            # /api/user/status 也可以，但 /api/user/info 似乎更常用于获取天数
            urls = [f"{self._base_url.rstrip('/')}/api/user/status"]
            for u in urls:
                r = requests.get(u, headers=headers, timeout=12, proxies=proxies)
                d = {}
                try: d = r.json() or {}
                except Exception: d = {}
                
                code = d.get('code')
                if code == 0 and isinstance(d.get('data'), dict):
                    data = d.get('data')
                    user_id = data.get('userId') or data.get('configureId')
                    email = data.get('email')
                    days = self._to_int(data.get('days'))
                    left_days = self._to_int(data.get('leftDays'))
                    out = {
                        'user_id': user_id or None,
                        'email': email or None,
                        'days': days,
                        'leftDays': left_days,
                    }
                    self.save_data('glados_user', out)
                    return out
        except Exception as e:
            logger.warning(f"拉取用户信息异常: {e}")
        return {}

    def _sync_history_from_api(self, api_history: List[Dict]):
        """
        将 API 返回的历史记录同步到本地存储
        API Item Example:
        {
            "id": 128424869,
            "user_id": 661475,
            "time": 1768695420698,
            "asset": "points",
            "business": "system:checkin:2026-01-18",
            "change": "3.00000000",
            "balance": "240.0000000000000000",
            "detail": "checkin:2026-01-18-661475"
        }
        """
        if not api_history:
            return
            
        formatted_history = []
        for item in api_history:
            try:
                ts = int(item.get('time') or 0)
                change = float(item.get('change') or 0)
                # 转换为整数展示，更简洁
                change_int = int(change) if change.is_integer() else change
                
                balance = float(item.get('balance') or 0)
                balance_int = int(balance) if balance.is_integer() else balance
                
                business = item.get('business', '')
                detail = item.get('detail', '')
                
                # 构造存入本地的格式
                dt = datetime.fromtimestamp(ts/1000.0)
                dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                
                # 简单的状态推断
                status = "变动"
                if "checkin" in business or "checkin" in detail:
                    status = "签到"
                elif "exchange" in business or "exchange" in detail:
                    status = "兑换"
                
                # 构造消息
                msg = detail or business or ""
                # 简单翻译
                if 'exchange' in msg and 'points for' in msg:
                    # exchange 200 points for 30 days
                    try:
                        import re
                        m = re.search(r'exchange (\d+) points for (\d+) days', msg)
                        if m:
                            pts, dys = m.groups()
                            msg = f"积分兑换{dys}天 (-{pts}点)"
                    except:
                        msg = "积分兑换套餐"
                elif 'checkin' in msg:
                    # checkin:2026-01-20-661475
                    msg = "每日签到奖励"
                    
                formatted_history.append({
                    'date': dt_str,
                    'ts': ts,
                    'status': status,
                    'message': msg,
                    'points_gain': change_int, # 复用字段名，实际是 change
                    'balance': balance_int,
                    'user_id': item.get('user_id')
                })
            except Exception:
                continue
        
        # 保存，由于 API 返回的是完整的最近记录，直接覆盖即可
        # 但为了保留更久的数据，可以做合并。此处简单起见，且 User 想要 API 数据，直接保存 API 返回的最新数据的解析结果
        # 如果需要保留更久，可以与 self.get_data('glados_history') 合并去重
        # 考虑到 API 给的是 authoritative 的历史，直接覆盖显示最准确
        self.save_data('glados_history', formatted_history)

    def _save_history(self, record: Dict[str, Any]):
        try:
            history = self.get_data('glados_history') or []
            history.append(record)
            tz = pytz.timezone(settings.TZ)
            now = datetime.now(tz)
            keep = []
            for r in history:
                try:
                    dt_str = r.get('date', '')
                    ts_val = r.get('ts')
                    if dt_str:
                        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                        dt = tz.localize(dt) if dt.tzinfo is None else dt
                    else:
                        dt = now
                except Exception:
                    dt = now
                if (now - dt).days < int(self._history_days):
                    if ts_val is None:
                        try:
                            ts_val = int(dt.timestamp() * 1000)
                        except Exception:
                            ts_val = int(time.time()*1000)
                    r['ts'] = ts_val
                    keep.append(r)
            keep = sorted(keep, key=lambda x: int(x.get('ts') or 0), reverse=True)
            self.save_data('glados_history', keep)
        except Exception:
            pass

    def get_state(self) -> bool:
        return self._enabled

    def get_service(self) -> List[Dict[str, Any]]:
        if self._enabled and self._cron:
            return [{
                "id": "gladossign",
                "name": "GlaDOS 签到",
                "trigger": CronTrigger.from_crontab(self._cron),
                "func": self.sign,
                "kwargs": {}
            }]
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VCard',
                        'props': {'variant': 'elevated', 'elevation': 1, 'rounded': 'lg', 'class': 'mb-3'},
                        'content': [
                            {'component': 'VCardTitle', 'props': {'class': 'text-h6 font-weight-bold'}, 'text': '基础设置'},
                            {'component': 'VCardText', 'content': [
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [{'component': 'VSwitch', 'props': {'model': 'enabled', 'label': '启用插件'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [{'component': 'VSwitch', 'props': {'model': 'notify', 'label': '开启通知'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [{'component': 'VSwitch', 'props': {'model': 'onlyonce', 'label': '立即运行一次'}}]},
                                ]},
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 6}, 'content': [{'component': 'VCronField', 'props': {'model': 'cron', 'label': '签到周期'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 6}, 'content': [{'component': 'VTextField', 'props': {'model': 'history_days', 'label': '历史保留天数', 'type': 'number', 'placeholder': '30'}}]},
                                ]}
                            ]}
                        ]
                    },
                    {
                        'component': 'VCard',
                        'props': {'variant': 'elevated', 'elevation': 1, 'rounded': 'lg', 'class': 'mb-3'},
                        'content': [
                            {'component': 'VCardTitle', 'props': {'class': 'text-h6 font-weight-bold'}, 'text': '域名与认证'},
                            {'component': 'VCardText', 'content': [
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                                        {'component': 'VAlert', 'props': {'type': 'warning', 'variant': 'outlined', 'class': 'mb-2', 'text': '控制台会校验「登录设备」：Cookie 必须与登录时的设备指纹配套，且同域。下面的一键提取会同时拿到 Cookie、设备指纹和登录域名，插件自动识别，无需手填。'}}
                                    ]},
                                ]},
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [{'component': 'VTextField', 'props': {'model': 'base_url', 'label': 'Base URL (基础域名，留空则用凭证里的域名)', 'placeholder': '留空即可：粘贴凭证后会自动识别，例如 https://glados.space'}}]},
                                ]},
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                                        {'component': 'VAlert', 'props': {'type': 'info', 'variant': 'tonal', 'class': 'mb-2', 'text': '使用步骤：① 点下方按钮复制提取代码；② 在已登录的 GlaDOS 控制台页面按 F12 → Console，粘贴回车；③ 页面底部弹出结果面板，凭证已自动复制；④ 粘贴到「① 一次性凭证」；⑤ 按提示手动复制 Cookie 到「② 完整 Cookie」；⑥ 保存并运行。'}}
                                    ]},
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [self._device_helper_button()]},
                                ]},
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [{'component': 'VTextarea', 'props': {'model': 'auth_bundle', 'label': '① 一次性凭证（设备指纹 + 登录域名）', 'rows': 3, 'placeholder': '粘贴提取代码输出的整段 JSON，例如 {"v":1,"cookie":"","device":"83xxxx-1080-1920","domain":"glados.space"}'}}]},
                                ]},
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [{'component': 'VTextarea', 'props': {'model': 'cookie', 'label': '② 完整 Cookie（必须手填）', 'rows': 3, 'placeholder': 'koa:sess=xxx; koa:sess.sig=yyy'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                                        {'component': 'VAlert', 'props': {'type': 'info', 'variant': 'tonal', 'text': 'Cookie 在哪：F12 → Application（应用程序）→ 左侧 Storage 下的 Cookies → 点你登录的域名 → 找到 koa:sess 与 koa:sess.sig，双击 Value 全选复制，拼成一行 koa:sess=<值>; koa:sess.sig=<值>。浏览器禁止脚本读取 HttpOnly Cookie，所以这一步必须手动复制一次。'}}
                                    ]},
                                ]},
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                                        {'component': 'VAlert', 'props': {'type': 'warning', 'variant': 'outlined', 'class': 'mt-2', 'text': '凭证有时效：Cookie 失效（控制台掉登录）后需重新提取。若通知提示 Cookie 项为 0，说明站点 Cookie 是 HttpOnly，请在浏览器开发者工具 Network 中复制 Cookie 请求头，填到下方「高级：手动填写」。换设备/换浏览器/改屏幕分辨率后设备指纹会变化，同样需要重新提取。提取代码仅在本机计算，不联网、不上传数据。'}}
                                    ]},
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                                        {'component': 'VExpansionPanels', 'props': {'variant': 'accordion', 'class': 'mt-2'}, 'content': [
                                            {'component': 'VExpansionPanel', 'content': [
                                                {'component': 'VExpansionPanelTitle', 'text': '高级：手动填写 Cookie / 设备指纹（可选，留空则用上面的凭证）'},
                                                {'component': 'VExpansionPanelText', 'content': [
                                                    {'component': 'VTextField', 'props': {'model': 'device_id', 'label': '设备指纹 (Authorization)（手动，通常无需填写）', 'placeholder': '例如 83xxxxxxxxxxxxxxxxxxxxxxxxxx-1080-1920'}},
                                                    {'component': 'VAlert', 'props': {'type': 'info', 'variant': 'tonal', 'class': 'mt-2', 'text': '设备指纹一般由「一次性凭证」自动带入；只有凭证解析失败时才需要在这里手填。'}},
                                                ]},
                                            ]},
                                        ]},
                                    ]},
                                ]},
                            ]}
                        ]
                    },
                    {
                        'component': 'VCard',
                        'props': {'variant': 'elevated', 'elevation': 1, 'rounded': 'lg', 'class': 'mb-3'},
                        'content': [
                            {'component': 'VCardTitle', 'props': {'class': 'text-h6 font-weight-bold'}, 'text': '积分自动兑换'},
                            {'component': 'VCardText', 'content': [
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 6}, 'content': [{'component': 'VSelect', 'props': {'model': 'auto_exchange', 'label': '自动兑换套餐', 'clearable': True, 'placeholder': '不自动兑换', 'items': [{'title': '10天（需100积分）', 'value': '10'}, {'title': '30天（需200积分）', 'value': '30'}, {'title': '100天（需500积分）', 'value': '100'}]}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 6}, 'content': [{'component': 'VAlert', 'props': {'type': 'info', 'variant': 'tonal', 'text': '签到完成后，积分达到套餐门槛才会兑换；默认关闭，每日最多自动兑换一次。'}}]},
                                ]}
                            ]}
                        ]
                    },
                    {
                        'component': 'VCard',
                        'props': {'variant': 'elevated', 'elevation': 2, 'rounded': 'lg', 'class': 'mb-3'},
                        'content': [
                            {'component': 'VCardTitle', 'props': {'class': 'text-h6 font-weight-bold'}, 'text': '🎁 注册与福利(AFF)'},
                            {'component': 'VCardText', 'content': [
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 8}, 'content': [
                                        {'component': 'div', 'props': {'class': 'text-body-2'}, 'text': 'GlaDOS感觉挺佛系的，靠每日签到可长期使用，有需求可以点击注册体验。'},
                                        {'component': 'div', 'props': {'class': 'text-caption text-medium-emphasis mt-2'}, 'text': '提示：注册后每日签到获取点数，可兑换套餐时长 (100点=10天 / 200点=30天 / 500点=100天)。'},
                                        {'component': 'VBtn', 'props': {'href': 'https://glados.space/landing/1F8CJ-TKYWO-KHOV3-PN7X2', 'target': '_blank', 'rel': 'noopener', 'color': 'indigo', 'variant': 'elevated', 'class': 'mt-2'}, 'text': '✨ 立即注册'}
                                    ]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                        {'component': 'VImg', 'props': {'src': 'https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/glados.png', 'height': 120, 'class': 'rounded-lg'}}
                                    ]}
                                ]}
                            ]}
                        ]
                    },
                    {
                        'component': 'VCard',
                        'props': {'variant': 'elevated', 'elevation': 1, 'rounded': 'lg', 'class': 'mb-3'},
                        'content': [
                            {'component': 'VCardTitle', 'props': {'class': 'text-h6 font-weight-bold'}, 'text': '网络与重试'},
                            {'component': 'VCardText', 'content': [
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VSwitch', 'props': {'model': 'proxy_enabled', 'label': '使用 MP 全局代理'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VTextField', 'props': {'model': 'timeout_seconds', 'label': '超时(秒)', 'type': 'number', 'placeholder': '30'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VTextField', 'props': {'model': 'max_attempts', 'label': '重试次数/模式', 'type': 'number', 'placeholder': '2'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VTextField', 'props': {'model': 'retry_interval_seconds', 'label': '重试间隔(秒)', 'type': 'number', 'placeholder': '2'}}]},
                                ]},
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                                        {'component': 'VAlert', 'props': {'type': 'info', 'variant': 'tonal', 'text': '说明：每种连接模式内按重试次数与间隔依次尝试；连接模式顺序为 代理→直连(可选)。建议在网络不稳时适当增大超时与间隔。'}}
                                    ]}
                                ]}
                            ]}
                        ]
                    },
                    
                ]
            }
        ], {
            "enabled": False,
            "notify": True,
            "onlyonce": False,
            "base_url": "https://glados.cloud",
            "auth_bundle": "",
            "cookie": "",
            "device_id": "",
            "auto_exchange": "",
            "proxy_enabled": True,
            "timeout_seconds": 30,
            "max_attempts": 2,
            "retry_no_proxy_fallback": True,
            "cron": "0 9 * * *",
            "history_days": 30,
        }

    def get_page(self) -> List[dict]:
        # 从 _fetch_user_summary 存储的数据中读取
        user_info = self.get_data('glados_user') or {}
        points_info = self.get_data('glados_points_info') or {}
        historys = self.get_data('glados_history') or []
        
        # 排序
        historys = sorted(historys, key=lambda x: int(x.get('ts') or 0), reverse=True)
        
        card = []
        if user_info or points_info:
            uid = user_info.get('user_id')
            email = user_info.get('email')
            days = user_info.get('days')
            left_days = user_info.get('leftDays')
            
            # 优先从 points_info 获取积分余额
            balance = points_info.get('points')
            if balance is None:
                 balance = "-"
            else:
                 # 格式化，去掉多余的 0
                 try:
                     balance = float(balance)
                     balance = int(balance) if balance.is_integer() else balance
                 except: pass

            latest = historys[0] if historys else {}
            
            # 查找最近一次【签到】记录用于首页展示 (忽略兑换记录)
            latest_checkin = next((h for h in historys if h.get('status') == '签到'), None)
            # 如果没有签到记录，则回退到第一条
            display_rec = latest_checkin if latest_checkin else latest
            
            latest_status = display_rec.get('status', '-')
            latest_gain = display_rec.get('points_gain', 0)
            latest_color = 'success' if int(latest_gain) > 0 else ('error' if int(latest_gain) < 0 else 'grey')
            latest_time = display_rec.get('date', '-')
            
            gain_emoji = '📈' if int(latest_gain or 0) > 0 else ('➖' if int(latest_gain or 0) == 0 else '📉')
            
            card = [
                {
                    'component': 'VCard',
                    'props': {'variant': 'elevated', 'elevation': 2, 'rounded': 'lg', 'class': 'mb-4'},
                    'content': [
                        {'component': 'VCardTitle', 'props': {'class': 'text-h5 font-weight-bold'}, 'text': '🚀 GlaDOS 用户摘要'},
                        {'component': 'VCardText', 'content': [
                            {'component': 'VRow', 'content': [
                                {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'large', 'variant': 'tonal', 'color': 'purple'}, 'text': f'🆔 用户ID {uid or "-"}'}
                                ]},
                                {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'large', 'variant': 'tonal', 'color': 'amber-darken-2'}, 'text': f'💰 点数 {balance or "-"}'}
                                ]},
                                {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'large', 'variant': 'tonal', 'color': latest_color}, 'text': f'{gain_emoji} 本次 {latest_gain}'}
                                ]},
                            ]},
                            {'component': 'VDivider'},
                            {'component': 'VRow', 'props': {'class': 'mt-3'}, 'content': [
                                {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'default', 'variant': 'elevated'}, 'text': f'📧 邮箱 {email or "-"}'}
                                ]},
                                {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'default', 'variant': 'elevated'}, 'text': f'📅 已用天数 {days if days is not None else "-"}'}
                                ]},
                                {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'default', 'variant': 'elevated'}, 'text': f'🕒 剩余天数 {left_days if left_days is not None else "-"}'}
                                ]},
                            ]},
                            {'component': 'VRow', 'props': {'class': 'mt-3'}, 'content': [
                                {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'default', 'variant': 'tonal'}, 'text': f'⏰ 更新时间 {latest_time}'}
                                ]},
                            ]},
                            {'component': 'VRow', 'props': {'class': 'mt-3'}, 'content': [
                                {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'default', 'variant': 'tonal', 'color': 'indigo'}, 'text': '💡 提示：点数可兑换套餐：100点=10天 / 200点=30天 / 500点=100天'}
                                ]}
                            ]},
                        ]}
                    ]
                }
            ]
        rows = []
        for h in historys:
            delta = int(h.get('points_gain') or 0)
            delta_color = 'success' if delta > 0 else ('grey' if delta == 0 else 'error')
            delta_emoji = '📈' if delta > 0 else ('➖' if delta == 0 else '📉')
            rows.append({
                'component': 'tr',
                'content': [
                    {'component': 'td', 'props': {'class': 'text-caption'}, 'text': h.get('date', '')},
                    {'component': 'td', 'content': [{'component': 'VChip', 'props': {'size': 'small', 'variant': 'outlined', 'color': 'primary'}, 'text': h.get('status', '-')}]},
                    {'component': 'td', 'content': [{'component': 'VChip', 'props': {'size': 'small', 'variant': 'outlined', 'color': delta_color}, 'text': f"{delta_emoji} {delta}"}]},
                    {'component': 'td', 'props': {'class': 'text-caption'}, 'text': h.get('message', '-')},
                ]
            })
        table = [
            {
                'component': 'VCard',
                'props': {'variant': 'elevated', 'elevation': 2, 'rounded': 'lg', 'class': 'mb-4'},
                'content': [
                    {'component': 'VCardTitle', 'props': {'class': 'text-h6 font-weight-bold'}, 'text': f'📊 签到历史 (近{len(rows)}条)'},
                    {'component': 'VCardText', 'content': [
                        {'component': 'VTable', 'props': {'hover': True, 'density': 'comfortable'}, 'content': [
                            {'component': 'thead', 'content': [{'component': 'tr', 'content': [
                                {'component': 'th', 'props': {'class': 'text-body-2'}, 'text': '时间'},
                                {'component': 'th', 'props': {'class': 'text-body-2'}, 'text': '状态'},
                                {'component': 'th', 'props': {'class': 'text-body-2'}, 'text': '点数变化'},
                                {'component': 'th', 'props': {'class': 'text-body-2'}, 'text': '消息'},
                            ]}]},
                            {'component': 'tbody', 'content': rows}
                        ]}
                        ]
                    }
                ]
            }
        ]
        if not historys:
            return [{
                'component': 'VAlert',
                'props': {'type': 'info', 'variant': 'tonal', 'text': '暂无签到记录，请先配置域名与Cookie后运行一次签到', 'class': 'mb-2'}
            }]
        return card + table

    def stop_service(self):
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            self._scheduler = None
        return True

    def get_command(self) -> List[Dict[str, Any]]: return []
    def get_api(self) -> List[Dict[str, Any]]: return []
