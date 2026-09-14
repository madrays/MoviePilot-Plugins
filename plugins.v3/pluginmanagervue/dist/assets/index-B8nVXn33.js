import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import PageComponent, { _ as _export_sfc } from './__federation_expose_Page-CEUe4Ddt.js';
import { p as propsFactory, i as includes, a as isOn, e as eventName, g as genericComponent, b as getCurrentInstance, c as provideTheme, d as createLayout, u as useRtl, m as makeThemeProps, f as makeLayoutProps, h as provideDefaults, j as convertToUnit, k as destructComputed, l as isCssColor, n as isParsableColor, o as parseColor, q as getForeground, r as getCurrentInstanceName, s as isObject, S as SUPPORTS_INTERSECTION, t as clamp, v as consoleWarn, w as useProxiedModel, x as useToggleScope, y as useLayoutItem, z as makeLayoutItemProps, A as deepEqual, B as wrapInArray, C as findChildrenWithProvide, D as useTheme, E as useIcon, I as IconValue, F as flattenFragments, G as useResizeObserver, H as IN_BROWSER, J as hasEvent, K as keyCodes, L as useLocale, M as EventProp, N as filterInputAttrs, O as matchesSelector, P as omit, Q as callEvent, R as pick, T as useDisplay, U as useGoTo, V as makeDisplayProps, W as focusableChildren, X as consoleError, Y as defineComponent, Z as deprecate, _ as isPrimitive, $ as getPropertyFromItem, a0 as focusChild, a1 as CircularBuffer, a2 as defer, a3 as templateRef, a4 as isClickInsideElement, a5 as getNextElement, a6 as debounce, a7 as ensureValidVNode, a8 as checkPrintable, a9 as noop, aa as pickWithRest, ab as keys, ac as getEventCoordinates, ad as HexToHSV, ae as HSVtoHex, af as HSLtoHSV, ag as HSVtoHSL, ah as RGBtoHSV, ai as HSVtoRGB, aj as has, ak as getDecimals, al as createRange, am as keyValues, an as SUPPORTS_EYE_DROPPER, ao as HSVtoCSS, ap as RGBtoCSS, aq as getContrast, ar as isComposingIgnoreKey, as as getObjectValueByPath, at as isEmpty, au as defineFunctionalComponent, av as breakpoints, aw as useDate, ax as humanReadableFileSize, ay as provideLocale, az as useLayout, aA as VuetifyLayoutKey, aB as refElement, aC as VClassIcon, aD as VComponentIcon, aE as VLigatureIcon, aF as VSvgIcon } from './date-CPBRTuSz.js';

true&&(function polyfill() {
  const relList = document.createElement("link").relList;
  if (relList && relList.supports && relList.supports("modulepreload")) {
    return;
  }
  for (const link of document.querySelectorAll('link[rel="modulepreload"]')) {
    processPreload(link);
  }
  new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type !== "childList") {
        continue;
      }
      for (const node of mutation.addedNodes) {
        if (node.tagName === "LINK" && node.rel === "modulepreload")
          processPreload(node);
      }
    }
  }).observe(document, { childList: true, subtree: true });
  function getFetchOpts(link) {
    const fetchOpts = {};
    if (link.integrity) fetchOpts.integrity = link.integrity;
    if (link.referrerPolicy) fetchOpts.referrerPolicy = link.referrerPolicy;
    if (link.crossOrigin === "use-credentials")
      fetchOpts.credentials = "include";
    else if (link.crossOrigin === "anonymous") fetchOpts.credentials = "omit";
    else fetchOpts.credentials = "same-origin";
    return fetchOpts;
  }
  function processPreload(link) {
    if (link.ep)
      return;
    link.ep = true;
    const fetchOpts = getFetchOpts(link);
    fetch(link.href, fetchOpts);
  }
}());

const {createTextVNode:_createTextVNode$7,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode$2k,createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "app-container" };
const _hoisted_2 = { class: "component-preview" };
const _hoisted_3 = { class: "text-white" };

const {ref: ref$P,reactive: reactive$3,onMounted: onMounted$f} = await importShared('vue');


const _sfc_main = {
  __name: 'App',
  setup(__props) {

const activeTab = ref$P('page');

const mockDatabase = reactive$3({
  plugins: [
    // 本地插件 (不在在线市场)
    {
      id: 'localplugin1',
      name: '本地测试插件',
      version: '1.0',
      order: 1,
      description: '这是一个本地开发的插件，不在在线市场',
      author: 'LocalDev',
      icon: '',
      type: 'local',
      installed: true,
      status: 'running'
    },
    {
      id: 'customtool',
      name: '自定义工具',
      version: '2.1',
      order: 2,
      description: '自定义开发的工具插件',
      author: 'CustomDev',
      icon: '',
      type: 'local',
      installed: false,
      status: 'stopped'
    },
    // 在线插件 (来自市场)
    {
      id: 'logsclean',
      name: '日志清理Vue',
      version: '2.0',
      order: 50,
      description: '定时清理插件产生的日志文件，支持按行数和时间清理，保持系统整洁',
      author: 'madrays',
      icon: 'https://cdn.jsdelivr.net/gh/madrays/MoviePilot-Plugins@main/icons/clean.png',
      type: 'online',
      installed: true,
      status: 'running'
    },
    {
      id: 'autosignin',
      name: '站点自动签到',
      version: '2.6',
      order: 10,
      description: '自动完成PT站点每日签到任务，支持多站点批量签到，获取魔力值和积分',
      author: 'jxxghp',
      icon: 'https://cdn.jsdelivr.net/gh/jxxghp/MoviePilot-Plugins@main/icons/signin.png',
      type: 'online',
      installed: true,
      status: 'running'
    },
    {
      id: 'douban',
      name: '豆瓣刮削器',
      version: '1.5',
      order: 5,
      description: '从豆瓣获取电影和电视剧的详细信息、评分、演员表等元数据',
      author: 'jxxghp',
      icon: 'https://cdn.jsdelivr.net/gh/jxxghp/MoviePilot-Plugins@main/icons/douban.png',
      type: 'online',
      installed: false,
      status: 'stopped'
    },
    {
      id: 'tmdb',
      name: 'TMDB元数据',
      version: '2.1',
      order: 3,
      description: '从TMDB获取影视作品的海报、背景图、演员信息等丰富的元数据内容',
      author: 'jxxghp',
      icon: 'https://cdn.jsdelivr.net/gh/jxxghp/MoviePilot-Plugins@main/icons/tmdb.png',
      type: 'online',
      installed: true,
      status: 'running'
    },
    {
      id: 'mediaserver',
      name: '媒体服务器',
      version: '1.8',
      order: 15,
      description: '连接和管理Plex、Emby、Jellyfin等媒体服务器，同步媒体库信息',
      author: 'jxxghp',
      icon: 'https://cdn.jsdelivr.net/gh/jxxghp/MoviePilot-Plugins@main/icons/mediaserver.png',
      type: 'online',
      installed: true,
      status: 'running'
    },
    {
      id: 'notification',
      name: '消息通知',
      version: '3.2',
      order: 20,
      description: '支持微信、Telegram、邮件等多种方式发送系统通知和下载完成提醒',
      author: 'jxxghp',
      icon: 'https://cdn.jsdelivr.net/gh/jxxghp/MoviePilot-Plugins@main/icons/notification.png',
      type: 'online',
      installed: false,
      status: 'stopped'
    },
    {
      id: 'pluginmanagervue',
      name: '插件管理器',
      version: '3.0',
      order: 99,
      description: '管理插件重载、卸载等功能，支持本地和在线插件管理',
      author: 'InfinityPacer',
      icon: 'https://cdn.jsdelivr.net/gh/InfinityPacer/MoviePilot-Plugins@main/icons/manager.png',
      type: 'online',
      installed: true,
      status: 'running'
    }
  ],
  status: {
    total_plugins: 9,
    installed_plugins: 6,
    directory_plugins: 9,
    enabled: true,
    last_reload_count: 0
  },
  lastReloadPlugins: [
    {
      id: 'autosignin',
      name: '站点自动签到',
      version: '2.6',
      icon: 'https://cdn.jsdelivr.net/gh/jxxghp/MoviePilot-Plugins@main/icons/signin.png'
    },
    {
      id: 'logsclean',
      name: '日志清理Vue',
      version: '2.0',
      icon: 'https://cdn.jsdelivr.net/gh/madrays/MoviePilot-Plugins@main/icons/clean.png'
    }
  ]
});

// 模拟API包装器
const mockPluginApiWrapper = {
  get: async (url) => {
    console.log(`[Mock API GET] ${url}`);
    await new Promise(resolve => setTimeout(resolve, 300));
    
    if (url.includes('/plugins')) {
      return {
        success: true,
        data: mockDatabase.plugins
      };
    }
    
    if (url.includes('/status')) {
      return {
        success: true,
        data: mockDatabase.status
      };
    }
    
    if (url.includes('/last_reload')) {
      return {
        success: true,
        data: mockDatabase.lastReloadPlugins
      };
    }
    
    throw new Error(`Mock API: 未知的GET端点 ${url}`);
  },
  
  post: async (url, data) => {
    console.log(`[Mock API POST] ${url}`, data);
    await new Promise(resolve => setTimeout(resolve, 500));
    
    if (url.includes('/reload')) {
      const pluginId = data?.plugin_id;
      if (!pluginId) {
        return {
          success: false,
          message: '插件ID不能为空'
        };
      }
      
      const plugin = mockDatabase.plugins.find(p => p.id === pluginId);
      if (!plugin) {
        return {
          success: false,
          message: `插件 ${pluginId} 不存在`
        };
      }
      
      if (!plugin.installed) {
        return {
          success: false,
          message: `插件 ${plugin.name} 未安装，无法重载`
        };
      }
      
      // 更新上次重载列表
      const existingIndex = mockDatabase.lastReloadPlugins.findIndex(p => p.id === pluginId);
      if (existingIndex >= 0) {
        mockDatabase.lastReloadPlugins.splice(existingIndex, 1);
      }
      mockDatabase.lastReloadPlugins.unshift({
        id: plugin.id,
        name: plugin.name,
        version: plugin.version,
        icon: plugin.icon
      });
      // 只保留最近5个
      mockDatabase.lastReloadPlugins = mockDatabase.lastReloadPlugins.slice(0, 5);
      
      showNotification(`模拟重载插件: ${plugin.name}`, 'success');
      return {
        success: true,
        message: `插件 ${plugin.name} 重载成功`
      };
    }
    
    if (url.includes('/uninstall')) {
      const pluginId = data?.plugin_id;
      const clearConfig = data?.clear_config || false;
      const clearData = data?.clear_data || false;
      
      if (!pluginId) {
        return {
          success: false,
          message: '插件ID不能为空'
        };
      }
      
      const plugin = mockDatabase.plugins.find(p => p.id === pluginId);
      if (!plugin) {
        return {
          success: false,
          message: `插件 ${pluginId} 不存在`
        };
      }
      
      if (!plugin.installed) {
        return {
          success: false,
          message: `插件 ${plugin.name} 未安装`
        };
      }
      
      // 模拟卸载
      plugin.installed = false;
      plugin.status = 'stopped';
      mockDatabase.status.installed_plugins--;
      
      // 从上次重载列表中移除
      const reloadIndex = mockDatabase.lastReloadPlugins.findIndex(p => p.id === pluginId);
      if (reloadIndex >= 0) {
        mockDatabase.lastReloadPlugins.splice(reloadIndex, 1);
      }
      
      let message = `插件 ${plugin.name} 卸载成功`;
      if (clearConfig) {
        message += '，已清除配置';
      }
      if (clearData) {
        message += '，已清除数据';
      }
      
      showNotification(`模拟卸载插件: ${plugin.name}`, 'success');
      return {
        success: true,
        message: message
      };
    }
    
    throw new Error(`Mock API: 未知的POST端点 ${url}`);
  }
};

const snackbar = reactive$3({
  show: false,
  text: '',
  color: 'success',
  timeout: 3000,
});

function showNotification(text, color = 'success') {
  snackbar.text = text;
  snackbar.color = color;
  snackbar.show = true;
}

function handleClose(componentName) {
  showNotification(`${componentName} 已关闭 (模拟)`, 'info');
}

onMounted$f(async () => {
  try {
    showNotification('插件管理器: 模拟环境已准备就绪', 'success');
  } catch (e) {
    console.error("Error during App.vue onMounted:", e);
    showNotification(`初始化失败: ${e.message || '未知错误'}`, 'error');
  }
});


return (_ctx, _cache) => {
  const _component_v_app_bar_title = _resolveComponent("v-app-bar-title");
  const _component_v_app_bar = _resolveComponent("v-app-bar");
  const _component_v_tab = _resolveComponent("v-tab");
  const _component_v_tabs = _resolveComponent("v-tabs");
  const _component_v_window_item = _resolveComponent("v-window-item");
  const _component_v_window = _resolveComponent("v-window");
  const _component_v_container = _resolveComponent("v-container");
  const _component_v_main = _resolveComponent("v-main");
  const _component_v_footer = _resolveComponent("v-footer");
  const _component_v_app = _resolveComponent("v-app");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_snackbar = _resolveComponent("v-snackbar");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode$2k(_component_v_app, null, {
      default: _withCtx(() => [
        _createVNode$2k(_component_v_app_bar, {
          color: "primary",
          app: ""
        }, {
          default: _withCtx(() => [
            _createVNode$2k(_component_v_app_bar_title, null, {
              default: _withCtx(() => _cache[5] || (_cache[5] = [
                _createTextVNode$7("插件管理器 - 本地测试")
              ])),
              _: 1,
              __: [5]
            })
          ]),
          _: 1
        }),
        _createVNode$2k(_component_v_main, null, {
          default: _withCtx(() => [
            _createVNode$2k(_component_v_container, null, {
              default: _withCtx(() => [
                _createVNode$2k(_component_v_tabs, {
                  modelValue: activeTab.value,
                  "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((activeTab).value = $event)),
                  "bg-color": "primary",
                  grow: ""
                }, {
                  default: _withCtx(() => [
                    _createVNode$2k(_component_v_tab, { value: "page" }, {
                      default: _withCtx(() => _cache[6] || (_cache[6] = [
                        _createTextVNode$7("插件管理")
                      ])),
                      _: 1,
                      __: [6]
                    })
                  ]),
                  _: 1
                }, 8, ["modelValue"]),
                _createVNode$2k(_component_v_window, {
                  modelValue: activeTab.value,
                  "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((activeTab).value = $event)),
                  class: "mt-4"
                }, {
                  default: _withCtx(() => [
                    _createVNode$2k(_component_v_window_item, { value: "page" }, {
                      default: _withCtx(() => [
                        _cache[7] || (_cache[7] = _createElementVNode("h2", { class: "text-h5 mb-4" }, "插件管理器 (Page.vue)", -1)),
                        _createElementVNode("div", _hoisted_2, [
                          _createVNode$2k(PageComponent, {
                            api: mockPluginApiWrapper,
                            onClose: _cache[1] || (_cache[1] = $event => (handleClose('Page')))
                          })
                        ])
                      ]),
                      _: 1,
                      __: [7]
                    })
                  ]),
                  _: 1
                }, 8, ["modelValue"])
              ]),
              _: 1
            })
          ]),
          _: 1
        }),
        _createVNode$2k(_component_v_footer, {
          app: "",
          color: "primary",
          class: "text-center d-flex justify-center"
        }, {
          default: _withCtx(() => [
            _createElementVNode("span", _hoisted_3, "MoviePilot 插件管理器本地测试 ©" + _toDisplayString(new Date().getFullYear()), 1)
          ]),
          _: 1
        })
      ]),
      _: 1
    }),
    _createVNode$2k(_component_v_snackbar, {
      modelValue: snackbar.show,
      "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((snackbar.show) = $event)),
      color: snackbar.color,
      timeout: snackbar.timeout,
      location: "top end"
    }, {
      actions: _withCtx(() => [
        _createVNode$2k(_component_v_btn, {
          variant: "text",
          onClick: _cache[3] || (_cache[3] = $event => (snackbar.show = false))
        }, {
          default: _withCtx(() => _cache[8] || (_cache[8] = [
            _createTextVNode$7(" 关闭 ")
          ])),
          _: 1,
          __: [8]
        })
      ]),
      default: _withCtx(() => [
        _createTextVNode$7(_toDisplayString(snackbar.text) + " ", 1)
      ]),
      _: 1
    }, 8, ["modelValue", "color", "timeout"])
  ]))
}
}

};
const App = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-2debe563"]]);

// Utilities
// Composables
const makeComponentProps = propsFactory({
  class: [String, Array, Object],
  style: {
    type: [String, Array, Object],
    default: null
  }
}, 'component');

// Utilities
const block = ['top', 'bottom'];
const inline = ['start', 'end', 'left', 'right'];
/** Parse a raw anchor string into an object */
function parseAnchor(anchor, isRtl) {
  let [side, align] = anchor.split(' ');
  if (!align) {
    align = includes(block, side) ? 'start' : includes(inline, side) ? 'top' : 'center';
  }
  return {
    side: toPhysical(side, isRtl),
    align: toPhysical(align, isRtl)
  };
}
function toPhysical(str, isRtl) {
  if (str === 'start') return isRtl ? 'right' : 'left';
  if (str === 'end') return isRtl ? 'left' : 'right';
  return str;
}
function flipSide(anchor) {
  return {
    side: {
      center: 'center',
      top: 'bottom',
      bottom: 'top',
      left: 'right',
      right: 'left'
    }[anchor.side],
    align: anchor.align
  };
}
function flipAlign(anchor) {
  return {
    side: anchor.side,
    align: {
      center: 'center',
      top: 'bottom',
      bottom: 'top',
      left: 'right',
      right: 'left'
    }[anchor.align]
  };
}
function flipCorner(anchor) {
  return {
    side: anchor.align,
    align: anchor.side
  };
}
function getAxis(anchor) {
  return includes(block, anchor.side) ? 'y' : 'x';
}

class Box {
  constructor(_ref) {
    let {
      x,
      y,
      width,
      height
    } = _ref;
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
  }
  get top() {
    return this.y;
  }
  get bottom() {
    return this.y + this.height;
  }
  get left() {
    return this.x;
  }
  get right() {
    return this.x + this.width;
  }
}
function getOverflow(a, b) {
  return {
    x: {
      before: Math.max(0, b.left - a.left),
      after: Math.max(0, a.right - b.right)
    },
    y: {
      before: Math.max(0, b.top - a.top),
      after: Math.max(0, a.bottom - b.bottom)
    }
  };
}
function getTargetBox(target) {
  if (Array.isArray(target)) {
    return new Box({
      x: target[0],
      y: target[1],
      width: 0,
      height: 0
    });
  } else {
    return target.getBoundingClientRect();
  }
}

// Utilities
/** @see https://stackoverflow.com/a/57876601/2074736 */
function nullifyTransforms(el) {
  const rect = el.getBoundingClientRect();
  const style = getComputedStyle(el);
  const tx = style.transform;
  if (tx) {
    let ta, sx, sy, dx, dy;
    if (tx.startsWith('matrix3d(')) {
      ta = tx.slice(9, -1).split(/, /);
      sx = Number(ta[0]);
      sy = Number(ta[5]);
      dx = Number(ta[12]);
      dy = Number(ta[13]);
    } else if (tx.startsWith('matrix(')) {
      ta = tx.slice(7, -1).split(/, /);
      sx = Number(ta[0]);
      sy = Number(ta[3]);
      dx = Number(ta[4]);
      dy = Number(ta[5]);
    } else {
      return new Box(rect);
    }
    const to = style.transformOrigin;
    const x = rect.x - dx - (1 - sx) * parseFloat(to);
    const y = rect.y - dy - (1 - sy) * parseFloat(to.slice(to.indexOf(' ') + 1));
    const w = sx ? rect.width / sx : el.offsetWidth + 1;
    const h = sy ? rect.height / sy : el.offsetHeight + 1;
    return new Box({
      x,
      y,
      width: w,
      height: h
    });
  } else {
    return new Box(rect);
  }
}
function animate(el, keyframes, options) {
  if (typeof el.animate === 'undefined') return {
    finished: Promise.resolve()
  };
  let animation;
  try {
    animation = el.animate(keyframes, options);
  } catch (err) {
    return {
      finished: Promise.resolve()
    };
  }
  if (typeof animation.finished === 'undefined') {
    animation.finished = new Promise(resolve => {
      animation.onfinish = () => {
        resolve(animation);
      };
    });
  }
  return animation;
}

// Utilities
const handlers = new WeakMap();
function bindProps(el, props) {
  Object.keys(props).forEach(k => {
    if (isOn(k)) {
      const name = eventName(k);
      const handler = handlers.get(el);
      if (props[k] == null) {
        handler?.forEach(v => {
          const [n, fn] = v;
          if (n === name) {
            el.removeEventListener(name, fn);
            handler.delete(v);
          }
        });
      } else if (!handler || ![...handler]?.some(v => v[0] === name && v[1] === props[k])) {
        el.addEventListener(name, props[k]);
        const _handler = handler || new Set();
        _handler.add([name, props[k]]);
        if (!handlers.has(el)) handlers.set(el, _handler);
      }
    } else {
      if (props[k] == null) {
        el.removeAttribute(k);
      } else {
        el.setAttribute(k, props[k]);
      }
    }
  });
}
function unbindProps(el, props) {
  Object.keys(props).forEach(k => {
    if (isOn(k)) {
      const name = eventName(k);
      const handler = handlers.get(el);
      handler?.forEach(v => {
        const [n, fn] = v;
        if (n === name) {
          el.removeEventListener(name, fn);
          handler.delete(v);
        }
      });
    } else {
      el.removeAttribute(k);
    }
  });
}

const {camelize: camelize$1,capitalize: capitalize$3,h: h$5} = await importShared('vue');
function createSimpleFunctional(klass) {
  let tag = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 'div';
  let name = arguments.length > 2 ? arguments[2] : undefined;
  return genericComponent()({
    name: name ?? capitalize$3(camelize$1(klass.replace(/__/g, '-'))),
    props: {
      tag: {
        type: String,
        default: tag
      },
      ...makeComponentProps()
    },
    setup(props, _ref) {
      let {
        slots
      } = _ref;
      return () => {
        return h$5(props.tag, {
          class: [klass, props.class],
          style: props.style
        }, slots.default?.());
      };
    }
  });
}

/**
 * Returns:
 *  - 'null' if the node is not attached to the DOM
 *  - the root node (HTMLDocument | ShadowRoot) otherwise
 */
function attachedRoot(node) {
  /* istanbul ignore next */
  if (typeof node.getRootNode !== 'function') {
    // Shadow DOM not supported (IE11), lets find the root of this node
    while (node.parentNode) node = node.parentNode;

    // The root parent is the document if the node is attached to the DOM
    if (node !== document) return null;
    return document;
  }
  const root = node.getRootNode();

  // The composed root node is the document if the node is attached to the DOM
  if (root !== document && root.getRootNode({
    composed: true
  }) !== document) return null;
  return root;
}

const standardEasing = 'cubic-bezier(0.4, 0, 0.2, 1)';
const deceleratedEasing = 'cubic-bezier(0.0, 0, 0.2, 1)'; // Entering
const acceleratedEasing = 'cubic-bezier(0.4, 0, 1, 1)'; // Leaving

// Utilities
function getPrefixedEventHandlers(attrs, suffix, getData) {
  return Object.keys(attrs).filter(key => isOn(key) && key.endsWith(suffix)).reduce((acc, key) => {
    acc[key.slice(0, -suffix.length)] = event => attrs[key](event, getData(event));
    return acc;
  }, {});
}

function getScrollParent(el) {
  let includeHidden = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
  while (el) {
    if (includeHidden ? isPotentiallyScrollable(el) : hasScrollbar(el)) return el;
    el = el.parentElement;
  }
  return document.scrollingElement;
}
function getScrollParents(el, stopAt) {
  const elements = [];
  if (stopAt && el && !stopAt.contains(el)) return elements;
  while (el) {
    if (hasScrollbar(el)) elements.push(el);
    if (el === stopAt) break;
    el = el.parentElement;
  }
  return elements;
}
function hasScrollbar(el) {
  if (!el || el.nodeType !== Node.ELEMENT_NODE) return false;
  const style = window.getComputedStyle(el);
  return style.overflowY === 'scroll' || style.overflowY === 'auto' && el.scrollHeight > el.clientHeight;
}
function isPotentiallyScrollable(el) {
  if (!el || el.nodeType !== Node.ELEMENT_NODE) return false;
  const style = window.getComputedStyle(el);
  return ['scroll', 'auto'].includes(style.overflowY);
}

function isFixedPosition(el) {
  while (el) {
    if (window.getComputedStyle(el).position === 'fixed') {
      return true;
    }
    el = el.offsetParent;
  }
  return false;
}

// Utilities
function useRender(render) {
  const vm = getCurrentInstance('useRender');
  vm.render = render;
}

const {createVNode:_createVNode$2j} = await importShared('vue');
const makeVAppProps = propsFactory({
  ...makeComponentProps(),
  ...makeLayoutProps({
    fullHeight: true
  }),
  ...makeThemeProps()
}, 'VApp');
const VApp = genericComponent()({
  name: 'VApp',
  props: makeVAppProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const theme = provideTheme(props);
    const {
      layoutClasses,
      getLayoutItem,
      items,
      layoutRef
    } = createLayout(props);
    const {
      rtlClasses
    } = useRtl();
    useRender(() => _createVNode$2j("div", {
      "ref": layoutRef,
      "class": ['v-application', theme.themeClasses.value, layoutClasses.value, rtlClasses.value, props.class],
      "style": [props.style]
    }, [_createVNode$2j("div", {
      "class": "v-application__wrap"
    }, [slots.default?.()])]));
    return {
      getLayoutItem,
      items,
      theme
    };
  }
});

// Utilities
// Types
// Composables
const makeTagProps = propsFactory({
  tag: {
    type: [String, Object, Function],
    default: 'div'
  }
}, 'tag');

const {createVNode:_createVNode$2i} = await importShared('vue');
const makeVToolbarTitleProps = propsFactory({
  text: String,
  ...makeComponentProps(),
  ...makeTagProps()
}, 'VToolbarTitle');
const VToolbarTitle = genericComponent()({
  name: 'VToolbarTitle',
  props: makeVToolbarTitleProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    useRender(() => {
      const hasText = !!(slots.default || slots.text || props.text);
      return _createVNode$2i(props.tag, {
        "class": ['v-toolbar-title', props.class],
        "style": props.style
      }, {
        default: () => [hasText && _createVNode$2i("div", {
          "class": "v-toolbar-title__placeholder"
        }, [slots.text ? slots.text() : props.text, slots.default?.()])]
      });
    });
    return {};
  }
});

// Utilities
const {h: h$4,Transition: Transition$5,TransitionGroup: TransitionGroup$1} = await importShared('vue');
const makeTransitionProps$1 = propsFactory({
  disabled: Boolean,
  group: Boolean,
  hideOnLeave: Boolean,
  leaveAbsolute: Boolean,
  mode: String,
  origin: String
}, 'transition');
function createCssTransition(name, origin, mode) {
  return genericComponent()({
    name,
    props: makeTransitionProps$1({
      mode,
      origin
    }),
    setup(props, _ref) {
      let {
        slots
      } = _ref;
      const functions = {
        onBeforeEnter(el) {
          if (props.origin) {
            el.style.transformOrigin = props.origin;
          }
        },
        onLeave(el) {
          if (props.leaveAbsolute) {
            const {
              offsetTop,
              offsetLeft,
              offsetWidth,
              offsetHeight
            } = el;
            el._transitionInitialStyles = {
              position: el.style.position,
              top: el.style.top,
              left: el.style.left,
              width: el.style.width,
              height: el.style.height
            };
            el.style.position = 'absolute';
            el.style.top = `${offsetTop}px`;
            el.style.left = `${offsetLeft}px`;
            el.style.width = `${offsetWidth}px`;
            el.style.height = `${offsetHeight}px`;
          }
          if (props.hideOnLeave) {
            el.style.setProperty('display', 'none', 'important');
          }
        },
        onAfterLeave(el) {
          if (props.leaveAbsolute && el?._transitionInitialStyles) {
            const {
              position,
              top,
              left,
              width,
              height
            } = el._transitionInitialStyles;
            delete el._transitionInitialStyles;
            el.style.position = position || '';
            el.style.top = top || '';
            el.style.left = left || '';
            el.style.width = width || '';
            el.style.height = height || '';
          }
        }
      };
      return () => {
        const tag = props.group ? TransitionGroup$1 : Transition$5;
        return h$4(tag, {
          name: props.disabled ? '' : name,
          css: !props.disabled,
          ...(props.group ? undefined : {
            mode: props.mode
          }),
          ...(props.disabled ? {} : functions)
        }, slots.default);
      };
    }
  });
}
function createJavascriptTransition(name, functions) {
  let mode = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : 'in-out';
  return genericComponent()({
    name,
    props: {
      mode: {
        type: String,
        default: mode
      },
      disabled: Boolean,
      group: Boolean
    },
    setup(props, _ref2) {
      let {
        slots
      } = _ref2;
      const tag = props.group ? TransitionGroup$1 : Transition$5;
      return () => {
        return h$4(tag, {
          name: props.disabled ? '' : name,
          css: !props.disabled,
          // mode: props.mode, // TODO: vuejs/vue-next#3104
          ...(props.disabled ? {} : functions)
        }, slots.default);
      };
    }
  });
}

// Utilities
const {camelize} = await importShared('vue');

function ExpandTransitionGenerator () {
  let expandedParentClass = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : '';
  let x = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
  const sizeProperty = x ? 'width' : 'height';
  const offsetProperty = camelize(`offset-${sizeProperty}`);
  return {
    onBeforeEnter(el) {
      el._parent = el.parentNode;
      el._initialStyle = {
        transition: el.style.transition,
        overflow: el.style.overflow,
        [sizeProperty]: el.style[sizeProperty]
      };
    },
    onEnter(el) {
      const initialStyle = el._initialStyle;
      if (!initialStyle) return;
      el.style.setProperty('transition', 'none', 'important');
      // Hide overflow to account for collapsed margins in the calculated height
      el.style.overflow = 'hidden';
      const offset = `${el[offsetProperty]}px`;
      el.style[sizeProperty] = '0';
      void el.offsetHeight; // force reflow

      el.style.transition = initialStyle.transition;
      if (expandedParentClass && el._parent) {
        el._parent.classList.add(expandedParentClass);
      }
      requestAnimationFrame(() => {
        el.style[sizeProperty] = offset;
      });
    },
    onAfterEnter: resetStyles,
    onEnterCancelled: resetStyles,
    onLeave(el) {
      el._initialStyle = {
        transition: '',
        overflow: el.style.overflow,
        [sizeProperty]: el.style[sizeProperty]
      };
      el.style.overflow = 'hidden';
      el.style[sizeProperty] = `${el[offsetProperty]}px`;
      void el.offsetHeight; // force reflow

      requestAnimationFrame(() => el.style[sizeProperty] = '0');
    },
    onAfterLeave,
    onLeaveCancelled: onAfterLeave
  };
  function onAfterLeave(el) {
    if (expandedParentClass && el._parent) {
      el._parent.classList.remove(expandedParentClass);
    }
    resetStyles(el);
  }
  function resetStyles(el) {
    if (!el._initialStyle) return;
    const size = el._initialStyle[sizeProperty];
    el.style.overflow = el._initialStyle.overflow;
    if (size != null) el.style[sizeProperty] = size;
    delete el._initialStyle;
  }
}

// Utilities
const {Transition: Transition$4,mergeProps:_mergeProps$15,createVNode:_createVNode$2h} = await importShared('vue');
const makeVDialogTransitionProps = propsFactory({
  target: [Object, Array]
}, 'v-dialog-transition');
const saved = new WeakMap();
const VDialogTransition = genericComponent()({
  name: 'VDialogTransition',
  props: makeVDialogTransitionProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const functions = {
      onBeforeEnter(el) {
        el.style.pointerEvents = 'none';
        el.style.visibility = 'hidden';
      },
      async onEnter(el, done) {
        await new Promise(resolve => requestAnimationFrame(resolve));
        await new Promise(resolve => requestAnimationFrame(resolve));
        el.style.visibility = '';
        const dimensions = getDimensions(props.target, el);
        const {
          x,
          y,
          sx,
          sy,
          speed
        } = dimensions;
        saved.set(el, dimensions);
        const animation = animate(el, [{
          transform: `translate(${x}px, ${y}px) scale(${sx}, ${sy})`,
          opacity: 0
        }, {}], {
          duration: 225 * speed,
          easing: deceleratedEasing
        });
        getChildren(el)?.forEach(el => {
          animate(el, [{
            opacity: 0
          }, {
            opacity: 0,
            offset: 0.33
          }, {}], {
            duration: 225 * 2 * speed,
            easing: standardEasing
          });
        });
        animation.finished.then(() => done());
      },
      onAfterEnter(el) {
        el.style.removeProperty('pointer-events');
      },
      onBeforeLeave(el) {
        el.style.pointerEvents = 'none';
      },
      async onLeave(el, done) {
        await new Promise(resolve => requestAnimationFrame(resolve));
        let dimensions;
        if (!saved.has(el) || Array.isArray(props.target) || props.target.offsetParent || props.target.getClientRects().length) {
          dimensions = getDimensions(props.target, el);
        } else {
          dimensions = saved.get(el);
        }
        const {
          x,
          y,
          sx,
          sy,
          speed
        } = dimensions;
        const animation = animate(el, [{}, {
          transform: `translate(${x}px, ${y}px) scale(${sx}, ${sy})`,
          opacity: 0
        }], {
          duration: 125 * speed,
          easing: acceleratedEasing
        });
        animation.finished.then(() => done());
        getChildren(el)?.forEach(el => {
          animate(el, [{}, {
            opacity: 0,
            offset: 0.2
          }, {
            opacity: 0
          }], {
            duration: 125 * 2 * speed,
            easing: standardEasing
          });
        });
      },
      onAfterLeave(el) {
        el.style.removeProperty('pointer-events');
      }
    };
    return () => {
      return props.target ? _createVNode$2h(Transition$4, _mergeProps$15({
        "name": "dialog-transition"
      }, functions, {
        "css": false
      }), slots) : _createVNode$2h(Transition$4, {
        "name": "dialog-transition"
      }, slots);
    };
  }
});

/** Animatable children (card, sheet, list) */
function getChildren(el) {
  const els = el.querySelector(':scope > .v-card, :scope > .v-sheet, :scope > .v-list')?.children;
  return els && [...els];
}
function getDimensions(target, el) {
  const targetBox = getTargetBox(target);
  const elBox = nullifyTransforms(el);
  const [originX, originY] = getComputedStyle(el).transformOrigin.split(' ').map(v => parseFloat(v));
  const [anchorSide, anchorOffset] = getComputedStyle(el).getPropertyValue('--v-overlay-anchor-origin').split(' ');
  let offsetX = targetBox.left + targetBox.width / 2;
  if (anchorSide === 'left' || anchorOffset === 'left') {
    offsetX -= targetBox.width / 2;
  } else if (anchorSide === 'right' || anchorOffset === 'right') {
    offsetX += targetBox.width / 2;
  }
  let offsetY = targetBox.top + targetBox.height / 2;
  if (anchorSide === 'top' || anchorOffset === 'top') {
    offsetY -= targetBox.height / 2;
  } else if (anchorSide === 'bottom' || anchorOffset === 'bottom') {
    offsetY += targetBox.height / 2;
  }
  const tsx = targetBox.width / elBox.width;
  const tsy = targetBox.height / elBox.height;
  const maxs = Math.max(1, tsx, tsy);
  const sx = tsx / maxs || 0;
  const sy = tsy / maxs || 0;

  // Animate elements larger than 12% of the screen area up to 1.5x slower
  const asa = elBox.width * elBox.height / (window.innerWidth * window.innerHeight);
  const speed = asa > 0.12 ? Math.min(1.5, (asa - 0.12) * 10 + 1) : 1;
  return {
    x: offsetX - (originX + elBox.left),
    y: offsetY - (originY + elBox.top),
    sx,
    sy,
    speed
  };
}

const VFabTransition = createCssTransition('fab-transition', 'center center', 'out-in');

// Generic transitions
const VDialogBottomTransition = createCssTransition('dialog-bottom-transition');
const VDialogTopTransition = createCssTransition('dialog-top-transition');
const VFadeTransition = createCssTransition('fade-transition');
const VScaleTransition = createCssTransition('scale-transition');
const VScrollXTransition = createCssTransition('scroll-x-transition');
const VScrollXReverseTransition = createCssTransition('scroll-x-reverse-transition');
const VScrollYTransition = createCssTransition('scroll-y-transition');
const VScrollYReverseTransition = createCssTransition('scroll-y-reverse-transition');
const VSlideXTransition = createCssTransition('slide-x-transition');
const VSlideXReverseTransition = createCssTransition('slide-x-reverse-transition');
const VSlideYTransition = createCssTransition('slide-y-transition');
const VSlideYReverseTransition = createCssTransition('slide-y-reverse-transition');

// Javascript transitions
const VExpandTransition = createJavascriptTransition('expand-transition', ExpandTransitionGenerator());
const VExpandXTransition = createJavascriptTransition('expand-x-transition', ExpandTransitionGenerator('', true));

const {toRefs: toRefs$4} = await importShared('vue');
const makeVDefaultsProviderProps = propsFactory({
  defaults: Object,
  disabled: Boolean,
  reset: [Number, String],
  root: [Boolean, String],
  scoped: Boolean
}, 'VDefaultsProvider');
const VDefaultsProvider = genericComponent(false)({
  name: 'VDefaultsProvider',
  props: makeVDefaultsProviderProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      defaults,
      disabled,
      reset,
      root,
      scoped
    } = toRefs$4(props);
    provideDefaults(defaults, {
      reset,
      root,
      scoped,
      disabled
    });
    return () => slots.default?.();
  }
});

// Utilities
const {computed: computed$1H} = await importShared('vue');
// Composables
const makeDimensionProps = propsFactory({
  height: [Number, String],
  maxHeight: [Number, String],
  maxWidth: [Number, String],
  minHeight: [Number, String],
  minWidth: [Number, String],
  width: [Number, String]
}, 'dimension');
function useDimension(props) {
  const dimensionStyles = computed$1H(() => {
    const styles = {};
    const height = convertToUnit(props.height);
    const maxHeight = convertToUnit(props.maxHeight);
    const maxWidth = convertToUnit(props.maxWidth);
    const minHeight = convertToUnit(props.minHeight);
    const minWidth = convertToUnit(props.minWidth);
    const width = convertToUnit(props.width);
    if (height != null) styles.height = height;
    if (maxHeight != null) styles.maxHeight = maxHeight;
    if (maxWidth != null) styles.maxWidth = maxWidth;
    if (minHeight != null) styles.minHeight = minHeight;
    if (minWidth != null) styles.minWidth = minWidth;
    if (width != null) styles.width = width;
    return styles;
  });
  return {
    dimensionStyles
  };
}

const {createVNode:_createVNode$2g} = await importShared('vue');
const {computed: computed$1G} = await importShared('vue');
function useAspectStyles(props) {
  return {
    aspectStyles: computed$1G(() => {
      const ratio = Number(props.aspectRatio);
      return ratio ? {
        paddingBottom: String(1 / ratio * 100) + '%'
      } : undefined;
    })
  };
}
const makeVResponsiveProps = propsFactory({
  aspectRatio: [String, Number],
  contentClass: null,
  inline: Boolean,
  ...makeComponentProps(),
  ...makeDimensionProps()
}, 'VResponsive');
const VResponsive = genericComponent()({
  name: 'VResponsive',
  props: makeVResponsiveProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      aspectStyles
    } = useAspectStyles(props);
    const {
      dimensionStyles
    } = useDimension(props);
    useRender(() => _createVNode$2g("div", {
      "class": ['v-responsive', {
        'v-responsive--inline': props.inline
      }, props.class],
      "style": [dimensionStyles.value, props.style]
    }, [_createVNode$2g("div", {
      "class": "v-responsive__sizer",
      "style": aspectStyles.value
    }, null), slots.additional?.(), slots.default && _createVNode$2g("div", {
      "class": ['v-responsive__content', props.contentClass]
    }, [slots.default()])]));
    return {};
  }
});

// Utilities
const {toValue: toValue$3} = await importShared('vue');
// Composables
function useColor(colors) {
  return destructComputed(() => {
    const _colors = toValue$3(colors);
    const classes = [];
    const styles = {};
    if (_colors.background) {
      if (isCssColor(_colors.background)) {
        styles.backgroundColor = _colors.background;
        if (!_colors.text && isParsableColor(_colors.background)) {
          const backgroundColor = parseColor(_colors.background);
          if (backgroundColor.a == null || backgroundColor.a === 1) {
            const textColor = getForeground(backgroundColor);
            styles.color = textColor;
            styles.caretColor = textColor;
          }
        }
      } else {
        classes.push(`bg-${_colors.background}`);
      }
    }
    if (_colors.text) {
      if (isCssColor(_colors.text)) {
        styles.color = _colors.text;
        styles.caretColor = _colors.text;
      } else {
        classes.push(`text-${_colors.text}`);
      }
    }
    return {
      colorClasses: classes,
      colorStyles: styles
    };
  });
}
function useTextColor(color) {
  const {
    colorClasses: textColorClasses,
    colorStyles: textColorStyles
  } = useColor(() => ({
    text: toValue$3(color)
  }));
  return {
    textColorClasses,
    textColorStyles
  };
}
function useBackgroundColor(color) {
  const {
    colorClasses: backgroundColorClasses,
    colorStyles: backgroundColorStyles
  } = useColor(() => ({
    background: toValue$3(color)
  }));
  return {
    backgroundColorClasses,
    backgroundColorStyles
  };
}

// Utilities
const {computed: computed$1F,isRef: isRef$1} = await importShared('vue');
// Composables
const makeRoundedProps = propsFactory({
  rounded: {
    type: [Boolean, Number, String],
    default: undefined
  },
  tile: Boolean
}, 'rounded');
function useRounded(props) {
  let name = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : getCurrentInstanceName();
  const roundedClasses = computed$1F(() => {
    const rounded = isRef$1(props) ? props.value : props.rounded;
    const tile = isRef$1(props) ? props.value : props.tile;
    const classes = [];
    if (rounded === true || rounded === '') {
      classes.push(`${name}--rounded`);
    } else if (typeof rounded === 'string' || rounded === 0) {
      for (const value of String(rounded).split(' ')) {
        classes.push(`rounded-${value}`);
      }
    } else if (tile || rounded === false) {
      classes.push('rounded-0');
    }
    return classes;
  });
  return {
    roundedClasses
  };
}

// Utilities
const {h: h$3,mergeProps: mergeProps$c,Transition: Transition$3,TransitionGroup} = await importShared('vue');
const makeTransitionProps = propsFactory({
  transition: {
    type: null,
    default: 'fade-transition',
    validator: val => val !== true
  }
}, 'transition');
const MaybeTransition = (props, _ref) => {
  let {
    slots
  } = _ref;
  const {
    transition,
    disabled,
    group,
    ...rest
  } = props;
  const {
    component = group ? TransitionGroup : Transition$3,
    ...customProps
  } = isObject(transition) ? transition : {};
  let transitionProps;
  if (isObject(transition)) {
    transitionProps = mergeProps$c(customProps, JSON.parse(JSON.stringify({
      disabled,
      group
    })), rest);
  } else {
    transitionProps = mergeProps$c({
      name: disabled || !transition ? '' : transition
    }, rest);
  }
  return h$3(component, transitionProps, slots);
};

// Utilities
function mounted$5(el, binding) {
  if (!SUPPORTS_INTERSECTION) return;
  const modifiers = binding.modifiers || {};
  const value = binding.value;
  const {
    handler,
    options
  } = typeof value === 'object' ? value : {
    handler: value,
    options: {}
  };
  const observer = new IntersectionObserver(function () {
    let entries = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];
    let observer = arguments.length > 1 ? arguments[1] : undefined;
    const _observe = el._observe?.[binding.instance.$.uid];
    if (!_observe) return; // Just in case, should never fire

    const isIntersecting = entries.some(entry => entry.isIntersecting);

    // If is not quiet or has already been
    // initted, invoke the user callback
    if (handler && (!modifiers.quiet || _observe.init) && (!modifiers.once || isIntersecting || _observe.init)) {
      handler(isIntersecting, entries, observer);
    }
    if (isIntersecting && modifiers.once) unmounted$5(el, binding);else _observe.init = true;
  }, options);
  el._observe = Object(el._observe);
  el._observe[binding.instance.$.uid] = {
    init: false,
    observer
  };
  observer.observe(el);
}
function unmounted$5(el, binding) {
  const observe = el._observe?.[binding.instance.$.uid];
  if (!observe) return;
  observe.observer.unobserve(el);
  delete el._observe[binding.instance.$.uid];
}
const Intersect = {
  mounted: mounted$5,
  unmounted: unmounted$5
};

const {createVNode:_createVNode$2f,Fragment:_Fragment$E,resolveDirective:_resolveDirective$c,mergeProps:_mergeProps$14,withDirectives:_withDirectives$j} = await importShared('vue');
const {computed: computed$1E,nextTick: nextTick$q,onBeforeMount: onBeforeMount$4,onBeforeUnmount: onBeforeUnmount$c,ref: ref$O,shallowRef: shallowRef$L,toRef: toRef$10,vShow,watch: watch$F,withDirectives: withDirectives$1} = await importShared('vue');
// not intended for public use, this is passed in by vuetify-loader
const makeVImgProps = propsFactory({
  absolute: Boolean,
  alt: String,
  cover: Boolean,
  color: String,
  draggable: {
    type: [Boolean, String],
    default: undefined
  },
  eager: Boolean,
  gradient: String,
  lazySrc: String,
  options: {
    type: Object,
    // For more information on types, navigate to:
    // https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API
    default: () => ({
      root: undefined,
      rootMargin: undefined,
      threshold: undefined
    })
  },
  sizes: String,
  src: {
    type: [String, Object],
    default: ''
  },
  crossorigin: String,
  referrerpolicy: String,
  srcset: String,
  position: String,
  ...makeVResponsiveProps(),
  ...makeComponentProps(),
  ...makeRoundedProps(),
  ...makeTransitionProps()
}, 'VImg');
const VImg = genericComponent()({
  name: 'VImg',
  directives: {
    intersect: Intersect
  },
  props: makeVImgProps(),
  emits: {
    loadstart: value => true,
    load: value => true,
    error: value => true
  },
  setup(props, _ref) {
    let {
      emit,
      slots
    } = _ref;
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.color);
    const {
      roundedClasses
    } = useRounded(props);
    const vm = getCurrentInstance('VImg');
    const currentSrc = shallowRef$L(''); // Set from srcset
    const image = ref$O();
    const state = shallowRef$L(props.eager ? 'loading' : 'idle');
    const naturalWidth = shallowRef$L();
    const naturalHeight = shallowRef$L();
    const normalisedSrc = computed$1E(() => {
      return props.src && typeof props.src === 'object' ? {
        src: props.src.src,
        srcset: props.srcset || props.src.srcset,
        lazySrc: props.lazySrc || props.src.lazySrc,
        aspect: Number(props.aspectRatio || props.src.aspect || 0)
      } : {
        src: props.src,
        srcset: props.srcset,
        lazySrc: props.lazySrc,
        aspect: Number(props.aspectRatio || 0)
      };
    });
    const aspectRatio = computed$1E(() => {
      return normalisedSrc.value.aspect || naturalWidth.value / naturalHeight.value || 0;
    });
    watch$F(() => props.src, () => {
      init(state.value !== 'idle');
    });
    watch$F(aspectRatio, (val, oldVal) => {
      if (!val && oldVal && image.value) {
        pollForSize(image.value);
      }
    });

    // TODO: getSrc when window width changes

    onBeforeMount$4(() => init());
    function init(isIntersecting) {
      if (props.eager && isIntersecting) return;
      if (SUPPORTS_INTERSECTION && !isIntersecting && !props.eager) return;
      state.value = 'loading';
      if (normalisedSrc.value.lazySrc) {
        const lazyImg = new Image();
        lazyImg.src = normalisedSrc.value.lazySrc;
        pollForSize(lazyImg, null);
      }
      if (!normalisedSrc.value.src) return;
      nextTick$q(() => {
        emit('loadstart', image.value?.currentSrc || normalisedSrc.value.src);
        setTimeout(() => {
          if (vm.isUnmounted) return;
          if (image.value?.complete) {
            if (!image.value.naturalWidth) {
              onError();
            }
            if (state.value === 'error') return;
            if (!aspectRatio.value) pollForSize(image.value, null);
            if (state.value === 'loading') onLoad();
          } else {
            if (!aspectRatio.value) pollForSize(image.value);
            getSrc();
          }
        });
      });
    }
    function onLoad() {
      if (vm.isUnmounted) return;
      getSrc();
      pollForSize(image.value);
      state.value = 'loaded';
      emit('load', image.value?.currentSrc || normalisedSrc.value.src);
    }
    function onError() {
      if (vm.isUnmounted) return;
      state.value = 'error';
      emit('error', image.value?.currentSrc || normalisedSrc.value.src);
    }
    function getSrc() {
      const img = image.value;
      if (img) currentSrc.value = img.currentSrc || img.src;
    }
    let timer = -1;
    onBeforeUnmount$c(() => {
      clearTimeout(timer);
    });
    function pollForSize(img) {
      let timeout = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 100;
      const poll = () => {
        clearTimeout(timer);
        if (vm.isUnmounted) return;
        const {
          naturalHeight: imgHeight,
          naturalWidth: imgWidth
        } = img;
        if (imgHeight || imgWidth) {
          naturalWidth.value = imgWidth;
          naturalHeight.value = imgHeight;
        } else if (!img.complete && state.value === 'loading' && timeout != null) {
          timer = window.setTimeout(poll, timeout);
        } else if (img.currentSrc.endsWith('.svg') || img.currentSrc.startsWith('data:image/svg+xml')) {
          naturalWidth.value = 1;
          naturalHeight.value = 1;
        }
      };
      poll();
    }
    const containClasses = toRef$10(() => ({
      'v-img__img--cover': props.cover,
      'v-img__img--contain': !props.cover
    }));
    const __image = () => {
      if (!normalisedSrc.value.src || state.value === 'idle') return null;
      const img = _createVNode$2f("img", {
        "class": ['v-img__img', containClasses.value],
        "style": {
          objectPosition: props.position
        },
        "crossorigin": props.crossorigin,
        "src": normalisedSrc.value.src,
        "srcset": normalisedSrc.value.srcset,
        "alt": props.alt,
        "referrerpolicy": props.referrerpolicy,
        "draggable": props.draggable,
        "sizes": props.sizes,
        "ref": image,
        "onLoad": onLoad,
        "onError": onError
      }, null);
      const sources = slots.sources?.();
      return _createVNode$2f(MaybeTransition, {
        "transition": props.transition,
        "appear": true
      }, {
        default: () => [withDirectives$1(sources ? _createVNode$2f("picture", {
          "class": "v-img__picture"
        }, [sources, img]) : img, [[vShow, state.value === 'loaded']])]
      });
    };
    const __preloadImage = () => _createVNode$2f(MaybeTransition, {
      "transition": props.transition
    }, {
      default: () => [normalisedSrc.value.lazySrc && state.value !== 'loaded' && _createVNode$2f("img", {
        "class": ['v-img__img', 'v-img__img--preload', containClasses.value],
        "style": {
          objectPosition: props.position
        },
        "crossorigin": props.crossorigin,
        "src": normalisedSrc.value.lazySrc,
        "alt": props.alt,
        "referrerpolicy": props.referrerpolicy,
        "draggable": props.draggable
      }, null)]
    });
    const __placeholder = () => {
      if (!slots.placeholder) return null;
      return _createVNode$2f(MaybeTransition, {
        "transition": props.transition,
        "appear": true
      }, {
        default: () => [(state.value === 'loading' || state.value === 'error' && !slots.error) && _createVNode$2f("div", {
          "class": "v-img__placeholder"
        }, [slots.placeholder()])]
      });
    };
    const __error = () => {
      if (!slots.error) return null;
      return _createVNode$2f(MaybeTransition, {
        "transition": props.transition,
        "appear": true
      }, {
        default: () => [state.value === 'error' && _createVNode$2f("div", {
          "class": "v-img__error"
        }, [slots.error()])]
      });
    };
    const __gradient = () => {
      if (!props.gradient) return null;
      return _createVNode$2f("div", {
        "class": "v-img__gradient",
        "style": {
          backgroundImage: `linear-gradient(${props.gradient})`
        }
      }, null);
    };
    const isBooted = shallowRef$L(false);
    {
      const stop = watch$F(aspectRatio, val => {
        if (val) {
          // Doesn't work with nextTick, idk why
          requestAnimationFrame(() => {
            requestAnimationFrame(() => {
              isBooted.value = true;
            });
          });
          stop();
        }
      });
    }
    useRender(() => {
      const responsiveProps = VResponsive.filterProps(props);
      return _withDirectives$j(_createVNode$2f(VResponsive, _mergeProps$14({
        "class": ['v-img', {
          'v-img--absolute': props.absolute,
          'v-img--booting': !isBooted.value
        }, backgroundColorClasses.value, roundedClasses.value, props.class],
        "style": [{
          width: convertToUnit(props.width === 'auto' ? naturalWidth.value : props.width)
        }, backgroundColorStyles.value, props.style]
      }, responsiveProps, {
        "aspectRatio": aspectRatio.value,
        "aria-label": props.alt,
        "role": props.alt ? 'img' : undefined
      }), {
        additional: () => _createVNode$2f(_Fragment$E, null, [_createVNode$2f(__image, null, null), _createVNode$2f(__preloadImage, null, null), _createVNode$2f(__gradient, null, null), _createVNode$2f(__placeholder, null, null), _createVNode$2f(__error, null, null)]),
        default: slots.default
      }), [[_resolveDirective$c("intersect"), {
        handler: init,
        options: props.options
      }, null, {
        once: true
      }]]);
    });
    return {
      currentSrc,
      image,
      state,
      naturalWidth,
      naturalHeight
    };
  }
});

// Utilities
const {computed: computed$1D} = await importShared('vue');
// Composables
const makeBorderProps = propsFactory({
  border: [Boolean, Number, String]
}, 'border');
function useBorder(props) {
  let name = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : getCurrentInstanceName();
  const borderClasses = computed$1D(() => {
    const border = props.border;
    if (border === true || border === '') {
      return `${name}--border`;
    } else if (typeof border === 'string' || border === 0) {
      return String(border).split(' ').map(v => `border-${v}`);
    }
    return [];
  });
  return {
    borderClasses
  };
}

// Utilities
const {isRef,toRef: toRef$$} = await importShared('vue');
// Composables
const makeElevationProps = propsFactory({
  elevation: {
    type: [Number, String],
    validator(v) {
      const value = parseInt(v);
      return !isNaN(value) && value >= 0 &&
      // Material Design has a maximum elevation of 24
      // https://material.io/design/environment/elevation.html#default-elevations
      value <= 24;
    }
  }
}, 'elevation');
function useElevation(props) {
  const elevationClasses = toRef$$(() => {
    const elevation = isRef(props) ? props.value : props.elevation;
    if (elevation == null) return [];
    return [`elevation-${elevation}`];
  });
  return {
    elevationClasses
  };
}

const {createVNode:_createVNode$2e} = await importShared('vue');
const {computed: computed$1C,shallowRef: shallowRef$K} = await importShared('vue');
const allowedDensities$1 = [null, 'prominent', 'default', 'comfortable', 'compact'];
const makeVToolbarProps = propsFactory({
  absolute: Boolean,
  collapse: Boolean,
  color: String,
  density: {
    type: String,
    default: 'default',
    validator: v => allowedDensities$1.includes(v)
  },
  extended: Boolean,
  extensionHeight: {
    type: [Number, String],
    default: 48
  },
  flat: Boolean,
  floating: Boolean,
  height: {
    type: [Number, String],
    default: 64
  },
  image: String,
  title: String,
  ...makeBorderProps(),
  ...makeComponentProps(),
  ...makeElevationProps(),
  ...makeRoundedProps(),
  ...makeTagProps({
    tag: 'header'
  }),
  ...makeThemeProps()
}, 'VToolbar');
const VToolbar = genericComponent()({
  name: 'VToolbar',
  props: makeVToolbarProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.color);
    const {
      borderClasses
    } = useBorder(props);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      roundedClasses
    } = useRounded(props);
    const {
      themeClasses
    } = provideTheme(props);
    const {
      rtlClasses
    } = useRtl();
    const isExtended = shallowRef$K(!!(props.extended || slots.extension?.()));
    const contentHeight = computed$1C(() => parseInt(Number(props.height) + (props.density === 'prominent' ? Number(props.height) : 0) - (props.density === 'comfortable' ? 8 : 0) - (props.density === 'compact' ? 16 : 0), 10));
    const extensionHeight = computed$1C(() => isExtended.value ? parseInt(Number(props.extensionHeight) + (props.density === 'prominent' ? Number(props.extensionHeight) : 0) - (props.density === 'comfortable' ? 4 : 0) - (props.density === 'compact' ? 8 : 0), 10) : 0);
    provideDefaults({
      VBtn: {
        variant: 'text'
      }
    });
    useRender(() => {
      const hasTitle = !!(props.title || slots.title);
      const hasImage = !!(slots.image || props.image);
      const extension = slots.extension?.();
      isExtended.value = !!(props.extended || extension);
      return _createVNode$2e(props.tag, {
        "class": ['v-toolbar', {
          'v-toolbar--absolute': props.absolute,
          'v-toolbar--collapse': props.collapse,
          'v-toolbar--flat': props.flat,
          'v-toolbar--floating': props.floating,
          [`v-toolbar--density-${props.density}`]: true
        }, backgroundColorClasses.value, borderClasses.value, elevationClasses.value, roundedClasses.value, themeClasses.value, rtlClasses.value, props.class],
        "style": [backgroundColorStyles.value, props.style]
      }, {
        default: () => [hasImage && _createVNode$2e("div", {
          "key": "image",
          "class": "v-toolbar__image"
        }, [!slots.image ? _createVNode$2e(VImg, {
          "key": "image-img",
          "cover": true,
          "src": props.image
        }, null) : _createVNode$2e(VDefaultsProvider, {
          "key": "image-defaults",
          "disabled": !props.image,
          "defaults": {
            VImg: {
              cover: true,
              src: props.image
            }
          }
        }, slots.image)]), _createVNode$2e(VDefaultsProvider, {
          "defaults": {
            VTabs: {
              height: convertToUnit(contentHeight.value)
            }
          }
        }, {
          default: () => [_createVNode$2e("div", {
            "class": "v-toolbar__content",
            "style": {
              height: convertToUnit(contentHeight.value)
            }
          }, [slots.prepend && _createVNode$2e("div", {
            "class": "v-toolbar__prepend"
          }, [slots.prepend?.()]), hasTitle && _createVNode$2e(VToolbarTitle, {
            "key": "title",
            "text": props.title
          }, {
            text: slots.title
          }), slots.default?.(), slots.append && _createVNode$2e("div", {
            "class": "v-toolbar__append"
          }, [slots.append?.()])])]
        }), _createVNode$2e(VDefaultsProvider, {
          "defaults": {
            VTabs: {
              height: convertToUnit(extensionHeight.value)
            }
          }
        }, {
          default: () => [_createVNode$2e(VExpandTransition, null, {
            default: () => [isExtended.value && _createVNode$2e("div", {
              "class": "v-toolbar__extension",
              "style": {
                height: convertToUnit(extensionHeight.value)
              }
            }, [extension])]
          })]
        })]
      });
    });
    return {
      contentHeight,
      extensionHeight
    };
  }
});

// Utilities
const {computed: computed$1B,onBeforeUnmount: onBeforeUnmount$b,onMounted: onMounted$e,ref: ref$N,shallowRef: shallowRef$J,watch: watch$E} = await importShared('vue');
// Composables
const makeScrollProps = propsFactory({
  scrollTarget: {
    type: String
  },
  scrollThreshold: {
    type: [String, Number],
    default: 300
  }
}, 'scroll');
function useScroll(props) {
  let args = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  const {
    canScroll
  } = args;
  let previousScroll = 0;
  let previousScrollHeight = 0;
  const target = ref$N(null);
  const currentScroll = shallowRef$J(0);
  const savedScroll = shallowRef$J(0);
  const currentThreshold = shallowRef$J(0);
  const isScrollActive = shallowRef$J(false);
  const isScrollingUp = shallowRef$J(false);
  const scrollThreshold = computed$1B(() => {
    return Number(props.scrollThreshold);
  });

  /**
   * 1: at top
   * 0: at threshold
   */
  const scrollRatio = computed$1B(() => {
    return clamp((scrollThreshold.value - currentScroll.value) / scrollThreshold.value || 0);
  });
  const onScroll = () => {
    const targetEl = target.value;
    if (!targetEl || canScroll && !canScroll.value) return;
    previousScroll = currentScroll.value;
    currentScroll.value = 'window' in targetEl ? targetEl.pageYOffset : targetEl.scrollTop;
    const currentScrollHeight = targetEl instanceof Window ? document.documentElement.scrollHeight : targetEl.scrollHeight;
    if (previousScrollHeight !== currentScrollHeight) {
      previousScrollHeight = currentScrollHeight;
      return;
    }
    isScrollingUp.value = currentScroll.value < previousScroll;
    currentThreshold.value = Math.abs(currentScroll.value - scrollThreshold.value);
  };
  watch$E(isScrollingUp, () => {
    savedScroll.value = savedScroll.value || currentScroll.value;
  });
  watch$E(isScrollActive, () => {
    savedScroll.value = 0;
  });
  onMounted$e(() => {
    watch$E(() => props.scrollTarget, scrollTarget => {
      const newTarget = scrollTarget ? document.querySelector(scrollTarget) : window;
      if (!newTarget) {
        consoleWarn(`Unable to locate element with identifier ${scrollTarget}`);
        return;
      }
      if (newTarget === target.value) return;
      target.value?.removeEventListener('scroll', onScroll);
      target.value = newTarget;
      target.value.addEventListener('scroll', onScroll, {
        passive: true
      });
    }, {
      immediate: true
    });
  });
  onBeforeUnmount$b(() => {
    target.value?.removeEventListener('scroll', onScroll);
  });

  // Do we need this? If yes - seems that
  // there's no need to expose onScroll
  canScroll && watch$E(canScroll, onScroll, {
    immediate: true
  });
  return {
    scrollThreshold,
    currentScroll,
    currentThreshold,
    isScrollActive,
    scrollRatio,
    // required only for testing
    // probably can be removed
    // later (2 chars chlng)
    isScrollingUp,
    savedScroll
  };
}

// Utilities
const {onMounted: onMounted$d,readonly: readonly$2,shallowRef: shallowRef$I,toRef: toRef$_} = await importShared('vue');


// Composables
function useSsrBoot() {
  const isBooted = shallowRef$I(false);
  onMounted$d(() => {
    window.requestAnimationFrame(() => {
      isBooted.value = true;
    });
  });
  const ssrBootStyles = toRef$_(() => !isBooted.value ? {
    transition: 'none !important'
  } : undefined);
  return {
    ssrBootStyles,
    isBooted: readonly$2(isBooted)
  };
}

const {mergeProps:_mergeProps$13,createVNode:_createVNode$2d} = await importShared('vue');
const {computed: computed$1A,ref: ref$M,shallowRef: shallowRef$H,toRef: toRef$Z,watchEffect: watchEffect$i} = await importShared('vue');
const makeVAppBarProps = propsFactory({
  scrollBehavior: String,
  modelValue: {
    type: Boolean,
    default: true
  },
  location: {
    type: String,
    default: 'top',
    validator: value => ['top', 'bottom'].includes(value)
  },
  ...makeVToolbarProps(),
  ...makeLayoutItemProps(),
  ...makeScrollProps(),
  height: {
    type: [Number, String],
    default: 64
  }
}, 'VAppBar');
const VAppBar = genericComponent()({
  name: 'VAppBar',
  props: makeVAppBarProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const vToolbarRef = ref$M();
    const isActive = useProxiedModel(props, 'modelValue');
    const scrollBehavior = computed$1A(() => {
      const behavior = new Set(props.scrollBehavior?.split(' ') ?? []);
      return {
        hide: behavior.has('hide'),
        fullyHide: behavior.has('fully-hide'),
        inverted: behavior.has('inverted'),
        collapse: behavior.has('collapse'),
        elevate: behavior.has('elevate'),
        fadeImage: behavior.has('fade-image')
        // shrink: behavior.has('shrink'),
      };
    });
    const canScroll = computed$1A(() => {
      const behavior = scrollBehavior.value;
      return behavior.hide || behavior.fullyHide || behavior.inverted || behavior.collapse || behavior.elevate || behavior.fadeImage ||
      // behavior.shrink ||
      !isActive.value;
    });
    const {
      currentScroll,
      scrollThreshold,
      isScrollingUp,
      scrollRatio
    } = useScroll(props, {
      canScroll
    });
    const canHide = toRef$Z(() => scrollBehavior.value.hide || scrollBehavior.value.fullyHide);
    const isCollapsed = computed$1A(() => props.collapse || scrollBehavior.value.collapse && (scrollBehavior.value.inverted ? scrollRatio.value > 0 : scrollRatio.value === 0));
    const isFlat = computed$1A(() => props.flat || scrollBehavior.value.fullyHide && !isActive.value || scrollBehavior.value.elevate && (scrollBehavior.value.inverted ? currentScroll.value > 0 : currentScroll.value === 0));
    const opacity = computed$1A(() => scrollBehavior.value.fadeImage ? scrollBehavior.value.inverted ? 1 - scrollRatio.value : scrollRatio.value : undefined);
    const height = computed$1A(() => {
      if (scrollBehavior.value.hide && scrollBehavior.value.inverted) return 0;
      const height = vToolbarRef.value?.contentHeight ?? 0;
      const extensionHeight = vToolbarRef.value?.extensionHeight ?? 0;
      if (!canHide.value) return height + extensionHeight;
      return currentScroll.value < scrollThreshold.value || scrollBehavior.value.fullyHide ? height + extensionHeight : height;
    });
    useToggleScope(() => !!props.scrollBehavior, () => {
      watchEffect$i(() => {
        if (canHide.value) {
          if (scrollBehavior.value.inverted) {
            isActive.value = currentScroll.value > scrollThreshold.value;
          } else {
            isActive.value = isScrollingUp.value || currentScroll.value < scrollThreshold.value;
          }
        } else {
          isActive.value = true;
        }
      });
    });
    const {
      ssrBootStyles
    } = useSsrBoot();
    const {
      layoutItemStyles
    } = useLayoutItem({
      id: props.name,
      order: computed$1A(() => parseInt(props.order, 10)),
      position: toRef$Z(() => props.location),
      layoutSize: height,
      elementSize: shallowRef$H(undefined),
      active: isActive,
      absolute: toRef$Z(() => props.absolute)
    });
    useRender(() => {
      const toolbarProps = VToolbar.filterProps(props);
      return _createVNode$2d(VToolbar, _mergeProps$13({
        "ref": vToolbarRef,
        "class": ['v-app-bar', {
          'v-app-bar--bottom': props.location === 'bottom'
        }, props.class],
        "style": [{
          ...layoutItemStyles.value,
          '--v-toolbar-image-opacity': opacity.value,
          height: undefined,
          ...ssrBootStyles.value
        }, props.style]
      }, toolbarProps, {
        "collapse": isCollapsed.value,
        "flat": isFlat.value
      }), slots);
    });
    return {};
  }
});

// Utilities
const {toRef: toRef$Y} = await importShared('vue');
const allowedDensities = [null, 'default', 'comfortable', 'compact'];

// typeof allowedDensities[number] evaluates to any
// when generating api types for whatever reason.

// Composables
const makeDensityProps = propsFactory({
  density: {
    type: String,
    default: 'default',
    validator: v => allowedDensities.includes(v)
  }
}, 'density');
function useDensity(props) {
  let name = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : getCurrentInstanceName();
  const densityClasses = toRef$Y(() => {
    return `${name}--density-${props.density}`;
  });
  return {
    densityClasses
  };
}

const {Fragment:_Fragment$D,createVNode:_createVNode$2c} = await importShared('vue');
const {toRef: toRef$X,toValue: toValue$2} = await importShared('vue');
const allowedVariants$2 = ['elevated', 'flat', 'tonal', 'outlined', 'text', 'plain'];
function genOverlays(isClickable, name) {
  return _createVNode$2c(_Fragment$D, null, [isClickable && _createVNode$2c("span", {
    "key": "overlay",
    "class": `${name}__overlay`
  }, null), _createVNode$2c("span", {
    "key": "underlay",
    "class": `${name}__underlay`
  }, null)]);
}
const makeVariantProps = propsFactory({
  color: String,
  variant: {
    type: String,
    default: 'elevated',
    validator: v => allowedVariants$2.includes(v)
  }
}, 'variant');
function useVariant(props) {
  let name = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : getCurrentInstanceName();
  const variantClasses = toRef$X(() => {
    const {
      variant
    } = toValue$2(props);
    return `${name}--variant-${variant}`;
  });
  const {
    colorClasses,
    colorStyles
  } = useColor(() => {
    const {
      variant,
      color
    } = toValue$2(props);
    return {
      [['elevated', 'flat'].includes(variant) ? 'background' : 'text']: color
    };
  });
  return {
    colorClasses,
    colorStyles,
    variantClasses
  };
}

const {createVNode:_createVNode$2b} = await importShared('vue');
const {toRef: toRef$W} = await importShared('vue');
const makeVBtnGroupProps = propsFactory({
  baseColor: String,
  divided: Boolean,
  ...makeBorderProps(),
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeElevationProps(),
  ...makeRoundedProps(),
  ...makeTagProps(),
  ...makeThemeProps(),
  ...makeVariantProps()
}, 'VBtnGroup');
const VBtnGroup = genericComponent()({
  name: 'VBtnGroup',
  props: makeVBtnGroupProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      themeClasses
    } = provideTheme(props);
    const {
      densityClasses
    } = useDensity(props);
    const {
      borderClasses
    } = useBorder(props);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      roundedClasses
    } = useRounded(props);
    provideDefaults({
      VBtn: {
        height: 'auto',
        baseColor: toRef$W(() => props.baseColor),
        color: toRef$W(() => props.color),
        density: toRef$W(() => props.density),
        flat: true,
        variant: toRef$W(() => props.variant)
      }
    });
    useRender(() => {
      return _createVNode$2b(props.tag, {
        "class": ['v-btn-group', {
          'v-btn-group--divided': props.divided
        }, themeClasses.value, borderClasses.value, densityClasses.value, elevationClasses.value, roundedClasses.value, props.class],
        "style": props.style
      }, slots);
    });
  }
});

const {computed: computed$1z,inject: inject$m,onBeforeUnmount: onBeforeUnmount$a,onMounted: onMounted$c,onUpdated,provide: provide$g,reactive: reactive$2,toRef: toRef$V,unref: unref$2,useId: useId$d,watch: watch$D} = await importShared('vue');
const makeGroupProps = propsFactory({
  modelValue: {
    type: null,
    default: undefined
  },
  multiple: Boolean,
  mandatory: [Boolean, String],
  max: Number,
  selectedClass: String,
  disabled: Boolean
}, 'group');
const makeGroupItemProps = propsFactory({
  value: null,
  disabled: Boolean,
  selectedClass: String
}, 'group-item');

// Composables

function useGroupItem(props, injectKey) {
  let required = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : true;
  const vm = getCurrentInstance('useGroupItem');
  if (!vm) {
    throw new Error('[Vuetify] useGroupItem composable must be used inside a component setup function');
  }
  const id = useId$d();
  provide$g(Symbol.for(`${injectKey.description}:id`), id);
  const group = inject$m(injectKey, null);
  if (!group) {
    if (!required) return group;
    throw new Error(`[Vuetify] Could not find useGroup injection with symbol ${injectKey.description}`);
  }
  const value = toRef$V(() => props.value);
  const disabled = computed$1z(() => !!(group.disabled.value || props.disabled));
  group.register({
    id,
    value,
    disabled
  }, vm);
  onBeforeUnmount$a(() => {
    group.unregister(id);
  });
  const isSelected = computed$1z(() => {
    return group.isSelected(id);
  });
  const isFirst = computed$1z(() => {
    return group.items.value[0].id === id;
  });
  const isLast = computed$1z(() => {
    return group.items.value[group.items.value.length - 1].id === id;
  });
  const selectedClass = computed$1z(() => isSelected.value && [group.selectedClass.value, props.selectedClass]);
  watch$D(isSelected, value => {
    vm.emit('group:selected', {
      value
    });
  }, {
    flush: 'sync'
  });
  return {
    id,
    isSelected,
    isFirst,
    isLast,
    toggle: () => group.select(id, !isSelected.value),
    select: value => group.select(id, value),
    selectedClass,
    value,
    disabled,
    group
  };
}
function useGroup(props, injectKey) {
  let isUnmounted = false;
  const items = reactive$2([]);
  const selected = useProxiedModel(props, 'modelValue', [], v => {
    if (v == null) return [];
    return getIds(items, wrapInArray(v));
  }, v => {
    const arr = getValues(items, v);
    return props.multiple ? arr : arr[0];
  });
  const groupVm = getCurrentInstance('useGroup');
  function register(item, vm) {
    // Is there a better way to fix this typing?
    const unwrapped = item;
    const key = Symbol.for(`${injectKey.description}:id`);
    const children = findChildrenWithProvide(key, groupVm?.vnode);
    const index = children.indexOf(vm);
    if (unref$2(unwrapped.value) == null) {
      unwrapped.value = index;
      unwrapped.useIndexAsValue = true;
    }
    if (index > -1) {
      items.splice(index, 0, unwrapped);
    } else {
      items.push(unwrapped);
    }
  }
  function unregister(id) {
    if (isUnmounted) return;

    // TODO: re-evaluate this line's importance in the future
    // should we only modify the model if mandatory is set.
    // selected.value = selected.value.filter(v => v !== id)

    forceMandatoryValue();
    const index = items.findIndex(item => item.id === id);
    items.splice(index, 1);
  }

  // If mandatory and nothing is selected, then select first non-disabled item
  function forceMandatoryValue() {
    const item = items.find(item => !item.disabled);
    if (item && props.mandatory === 'force' && !selected.value.length) {
      selected.value = [item.id];
    }
  }
  onMounted$c(() => {
    forceMandatoryValue();
  });
  onBeforeUnmount$a(() => {
    isUnmounted = true;
  });
  onUpdated(() => {
    // #19655 update the items that use the index as the value.
    for (let i = 0; i < items.length; i++) {
      if (items[i].useIndexAsValue) {
        items[i].value = i;
      }
    }
  });
  function select(id, value) {
    const item = items.find(item => item.id === id);
    if (value && item?.disabled) return;
    if (props.multiple) {
      const internalValue = selected.value.slice();
      const index = internalValue.findIndex(v => v === id);
      const isSelected = ~index;
      value = value ?? !isSelected;

      // We can't remove value if group is
      // mandatory, value already exists,
      // and it is the only value
      if (isSelected && props.mandatory && internalValue.length <= 1) return;

      // We can't add value if it would
      // cause max limit to be exceeded
      if (!isSelected && props.max != null && internalValue.length + 1 > props.max) return;
      if (index < 0 && value) internalValue.push(id);else if (index >= 0 && !value) internalValue.splice(index, 1);
      selected.value = internalValue;
    } else {
      const isSelected = selected.value.includes(id);
      if (props.mandatory && isSelected) return;
      selected.value = value ?? !isSelected ? [id] : [];
    }
  }
  function step(offset) {
    // getting an offset from selected value obviously won't work with multiple values
    if (props.multiple) consoleWarn('This method is not supported when using "multiple" prop');
    if (!selected.value.length) {
      const item = items.find(item => !item.disabled);
      item && (selected.value = [item.id]);
    } else {
      const currentId = selected.value[0];
      const currentIndex = items.findIndex(i => i.id === currentId);
      let newIndex = (currentIndex + offset) % items.length;
      let newItem = items[newIndex];
      while (newItem.disabled && newIndex !== currentIndex) {
        newIndex = (newIndex + offset) % items.length;
        newItem = items[newIndex];
      }
      if (newItem.disabled) return;
      selected.value = [items[newIndex].id];
    }
  }
  const state = {
    register,
    unregister,
    selected,
    select,
    disabled: toRef$V(() => props.disabled),
    prev: () => step(items.length - 1),
    next: () => step(1),
    isSelected: id => selected.value.includes(id),
    selectedClass: toRef$V(() => props.selectedClass),
    items: toRef$V(() => items),
    getItemIndex: value => getItemIndex(items, value)
  };
  provide$g(injectKey, state);
  return state;
}
function getItemIndex(items, value) {
  const ids = getIds(items, [value]);
  if (!ids.length) return -1;
  return items.findIndex(item => item.id === ids[0]);
}
function getIds(items, modelValue) {
  const ids = [];
  modelValue.forEach(value => {
    const item = items.find(item => deepEqual(value, item.value));
    const itemByIndex = items[value];
    if (item?.value != null) {
      ids.push(item.id);
    } else if (itemByIndex != null) {
      ids.push(itemByIndex.id);
    }
  });
  return ids;
}
function getValues(items, ids) {
  const values = [];
  ids.forEach(id => {
    const itemIndex = items.findIndex(item => item.id === id);
    if (~itemIndex) {
      const item = items[itemIndex];
      values.push(item.value != null ? item.value : itemIndex);
    }
  });
  return values;
}

const {mergeProps:_mergeProps$12,createVNode:_createVNode$2a} = await importShared('vue');
const VBtnToggleSymbol = Symbol.for('vuetify:v-btn-toggle');
const makeVBtnToggleProps = propsFactory({
  ...makeVBtnGroupProps(),
  ...makeGroupProps()
}, 'VBtnToggle');
const VBtnToggle = genericComponent()({
  name: 'VBtnToggle',
  props: makeVBtnToggleProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      isSelected,
      next,
      prev,
      select,
      selected
    } = useGroup(props, VBtnToggleSymbol);
    useRender(() => {
      const btnGroupProps = VBtnGroup.filterProps(props);
      return _createVNode$2a(VBtnGroup, _mergeProps$12({
        "class": ['v-btn-toggle', props.class]
      }, btnGroupProps, {
        "style": props.style
      }), {
        default: () => [slots.default?.({
          isSelected,
          next,
          prev,
          select,
          selected
        })]
      });
    });
    return {
      next,
      prev,
      select
    };
  }
});

// Utilities
const predefinedSizes = ['x-small', 'small', 'default', 'large', 'x-large'];
// Composables
const makeSizeProps = propsFactory({
  size: {
    type: [String, Number],
    default: 'default'
  }
}, 'size');
function useSize(props) {
  let name = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : getCurrentInstanceName();
  return destructComputed(() => {
    const size = props.size;
    let sizeClasses;
    let sizeStyles;
    if (includes(predefinedSizes, size)) {
      sizeClasses = `${name}--size-${size}`;
    } else if (size) {
      sizeStyles = {
        width: convertToUnit(size),
        height: convertToUnit(size)
      };
    }
    return {
      sizeClasses,
      sizeStyles
    };
  });
}

const {createVNode:_createVNode$29} = await importShared('vue');
const {shallowRef: shallowRef$G,Text} = await importShared('vue');
const makeVIconProps = propsFactory({
  color: String,
  disabled: Boolean,
  start: Boolean,
  end: Boolean,
  icon: IconValue,
  opacity: [String, Number],
  ...makeComponentProps(),
  ...makeSizeProps(),
  ...makeTagProps({
    tag: 'i'
  }),
  ...makeThemeProps()
}, 'VIcon');
const VIcon = genericComponent()({
  name: 'VIcon',
  props: makeVIconProps(),
  setup(props, _ref) {
    let {
      attrs,
      slots
    } = _ref;
    const slotIcon = shallowRef$G();
    const {
      themeClasses
    } = useTheme();
    const {
      iconData
    } = useIcon(() => slotIcon.value || props.icon);
    const {
      sizeClasses
    } = useSize(props);
    const {
      textColorClasses,
      textColorStyles
    } = useTextColor(() => props.color);
    useRender(() => {
      const slotValue = slots.default?.();
      if (slotValue) {
        slotIcon.value = flattenFragments(slotValue).filter(node => node.type === Text && node.children && typeof node.children === 'string')[0]?.children;
      }
      const hasClick = !!(attrs.onClick || attrs.onClickOnce);
      return _createVNode$29(iconData.value.component, {
        "tag": props.tag,
        "icon": iconData.value.icon,
        "class": ['v-icon', 'notranslate', themeClasses.value, sizeClasses.value, textColorClasses.value, {
          'v-icon--clickable': hasClick,
          'v-icon--disabled': props.disabled,
          'v-icon--start': props.start,
          'v-icon--end': props.end
        }, props.class],
        "style": [{
          '--v-icon-opacity': props.opacity
        }, !sizeClasses.value ? {
          fontSize: convertToUnit(props.size),
          height: convertToUnit(props.size),
          width: convertToUnit(props.size)
        } : undefined, textColorStyles.value, props.style],
        "role": hasClick ? 'button' : undefined,
        "aria-hidden": !hasClick,
        "tabindex": hasClick ? props.disabled ? -1 : 0 : undefined
      }, {
        default: () => [slotValue]
      });
    });
    return {};
  }
});

// Utilities
const {onBeforeUnmount: onBeforeUnmount$9,ref: ref$L,shallowRef: shallowRef$F,watch: watch$C} = await importShared('vue');
function useIntersectionObserver(callback, options) {
  const intersectionRef = ref$L();
  const isIntersecting = shallowRef$F(false);
  if (SUPPORTS_INTERSECTION) {
    const observer = new IntersectionObserver(entries => {
      isIntersecting.value = !!entries.find(entry => entry.isIntersecting);
    }, options);
    onBeforeUnmount$9(() => {
      observer.disconnect();
    });
    watch$C(intersectionRef, (newValue, oldValue) => {
      if (oldValue) {
        observer.unobserve(oldValue);
        isIntersecting.value = false;
      }
      if (newValue) observer.observe(newValue);
    }, {
      flush: 'post'
    });
  }
  return {
    intersectionRef,
    isIntersecting
  };
}

const {createVNode:_createVNode$28} = await importShared('vue');
const {ref: ref$K,toRef: toRef$U,watchEffect: watchEffect$h} = await importShared('vue');
const makeVProgressCircularProps = propsFactory({
  bgColor: String,
  color: String,
  indeterminate: [Boolean, String],
  modelValue: {
    type: [Number, String],
    default: 0
  },
  rotate: {
    type: [Number, String],
    default: 0
  },
  width: {
    type: [Number, String],
    default: 4
  },
  ...makeComponentProps(),
  ...makeSizeProps(),
  ...makeTagProps({
    tag: 'div'
  }),
  ...makeThemeProps()
}, 'VProgressCircular');
const VProgressCircular = genericComponent()({
  name: 'VProgressCircular',
  props: makeVProgressCircularProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const MAGIC_RADIUS_CONSTANT = 20;
    const CIRCUMFERENCE = 2 * Math.PI * MAGIC_RADIUS_CONSTANT;
    const root = ref$K();
    const {
      themeClasses
    } = provideTheme(props);
    const {
      sizeClasses,
      sizeStyles
    } = useSize(props);
    const {
      textColorClasses,
      textColorStyles
    } = useTextColor(() => props.color);
    const {
      textColorClasses: underlayColorClasses,
      textColorStyles: underlayColorStyles
    } = useTextColor(() => props.bgColor);
    const {
      intersectionRef,
      isIntersecting
    } = useIntersectionObserver();
    const {
      resizeRef,
      contentRect
    } = useResizeObserver();
    const normalizedValue = toRef$U(() => Math.max(0, Math.min(100, parseFloat(props.modelValue))));
    const width = toRef$U(() => Number(props.width));
    const size = toRef$U(() => {
      // Get size from element if size prop value is small, large etc
      return sizeStyles.value ? Number(props.size) : contentRect.value ? contentRect.value.width : Math.max(width.value, 32);
    });
    const diameter = toRef$U(() => MAGIC_RADIUS_CONSTANT / (1 - width.value / size.value) * 2);
    const strokeWidth = toRef$U(() => width.value / size.value * diameter.value);
    const strokeDashOffset = toRef$U(() => convertToUnit((100 - normalizedValue.value) / 100 * CIRCUMFERENCE));
    watchEffect$h(() => {
      intersectionRef.value = root.value;
      resizeRef.value = root.value;
    });
    useRender(() => _createVNode$28(props.tag, {
      "ref": root,
      "class": ['v-progress-circular', {
        'v-progress-circular--indeterminate': !!props.indeterminate,
        'v-progress-circular--visible': isIntersecting.value,
        'v-progress-circular--disable-shrink': props.indeterminate === 'disable-shrink'
      }, themeClasses.value, sizeClasses.value, textColorClasses.value, props.class],
      "style": [sizeStyles.value, textColorStyles.value, props.style],
      "role": "progressbar",
      "aria-valuemin": "0",
      "aria-valuemax": "100",
      "aria-valuenow": props.indeterminate ? undefined : normalizedValue.value
    }, {
      default: () => [_createVNode$28("svg", {
        "style": {
          transform: `rotate(calc(-90deg + ${Number(props.rotate)}deg))`
        },
        "xmlns": "http://www.w3.org/2000/svg",
        "viewBox": `0 0 ${diameter.value} ${diameter.value}`
      }, [_createVNode$28("circle", {
        "class": ['v-progress-circular__underlay', underlayColorClasses.value],
        "style": underlayColorStyles.value,
        "fill": "transparent",
        "cx": "50%",
        "cy": "50%",
        "r": MAGIC_RADIUS_CONSTANT,
        "stroke-width": strokeWidth.value,
        "stroke-dasharray": CIRCUMFERENCE,
        "stroke-dashoffset": 0
      }, null), _createVNode$28("circle", {
        "class": "v-progress-circular__overlay",
        "fill": "transparent",
        "cx": "50%",
        "cy": "50%",
        "r": MAGIC_RADIUS_CONSTANT,
        "stroke-width": strokeWidth.value,
        "stroke-dasharray": CIRCUMFERENCE,
        "stroke-dashoffset": strokeDashOffset.value
      }, null)]), slots.default && _createVNode$28("div", {
        "class": "v-progress-circular__content"
      }, [slots.default({
        value: normalizedValue.value
      })])]
    }));
    return {};
  }
});

const {computed: computed$1y} = await importShared('vue');
const oppositeMap = {
  center: 'center',
  top: 'bottom',
  bottom: 'top',
  left: 'right',
  right: 'left'
};
const makeLocationProps = propsFactory({
  location: String
}, 'location');
function useLocation(props) {
  let opposite = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
  let offset = arguments.length > 2 ? arguments[2] : undefined;
  const {
    isRtl
  } = useRtl();
  const locationStyles = computed$1y(() => {
    if (!props.location) return {};
    const {
      side,
      align
    } = parseAnchor(props.location.split(' ').length > 1 ? props.location : `${props.location} center`, isRtl.value);
    function getOffset(side) {
      return offset ? offset(side) : 0;
    }
    const styles = {};
    if (side !== 'center') {
      if (opposite) styles[oppositeMap[side]] = `calc(100% - ${getOffset(side)}px)`;else styles[side] = 0;
    }
    if (align !== 'center') {
      if (opposite) styles[oppositeMap[align]] = `calc(100% - ${getOffset(align)}px)`;else styles[align] = 0;
    } else {
      if (side === 'center') styles.top = styles.left = '50%';else {
        styles[{
          top: 'left',
          bottom: 'left',
          left: 'top',
          right: 'top'
        }[side]] = '50%';
      }
      styles.transform = {
        top: 'translateX(-50%)',
        bottom: 'translateX(-50%)',
        left: 'translateY(-50%)',
        right: 'translateY(-50%)',
        center: 'translate(-50%, -50%)'
      }[side];
    }
    return styles;
  });
  return {
    locationStyles
  };
}

const {createVNode:_createVNode$27} = await importShared('vue');
const {computed: computed$1x,Transition: Transition$2} = await importShared('vue');
const makeVProgressLinearProps = propsFactory({
  absolute: Boolean,
  active: {
    type: Boolean,
    default: true
  },
  bgColor: String,
  bgOpacity: [Number, String],
  bufferValue: {
    type: [Number, String],
    default: 0
  },
  bufferColor: String,
  bufferOpacity: [Number, String],
  clickable: Boolean,
  color: String,
  height: {
    type: [Number, String],
    default: 4
  },
  indeterminate: Boolean,
  max: {
    type: [Number, String],
    default: 100
  },
  modelValue: {
    type: [Number, String],
    default: 0
  },
  opacity: [Number, String],
  reverse: Boolean,
  stream: Boolean,
  striped: Boolean,
  roundedBar: Boolean,
  ...makeComponentProps(),
  ...makeLocationProps({
    location: 'top'
  }),
  ...makeRoundedProps(),
  ...makeTagProps(),
  ...makeThemeProps()
}, 'VProgressLinear');
const VProgressLinear = genericComponent()({
  name: 'VProgressLinear',
  props: makeVProgressLinearProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const progress = useProxiedModel(props, 'modelValue');
    const {
      isRtl,
      rtlClasses
    } = useRtl();
    const {
      themeClasses
    } = provideTheme(props);
    const {
      locationStyles
    } = useLocation(props);
    const {
      textColorClasses,
      textColorStyles
    } = useTextColor(() => props.color);
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.bgColor || props.color);
    const {
      backgroundColorClasses: bufferColorClasses,
      backgroundColorStyles: bufferColorStyles
    } = useBackgroundColor(() => props.bufferColor || props.bgColor || props.color);
    const {
      backgroundColorClasses: barColorClasses,
      backgroundColorStyles: barColorStyles
    } = useBackgroundColor(() => props.color);
    const {
      roundedClasses
    } = useRounded(props);
    const {
      intersectionRef,
      isIntersecting
    } = useIntersectionObserver();
    const max = computed$1x(() => parseFloat(props.max));
    const height = computed$1x(() => parseFloat(props.height));
    const normalizedBuffer = computed$1x(() => clamp(parseFloat(props.bufferValue) / max.value * 100, 0, 100));
    const normalizedValue = computed$1x(() => clamp(parseFloat(progress.value) / max.value * 100, 0, 100));
    const isReversed = computed$1x(() => isRtl.value !== props.reverse);
    const transition = computed$1x(() => props.indeterminate ? 'fade-transition' : 'slide-x-transition');
    const isForcedColorsModeActive = IN_BROWSER && window.matchMedia?.('(forced-colors: active)').matches;
    function handleClick(e) {
      if (!intersectionRef.value) return;
      const {
        left,
        right,
        width
      } = intersectionRef.value.getBoundingClientRect();
      const value = isReversed.value ? width - e.clientX + (right - width) : e.clientX - left;
      progress.value = Math.round(value / width * max.value);
    }
    useRender(() => _createVNode$27(props.tag, {
      "ref": intersectionRef,
      "class": ['v-progress-linear', {
        'v-progress-linear--absolute': props.absolute,
        'v-progress-linear--active': props.active && isIntersecting.value,
        'v-progress-linear--reverse': isReversed.value,
        'v-progress-linear--rounded': props.rounded,
        'v-progress-linear--rounded-bar': props.roundedBar,
        'v-progress-linear--striped': props.striped
      }, roundedClasses.value, themeClasses.value, rtlClasses.value, props.class],
      "style": [{
        bottom: props.location === 'bottom' ? 0 : undefined,
        top: props.location === 'top' ? 0 : undefined,
        height: props.active ? convertToUnit(height.value) : 0,
        '--v-progress-linear-height': convertToUnit(height.value),
        ...(props.absolute ? locationStyles.value : {})
      }, props.style],
      "role": "progressbar",
      "aria-hidden": props.active ? 'false' : 'true',
      "aria-valuemin": "0",
      "aria-valuemax": props.max,
      "aria-valuenow": props.indeterminate ? undefined : Math.min(parseFloat(progress.value), max.value),
      "onClick": props.clickable && handleClick
    }, {
      default: () => [props.stream && _createVNode$27("div", {
        "key": "stream",
        "class": ['v-progress-linear__stream', textColorClasses.value],
        "style": {
          ...textColorStyles.value,
          [isReversed.value ? 'left' : 'right']: convertToUnit(-height.value),
          borderTop: `${convertToUnit(height.value / 2)} dotted`,
          opacity: parseFloat(props.bufferOpacity),
          top: `calc(50% - ${convertToUnit(height.value / 4)})`,
          width: convertToUnit(100 - normalizedBuffer.value, '%'),
          '--v-progress-linear-stream-to': convertToUnit(height.value * (isReversed.value ? 1 : -1))
        }
      }, null), _createVNode$27("div", {
        "class": ['v-progress-linear__background', !isForcedColorsModeActive ? backgroundColorClasses.value : undefined],
        "style": [backgroundColorStyles.value, {
          opacity: parseFloat(props.bgOpacity),
          width: props.stream ? 0 : undefined
        }]
      }, null), _createVNode$27("div", {
        "class": ['v-progress-linear__buffer', !isForcedColorsModeActive ? bufferColorClasses.value : undefined],
        "style": [bufferColorStyles.value, {
          opacity: parseFloat(props.bufferOpacity),
          width: convertToUnit(normalizedBuffer.value, '%')
        }]
      }, null), _createVNode$27(Transition$2, {
        "name": transition.value
      }, {
        default: () => [!props.indeterminate ? _createVNode$27("div", {
          "class": ['v-progress-linear__determinate', !isForcedColorsModeActive ? barColorClasses.value : undefined],
          "style": [barColorStyles.value, {
            width: convertToUnit(normalizedValue.value, '%')
          }]
        }, null) : _createVNode$27("div", {
          "class": "v-progress-linear__indeterminate"
        }, [['long', 'short'].map(bar => _createVNode$27("div", {
          "key": bar,
          "class": ['v-progress-linear__indeterminate', bar, !isForcedColorsModeActive ? barColorClasses.value : undefined],
          "style": barColorStyles.value
        }, null))])]
      }), slots.default && _createVNode$27("div", {
        "class": "v-progress-linear__content"
      }, [slots.default({
        value: normalizedValue.value,
        buffer: normalizedBuffer.value
      })])]
    }));
    return {};
  }
});

const {createVNode:_createVNode$26} = await importShared('vue');
const {toRef: toRef$T} = await importShared('vue');
// Composables
const makeLoaderProps = propsFactory({
  loading: [Boolean, String]
}, 'loader');
function useLoader(props) {
  let name = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : getCurrentInstanceName();
  const loaderClasses = toRef$T(() => ({
    [`${name}--loading`]: props.loading
  }));
  return {
    loaderClasses
  };
}
function LoaderSlot(props, _ref) {
  let {
    slots
  } = _ref;
  return _createVNode$26("div", {
    "class": `${props.name}__loader`
  }, [slots.default?.({
    color: props.color,
    isActive: props.active
  }) || _createVNode$26(VProgressLinear, {
    "absolute": props.absolute,
    "active": props.active,
    "color": props.color,
    "height": "2",
    "indeterminate": true
  }, null)]);
}

// Utilities
const {toRef: toRef$S} = await importShared('vue');
const positionValues = ['static', 'relative', 'fixed', 'absolute', 'sticky'];
// Composables
const makePositionProps = propsFactory({
  position: {
    type: String,
    validator: /* istanbul ignore next */v => positionValues.includes(v)
  }
}, 'position');
function usePosition(props) {
  let name = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : getCurrentInstanceName();
  const positionClasses = toRef$S(() => {
    return props.position ? `${name}--${props.position}` : undefined;
  });
  return {
    positionClasses
  };
}

// Utilities
const {computed: computed$1w,nextTick: nextTick$p,onScopeDispose: onScopeDispose$a,reactive: reactive$1,resolveDynamicComponent,toRef: toRef$R} = await importShared('vue');
function useRoute() {
  const vm = getCurrentInstance('useRoute');
  return computed$1w(() => vm?.proxy?.$route);
}
function useRouter() {
  return getCurrentInstance('useRouter')?.proxy?.$router;
}
function useLink(props, attrs) {
  const RouterLink = resolveDynamicComponent('RouterLink');
  const isLink = toRef$R(() => !!(props.href || props.to));
  const isClickable = computed$1w(() => {
    return isLink?.value || hasEvent(attrs, 'click') || hasEvent(props, 'click');
  });
  if (typeof RouterLink === 'string' || !('useLink' in RouterLink)) {
    const href = toRef$R(() => props.href);
    return {
      isLink,
      isClickable,
      href,
      linkProps: reactive$1({
        href
      })
    };
  }

  // vue-router useLink `to` prop needs to be reactive and useLink will crash if undefined
  const routerLink = RouterLink.useLink({
    to: toRef$R(() => props.to || ''),
    replace: toRef$R(() => props.replace)
  });
  // Actual link needs to be undefined when to prop is not used
  const link = computed$1w(() => props.to ? routerLink : undefined);
  const route = useRoute();
  const isActive = computed$1w(() => {
    if (!link.value) return false;
    if (!props.exact) return link.value.isActive?.value ?? false;
    if (!route.value) return link.value.isExactActive?.value ?? false;
    return link.value.isExactActive?.value && deepEqual(link.value.route.value.query, route.value.query);
  });
  const href = computed$1w(() => props.to ? link.value?.route.value.href : props.href);
  return {
    isLink,
    isClickable,
    isActive,
    route: link.value?.route,
    navigate: link.value?.navigate,
    href,
    linkProps: reactive$1({
      href,
      'aria-current': toRef$R(() => isActive.value ? 'page' : undefined)
    })
  };
}
const makeRouterProps = propsFactory({
  href: String,
  replace: Boolean,
  to: [String, Object],
  exact: Boolean
}, 'router');
let inTransition = false;
function useBackButton(router, cb) {
  let popped = false;
  let removeBefore;
  let removeAfter;
  if (IN_BROWSER && router?.beforeEach) {
    nextTick$p(() => {
      window.addEventListener('popstate', onPopstate);
      removeBefore = router.beforeEach((to, from, next) => {
        if (!inTransition) {
          setTimeout(() => popped ? cb(next) : next());
        } else {
          popped ? cb(next) : next();
        }
        inTransition = true;
      });
      removeAfter = router?.afterEach(() => {
        inTransition = false;
      });
    });
    onScopeDispose$a(() => {
      window.removeEventListener('popstate', onPopstate);
      removeBefore?.();
      removeAfter?.();
    });
  }
  function onPopstate(e) {
    if (e.state?.replaced) return;
    popped = true;
    setTimeout(() => popped = false);
  }
}

// Utilities
const {nextTick: nextTick$o,watch: watch$B} = await importShared('vue');


// Types

function useSelectLink(link, select) {
  watch$B(() => link.isActive?.value, isActive => {
    if (link.isLink.value && isActive && select) {
      nextTick$o(() => {
        select(true);
      });
    }
  }, {
    immediate: true
  });
}

// Styles
const stopSymbol = Symbol('rippleStop');
const DELAY_RIPPLE = 80;
function transform(el, value) {
  el.style.transform = value;
  el.style.webkitTransform = value;
}
function isTouchEvent(e) {
  return e.constructor.name === 'TouchEvent';
}
function isKeyboardEvent(e) {
  return e.constructor.name === 'KeyboardEvent';
}
const calculate = function (e, el) {
  let value = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
  let localX = 0;
  let localY = 0;
  if (!isKeyboardEvent(e)) {
    const offset = el.getBoundingClientRect();
    const target = isTouchEvent(e) ? e.touches[e.touches.length - 1] : e;
    localX = target.clientX - offset.left;
    localY = target.clientY - offset.top;
  }
  let radius = 0;
  let scale = 0.3;
  if (el._ripple?.circle) {
    scale = 0.15;
    radius = el.clientWidth / 2;
    radius = value.center ? radius : radius + Math.sqrt((localX - radius) ** 2 + (localY - radius) ** 2) / 4;
  } else {
    radius = Math.sqrt(el.clientWidth ** 2 + el.clientHeight ** 2) / 2;
  }
  const centerX = `${(el.clientWidth - radius * 2) / 2}px`;
  const centerY = `${(el.clientHeight - radius * 2) / 2}px`;
  const x = value.center ? centerX : `${localX - radius}px`;
  const y = value.center ? centerY : `${localY - radius}px`;
  return {
    radius,
    scale,
    x,
    y,
    centerX,
    centerY
  };
};
const ripples = {
  /* eslint-disable max-statements */
  show(e, el) {
    let value = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
    if (!el?._ripple?.enabled) {
      return;
    }
    const container = document.createElement('span');
    const animation = document.createElement('span');
    container.appendChild(animation);
    container.className = 'v-ripple__container';
    if (value.class) {
      container.className += ` ${value.class}`;
    }
    const {
      radius,
      scale,
      x,
      y,
      centerX,
      centerY
    } = calculate(e, el, value);
    const size = `${radius * 2}px`;
    animation.className = 'v-ripple__animation';
    animation.style.width = size;
    animation.style.height = size;
    el.appendChild(container);
    const computed = window.getComputedStyle(el);
    if (computed && computed.position === 'static') {
      el.style.position = 'relative';
      el.dataset.previousPosition = 'static';
    }
    animation.classList.add('v-ripple__animation--enter');
    animation.classList.add('v-ripple__animation--visible');
    transform(animation, `translate(${x}, ${y}) scale3d(${scale},${scale},${scale})`);
    animation.dataset.activated = String(performance.now());
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        animation.classList.remove('v-ripple__animation--enter');
        animation.classList.add('v-ripple__animation--in');
        transform(animation, `translate(${centerX}, ${centerY}) scale3d(1,1,1)`);
      });
    });
  },
  hide(el) {
    if (!el?._ripple?.enabled) return;
    const ripples = el.getElementsByClassName('v-ripple__animation');
    if (ripples.length === 0) return;
    const animation = ripples[ripples.length - 1];
    if (animation.dataset.isHiding) return;else animation.dataset.isHiding = 'true';
    const diff = performance.now() - Number(animation.dataset.activated);
    const delay = Math.max(250 - diff, 0);
    setTimeout(() => {
      animation.classList.remove('v-ripple__animation--in');
      animation.classList.add('v-ripple__animation--out');
      setTimeout(() => {
        const ripples = el.getElementsByClassName('v-ripple__animation');
        if (ripples.length === 1 && el.dataset.previousPosition) {
          el.style.position = el.dataset.previousPosition;
          delete el.dataset.previousPosition;
        }
        if (animation.parentNode?.parentNode === el) el.removeChild(animation.parentNode);
      }, 300);
    }, delay);
  }
};
function isRippleEnabled(value) {
  return typeof value === 'undefined' || !!value;
}
function rippleShow(e) {
  const value = {};
  const element = e.currentTarget;
  if (!element?._ripple || element._ripple.touched || e[stopSymbol]) return;

  // Don't allow the event to trigger ripples on any other elements
  e[stopSymbol] = true;
  if (isTouchEvent(e)) {
    element._ripple.touched = true;
    element._ripple.isTouch = true;
  } else {
    // It's possible for touch events to fire
    // as mouse events on Android/iOS, this
    // will skip the event call if it has
    // already been registered as touch
    if (element._ripple.isTouch) return;
  }
  value.center = element._ripple.centered || isKeyboardEvent(e);
  if (element._ripple.class) {
    value.class = element._ripple.class;
  }
  if (isTouchEvent(e)) {
    // already queued that shows or hides the ripple
    if (element._ripple.showTimerCommit) return;
    element._ripple.showTimerCommit = () => {
      ripples.show(e, element, value);
    };
    element._ripple.showTimer = window.setTimeout(() => {
      if (element?._ripple?.showTimerCommit) {
        element._ripple.showTimerCommit();
        element._ripple.showTimerCommit = null;
      }
    }, DELAY_RIPPLE);
  } else {
    ripples.show(e, element, value);
  }
}
function rippleStop(e) {
  e[stopSymbol] = true;
}
function rippleHide(e) {
  const element = e.currentTarget;
  if (!element?._ripple) return;
  window.clearTimeout(element._ripple.showTimer);

  // The touch interaction occurs before the show timer is triggered.
  // We still want to show ripple effect.
  if (e.type === 'touchend' && element._ripple.showTimerCommit) {
    element._ripple.showTimerCommit();
    element._ripple.showTimerCommit = null;

    // re-queue ripple hiding
    element._ripple.showTimer = window.setTimeout(() => {
      rippleHide(e);
    });
    return;
  }
  window.setTimeout(() => {
    if (element._ripple) {
      element._ripple.touched = false;
    }
  });
  ripples.hide(element);
}
function rippleCancelShow(e) {
  const element = e.currentTarget;
  if (!element?._ripple) return;
  if (element._ripple.showTimerCommit) {
    element._ripple.showTimerCommit = null;
  }
  window.clearTimeout(element._ripple.showTimer);
}
let keyboardRipple = false;
function keyboardRippleShow(e) {
  if (!keyboardRipple && (e.keyCode === keyCodes.enter || e.keyCode === keyCodes.space)) {
    keyboardRipple = true;
    rippleShow(e);
  }
}
function keyboardRippleHide(e) {
  keyboardRipple = false;
  rippleHide(e);
}
function focusRippleHide(e) {
  if (keyboardRipple) {
    keyboardRipple = false;
    rippleHide(e);
  }
}
function updateRipple(el, binding, wasEnabled) {
  const {
    value,
    modifiers
  } = binding;
  const enabled = isRippleEnabled(value);
  if (!enabled) {
    ripples.hide(el);
  }
  el._ripple = el._ripple ?? {};
  el._ripple.enabled = enabled;
  el._ripple.centered = modifiers.center;
  el._ripple.circle = modifiers.circle;
  if (isObject(value) && value.class) {
    el._ripple.class = value.class;
  }
  if (enabled && !wasEnabled) {
    if (modifiers.stop) {
      el.addEventListener('touchstart', rippleStop, {
        passive: true
      });
      el.addEventListener('mousedown', rippleStop);
      return;
    }
    el.addEventListener('touchstart', rippleShow, {
      passive: true
    });
    el.addEventListener('touchend', rippleHide, {
      passive: true
    });
    el.addEventListener('touchmove', rippleCancelShow, {
      passive: true
    });
    el.addEventListener('touchcancel', rippleHide);
    el.addEventListener('mousedown', rippleShow);
    el.addEventListener('mouseup', rippleHide);
    el.addEventListener('mouseleave', rippleHide);
    el.addEventListener('keydown', keyboardRippleShow);
    el.addEventListener('keyup', keyboardRippleHide);
    el.addEventListener('blur', focusRippleHide);

    // Anchor tags can be dragged, causes other hides to fail - #1537
    el.addEventListener('dragstart', rippleHide, {
      passive: true
    });
  } else if (!enabled && wasEnabled) {
    removeListeners(el);
  }
}
function removeListeners(el) {
  el.removeEventListener('mousedown', rippleShow);
  el.removeEventListener('touchstart', rippleShow);
  el.removeEventListener('touchend', rippleHide);
  el.removeEventListener('touchmove', rippleCancelShow);
  el.removeEventListener('touchcancel', rippleHide);
  el.removeEventListener('mouseup', rippleHide);
  el.removeEventListener('mouseleave', rippleHide);
  el.removeEventListener('keydown', keyboardRippleShow);
  el.removeEventListener('keyup', keyboardRippleHide);
  el.removeEventListener('dragstart', rippleHide);
  el.removeEventListener('blur', focusRippleHide);
}
function mounted$4(el, binding) {
  updateRipple(el, binding, false);
}
function unmounted$4(el) {
  delete el._ripple;
  removeListeners(el);
}
function updated$1(el, binding) {
  if (binding.value === binding.oldValue) {
    return;
  }
  const wasEnabled = isRippleEnabled(binding.oldValue);
  updateRipple(el, binding, wasEnabled);
}
const Ripple = {
  mounted: mounted$4,
  unmounted: unmounted$4,
  updated: updated$1
};

const {createVNode:_createVNode$25,mergeProps:_mergeProps$11} = await importShared('vue');
const {computed: computed$1v,toDisplayString: toDisplayString$4,toRef: toRef$Q,withDirectives} = await importShared('vue');
const makeVBtnProps = propsFactory({
  active: {
    type: Boolean,
    default: undefined
  },
  activeColor: String,
  baseColor: String,
  symbol: {
    type: null,
    default: VBtnToggleSymbol
  },
  flat: Boolean,
  icon: [Boolean, String, Function, Object],
  prependIcon: IconValue,
  appendIcon: IconValue,
  block: Boolean,
  readonly: Boolean,
  slim: Boolean,
  stacked: Boolean,
  ripple: {
    type: [Boolean, Object],
    default: true
  },
  text: {
    type: [String, Number, Boolean],
    default: undefined
  },
  ...makeBorderProps(),
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeDimensionProps(),
  ...makeElevationProps(),
  ...makeGroupItemProps(),
  ...makeLoaderProps(),
  ...makeLocationProps(),
  ...makePositionProps(),
  ...makeRoundedProps(),
  ...makeRouterProps(),
  ...makeSizeProps(),
  ...makeTagProps({
    tag: 'button'
  }),
  ...makeThemeProps(),
  ...makeVariantProps({
    variant: 'elevated'
  })
}, 'VBtn');
const VBtn = genericComponent()({
  name: 'VBtn',
  props: makeVBtnProps(),
  emits: {
    'group:selected': val => true
  },
  setup(props, _ref) {
    let {
      attrs,
      slots
    } = _ref;
    const {
      themeClasses
    } = provideTheme(props);
    const {
      borderClasses
    } = useBorder(props);
    const {
      densityClasses
    } = useDensity(props);
    const {
      dimensionStyles
    } = useDimension(props);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      loaderClasses
    } = useLoader(props);
    const {
      locationStyles
    } = useLocation(props);
    const {
      positionClasses
    } = usePosition(props);
    const {
      roundedClasses
    } = useRounded(props);
    const {
      sizeClasses,
      sizeStyles
    } = useSize(props);
    const group = useGroupItem(props, props.symbol, false);
    const link = useLink(props, attrs);
    const isActive = computed$1v(() => {
      if (props.active !== undefined) {
        return props.active;
      }
      if (link.isLink.value) {
        return link.isActive?.value;
      }
      return group?.isSelected.value;
    });
    const color = toRef$Q(() => isActive.value ? props.activeColor ?? props.color : props.color);
    const variantProps = computed$1v(() => {
      const showColor = group?.isSelected.value && (!link.isLink.value || link.isActive?.value) || !group || link.isActive?.value;
      return {
        color: showColor ? color.value ?? props.baseColor : props.baseColor,
        variant: props.variant
      };
    });
    const {
      colorClasses,
      colorStyles,
      variantClasses
    } = useVariant(variantProps);
    const isDisabled = computed$1v(() => group?.disabled.value || props.disabled);
    const isElevated = toRef$Q(() => {
      return props.variant === 'elevated' && !(props.disabled || props.flat || props.border);
    });
    const valueAttr = computed$1v(() => {
      if (props.value === undefined || typeof props.value === 'symbol') return undefined;
      return Object(props.value) === props.value ? JSON.stringify(props.value, null, 0) : props.value;
    });
    function onClick(e) {
      if (isDisabled.value || link.isLink.value && (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0 || attrs.target === '_blank')) return;
      link.navigate?.(e);
      group?.toggle();
    }
    useSelectLink(link, group?.select);
    useRender(() => {
      const Tag = link.isLink.value ? 'a' : props.tag;
      const hasPrepend = !!(props.prependIcon || slots.prepend);
      const hasAppend = !!(props.appendIcon || slots.append);
      const hasIcon = !!(props.icon && props.icon !== true);
      return withDirectives(_createVNode$25(Tag, _mergeProps$11({
        "type": Tag === 'a' ? undefined : 'button',
        "class": ['v-btn', group?.selectedClass.value, {
          'v-btn--active': isActive.value,
          'v-btn--block': props.block,
          'v-btn--disabled': isDisabled.value,
          'v-btn--elevated': isElevated.value,
          'v-btn--flat': props.flat,
          'v-btn--icon': !!props.icon,
          'v-btn--loading': props.loading,
          'v-btn--readonly': props.readonly,
          'v-btn--slim': props.slim,
          'v-btn--stacked': props.stacked
        }, themeClasses.value, borderClasses.value, colorClasses.value, densityClasses.value, elevationClasses.value, loaderClasses.value, positionClasses.value, roundedClasses.value, sizeClasses.value, variantClasses.value, props.class],
        "style": [colorStyles.value, dimensionStyles.value, locationStyles.value, sizeStyles.value, props.style],
        "aria-busy": props.loading ? true : undefined,
        "disabled": isDisabled.value || undefined,
        "tabindex": props.loading || props.readonly ? -1 : undefined,
        "onClick": onClick,
        "value": valueAttr.value
      }, link.linkProps), {
        default: () => [genOverlays(true, 'v-btn'), !props.icon && hasPrepend && _createVNode$25("span", {
          "key": "prepend",
          "class": "v-btn__prepend"
        }, [!slots.prepend ? _createVNode$25(VIcon, {
          "key": "prepend-icon",
          "icon": props.prependIcon
        }, null) : _createVNode$25(VDefaultsProvider, {
          "key": "prepend-defaults",
          "disabled": !props.prependIcon,
          "defaults": {
            VIcon: {
              icon: props.prependIcon
            }
          }
        }, slots.prepend)]), _createVNode$25("span", {
          "class": "v-btn__content",
          "data-no-activator": ""
        }, [!slots.default && hasIcon ? _createVNode$25(VIcon, {
          "key": "content-icon",
          "icon": props.icon
        }, null) : _createVNode$25(VDefaultsProvider, {
          "key": "content-defaults",
          "disabled": !hasIcon,
          "defaults": {
            VIcon: {
              icon: props.icon
            }
          }
        }, {
          default: () => [slots.default?.() ?? toDisplayString$4(props.text)]
        })]), !props.icon && hasAppend && _createVNode$25("span", {
          "key": "append",
          "class": "v-btn__append"
        }, [!slots.append ? _createVNode$25(VIcon, {
          "key": "append-icon",
          "icon": props.appendIcon
        }, null) : _createVNode$25(VDefaultsProvider, {
          "key": "append-defaults",
          "disabled": !props.appendIcon,
          "defaults": {
            VIcon: {
              icon: props.appendIcon
            }
          }
        }, slots.append)]), !!props.loading && _createVNode$25("span", {
          "key": "loader",
          "class": "v-btn__loader"
        }, [slots.loader?.() ?? _createVNode$25(VProgressCircular, {
          "color": typeof props.loading === 'boolean' ? undefined : props.loading,
          "indeterminate": true,
          "width": "2"
        }, null)])]
      }), [[Ripple, !isDisabled.value && props.ripple, '', {
        center: !!props.icon
      }]]);
    });
    return {
      group
    };
  }
});

const {mergeProps:_mergeProps$10,createVNode:_createVNode$24} = await importShared('vue');
const makeVAppBarNavIconProps = propsFactory({
  ...makeVBtnProps({
    icon: '$menu',
    variant: 'text'
  })
}, 'VAppBarNavIcon');
const VAppBarNavIcon = genericComponent()({
  name: 'VAppBarNavIcon',
  props: makeVAppBarNavIconProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    useRender(() => _createVNode$24(VBtn, _mergeProps$10(props, {
      "class": ['v-app-bar-nav-icon']
    }), slots));
    return {};
  }
});

const {mergeProps:_mergeProps$$,createVNode:_createVNode$23} = await importShared('vue');
const VAppBarTitle = genericComponent()({
  name: 'VAppBarTitle',
  props: makeVToolbarTitleProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    useRender(() => _createVNode$23(VToolbarTitle, _mergeProps$$(props, {
      "class": "v-app-bar-title"
    }), slots));
    return {};
  }
});

// Utilities
const VAlertTitle = createSimpleFunctional('v-alert-title');

const {createVNode:_createVNode$22,mergeProps:_mergeProps$_} = await importShared('vue');
const {toRef: toRef$P} = await importShared('vue');
const allowedTypes = ['success', 'info', 'warning', 'error'];
const makeVAlertProps = propsFactory({
  border: {
    type: [Boolean, String],
    validator: val => {
      return typeof val === 'boolean' || ['top', 'end', 'bottom', 'start'].includes(val);
    }
  },
  borderColor: String,
  closable: Boolean,
  closeIcon: {
    type: IconValue,
    default: '$close'
  },
  closeLabel: {
    type: String,
    default: '$vuetify.close'
  },
  icon: {
    type: [Boolean, String, Function, Object],
    default: null
  },
  modelValue: {
    type: Boolean,
    default: true
  },
  prominent: Boolean,
  title: String,
  text: String,
  type: {
    type: String,
    validator: val => allowedTypes.includes(val)
  },
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeDimensionProps(),
  ...makeElevationProps(),
  ...makeLocationProps(),
  ...makePositionProps(),
  ...makeRoundedProps(),
  ...makeTagProps(),
  ...makeThemeProps(),
  ...makeVariantProps({
    variant: 'flat'
  })
}, 'VAlert');
const VAlert = genericComponent()({
  name: 'VAlert',
  props: makeVAlertProps(),
  emits: {
    'click:close': e => true,
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      emit,
      slots
    } = _ref;
    const isActive = useProxiedModel(props, 'modelValue');
    const icon = toRef$P(() => {
      if (props.icon === false) return undefined;
      if (!props.type) return props.icon;
      return props.icon ?? `$${props.type}`;
    });
    const {
      themeClasses
    } = provideTheme(props);
    const {
      colorClasses,
      colorStyles,
      variantClasses
    } = useVariant(() => ({
      color: props.color ?? props.type,
      variant: props.variant
    }));
    const {
      densityClasses
    } = useDensity(props);
    const {
      dimensionStyles
    } = useDimension(props);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      locationStyles
    } = useLocation(props);
    const {
      positionClasses
    } = usePosition(props);
    const {
      roundedClasses
    } = useRounded(props);
    const {
      textColorClasses,
      textColorStyles
    } = useTextColor(() => props.borderColor);
    const {
      t
    } = useLocale();
    const closeProps = toRef$P(() => ({
      'aria-label': t(props.closeLabel),
      onClick(e) {
        isActive.value = false;
        emit('click:close', e);
      }
    }));
    return () => {
      const hasPrepend = !!(slots.prepend || icon.value);
      const hasTitle = !!(slots.title || props.title);
      const hasClose = !!(slots.close || props.closable);
      return isActive.value && _createVNode$22(props.tag, {
        "class": ['v-alert', props.border && {
          'v-alert--border': !!props.border,
          [`v-alert--border-${props.border === true ? 'start' : props.border}`]: true
        }, {
          'v-alert--prominent': props.prominent
        }, themeClasses.value, colorClasses.value, densityClasses.value, elevationClasses.value, positionClasses.value, roundedClasses.value, variantClasses.value, props.class],
        "style": [colorStyles.value, dimensionStyles.value, locationStyles.value, props.style],
        "role": "alert"
      }, {
        default: () => [genOverlays(false, 'v-alert'), props.border && _createVNode$22("div", {
          "key": "border",
          "class": ['v-alert__border', textColorClasses.value],
          "style": textColorStyles.value
        }, null), hasPrepend && _createVNode$22("div", {
          "key": "prepend",
          "class": "v-alert__prepend"
        }, [!slots.prepend ? _createVNode$22(VIcon, {
          "key": "prepend-icon",
          "density": props.density,
          "icon": icon.value,
          "size": props.prominent ? 44 : 28
        }, null) : _createVNode$22(VDefaultsProvider, {
          "key": "prepend-defaults",
          "disabled": !icon.value,
          "defaults": {
            VIcon: {
              density: props.density,
              icon: icon.value,
              size: props.prominent ? 44 : 28
            }
          }
        }, slots.prepend)]), _createVNode$22("div", {
          "class": "v-alert__content"
        }, [hasTitle && _createVNode$22(VAlertTitle, {
          "key": "title"
        }, {
          default: () => [slots.title?.() ?? props.title]
        }), slots.text?.() ?? props.text, slots.default?.()]), slots.append && _createVNode$22("div", {
          "key": "append",
          "class": "v-alert__append"
        }, [slots.append()]), hasClose && _createVNode$22("div", {
          "key": "close",
          "class": "v-alert__close"
        }, [!slots.close ? _createVNode$22(VBtn, _mergeProps$_({
          "key": "close-btn",
          "icon": props.closeIcon,
          "size": "x-small",
          "variant": "text"
        }, closeProps.value), null) : _createVNode$22(VDefaultsProvider, {
          "key": "close-defaults",
          "defaults": {
            VBtn: {
              icon: props.closeIcon,
              size: 'x-small',
              variant: 'text'
            }
          }
        }, {
          default: () => [slots.close?.({
            props: closeProps.value
          })]
        })])]
      });
    };
  }
});

const {createVNode:_createVNode$21} = await importShared('vue');
const makeVAvatarProps = propsFactory({
  start: Boolean,
  end: Boolean,
  icon: IconValue,
  image: String,
  text: String,
  ...makeBorderProps(),
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeRoundedProps(),
  ...makeSizeProps(),
  ...makeTagProps(),
  ...makeThemeProps(),
  ...makeVariantProps({
    variant: 'flat'
  })
}, 'VAvatar');
const VAvatar = genericComponent()({
  name: 'VAvatar',
  props: makeVAvatarProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      themeClasses
    } = provideTheme(props);
    const {
      borderClasses
    } = useBorder(props);
    const {
      colorClasses,
      colorStyles,
      variantClasses
    } = useVariant(props);
    const {
      densityClasses
    } = useDensity(props);
    const {
      roundedClasses
    } = useRounded(props);
    const {
      sizeClasses,
      sizeStyles
    } = useSize(props);
    useRender(() => _createVNode$21(props.tag, {
      "class": ['v-avatar', {
        'v-avatar--start': props.start,
        'v-avatar--end': props.end
      }, themeClasses.value, borderClasses.value, colorClasses.value, densityClasses.value, roundedClasses.value, sizeClasses.value, variantClasses.value, props.class],
      "style": [colorStyles.value, sizeStyles.value, props.style]
    }, {
      default: () => [!slots.default ? props.image ? _createVNode$21(VImg, {
        "key": "image",
        "src": props.image,
        "alt": "",
        "cover": true
      }, null) : props.icon ? _createVNode$21(VIcon, {
        "key": "icon",
        "icon": props.icon
      }, null) : props.text : _createVNode$21(VDefaultsProvider, {
        "key": "content-defaults",
        "defaults": {
          VImg: {
            cover: true,
            src: props.image
          },
          VIcon: {
            icon: props.icon
          }
        }
      }, {
        default: () => [slots.default()]
      }), genOverlays(false, 'v-avatar')]
    }));
    return {};
  }
});

const {createVNode:_createVNode$20} = await importShared('vue');
const makeVLabelProps = propsFactory({
  text: String,
  onClick: EventProp(),
  ...makeComponentProps(),
  ...makeThemeProps()
}, 'VLabel');
const VLabel = genericComponent()({
  name: 'VLabel',
  props: makeVLabelProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    useRender(() => _createVNode$20("label", {
      "class": ['v-label', {
        'v-label--clickable': !!props.onClick
      }, props.class],
      "style": props.style,
      "onClick": props.onClick
    }, [props.text, slots.default?.()]));
    return {};
  }
});

const {createVNode:_createVNode$1$} = await importShared('vue');
const {onScopeDispose: onScopeDispose$9,provide: provide$f,toRef: toRef$O,useId: useId$c} = await importShared('vue');
const VSelectionControlGroupSymbol = Symbol.for('vuetify:selection-control-group');
const makeSelectionControlGroupProps = propsFactory({
  color: String,
  disabled: {
    type: Boolean,
    default: null
  },
  defaultsTarget: String,
  error: Boolean,
  id: String,
  inline: Boolean,
  falseIcon: IconValue,
  trueIcon: IconValue,
  ripple: {
    type: [Boolean, Object],
    default: true
  },
  multiple: {
    type: Boolean,
    default: null
  },
  name: String,
  readonly: {
    type: Boolean,
    default: null
  },
  modelValue: null,
  type: String,
  valueComparator: {
    type: Function,
    default: deepEqual
  },
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeThemeProps()
}, 'SelectionControlGroup');
const makeVSelectionControlGroupProps = propsFactory({
  ...makeSelectionControlGroupProps({
    defaultsTarget: 'VSelectionControl'
  })
}, 'VSelectionControlGroup');
const VSelectionControlGroup = genericComponent()({
  name: 'VSelectionControlGroup',
  props: makeVSelectionControlGroupProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const modelValue = useProxiedModel(props, 'modelValue');
    const uid = useId$c();
    const id = toRef$O(() => props.id || `v-selection-control-group-${uid}`);
    const name = toRef$O(() => props.name || id.value);
    const updateHandlers = new Set();
    provide$f(VSelectionControlGroupSymbol, {
      modelValue,
      forceUpdate: () => {
        updateHandlers.forEach(fn => fn());
      },
      onForceUpdate: cb => {
        updateHandlers.add(cb);
        onScopeDispose$9(() => {
          updateHandlers.delete(cb);
        });
      }
    });
    provideDefaults({
      [props.defaultsTarget]: {
        color: toRef$O(() => props.color),
        disabled: toRef$O(() => props.disabled),
        density: toRef$O(() => props.density),
        error: toRef$O(() => props.error),
        inline: toRef$O(() => props.inline),
        modelValue,
        multiple: toRef$O(() => !!props.multiple || props.multiple == null && Array.isArray(modelValue.value)),
        name,
        falseIcon: toRef$O(() => props.falseIcon),
        trueIcon: toRef$O(() => props.trueIcon),
        readonly: toRef$O(() => props.readonly),
        ripple: toRef$O(() => props.ripple),
        type: toRef$O(() => props.type),
        valueComparator: toRef$O(() => props.valueComparator)
      }
    });
    useRender(() => _createVNode$1$("div", {
      "class": ['v-selection-control-group', {
        'v-selection-control-group--inline': props.inline
      }, props.class],
      "style": props.style,
      "role": props.type === 'radio' ? 'radiogroup' : undefined
    }, [slots.default?.()]));
    return {};
  }
});

const {mergeProps:_mergeProps$Z,createVNode:_createVNode$1_,Fragment:_Fragment$C,resolveDirective:_resolveDirective$b,withDirectives:_withDirectives$i} = await importShared('vue');
const {computed: computed$1u,inject: inject$l,nextTick: nextTick$n,ref: ref$J,shallowRef: shallowRef$E,toRef: toRef$N,useId: useId$b} = await importShared('vue');
const makeVSelectionControlProps = propsFactory({
  label: String,
  baseColor: String,
  trueValue: null,
  falseValue: null,
  value: null,
  ...makeComponentProps(),
  ...makeSelectionControlGroupProps()
}, 'VSelectionControl');
function useSelectionControl(props) {
  const group = inject$l(VSelectionControlGroupSymbol, undefined);
  const {
    densityClasses
  } = useDensity(props);
  const modelValue = useProxiedModel(props, 'modelValue');
  const trueValue = computed$1u(() => props.trueValue !== undefined ? props.trueValue : props.value !== undefined ? props.value : true);
  const falseValue = computed$1u(() => props.falseValue !== undefined ? props.falseValue : false);
  const isMultiple = computed$1u(() => !!props.multiple || props.multiple == null && Array.isArray(modelValue.value));
  const model = computed$1u({
    get() {
      const val = group ? group.modelValue.value : modelValue.value;
      return isMultiple.value ? wrapInArray(val).some(v => props.valueComparator(v, trueValue.value)) : props.valueComparator(val, trueValue.value);
    },
    set(val) {
      if (props.readonly) return;
      const currentValue = val ? trueValue.value : falseValue.value;
      let newVal = currentValue;
      if (isMultiple.value) {
        newVal = val ? [...wrapInArray(modelValue.value), currentValue] : wrapInArray(modelValue.value).filter(item => !props.valueComparator(item, trueValue.value));
      }
      if (group) {
        group.modelValue.value = newVal;
      } else {
        modelValue.value = newVal;
      }
    }
  });
  const {
    textColorClasses,
    textColorStyles
  } = useTextColor(() => {
    if (props.error || props.disabled) return undefined;
    return model.value ? props.color : props.baseColor;
  });
  const {
    backgroundColorClasses,
    backgroundColorStyles
  } = useBackgroundColor(() => {
    return model.value && !props.error && !props.disabled ? props.color : props.baseColor;
  });
  const icon = computed$1u(() => model.value ? props.trueIcon : props.falseIcon);
  return {
    group,
    densityClasses,
    trueValue,
    falseValue,
    model,
    textColorClasses,
    textColorStyles,
    backgroundColorClasses,
    backgroundColorStyles,
    icon
  };
}
const VSelectionControl = genericComponent()({
  name: 'VSelectionControl',
  directives: {
    Ripple
  },
  inheritAttrs: false,
  props: makeVSelectionControlProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      attrs,
      slots
    } = _ref;
    const {
      group,
      densityClasses,
      icon,
      model,
      textColorClasses,
      textColorStyles,
      backgroundColorClasses,
      backgroundColorStyles,
      trueValue
    } = useSelectionControl(props);
    const uid = useId$b();
    const isFocused = shallowRef$E(false);
    const isFocusVisible = shallowRef$E(false);
    const input = ref$J();
    const id = toRef$N(() => props.id || `input-${uid}`);
    const isInteractive = toRef$N(() => !props.disabled && !props.readonly);
    group?.onForceUpdate(() => {
      if (input.value) {
        input.value.checked = model.value;
      }
    });
    function onFocus(e) {
      if (!isInteractive.value) return;
      isFocused.value = true;
      if (matchesSelector(e.target, ':focus-visible') !== false) {
        isFocusVisible.value = true;
      }
    }
    function onBlur() {
      isFocused.value = false;
      isFocusVisible.value = false;
    }
    function onClickLabel(e) {
      e.stopPropagation();
    }
    function onInput(e) {
      if (!isInteractive.value) {
        if (input.value) {
          // model value is not updated when input is not interactive
          // but the internal checked state of the input is still updated,
          // so here it's value is restored
          input.value.checked = model.value;
        }
        return;
      }
      if (props.readonly && group) {
        nextTick$n(() => group.forceUpdate());
      }
      model.value = e.target.checked;
    }
    useRender(() => {
      const label = slots.label ? slots.label({
        label: props.label,
        props: {
          for: id.value
        }
      }) : props.label;
      const [rootAttrs, inputAttrs] = filterInputAttrs(attrs);
      const inputNode = _createVNode$1_("input", _mergeProps$Z({
        "ref": input,
        "checked": model.value,
        "disabled": !!props.disabled,
        "id": id.value,
        "onBlur": onBlur,
        "onFocus": onFocus,
        "onInput": onInput,
        "aria-disabled": !!props.disabled,
        "aria-label": props.label,
        "type": props.type,
        "value": trueValue.value,
        "name": props.name,
        "aria-checked": props.type === 'checkbox' ? model.value : undefined
      }, inputAttrs), null);
      return _createVNode$1_("div", _mergeProps$Z({
        "class": ['v-selection-control', {
          'v-selection-control--dirty': model.value,
          'v-selection-control--disabled': props.disabled,
          'v-selection-control--error': props.error,
          'v-selection-control--focused': isFocused.value,
          'v-selection-control--focus-visible': isFocusVisible.value,
          'v-selection-control--inline': props.inline
        }, densityClasses.value, props.class]
      }, rootAttrs, {
        "style": props.style
      }), [_createVNode$1_("div", {
        "class": ['v-selection-control__wrapper', textColorClasses.value],
        "style": textColorStyles.value
      }, [slots.default?.({
        backgroundColorClasses,
        backgroundColorStyles
      }), _withDirectives$i(_createVNode$1_("div", {
        "class": ['v-selection-control__input']
      }, [slots.input?.({
        model,
        textColorClasses,
        textColorStyles,
        backgroundColorClasses,
        backgroundColorStyles,
        inputNode,
        icon: icon.value,
        props: {
          onFocus,
          onBlur,
          id: id.value
        }
      }) ?? _createVNode$1_(_Fragment$C, null, [icon.value && _createVNode$1_(VIcon, {
        "key": "icon",
        "icon": icon.value
      }, null), inputNode])]), [[_resolveDirective$b("ripple"), props.ripple && [!props.disabled && !props.readonly, null, ['center', 'circle']]]])]), label && _createVNode$1_(VLabel, {
        "for": id.value,
        "onClick": onClickLabel
      }, {
        default: () => [label]
      })]);
    });
    return {
      isFocused,
      input
    };
  }
});

const {mergeProps:_mergeProps$Y,createVNode:_createVNode$1Z} = await importShared('vue');
const {toRef: toRef$M} = await importShared('vue');
const makeVCheckboxBtnProps = propsFactory({
  indeterminate: Boolean,
  indeterminateIcon: {
    type: IconValue,
    default: '$checkboxIndeterminate'
  },
  ...makeVSelectionControlProps({
    falseIcon: '$checkboxOff',
    trueIcon: '$checkboxOn'
  })
}, 'VCheckboxBtn');
const VCheckboxBtn = genericComponent()({
  name: 'VCheckboxBtn',
  props: makeVCheckboxBtnProps(),
  emits: {
    'update:modelValue': value => true,
    'update:indeterminate': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const indeterminate = useProxiedModel(props, 'indeterminate');
    const model = useProxiedModel(props, 'modelValue');
    function onChange(v) {
      if (indeterminate.value) {
        indeterminate.value = false;
      }
    }
    const falseIcon = toRef$M(() => {
      return indeterminate.value ? props.indeterminateIcon : props.falseIcon;
    });
    const trueIcon = toRef$M(() => {
      return indeterminate.value ? props.indeterminateIcon : props.trueIcon;
    });
    useRender(() => {
      const controlProps = omit(VSelectionControl.filterProps(props), ['modelValue']);
      return _createVNode$1Z(VSelectionControl, _mergeProps$Y(controlProps, {
        "modelValue": model.value,
        "onUpdate:modelValue": [$event => model.value = $event, onChange],
        "class": ['v-checkbox-btn', props.class],
        "style": props.style,
        "type": "checkbox",
        "falseIcon": falseIcon.value,
        "trueIcon": trueIcon.value,
        "aria-checked": indeterminate.value ? 'mixed' : undefined
      }), slots);
    });
    return {};
  }
});

const {createVNode:_createVNode$1Y} = await importShared('vue');
function useInputIcon(props) {
  const {
    t
  } = useLocale();
  function InputIcon(_ref) {
    let {
      name,
      color
    } = _ref;
    const localeKey = {
      prepend: 'prependAction',
      prependInner: 'prependAction',
      append: 'appendAction',
      appendInner: 'appendAction',
      clear: 'clear'
    }[name];
    const listener = props[`onClick:${name}`];
    function onKeydown(e) {
      if (e.key !== 'Enter' && e.key !== ' ') return;
      e.preventDefault();
      e.stopPropagation();
      callEvent(listener, new PointerEvent('click', e));
    }
    const label = listener && localeKey ? t(`$vuetify.input.${localeKey}`, props.label ?? '') : undefined;
    return _createVNode$1Y(VIcon, {
      "icon": props[`${name}Icon`],
      "aria-label": label,
      "onClick": listener,
      "onKeydown": onKeydown,
      "color": color
    }, null);
  }
  return {
    InputIcon
  };
}

const {createVNode:_createVNode$1X} = await importShared('vue');
const {computed: computed$1t} = await importShared('vue');
const makeVMessagesProps = propsFactory({
  active: Boolean,
  color: String,
  messages: {
    type: [Array, String],
    default: () => []
  },
  ...makeComponentProps(),
  ...makeTransitionProps({
    transition: {
      component: VSlideYTransition,
      leaveAbsolute: true,
      group: true
    }
  })
}, 'VMessages');
const VMessages = genericComponent()({
  name: 'VMessages',
  props: makeVMessagesProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const messages = computed$1t(() => wrapInArray(props.messages));
    const {
      textColorClasses,
      textColorStyles
    } = useTextColor(() => props.color);
    useRender(() => _createVNode$1X(MaybeTransition, {
      "transition": props.transition,
      "tag": "div",
      "class": ['v-messages', textColorClasses.value, props.class],
      "style": [textColorStyles.value, props.style]
    }, {
      default: () => [props.active && messages.value.map((message, i) => _createVNode$1X("div", {
        "class": "v-messages__message",
        "key": `${i}-${messages.value}`
      }, [slots.message ? slots.message({
        message
      }) : message]))]
    }));
    return {};
  }
});

const {toRef: toRef$L} = await importShared('vue');
// Composables
const makeFocusProps = propsFactory({
  focused: Boolean,
  'onUpdate:focused': EventProp()
}, 'focus');
function useFocus(props) {
  let name = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : getCurrentInstanceName();
  const isFocused = useProxiedModel(props, 'focused');
  const focusClasses = toRef$L(() => {
    return {
      [`${name}--focused`]: isFocused.value
    };
  });
  function focus() {
    isFocused.value = true;
  }
  function blur() {
    isFocused.value = false;
  }
  return {
    focusClasses,
    isFocused,
    focus,
    blur
  };
}

const {computed: computed$1s,inject: inject$k,markRaw,provide: provide$e,ref: ref$I,shallowRef: shallowRef$D,toRef: toRef$K,watch: watch$A} = await importShared('vue');
const FormKey = Symbol.for('vuetify:form');
const makeFormProps = propsFactory({
  disabled: Boolean,
  fastFail: Boolean,
  readonly: Boolean,
  modelValue: {
    type: Boolean,
    default: null
  },
  validateOn: {
    type: String,
    default: 'input'
  }
}, 'form');
function createForm(props) {
  const model = useProxiedModel(props, 'modelValue');
  const isDisabled = toRef$K(() => props.disabled);
  const isReadonly = toRef$K(() => props.readonly);
  const isValidating = shallowRef$D(false);
  const items = ref$I([]);
  const errors = ref$I([]);
  async function validate() {
    const results = [];
    let valid = true;
    errors.value = [];
    isValidating.value = true;
    for (const item of items.value) {
      const itemErrorMessages = await item.validate();
      if (itemErrorMessages.length > 0) {
        valid = false;
        results.push({
          id: item.id,
          errorMessages: itemErrorMessages
        });
      }
      if (!valid && props.fastFail) break;
    }
    errors.value = results;
    isValidating.value = false;
    return {
      valid,
      errors: errors.value
    };
  }
  function reset() {
    items.value.forEach(item => item.reset());
  }
  function resetValidation() {
    items.value.forEach(item => item.resetValidation());
  }
  watch$A(items, () => {
    let valid = 0;
    let invalid = 0;
    const results = [];
    for (const item of items.value) {
      if (item.isValid === false) {
        invalid++;
        results.push({
          id: item.id,
          errorMessages: item.errorMessages
        });
      } else if (item.isValid === true) valid++;
    }
    errors.value = results;
    model.value = invalid > 0 ? false : valid === items.value.length ? true : null;
  }, {
    deep: true,
    flush: 'post'
  });
  provide$e(FormKey, {
    register: _ref => {
      let {
        id,
        vm,
        validate,
        reset,
        resetValidation
      } = _ref;
      if (items.value.some(item => item.id === id)) {
        consoleWarn(`Duplicate input name "${id}"`);
      }
      items.value.push({
        id,
        validate,
        reset,
        resetValidation,
        vm: markRaw(vm),
        isValid: null,
        errorMessages: []
      });
    },
    unregister: id => {
      items.value = items.value.filter(item => {
        return item.id !== id;
      });
    },
    update: (id, isValid, errorMessages) => {
      const found = items.value.find(item => item.id === id);
      if (!found) return;
      found.isValid = isValid;
      found.errorMessages = errorMessages;
    },
    isDisabled,
    isReadonly,
    isValidating,
    isValid: model,
    items,
    validateOn: toRef$K(() => props.validateOn)
  });
  return {
    errors,
    isDisabled,
    isReadonly,
    isValidating,
    isValid: model,
    items,
    validate,
    reset,
    resetValidation
  };
}
function useForm(props) {
  const form = inject$k(FormKey, null);
  return {
    ...form,
    isReadonly: computed$1s(() => !!(props?.readonly ?? form?.isReadonly.value)),
    isDisabled: computed$1s(() => !!(props?.disabled ?? form?.isDisabled.value))
  };
}

// Utilities
const {computed: computed$1r,inject: inject$j,toRef: toRef$J} = await importShared('vue');
const RulesSymbol = Symbol.for('vuetify:rules');
function useRules(fn) {
  const resolveRules = inject$j(RulesSymbol, null);
  if (!resolveRules) return toRef$J(fn);
  return resolveRules(fn);
}

const {computed: computed$1q,nextTick: nextTick$m,onBeforeMount: onBeforeMount$3,onBeforeUnmount: onBeforeUnmount$8,onMounted: onMounted$b,ref: ref$H,shallowRef: shallowRef$C,unref: unref$1,useId: useId$a,watch: watch$z} = await importShared('vue');
const makeValidationProps = propsFactory({
  disabled: {
    type: Boolean,
    default: null
  },
  error: Boolean,
  errorMessages: {
    type: [Array, String],
    default: () => []
  },
  maxErrors: {
    type: [Number, String],
    default: 1
  },
  name: String,
  label: String,
  readonly: {
    type: Boolean,
    default: null
  },
  rules: {
    type: Array,
    default: () => []
  },
  modelValue: null,
  validateOn: String,
  validationValue: null,
  ...makeFocusProps()
}, 'validation');
function useValidation(props) {
  let name = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : getCurrentInstanceName();
  let id = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : useId$a();
  const model = useProxiedModel(props, 'modelValue');
  const validationModel = computed$1q(() => props.validationValue === undefined ? model.value : props.validationValue);
  const form = useForm(props);
  const rules = useRules(() => props.rules);
  const internalErrorMessages = ref$H([]);
  const isPristine = shallowRef$C(true);
  const isDirty = computed$1q(() => !!(wrapInArray(model.value === '' ? null : model.value).length || wrapInArray(validationModel.value === '' ? null : validationModel.value).length));
  const errorMessages = computed$1q(() => {
    return props.errorMessages?.length ? wrapInArray(props.errorMessages).concat(internalErrorMessages.value).slice(0, Math.max(0, Number(props.maxErrors))) : internalErrorMessages.value;
  });
  const validateOn = computed$1q(() => {
    let value = (props.validateOn ?? form.validateOn?.value) || 'input';
    if (value === 'lazy') value = 'input lazy';
    if (value === 'eager') value = 'input eager';
    const set = new Set(value?.split(' ') ?? []);
    return {
      input: set.has('input'),
      blur: set.has('blur') || set.has('input') || set.has('invalid-input'),
      invalidInput: set.has('invalid-input'),
      lazy: set.has('lazy'),
      eager: set.has('eager')
    };
  });
  const isValid = computed$1q(() => {
    if (props.error || props.errorMessages?.length) return false;
    if (!props.rules.length) return true;
    if (isPristine.value) {
      return internalErrorMessages.value.length || validateOn.value.lazy ? null : true;
    } else {
      return !internalErrorMessages.value.length;
    }
  });
  const isValidating = shallowRef$C(false);
  const validationClasses = computed$1q(() => {
    return {
      [`${name}--error`]: isValid.value === false,
      [`${name}--dirty`]: isDirty.value,
      [`${name}--disabled`]: form.isDisabled.value,
      [`${name}--readonly`]: form.isReadonly.value
    };
  });
  const vm = getCurrentInstance('validation');
  const uid = computed$1q(() => props.name ?? unref$1(id));
  onBeforeMount$3(() => {
    form.register?.({
      id: uid.value,
      vm,
      validate,
      reset,
      resetValidation
    });
  });
  onBeforeUnmount$8(() => {
    form.unregister?.(uid.value);
  });
  onMounted$b(async () => {
    if (!validateOn.value.lazy) {
      await validate(!validateOn.value.eager);
    }
    form.update?.(uid.value, isValid.value, errorMessages.value);
  });
  useToggleScope(() => validateOn.value.input || validateOn.value.invalidInput && isValid.value === false, () => {
    watch$z(validationModel, () => {
      if (validationModel.value != null) {
        validate();
      } else if (props.focused) {
        const unwatch = watch$z(() => props.focused, val => {
          if (!val) validate();
          unwatch();
        });
      }
    });
  });
  useToggleScope(() => validateOn.value.blur, () => {
    watch$z(() => props.focused, val => {
      if (!val) validate();
    });
  });
  watch$z([isValid, errorMessages], () => {
    form.update?.(uid.value, isValid.value, errorMessages.value);
  });
  async function reset() {
    model.value = null;
    await nextTick$m();
    await resetValidation();
  }
  async function resetValidation() {
    isPristine.value = true;
    if (!validateOn.value.lazy) {
      await validate(!validateOn.value.eager);
    } else {
      internalErrorMessages.value = [];
    }
  }
  async function validate() {
    let silent = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;
    const results = [];
    isValidating.value = true;
    for (const rule of rules.value) {
      if (results.length >= Number(props.maxErrors ?? 1)) {
        break;
      }
      const handler = typeof rule === 'function' ? rule : () => rule;
      const result = await handler(validationModel.value);
      if (result === true) continue;
      if (result !== false && typeof result !== 'string') {
        // eslint-disable-next-line no-console
        console.warn(`${result} is not a valid value. Rule functions must return boolean true or a string.`);
        continue;
      }
      results.push(result || '');
    }
    internalErrorMessages.value = results;
    isValidating.value = false;
    isPristine.value = silent;
    return internalErrorMessages.value;
  }
  return {
    errorMessages,
    isDirty,
    isDisabled: form.isDisabled,
    isReadonly: form.isReadonly,
    isPristine,
    isValid,
    isValidating,
    reset,
    resetValidation,
    validate,
    validationClasses
  };
}

const {createVNode:_createVNode$1W} = await importShared('vue');
const {computed: computed$1p,toRef: toRef$I,useId: useId$9} = await importShared('vue');
const makeVInputProps = propsFactory({
  id: String,
  appendIcon: IconValue,
  baseColor: String,
  centerAffix: {
    type: Boolean,
    default: true
  },
  color: String,
  glow: Boolean,
  iconColor: [Boolean, String],
  prependIcon: IconValue,
  hideDetails: [Boolean, String],
  hideSpinButtons: Boolean,
  hint: String,
  persistentHint: Boolean,
  messages: {
    type: [Array, String],
    default: () => []
  },
  direction: {
    type: String,
    default: 'horizontal',
    validator: v => ['horizontal', 'vertical'].includes(v)
  },
  'onClick:prepend': EventProp(),
  'onClick:append': EventProp(),
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...pick(makeDimensionProps(), ['maxWidth', 'minWidth', 'width']),
  ...makeThemeProps(),
  ...makeValidationProps()
}, 'VInput');
const VInput = genericComponent()({
  name: 'VInput',
  props: {
    ...makeVInputProps()
  },
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      attrs,
      slots,
      emit
    } = _ref;
    const {
      densityClasses
    } = useDensity(props);
    const {
      dimensionStyles
    } = useDimension(props);
    const {
      themeClasses
    } = provideTheme(props);
    const {
      rtlClasses
    } = useRtl();
    const {
      InputIcon
    } = useInputIcon(props);
    const uid = useId$9();
    const id = computed$1p(() => props.id || `input-${uid}`);
    const messagesId = computed$1p(() => `${id.value}-messages`);
    const {
      errorMessages,
      isDirty,
      isDisabled,
      isReadonly,
      isPristine,
      isValid,
      isValidating,
      reset,
      resetValidation,
      validate,
      validationClasses
    } = useValidation(props, 'v-input', id);
    const slotProps = computed$1p(() => ({
      id,
      messagesId,
      isDirty,
      isDisabled,
      isReadonly,
      isPristine,
      isValid,
      isValidating,
      reset,
      resetValidation,
      validate
    }));
    const color = toRef$I(() => {
      return props.error || props.disabled ? undefined : props.focused ? props.color : props.baseColor;
    });
    const iconColor = toRef$I(() => {
      if (!props.iconColor) return undefined;
      return props.iconColor === true ? color.value : props.iconColor;
    });
    const messages = computed$1p(() => {
      if (props.errorMessages?.length || !isPristine.value && errorMessages.value.length) {
        return errorMessages.value;
      } else if (props.hint && (props.persistentHint || props.focused)) {
        return props.hint;
      } else {
        return props.messages;
      }
    });
    useRender(() => {
      const hasPrepend = !!(slots.prepend || props.prependIcon);
      const hasAppend = !!(slots.append || props.appendIcon);
      const hasMessages = messages.value.length > 0;
      const hasDetails = !props.hideDetails || props.hideDetails === 'auto' && (hasMessages || !!slots.details);
      return _createVNode$1W("div", {
        "class": ['v-input', `v-input--${props.direction}`, {
          'v-input--center-affix': props.centerAffix,
          'v-input--focused': props.focused,
          'v-input--glow': props.glow,
          'v-input--hide-spin-buttons': props.hideSpinButtons
        }, densityClasses.value, themeClasses.value, rtlClasses.value, validationClasses.value, props.class],
        "style": [dimensionStyles.value, props.style]
      }, [hasPrepend && _createVNode$1W("div", {
        "key": "prepend",
        "class": "v-input__prepend"
      }, [slots.prepend?.(slotProps.value), props.prependIcon && _createVNode$1W(InputIcon, {
        "key": "prepend-icon",
        "name": "prepend",
        "color": iconColor.value
      }, null)]), slots.default && _createVNode$1W("div", {
        "class": "v-input__control"
      }, [slots.default?.(slotProps.value)]), hasAppend && _createVNode$1W("div", {
        "key": "append",
        "class": "v-input__append"
      }, [props.appendIcon && _createVNode$1W(InputIcon, {
        "key": "append-icon",
        "name": "append",
        "color": iconColor.value
      }, null), slots.append?.(slotProps.value)]), hasDetails && _createVNode$1W("div", {
        "id": messagesId.value,
        "class": "v-input__details",
        "role": "alert",
        "aria-live": "polite"
      }, [_createVNode$1W(VMessages, {
        "active": hasMessages,
        "messages": messages.value
      }, {
        message: slots.message
      }), slots.details?.(slotProps.value)])]);
    });
    return {
      reset,
      resetValidation,
      validate,
      isValid,
      errorMessages
    };
  }
});

const {mergeProps:_mergeProps$X,createVNode:_createVNode$1V} = await importShared('vue');
const {useId: useId$8} = await importShared('vue');
const makeVCheckboxProps = propsFactory({
  ...makeVInputProps(),
  ...omit(makeVCheckboxBtnProps(), ['inline'])
}, 'VCheckbox');
const VCheckbox = genericComponent()({
  name: 'VCheckbox',
  inheritAttrs: false,
  props: makeVCheckboxProps(),
  emits: {
    'update:modelValue': value => true,
    'update:focused': focused => true
  },
  setup(props, _ref) {
    let {
      attrs,
      slots
    } = _ref;
    const model = useProxiedModel(props, 'modelValue');
    const {
      isFocused,
      focus,
      blur
    } = useFocus(props);
    const uid = useId$8();
    useRender(() => {
      const [rootAttrs, controlAttrs] = filterInputAttrs(attrs);
      const inputProps = VInput.filterProps(props);
      const checkboxProps = VCheckboxBtn.filterProps(props);
      return _createVNode$1V(VInput, _mergeProps$X({
        "class": ['v-checkbox', props.class]
      }, rootAttrs, inputProps, {
        "modelValue": model.value,
        "onUpdate:modelValue": $event => model.value = $event,
        "id": props.id || `checkbox-${uid}`,
        "focused": isFocused.value,
        "style": props.style
      }), {
        ...slots,
        default: _ref2 => {
          let {
            id,
            messagesId,
            isDisabled,
            isReadonly,
            isValid
          } = _ref2;
          return _createVNode$1V(VCheckboxBtn, _mergeProps$X(checkboxProps, {
            "id": id.value,
            "aria-describedby": messagesId.value,
            "disabled": isDisabled.value,
            "readonly": isReadonly.value
          }, controlAttrs, {
            "error": isValid.value === false,
            "modelValue": model.value,
            "onUpdate:modelValue": $event => model.value = $event,
            "onFocus": focus,
            "onBlur": blur
          }), slots);
        }
      });
    });
    return {};
  }
});

function calculateUpdatedTarget(_ref) {
  let {
    selectedElement,
    containerElement,
    isRtl,
    isHorizontal
  } = _ref;
  const containerSize = getOffsetSize(isHorizontal, containerElement);
  const scrollPosition = getScrollPosition(isHorizontal, isRtl, containerElement);
  const childrenSize = getOffsetSize(isHorizontal, selectedElement);
  const childrenStartPosition = getOffsetPosition(isHorizontal, selectedElement);
  const additionalOffset = childrenSize * 0.4;
  if (scrollPosition > childrenStartPosition) {
    return childrenStartPosition - additionalOffset;
  } else if (scrollPosition + containerSize < childrenStartPosition + childrenSize) {
    return childrenStartPosition - containerSize + childrenSize + additionalOffset;
  }
  return scrollPosition;
}
function calculateCenteredTarget(_ref2) {
  let {
    selectedElement,
    containerElement,
    isHorizontal
  } = _ref2;
  const containerOffsetSize = getOffsetSize(isHorizontal, containerElement);
  const childrenOffsetPosition = getOffsetPosition(isHorizontal, selectedElement);
  const childrenOffsetSize = getOffsetSize(isHorizontal, selectedElement);
  return childrenOffsetPosition - containerOffsetSize / 2 + childrenOffsetSize / 2;
}
function getScrollSize(isHorizontal, element) {
  const key = isHorizontal ? 'scrollWidth' : 'scrollHeight';
  return element?.[key] || 0;
}
function getClientSize(isHorizontal, element) {
  const key = isHorizontal ? 'clientWidth' : 'clientHeight';
  return element?.[key] || 0;
}
function getScrollPosition(isHorizontal, rtl, element) {
  if (!element) {
    return 0;
  }
  const {
    scrollLeft,
    offsetWidth,
    scrollWidth
  } = element;
  if (isHorizontal) {
    return rtl ? scrollWidth - offsetWidth + scrollLeft : scrollLeft;
  }
  return element.scrollTop;
}
function getOffsetSize(isHorizontal, element) {
  const key = isHorizontal ? 'offsetWidth' : 'offsetHeight';
  return element?.[key] || 0;
}
function getOffsetPosition(isHorizontal, element) {
  const key = isHorizontal ? 'offsetLeft' : 'offsetTop';
  return element?.[key] || 0;
}

const {createVNode:_createVNode$1U} = await importShared('vue');
const {computed: computed$1o,shallowRef: shallowRef$B,watch: watch$y} = await importShared('vue');
const VSlideGroupSymbol = Symbol.for('vuetify:v-slide-group');
const makeVSlideGroupProps = propsFactory({
  centerActive: Boolean,
  direction: {
    type: String,
    default: 'horizontal'
  },
  symbol: {
    type: null,
    default: VSlideGroupSymbol
  },
  nextIcon: {
    type: IconValue,
    default: '$next'
  },
  prevIcon: {
    type: IconValue,
    default: '$prev'
  },
  showArrows: {
    type: [Boolean, String],
    validator: v => typeof v === 'boolean' || ['always', 'desktop', 'mobile'].includes(v)
  },
  ...makeComponentProps(),
  ...makeDisplayProps({
    mobile: null
  }),
  ...makeTagProps(),
  ...makeGroupProps({
    selectedClass: 'v-slide-group-item--active'
  })
}, 'VSlideGroup');
const VSlideGroup = genericComponent()({
  name: 'VSlideGroup',
  props: makeVSlideGroupProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      isRtl
    } = useRtl();
    const {
      displayClasses,
      mobile
    } = useDisplay(props);
    const group = useGroup(props, props.symbol);
    const isOverflowing = shallowRef$B(false);
    const scrollOffset = shallowRef$B(0);
    const containerSize = shallowRef$B(0);
    const contentSize = shallowRef$B(0);
    const isHorizontal = computed$1o(() => props.direction === 'horizontal');
    const {
      resizeRef: containerRef,
      contentRect: containerRect
    } = useResizeObserver();
    const {
      resizeRef: contentRef,
      contentRect
    } = useResizeObserver();
    const goTo = useGoTo();
    const goToOptions = computed$1o(() => {
      return {
        container: containerRef.el,
        duration: 200,
        easing: 'easeOutQuart'
      };
    });
    const firstSelectedIndex = computed$1o(() => {
      if (!group.selected.value.length) return -1;
      return group.items.value.findIndex(item => item.id === group.selected.value[0]);
    });
    const lastSelectedIndex = computed$1o(() => {
      if (!group.selected.value.length) return -1;
      return group.items.value.findIndex(item => item.id === group.selected.value[group.selected.value.length - 1]);
    });
    if (IN_BROWSER) {
      let frame = -1;
      watch$y(() => [group.selected.value, containerRect.value, contentRect.value, isHorizontal.value], () => {
        cancelAnimationFrame(frame);
        frame = requestAnimationFrame(() => {
          if (containerRect.value && contentRect.value) {
            const sizeProperty = isHorizontal.value ? 'width' : 'height';
            containerSize.value = containerRect.value[sizeProperty];
            contentSize.value = contentRect.value[sizeProperty];
            isOverflowing.value = containerSize.value + 1 < contentSize.value;
          }
          if (firstSelectedIndex.value >= 0 && contentRef.el) {
            // TODO: Is this too naive? Should we store element references in group composable?
            const selectedElement = contentRef.el.children[lastSelectedIndex.value];
            scrollToChildren(selectedElement, props.centerActive);
          }
        });
      });
    }
    const isFocused = shallowRef$B(false);
    function scrollToChildren(children, center) {
      let target = 0;
      if (center) {
        target = calculateCenteredTarget({
          containerElement: containerRef.el,
          isHorizontal: isHorizontal.value,
          selectedElement: children
        });
      } else {
        target = calculateUpdatedTarget({
          containerElement: containerRef.el,
          isHorizontal: isHorizontal.value,
          isRtl: isRtl.value,
          selectedElement: children
        });
      }
      scrollToPosition(target);
    }
    function scrollToPosition(newPosition) {
      if (!IN_BROWSER || !containerRef.el) return;
      const offsetSize = getOffsetSize(isHorizontal.value, containerRef.el);
      const scrollPosition = getScrollPosition(isHorizontal.value, isRtl.value, containerRef.el);
      const scrollSize = getScrollSize(isHorizontal.value, containerRef.el);
      if (scrollSize <= offsetSize ||
      // Prevent scrolling by only a couple of pixels, which doesn't look smooth
      Math.abs(newPosition - scrollPosition) < 16) return;
      if (isHorizontal.value && isRtl.value && containerRef.el) {
        const {
          scrollWidth,
          offsetWidth: containerWidth
        } = containerRef.el;
        newPosition = scrollWidth - containerWidth - newPosition;
      }
      if (isHorizontal.value) {
        goTo.horizontal(newPosition, goToOptions.value);
      } else {
        goTo(newPosition, goToOptions.value);
      }
    }
    function onScroll(e) {
      const {
        scrollTop,
        scrollLeft
      } = e.target;
      scrollOffset.value = isHorizontal.value ? scrollLeft : scrollTop;
    }
    function onFocusin(e) {
      isFocused.value = true;
      if (!isOverflowing.value || !contentRef.el) return;

      // Focused element is likely to be the root of an item, so a
      // breadth-first search will probably find it in the first iteration
      for (const el of e.composedPath()) {
        for (const item of contentRef.el.children) {
          if (item === el) {
            scrollToChildren(item);
            return;
          }
        }
      }
    }
    function onFocusout(e) {
      isFocused.value = false;
    }

    // Affix clicks produce onFocus that we have to ignore to avoid extra scrollToChildren
    let ignoreFocusEvent = false;
    function onFocus(e) {
      if (!ignoreFocusEvent && !isFocused.value && !(e.relatedTarget && contentRef.el?.contains(e.relatedTarget))) focus();
      ignoreFocusEvent = false;
    }
    function onFocusAffixes() {
      ignoreFocusEvent = true;
    }
    function onKeydown(e) {
      if (!contentRef.el) return;
      function toFocus(location) {
        e.preventDefault();
        focus(location);
      }
      if (isHorizontal.value) {
        if (e.key === 'ArrowRight') {
          toFocus(isRtl.value ? 'prev' : 'next');
        } else if (e.key === 'ArrowLeft') {
          toFocus(isRtl.value ? 'next' : 'prev');
        }
      } else {
        if (e.key === 'ArrowDown') {
          toFocus('next');
        } else if (e.key === 'ArrowUp') {
          toFocus('prev');
        }
      }
      if (e.key === 'Home') {
        toFocus('first');
      } else if (e.key === 'End') {
        toFocus('last');
      }
    }
    function getSiblingElement(el, location) {
      if (!el) return undefined;
      let sibling = el;
      do {
        sibling = sibling?.[location === 'next' ? 'nextElementSibling' : 'previousElementSibling'];
      } while (sibling?.hasAttribute('disabled'));
      return sibling;
    }
    function focus(location) {
      if (!contentRef.el) return;
      let el;
      if (!location) {
        const focusable = focusableChildren(contentRef.el);
        el = focusable[0];
      } else if (location === 'next') {
        el = getSiblingElement(contentRef.el.querySelector(':focus'), location);
        if (!el) return focus('first');
      } else if (location === 'prev') {
        el = getSiblingElement(contentRef.el.querySelector(':focus'), location);
        if (!el) return focus('last');
      } else if (location === 'first') {
        el = contentRef.el.firstElementChild;
        if (el?.hasAttribute('disabled')) el = getSiblingElement(el, 'next');
      } else if (location === 'last') {
        el = contentRef.el.lastElementChild;
        if (el?.hasAttribute('disabled')) el = getSiblingElement(el, 'prev');
      }
      if (el) {
        el.focus({
          preventScroll: true
        });
      }
    }
    function scrollTo(location) {
      const direction = isHorizontal.value && isRtl.value ? -1 : 1;
      const offsetStep = (location === 'prev' ? -direction : direction) * containerSize.value;
      let newPosition = scrollOffset.value + offsetStep;

      // TODO: improve it
      if (isHorizontal.value && isRtl.value && containerRef.el) {
        const {
          scrollWidth,
          offsetWidth: containerWidth
        } = containerRef.el;
        newPosition += scrollWidth - containerWidth;
      }
      scrollToPosition(newPosition);
    }
    const slotProps = computed$1o(() => ({
      next: group.next,
      prev: group.prev,
      select: group.select,
      isSelected: group.isSelected
    }));
    const hasAffixes = computed$1o(() => {
      switch (props.showArrows) {
        // Always show arrows on desktop & mobile
        case 'always':
          return true;

        // Always show arrows on desktop
        case 'desktop':
          return !mobile.value;

        // Show arrows on mobile when overflowing.
        // This matches the default 2.2 behavior
        case true:
          return isOverflowing.value || Math.abs(scrollOffset.value) > 0;

        // Always show on mobile
        case 'mobile':
          return mobile.value || isOverflowing.value || Math.abs(scrollOffset.value) > 0;

        // https://material.io/components/tabs#scrollable-tabs
        // Always show arrows when
        // overflowed on desktop
        default:
          return !mobile.value && (isOverflowing.value || Math.abs(scrollOffset.value) > 0);
      }
    });
    const hasPrev = computed$1o(() => {
      // 1 pixel in reserve, may be lost after rounding
      return Math.abs(scrollOffset.value) > 1;
    });
    const hasNext = computed$1o(() => {
      if (!containerRef.value) return false;
      const scrollSize = getScrollSize(isHorizontal.value, containerRef.el);
      const clientSize = getClientSize(isHorizontal.value, containerRef.el);
      const scrollSizeMax = scrollSize - clientSize;

      // 1 pixel in reserve, may be lost after rounding
      return scrollSizeMax - Math.abs(scrollOffset.value) > 1;
    });
    useRender(() => _createVNode$1U(props.tag, {
      "class": ['v-slide-group', {
        'v-slide-group--vertical': !isHorizontal.value,
        'v-slide-group--has-affixes': hasAffixes.value,
        'v-slide-group--is-overflowing': isOverflowing.value
      }, displayClasses.value, props.class],
      "style": props.style,
      "tabindex": isFocused.value || group.selected.value.length ? -1 : 0,
      "onFocus": onFocus
    }, {
      default: () => [hasAffixes.value && _createVNode$1U("div", {
        "key": "prev",
        "class": ['v-slide-group__prev', {
          'v-slide-group__prev--disabled': !hasPrev.value
        }],
        "onMousedown": onFocusAffixes,
        "onClick": () => hasPrev.value && scrollTo('prev')
      }, [slots.prev?.(slotProps.value) ?? _createVNode$1U(VFadeTransition, null, {
        default: () => [_createVNode$1U(VIcon, {
          "icon": isRtl.value ? props.nextIcon : props.prevIcon
        }, null)]
      })]), _createVNode$1U("div", {
        "key": "container",
        "ref": containerRef,
        "class": "v-slide-group__container",
        "onScroll": onScroll
      }, [_createVNode$1U("div", {
        "ref": contentRef,
        "class": "v-slide-group__content",
        "onFocusin": onFocusin,
        "onFocusout": onFocusout,
        "onKeydown": onKeydown
      }, [slots.default?.(slotProps.value)])]), hasAffixes.value && _createVNode$1U("div", {
        "key": "next",
        "class": ['v-slide-group__next', {
          'v-slide-group__next--disabled': !hasNext.value
        }],
        "onMousedown": onFocusAffixes,
        "onClick": () => hasNext.value && scrollTo('next')
      }, [slots.next?.(slotProps.value) ?? _createVNode$1U(VFadeTransition, null, {
        default: () => [_createVNode$1U(VIcon, {
          "icon": isRtl.value ? props.prevIcon : props.nextIcon
        }, null)]
      })])]
    }));
    return {
      selected: group.selected,
      scrollTo,
      scrollOffset,
      focus,
      hasPrev,
      hasNext
    };
  }
});

const {mergeProps:_mergeProps$W,createVNode:_createVNode$1T} = await importShared('vue');
const {toRef: toRef$H} = await importShared('vue');
const VChipGroupSymbol = Symbol.for('vuetify:v-chip-group');
const makeVChipGroupProps = propsFactory({
  baseColor: String,
  column: Boolean,
  filter: Boolean,
  valueComparator: {
    type: Function,
    default: deepEqual
  },
  ...makeVSlideGroupProps(),
  ...makeComponentProps(),
  ...makeGroupProps({
    selectedClass: 'v-chip--selected'
  }),
  ...makeTagProps(),
  ...makeThemeProps(),
  ...makeVariantProps({
    variant: 'tonal'
  })
}, 'VChipGroup');
const VChipGroup = genericComponent()({
  name: 'VChipGroup',
  props: makeVChipGroupProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      themeClasses
    } = provideTheme(props);
    const {
      isSelected,
      select,
      next,
      prev,
      selected
    } = useGroup(props, VChipGroupSymbol);
    provideDefaults({
      VChip: {
        baseColor: toRef$H(() => props.baseColor),
        color: toRef$H(() => props.color),
        disabled: toRef$H(() => props.disabled),
        filter: toRef$H(() => props.filter),
        variant: toRef$H(() => props.variant)
      }
    });
    useRender(() => {
      const slideGroupProps = VSlideGroup.filterProps(props);
      return _createVNode$1T(VSlideGroup, _mergeProps$W(slideGroupProps, {
        "class": ['v-chip-group', {
          'v-chip-group--column': props.column
        }, themeClasses.value, props.class],
        "style": props.style
      }), {
        default: () => [slots.default?.({
          isSelected,
          select,
          next,
          prev,
          selected: selected.value
        })]
      });
    });
    return {};
  }
});

const {createVNode:_createVNode$1S,vShow:_vShow$9,withDirectives:_withDirectives$h,Fragment:_Fragment$B,mergeProps:_mergeProps$V,resolveDirective:_resolveDirective$a} = await importShared('vue');
const {computed: computed$1n,toDisplayString: toDisplayString$3,toRef: toRef$G} = await importShared('vue');
const makeVChipProps = propsFactory({
  activeClass: String,
  appendAvatar: String,
  appendIcon: IconValue,
  baseColor: String,
  closable: Boolean,
  closeIcon: {
    type: IconValue,
    default: '$delete'
  },
  closeLabel: {
    type: String,
    default: '$vuetify.close'
  },
  draggable: Boolean,
  filter: Boolean,
  filterIcon: {
    type: IconValue,
    default: '$complete'
  },
  label: Boolean,
  link: {
    type: Boolean,
    default: undefined
  },
  pill: Boolean,
  prependAvatar: String,
  prependIcon: IconValue,
  ripple: {
    type: [Boolean, Object],
    default: true
  },
  text: {
    type: [String, Number, Boolean],
    default: undefined
  },
  modelValue: {
    type: Boolean,
    default: true
  },
  onClick: EventProp(),
  onClickOnce: EventProp(),
  ...makeBorderProps(),
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeElevationProps(),
  ...makeGroupItemProps(),
  ...makeRoundedProps(),
  ...makeRouterProps(),
  ...makeSizeProps(),
  ...makeTagProps({
    tag: 'span'
  }),
  ...makeThemeProps(),
  ...makeVariantProps({
    variant: 'tonal'
  })
}, 'VChip');
const VChip = genericComponent()({
  name: 'VChip',
  directives: {
    Ripple
  },
  props: makeVChipProps(),
  emits: {
    'click:close': e => true,
    'update:modelValue': value => true,
    'group:selected': val => true,
    click: e => true
  },
  setup(props, _ref) {
    let {
      attrs,
      emit,
      slots
    } = _ref;
    const {
      t
    } = useLocale();
    const {
      borderClasses
    } = useBorder(props);
    const {
      densityClasses
    } = useDensity(props);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      roundedClasses
    } = useRounded(props);
    const {
      sizeClasses
    } = useSize(props);
    const {
      themeClasses
    } = provideTheme(props);
    const isActive = useProxiedModel(props, 'modelValue');
    const group = useGroupItem(props, VChipGroupSymbol, false);
    const link = useLink(props, attrs);
    const isLink = toRef$G(() => props.link !== false && link.isLink.value);
    const isClickable = computed$1n(() => !props.disabled && props.link !== false && (!!group || props.link || link.isClickable.value));
    const closeProps = toRef$G(() => ({
      'aria-label': t(props.closeLabel),
      onClick(e) {
        e.preventDefault();
        e.stopPropagation();
        isActive.value = false;
        emit('click:close', e);
      }
    }));
    const {
      colorClasses,
      colorStyles,
      variantClasses
    } = useVariant(() => {
      const showColor = !group || group.isSelected.value;
      return {
        color: showColor ? props.color ?? props.baseColor : props.baseColor,
        variant: props.variant
      };
    });
    function onClick(e) {
      emit('click', e);
      if (!isClickable.value) return;
      link.navigate?.(e);
      group?.toggle();
    }
    function onKeyDown(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        onClick(e);
      }
    }
    return () => {
      const Tag = link.isLink.value ? 'a' : props.tag;
      const hasAppendMedia = !!(props.appendIcon || props.appendAvatar);
      const hasAppend = !!(hasAppendMedia || slots.append);
      const hasClose = !!(slots.close || props.closable);
      const hasFilter = !!(slots.filter || props.filter) && group;
      const hasPrependMedia = !!(props.prependIcon || props.prependAvatar);
      const hasPrepend = !!(hasPrependMedia || slots.prepend);
      return isActive.value && _withDirectives$h(_createVNode$1S(Tag, _mergeProps$V({
        "class": ['v-chip', {
          'v-chip--disabled': props.disabled,
          'v-chip--label': props.label,
          'v-chip--link': isClickable.value,
          'v-chip--filter': hasFilter,
          'v-chip--pill': props.pill,
          [`${props.activeClass}`]: props.activeClass && link.isActive?.value
        }, themeClasses.value, borderClasses.value, colorClasses.value, densityClasses.value, elevationClasses.value, roundedClasses.value, sizeClasses.value, variantClasses.value, group?.selectedClass.value, props.class],
        "style": [colorStyles.value, props.style],
        "disabled": props.disabled || undefined,
        "draggable": props.draggable,
        "tabindex": isClickable.value ? 0 : undefined,
        "onClick": onClick,
        "onKeydown": isClickable.value && !isLink.value && onKeyDown
      }, link.linkProps), {
        default: () => [genOverlays(isClickable.value, 'v-chip'), hasFilter && _createVNode$1S(VExpandXTransition, {
          "key": "filter"
        }, {
          default: () => [_withDirectives$h(_createVNode$1S("div", {
            "class": "v-chip__filter"
          }, [!slots.filter ? _createVNode$1S(VIcon, {
            "key": "filter-icon",
            "icon": props.filterIcon
          }, null) : _createVNode$1S(VDefaultsProvider, {
            "key": "filter-defaults",
            "disabled": !props.filterIcon,
            "defaults": {
              VIcon: {
                icon: props.filterIcon
              }
            }
          }, slots.filter)]), [[_vShow$9, group.isSelected.value]])]
        }), hasPrepend && _createVNode$1S("div", {
          "key": "prepend",
          "class": "v-chip__prepend"
        }, [!slots.prepend ? _createVNode$1S(_Fragment$B, null, [props.prependIcon && _createVNode$1S(VIcon, {
          "key": "prepend-icon",
          "icon": props.prependIcon,
          "start": true
        }, null), props.prependAvatar && _createVNode$1S(VAvatar, {
          "key": "prepend-avatar",
          "image": props.prependAvatar,
          "start": true
        }, null)]) : _createVNode$1S(VDefaultsProvider, {
          "key": "prepend-defaults",
          "disabled": !hasPrependMedia,
          "defaults": {
            VAvatar: {
              image: props.prependAvatar,
              start: true
            },
            VIcon: {
              icon: props.prependIcon,
              start: true
            }
          }
        }, slots.prepend)]), _createVNode$1S("div", {
          "class": "v-chip__content",
          "data-no-activator": ""
        }, [slots.default?.({
          isSelected: group?.isSelected.value,
          selectedClass: group?.selectedClass.value,
          select: group?.select,
          toggle: group?.toggle,
          value: group?.value.value,
          disabled: props.disabled
        }) ?? toDisplayString$3(props.text)]), hasAppend && _createVNode$1S("div", {
          "key": "append",
          "class": "v-chip__append"
        }, [!slots.append ? _createVNode$1S(_Fragment$B, null, [props.appendIcon && _createVNode$1S(VIcon, {
          "key": "append-icon",
          "end": true,
          "icon": props.appendIcon
        }, null), props.appendAvatar && _createVNode$1S(VAvatar, {
          "key": "append-avatar",
          "end": true,
          "image": props.appendAvatar
        }, null)]) : _createVNode$1S(VDefaultsProvider, {
          "key": "append-defaults",
          "disabled": !hasAppendMedia,
          "defaults": {
            VAvatar: {
              end: true,
              image: props.appendAvatar
            },
            VIcon: {
              end: true,
              icon: props.appendIcon
            }
          }
        }, slots.append)]), hasClose && _createVNode$1S("button", _mergeProps$V({
          "key": "close",
          "class": "v-chip__close",
          "type": "button",
          "data-testid": "close-chip"
        }, closeProps.value), [!slots.close ? _createVNode$1S(VIcon, {
          "key": "close-icon",
          "icon": props.closeIcon,
          "size": "x-small"
        }, null) : _createVNode$1S(VDefaultsProvider, {
          "key": "close-defaults",
          "defaults": {
            VIcon: {
              icon: props.closeIcon,
              size: 'x-small'
            }
          }
        }, slots.close)])]
      }), [[_resolveDirective$a("ripple"), isClickable.value && props.ripple, null]]);
    };
  }
});

// Utilities
const {computed: computed$1m,inject: inject$i,provide: provide$d,shallowRef: shallowRef$A} = await importShared('vue');

// List
const ListKey = Symbol.for('vuetify:list');
function createList() {
  const parent = inject$i(ListKey, {
    hasPrepend: shallowRef$A(false),
    updateHasPrepend: () => null
  });
  const data = {
    hasPrepend: shallowRef$A(false),
    updateHasPrepend: value => {
      if (value) data.hasPrepend.value = value;
    }
  };
  provide$d(ListKey, data);
  return parent;
}
function useList() {
  return inject$i(ListKey, null);
}

/* eslint-disable sonarjs/no-identical-functions */
// Utilities
const {toRaw: toRaw$4} = await importShared('vue');
const independentActiveStrategy = mandatory => {
  const strategy = {
    activate: _ref => {
      let {
        id,
        value,
        activated
      } = _ref;
      id = toRaw$4(id);

      // When mandatory and we're trying to deselect when id
      // is the only currently selected item then do nothing
      if (mandatory && !value && activated.size === 1 && activated.has(id)) return activated;
      if (value) {
        activated.add(id);
      } else {
        activated.delete(id);
      }
      return activated;
    },
    in: (v, children, parents) => {
      let set = new Set();
      if (v != null) {
        for (const id of wrapInArray(v)) {
          set = strategy.activate({
            id,
            value: true,
            activated: new Set(set),
            children,
            parents
          });
        }
      }
      return set;
    },
    out: v => {
      return Array.from(v);
    }
  };
  return strategy;
};
const independentSingleActiveStrategy = mandatory => {
  const parentStrategy = independentActiveStrategy(mandatory);
  const strategy = {
    activate: _ref2 => {
      let {
        activated,
        id,
        ...rest
      } = _ref2;
      id = toRaw$4(id);
      const singleSelected = activated.has(id) ? new Set([id]) : new Set();
      return parentStrategy.activate({
        ...rest,
        id,
        activated: singleSelected
      });
    },
    in: (v, children, parents) => {
      let set = new Set();
      if (v != null) {
        const arr = wrapInArray(v);
        if (arr.length) {
          set = parentStrategy.in(arr.slice(0, 1), children, parents);
        }
      }
      return set;
    },
    out: (v, children, parents) => {
      return parentStrategy.out(v, children, parents);
    }
  };
  return strategy;
};
const leafActiveStrategy = mandatory => {
  const parentStrategy = independentActiveStrategy(mandatory);
  const strategy = {
    activate: _ref3 => {
      let {
        id,
        activated,
        children,
        ...rest
      } = _ref3;
      id = toRaw$4(id);
      if (children.has(id)) return activated;
      return parentStrategy.activate({
        id,
        activated,
        children,
        ...rest
      });
    },
    in: parentStrategy.in,
    out: parentStrategy.out
  };
  return strategy;
};
const leafSingleActiveStrategy = mandatory => {
  const parentStrategy = independentSingleActiveStrategy(mandatory);
  const strategy = {
    activate: _ref4 => {
      let {
        id,
        activated,
        children,
        ...rest
      } = _ref4;
      id = toRaw$4(id);
      if (children.has(id)) return activated;
      return parentStrategy.activate({
        id,
        activated,
        children,
        ...rest
      });
    },
    in: parentStrategy.in,
    out: parentStrategy.out
  };
  return strategy;
};

const singleOpenStrategy = {
  open: _ref => {
    let {
      id,
      value,
      opened,
      parents
    } = _ref;
    if (value) {
      const newOpened = new Set();
      newOpened.add(id);
      let parent = parents.get(id);
      while (parent != null) {
        newOpened.add(parent);
        parent = parents.get(parent);
      }
      return newOpened;
    } else {
      opened.delete(id);
      return opened;
    }
  },
  select: () => null
};
const multipleOpenStrategy = {
  open: _ref2 => {
    let {
      id,
      value,
      opened,
      parents
    } = _ref2;
    if (value) {
      let parent = parents.get(id);
      opened.add(id);
      while (parent != null && parent !== id) {
        opened.add(parent);
        parent = parents.get(parent);
      }
      return opened;
    } else {
      opened.delete(id);
    }
    return opened;
  },
  select: () => null
};
const listOpenStrategy = {
  open: multipleOpenStrategy.open,
  select: _ref3 => {
    let {
      id,
      value,
      opened,
      parents
    } = _ref3;
    if (!value) return opened;
    const path = [];
    let parent = parents.get(id);
    while (parent != null) {
      path.push(parent);
      parent = parents.get(parent);
    }
    return new Set(path);
  }
};

/* eslint-disable sonarjs/no-identical-functions */
// Utilities
const {toRaw: toRaw$3} = await importShared('vue');

const independentSelectStrategy = mandatory => {
  const strategy = {
    select: _ref => {
      let {
        id,
        value,
        selected
      } = _ref;
      id = toRaw$3(id);

      // When mandatory and we're trying to deselect when id
      // is the only currently selected item then do nothing
      if (mandatory && !value) {
        const on = Array.from(selected.entries()).reduce((arr, _ref2) => {
          let [key, value] = _ref2;
          if (value === 'on') arr.push(key);
          return arr;
        }, []);
        if (on.length === 1 && on[0] === id) return selected;
      }
      selected.set(id, value ? 'on' : 'off');
      return selected;
    },
    in: (v, children, parents) => {
      const map = new Map();
      for (const id of v || []) {
        strategy.select({
          id,
          value: true,
          selected: map,
          children,
          parents
        });
      }
      return map;
    },
    out: v => {
      const arr = [];
      for (const [key, value] of v.entries()) {
        if (value === 'on') arr.push(key);
      }
      return arr;
    }
  };
  return strategy;
};
const independentSingleSelectStrategy = mandatory => {
  const parentStrategy = independentSelectStrategy(mandatory);
  const strategy = {
    select: _ref3 => {
      let {
        selected,
        id,
        ...rest
      } = _ref3;
      id = toRaw$3(id);
      const singleSelected = selected.has(id) ? new Map([[id, selected.get(id)]]) : new Map();
      return parentStrategy.select({
        ...rest,
        id,
        selected: singleSelected
      });
    },
    in: (v, children, parents) => {
      if (v?.length) {
        return parentStrategy.in(v.slice(0, 1), children, parents);
      }
      return new Map();
    },
    out: (v, children, parents) => {
      return parentStrategy.out(v, children, parents);
    }
  };
  return strategy;
};
const leafSelectStrategy = mandatory => {
  const parentStrategy = independentSelectStrategy(mandatory);
  const strategy = {
    select: _ref4 => {
      let {
        id,
        selected,
        children,
        ...rest
      } = _ref4;
      id = toRaw$3(id);
      if (children.has(id)) return selected;
      return parentStrategy.select({
        id,
        selected,
        children,
        ...rest
      });
    },
    in: parentStrategy.in,
    out: parentStrategy.out
  };
  return strategy;
};
const leafSingleSelectStrategy = mandatory => {
  const parentStrategy = independentSingleSelectStrategy(mandatory);
  const strategy = {
    select: _ref5 => {
      let {
        id,
        selected,
        children,
        ...rest
      } = _ref5;
      id = toRaw$3(id);
      if (children.has(id)) return selected;
      return parentStrategy.select({
        id,
        selected,
        children,
        ...rest
      });
    },
    in: parentStrategy.in,
    out: parentStrategy.out
  };
  return strategy;
};
const classicSelectStrategy = mandatory => {
  const strategy = {
    select: _ref6 => {
      let {
        id,
        value,
        selected,
        children,
        parents
      } = _ref6;
      id = toRaw$3(id);
      const original = new Map(selected);
      const items = [id];
      while (items.length) {
        const item = items.shift();
        selected.set(toRaw$3(item), value ? 'on' : 'off');
        if (children.has(item)) {
          items.push(...children.get(item));
        }
      }
      let parent = toRaw$3(parents.get(id));
      while (parent) {
        const childrenIds = children.get(parent);
        const everySelected = childrenIds.every(cid => selected.get(toRaw$3(cid)) === 'on');
        const noneSelected = childrenIds.every(cid => !selected.has(toRaw$3(cid)) || selected.get(toRaw$3(cid)) === 'off');
        selected.set(parent, everySelected ? 'on' : noneSelected ? 'off' : 'indeterminate');
        parent = toRaw$3(parents.get(parent));
      }

      // If mandatory and planned deselect results in no selected
      // items then we can't do it, so return original state
      if (mandatory && !value) {
        const on = Array.from(selected.entries()).reduce((arr, _ref7) => {
          let [key, value] = _ref7;
          if (value === 'on') arr.push(key);
          return arr;
        }, []);
        if (on.length === 0) return original;
      }
      return selected;
    },
    in: (v, children, parents) => {
      let map = new Map();
      for (const id of v || []) {
        map = strategy.select({
          id,
          value: true,
          selected: map,
          children,
          parents
        });
      }
      return map;
    },
    out: (v, children) => {
      const arr = [];
      for (const [key, value] of v.entries()) {
        if (value === 'on' && !children.has(key)) arr.push(key);
      }
      return arr;
    }
  };
  return strategy;
};
const trunkSelectStrategy = mandatory => {
  const parentStrategy = classicSelectStrategy(mandatory);
  const strategy = {
    select: parentStrategy.select,
    in: parentStrategy.in,
    out: (v, children, parents) => {
      const arr = [];
      for (const [key, value] of v.entries()) {
        if (value === 'on') {
          if (parents.has(key)) {
            const parent = parents.get(key);
            if (v.get(parent) === 'on') continue;
          }
          arr.push(key);
        }
      }
      return arr;
    }
  };
  return strategy;
};

const {computed: computed$1l,inject: inject$h,onBeforeMount: onBeforeMount$2,onBeforeUnmount: onBeforeUnmount$7,provide: provide$c,ref: ref$G,shallowRef: shallowRef$z,toRaw: toRaw$2,toRef: toRef$F,toValue: toValue$1} = await importShared('vue');
const VNestedSymbol = Symbol.for('vuetify:nested');
const emptyNested = {
  id: shallowRef$z(),
  root: {
    register: () => null,
    unregister: () => null,
    parents: ref$G(new Map()),
    children: ref$G(new Map()),
    open: () => null,
    openOnSelect: () => null,
    activate: () => null,
    select: () => null,
    activatable: ref$G(false),
    selectable: ref$G(false),
    opened: ref$G(new Set()),
    activated: ref$G(new Set()),
    selected: ref$G(new Map()),
    selectedValues: ref$G([]),
    getPath: () => []
  }
};
const makeNestedProps = propsFactory({
  activatable: Boolean,
  selectable: Boolean,
  activeStrategy: [String, Function, Object],
  selectStrategy: [String, Function, Object],
  openStrategy: [String, Object],
  opened: null,
  activated: null,
  selected: null,
  mandatory: Boolean
}, 'nested');
const useNested = props => {
  let isUnmounted = false;
  const children = ref$G(new Map());
  const parents = ref$G(new Map());
  const opened = useProxiedModel(props, 'opened', props.opened, v => new Set(v), v => [...v.values()]);
  const activeStrategy = computed$1l(() => {
    if (typeof props.activeStrategy === 'object') return props.activeStrategy;
    if (typeof props.activeStrategy === 'function') return props.activeStrategy(props.mandatory);
    switch (props.activeStrategy) {
      case 'leaf':
        return leafActiveStrategy(props.mandatory);
      case 'single-leaf':
        return leafSingleActiveStrategy(props.mandatory);
      case 'independent':
        return independentActiveStrategy(props.mandatory);
      case 'single-independent':
      default:
        return independentSingleActiveStrategy(props.mandatory);
    }
  });
  const selectStrategy = computed$1l(() => {
    if (typeof props.selectStrategy === 'object') return props.selectStrategy;
    if (typeof props.selectStrategy === 'function') return props.selectStrategy(props.mandatory);
    switch (props.selectStrategy) {
      case 'single-leaf':
        return leafSingleSelectStrategy(props.mandatory);
      case 'leaf':
        return leafSelectStrategy(props.mandatory);
      case 'independent':
        return independentSelectStrategy(props.mandatory);
      case 'single-independent':
        return independentSingleSelectStrategy(props.mandatory);
      case 'trunk':
        return trunkSelectStrategy(props.mandatory);
      case 'classic':
      default:
        return classicSelectStrategy(props.mandatory);
    }
  });
  const openStrategy = computed$1l(() => {
    if (typeof props.openStrategy === 'object') return props.openStrategy;
    switch (props.openStrategy) {
      case 'list':
        return listOpenStrategy;
      case 'single':
        return singleOpenStrategy;
      case 'multiple':
      default:
        return multipleOpenStrategy;
    }
  });
  const activated = useProxiedModel(props, 'activated', props.activated, v => activeStrategy.value.in(v, children.value, parents.value), v => activeStrategy.value.out(v, children.value, parents.value));
  const selected = useProxiedModel(props, 'selected', props.selected, v => selectStrategy.value.in(v, children.value, parents.value), v => selectStrategy.value.out(v, children.value, parents.value));
  onBeforeUnmount$7(() => {
    isUnmounted = true;
  });
  function getPath(id) {
    const path = [];
    let parent = id;
    while (parent != null) {
      path.unshift(parent);
      parent = parents.value.get(parent);
    }
    return path;
  }
  const vm = getCurrentInstance('nested');
  const nodeIds = new Set();
  const nested = {
    id: shallowRef$z(),
    root: {
      opened,
      activatable: toRef$F(() => props.activatable),
      selectable: toRef$F(() => props.selectable),
      activated,
      selected,
      selectedValues: computed$1l(() => {
        const arr = [];
        for (const [key, value] of selected.value.entries()) {
          if (value === 'on') arr.push(key);
        }
        return arr;
      }),
      register: (id, parentId, isGroup) => {
        if (nodeIds.has(id)) {
          const path = getPath(id).map(String).join(' -> ');
          const newPath = getPath(parentId).concat(id).map(String).join(' -> ');
          consoleError(`Multiple nodes with the same ID\n\t${path}\n\t${newPath}`);
          return;
        } else {
          nodeIds.add(id);
        }
        parentId && id !== parentId && parents.value.set(id, parentId);
        isGroup && children.value.set(id, []);
        if (parentId != null) {
          children.value.set(parentId, [...(children.value.get(parentId) || []), id]);
        }
      },
      unregister: id => {
        if (isUnmounted) return;
        nodeIds.delete(id);
        children.value.delete(id);
        const parent = parents.value.get(id);
        if (parent) {
          const list = children.value.get(parent) ?? [];
          children.value.set(parent, list.filter(child => child !== id));
        }
        parents.value.delete(id);
      },
      open: (id, value, event) => {
        vm.emit('click:open', {
          id,
          value,
          path: getPath(id),
          event
        });
        const newOpened = openStrategy.value.open({
          id,
          value,
          opened: new Set(opened.value),
          children: children.value,
          parents: parents.value,
          event
        });
        newOpened && (opened.value = newOpened);
      },
      openOnSelect: (id, value, event) => {
        const newOpened = openStrategy.value.select({
          id,
          value,
          selected: new Map(selected.value),
          opened: new Set(opened.value),
          children: children.value,
          parents: parents.value,
          event
        });
        newOpened && (opened.value = newOpened);
      },
      select: (id, value, event) => {
        vm.emit('click:select', {
          id,
          value,
          path: getPath(id),
          event
        });
        const newSelected = selectStrategy.value.select({
          id,
          value,
          selected: new Map(selected.value),
          children: children.value,
          parents: parents.value,
          event
        });
        newSelected && (selected.value = newSelected);
        nested.root.openOnSelect(id, value, event);
      },
      activate: (id, value, event) => {
        if (!props.activatable) {
          return nested.root.select(id, true, event);
        }
        vm.emit('click:activate', {
          id,
          value,
          path: getPath(id),
          event
        });
        const newActivated = activeStrategy.value.activate({
          id,
          value,
          activated: new Set(activated.value),
          children: children.value,
          parents: parents.value,
          event
        });
        if (newActivated.size !== activated.value.size) {
          activated.value = newActivated;
        } else {
          for (const value of newActivated) {
            if (!activated.value.has(value)) {
              activated.value = newActivated;
              return;
            }
          }
          for (const value of activated.value) {
            if (!newActivated.has(value)) {
              activated.value = newActivated;
              return;
            }
          }
        }
      },
      children,
      parents,
      getPath
    }
  };
  provide$c(VNestedSymbol, nested);
  return nested.root;
};
const useNestedItem = (id, isGroup) => {
  const parent = inject$h(VNestedSymbol, emptyNested);
  const uidSymbol = Symbol('nested item');
  const computedId = computed$1l(() => toValue$1(id) ?? uidSymbol);
  const item = {
    ...parent,
    id: computedId,
    open: (open, e) => parent.root.open(computedId.value, open, e),
    openOnSelect: (open, e) => parent.root.openOnSelect(computedId.value, open, e),
    isOpen: computed$1l(() => parent.root.opened.value.has(computedId.value)),
    parent: computed$1l(() => parent.root.parents.value.get(computedId.value)),
    activate: (activated, e) => parent.root.activate(computedId.value, activated, e),
    isActivated: computed$1l(() => parent.root.activated.value.has(toRaw$2(computedId.value))),
    select: (selected, e) => parent.root.select(computedId.value, selected, e),
    isSelected: computed$1l(() => parent.root.selected.value.get(toRaw$2(computedId.value)) === 'on'),
    isIndeterminate: computed$1l(() => parent.root.selected.value.get(toRaw$2(computedId.value)) === 'indeterminate'),
    isLeaf: computed$1l(() => !parent.root.children.value.get(computedId.value)),
    isGroupActivator: parent.isGroupActivator
  };
  onBeforeMount$2(() => {
    !parent.isGroupActivator && parent.root.register(computedId.value, parent.id.value, isGroup);
  });
  onBeforeUnmount$7(() => {
    !parent.isGroupActivator && parent.root.unregister(computedId.value);
  });
  isGroup && provide$c(VNestedSymbol, item);
  return item;
};
const useNestedGroupActivator = () => {
  const parent = inject$h(VNestedSymbol, emptyNested);
  provide$c(VNestedSymbol, {
    ...parent,
    isGroupActivator: true
  });
};

const {createVNode:_createVNode$1R,vShow:_vShow$8,withDirectives:_withDirectives$g} = await importShared('vue');
const {computed: computed$1k} = await importShared('vue');
const VListGroupActivator = defineComponent({
  name: 'VListGroupActivator',
  setup(_, _ref) {
    let {
      slots
    } = _ref;
    useNestedGroupActivator();
    return () => slots.default?.();
  }
});
const makeVListGroupProps = propsFactory({
  /* @deprecated */
  activeColor: String,
  baseColor: String,
  color: String,
  collapseIcon: {
    type: IconValue,
    default: '$collapse'
  },
  expandIcon: {
    type: IconValue,
    default: '$expand'
  },
  prependIcon: IconValue,
  appendIcon: IconValue,
  fluid: Boolean,
  subgroup: Boolean,
  title: String,
  value: null,
  ...makeComponentProps(),
  ...makeTagProps()
}, 'VListGroup');
const VListGroup = genericComponent()({
  name: 'VListGroup',
  props: makeVListGroupProps(),
  setup(props, _ref2) {
    let {
      slots
    } = _ref2;
    const {
      isOpen,
      open,
      id: _id
    } = useNestedItem(() => props.value, true);
    const id = computed$1k(() => `v-list-group--id-${String(_id.value)}`);
    const list = useList();
    const {
      isBooted
    } = useSsrBoot();
    function onClick(e) {
      e.stopPropagation();
      if (['INPUT', 'TEXTAREA'].includes(e.target?.tagName)) return;
      open(!isOpen.value, e);
    }
    const activatorProps = computed$1k(() => ({
      onClick,
      class: 'v-list-group__header',
      id: id.value
    }));
    const toggleIcon = computed$1k(() => isOpen.value ? props.collapseIcon : props.expandIcon);
    const activatorDefaults = computed$1k(() => ({
      VListItem: {
        active: isOpen.value,
        activeColor: props.activeColor,
        baseColor: props.baseColor,
        color: props.color,
        prependIcon: props.prependIcon || props.subgroup && toggleIcon.value,
        appendIcon: props.appendIcon || !props.subgroup && toggleIcon.value,
        title: props.title,
        value: props.value
      }
    }));
    useRender(() => _createVNode$1R(props.tag, {
      "class": ['v-list-group', {
        'v-list-group--prepend': list?.hasPrepend.value,
        'v-list-group--fluid': props.fluid,
        'v-list-group--subgroup': props.subgroup,
        'v-list-group--open': isOpen.value
      }, props.class],
      "style": props.style
    }, {
      default: () => [slots.activator && _createVNode$1R(VDefaultsProvider, {
        "defaults": activatorDefaults.value
      }, {
        default: () => [_createVNode$1R(VListGroupActivator, null, {
          default: () => [slots.activator({
            props: activatorProps.value,
            isOpen: isOpen.value
          })]
        })]
      }), _createVNode$1R(MaybeTransition, {
        "transition": {
          component: VExpandTransition
        },
        "disabled": !isBooted.value
      }, {
        default: () => [_withDirectives$g(_createVNode$1R("div", {
          "class": "v-list-group__items",
          "role": "group",
          "aria-labelledby": id.value
        }, [slots.default?.()]), [[_vShow$8, isOpen.value]])]
      })]
    }));
    return {
      isOpen
    };
  }
});

const {createVNode:_createVNode$1Q} = await importShared('vue');
const makeVListItemSubtitleProps = propsFactory({
  opacity: [Number, String],
  ...makeComponentProps(),
  ...makeTagProps()
}, 'VListItemSubtitle');
const VListItemSubtitle = genericComponent()({
  name: 'VListItemSubtitle',
  props: makeVListItemSubtitleProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    useRender(() => _createVNode$1Q(props.tag, {
      "class": ['v-list-item-subtitle', props.class],
      "style": [{
        '--v-list-item-subtitle-opacity': props.opacity
      }, props.style]
    }, slots));
    return {};
  }
});

// Utilities
const VListItemTitle = createSimpleFunctional('v-list-item-title');

const {Fragment:_Fragment$A,createVNode:_createVNode$1P,resolveDirective:_resolveDirective$9,mergeProps:_mergeProps$U,withDirectives:_withDirectives$f} = await importShared('vue');
const {computed: computed$1j,onBeforeMount: onBeforeMount$1,toDisplayString: toDisplayString$2,toRef: toRef$E,watch: watch$x} = await importShared('vue');
const makeVListItemProps = propsFactory({
  active: {
    type: Boolean,
    default: undefined
  },
  activeClass: String,
  /* @deprecated */
  activeColor: String,
  appendAvatar: String,
  appendIcon: IconValue,
  baseColor: String,
  disabled: Boolean,
  lines: [Boolean, String],
  link: {
    type: Boolean,
    default: undefined
  },
  nav: Boolean,
  prependAvatar: String,
  prependIcon: IconValue,
  ripple: {
    type: [Boolean, Object],
    default: true
  },
  slim: Boolean,
  subtitle: {
    type: [String, Number, Boolean],
    default: undefined
  },
  title: {
    type: [String, Number, Boolean],
    default: undefined
  },
  value: null,
  onClick: EventProp(),
  onClickOnce: EventProp(),
  ...makeBorderProps(),
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeDimensionProps(),
  ...makeElevationProps(),
  ...makeRoundedProps(),
  ...makeRouterProps(),
  ...makeTagProps(),
  ...makeThemeProps(),
  ...makeVariantProps({
    variant: 'text'
  })
}, 'VListItem');
const VListItem = genericComponent()({
  name: 'VListItem',
  directives: {
    Ripple
  },
  props: makeVListItemProps(),
  emits: {
    click: e => true
  },
  setup(props, _ref) {
    let {
      attrs,
      slots,
      emit
    } = _ref;
    const link = useLink(props, attrs);
    const id = computed$1j(() => props.value === undefined ? link.href.value : props.value);
    const {
      activate,
      isActivated,
      select,
      isOpen,
      isSelected,
      isIndeterminate,
      isGroupActivator,
      root,
      parent,
      openOnSelect,
      id: uid
    } = useNestedItem(id, false);
    const list = useList();
    const isActive = computed$1j(() => props.active !== false && (props.active || link.isActive?.value || (root.activatable.value ? isActivated.value : isSelected.value)));
    const isLink = toRef$E(() => props.link !== false && link.isLink.value);
    const isSelectable = computed$1j(() => !!list && (root.selectable.value || root.activatable.value || props.value != null));
    const isClickable = computed$1j(() => !props.disabled && props.link !== false && (props.link || link.isClickable.value || isSelectable.value));
    const roundedProps = toRef$E(() => props.rounded || props.nav);
    const color = toRef$E(() => props.color ?? props.activeColor);
    const variantProps = toRef$E(() => ({
      color: isActive.value ? color.value ?? props.baseColor : props.baseColor,
      variant: props.variant
    }));

    // useNestedItem doesn't call register until beforeMount,
    // so this can't be an immediate watcher as we don't know parent yet
    watch$x(() => link.isActive?.value, val => {
      if (!val) return;
      handleActiveLink();
    });
    onBeforeMount$1(() => {
      if (link.isActive?.value) handleActiveLink();
    });
    function handleActiveLink() {
      if (parent.value != null) {
        root.open(parent.value, true);
      }
      openOnSelect(true);
    }
    const {
      themeClasses
    } = provideTheme(props);
    const {
      borderClasses
    } = useBorder(props);
    const {
      colorClasses,
      colorStyles,
      variantClasses
    } = useVariant(variantProps);
    const {
      densityClasses
    } = useDensity(props);
    const {
      dimensionStyles
    } = useDimension(props);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      roundedClasses
    } = useRounded(roundedProps);
    const lineClasses = toRef$E(() => props.lines ? `v-list-item--${props.lines}-line` : undefined);
    const slotProps = computed$1j(() => ({
      isActive: isActive.value,
      select,
      isOpen: isOpen.value,
      isSelected: isSelected.value,
      isIndeterminate: isIndeterminate.value
    }));
    function onClick(e) {
      emit('click', e);
      if (['INPUT', 'TEXTAREA'].includes(e.target?.tagName)) return;
      if (!isClickable.value) return;
      link.navigate?.(e);
      if (isGroupActivator) return;
      if (root.activatable.value) {
        activate(!isActivated.value, e);
      } else if (root.selectable.value) {
        select(!isSelected.value, e);
      } else if (props.value != null) {
        select(!isSelected.value, e);
      }
    }
    function onKeyDown(e) {
      const target = e.target;
      if (['INPUT', 'TEXTAREA'].includes(target.tagName)) return;
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        e.target.dispatchEvent(new MouseEvent('click', e));
      }
    }
    useRender(() => {
      const Tag = isLink.value ? 'a' : props.tag;
      const hasTitle = slots.title || props.title != null;
      const hasSubtitle = slots.subtitle || props.subtitle != null;
      const hasAppendMedia = !!(props.appendAvatar || props.appendIcon);
      const hasAppend = !!(hasAppendMedia || slots.append);
      const hasPrependMedia = !!(props.prependAvatar || props.prependIcon);
      const hasPrepend = !!(hasPrependMedia || slots.prepend);
      list?.updateHasPrepend(hasPrepend);
      if (props.activeColor) {
        deprecate('active-color', ['color', 'base-color']);
      }
      return _withDirectives$f(_createVNode$1P(Tag, _mergeProps$U({
        "class": ['v-list-item', {
          'v-list-item--active': isActive.value,
          'v-list-item--disabled': props.disabled,
          'v-list-item--link': isClickable.value,
          'v-list-item--nav': props.nav,
          'v-list-item--prepend': !hasPrepend && list?.hasPrepend.value,
          'v-list-item--slim': props.slim,
          [`${props.activeClass}`]: props.activeClass && isActive.value
        }, themeClasses.value, borderClasses.value, colorClasses.value, densityClasses.value, elevationClasses.value, lineClasses.value, roundedClasses.value, variantClasses.value, props.class],
        "style": [colorStyles.value, dimensionStyles.value, props.style],
        "tabindex": isClickable.value ? list ? -2 : 0 : undefined,
        "aria-selected": isSelectable.value ? root.activatable.value ? isActivated.value : root.selectable.value ? isSelected.value : isActive.value : undefined,
        "onClick": onClick,
        "onKeydown": isClickable.value && !isLink.value && onKeyDown
      }, link.linkProps), {
        default: () => [genOverlays(isClickable.value || isActive.value, 'v-list-item'), hasPrepend && _createVNode$1P("div", {
          "key": "prepend",
          "class": "v-list-item__prepend"
        }, [!slots.prepend ? _createVNode$1P(_Fragment$A, null, [props.prependAvatar && _createVNode$1P(VAvatar, {
          "key": "prepend-avatar",
          "density": props.density,
          "image": props.prependAvatar
        }, null), props.prependIcon && _createVNode$1P(VIcon, {
          "key": "prepend-icon",
          "density": props.density,
          "icon": props.prependIcon
        }, null)]) : _createVNode$1P(VDefaultsProvider, {
          "key": "prepend-defaults",
          "disabled": !hasPrependMedia,
          "defaults": {
            VAvatar: {
              density: props.density,
              image: props.prependAvatar
            },
            VIcon: {
              density: props.density,
              icon: props.prependIcon
            },
            VListItemAction: {
              start: true
            }
          }
        }, {
          default: () => [slots.prepend?.(slotProps.value)]
        }), _createVNode$1P("div", {
          "class": "v-list-item__spacer"
        }, null)]), _createVNode$1P("div", {
          "class": "v-list-item__content",
          "data-no-activator": ""
        }, [hasTitle && _createVNode$1P(VListItemTitle, {
          "key": "title"
        }, {
          default: () => [slots.title?.({
            title: props.title
          }) ?? toDisplayString$2(props.title)]
        }), hasSubtitle && _createVNode$1P(VListItemSubtitle, {
          "key": "subtitle"
        }, {
          default: () => [slots.subtitle?.({
            subtitle: props.subtitle
          }) ?? toDisplayString$2(props.subtitle)]
        }), slots.default?.(slotProps.value)]), hasAppend && _createVNode$1P("div", {
          "key": "append",
          "class": "v-list-item__append"
        }, [!slots.append ? _createVNode$1P(_Fragment$A, null, [props.appendIcon && _createVNode$1P(VIcon, {
          "key": "append-icon",
          "density": props.density,
          "icon": props.appendIcon
        }, null), props.appendAvatar && _createVNode$1P(VAvatar, {
          "key": "append-avatar",
          "density": props.density,
          "image": props.appendAvatar
        }, null)]) : _createVNode$1P(VDefaultsProvider, {
          "key": "append-defaults",
          "disabled": !hasAppendMedia,
          "defaults": {
            VAvatar: {
              density: props.density,
              image: props.appendAvatar
            },
            VIcon: {
              density: props.density,
              icon: props.appendIcon
            },
            VListItemAction: {
              end: true
            }
          }
        }, {
          default: () => [slots.append?.(slotProps.value)]
        }), _createVNode$1P("div", {
          "class": "v-list-item__spacer"
        }, null)])]
      }), [[_resolveDirective$9("ripple"), isClickable.value && props.ripple]]);
    });
    return {
      activate,
      isActivated,
      isGroupActivator,
      isSelected,
      list,
      select,
      root,
      id: uid,
      link
    };
  }
});

const {createVNode:_createVNode$1O} = await importShared('vue');
const makeVListSubheaderProps = propsFactory({
  color: String,
  inset: Boolean,
  sticky: Boolean,
  title: String,
  ...makeComponentProps(),
  ...makeTagProps()
}, 'VListSubheader');
const VListSubheader = genericComponent()({
  name: 'VListSubheader',
  props: makeVListSubheaderProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      textColorClasses,
      textColorStyles
    } = useTextColor(() => props.color);
    useRender(() => {
      const hasText = !!(slots.default || props.title);
      return _createVNode$1O(props.tag, {
        "class": ['v-list-subheader', {
          'v-list-subheader--inset': props.inset,
          'v-list-subheader--sticky': props.sticky
        }, textColorClasses.value, props.class],
        "style": [{
          textColorStyles
        }, props.style]
      }, {
        default: () => [hasText && _createVNode$1O("div", {
          "class": "v-list-subheader__text"
        }, [slots.default?.() ?? props.title])]
      });
    });
    return {};
  }
});

const {createVNode:_createVNode$1N} = await importShared('vue');
const {computed: computed$1i} = await importShared('vue');
const makeVDividerProps = propsFactory({
  color: String,
  inset: Boolean,
  length: [Number, String],
  opacity: [Number, String],
  thickness: [Number, String],
  vertical: Boolean,
  ...makeComponentProps(),
  ...makeThemeProps()
}, 'VDivider');
const VDivider = genericComponent()({
  name: 'VDivider',
  props: makeVDividerProps(),
  setup(props, _ref) {
    let {
      attrs,
      slots
    } = _ref;
    const {
      themeClasses
    } = provideTheme(props);
    const {
      textColorClasses,
      textColorStyles
    } = useTextColor(() => props.color);
    const dividerStyles = computed$1i(() => {
      const styles = {};
      if (props.length) {
        styles[props.vertical ? 'height' : 'width'] = convertToUnit(props.length);
      }
      if (props.thickness) {
        styles[props.vertical ? 'borderRightWidth' : 'borderTopWidth'] = convertToUnit(props.thickness);
      }
      return styles;
    });
    useRender(() => {
      const divider = _createVNode$1N("hr", {
        "class": [{
          'v-divider': true,
          'v-divider--inset': props.inset,
          'v-divider--vertical': props.vertical
        }, themeClasses.value, textColorClasses.value, props.class],
        "style": [dividerStyles.value, textColorStyles.value, {
          '--v-border-opacity': props.opacity
        }, props.style],
        "aria-orientation": !attrs.role || attrs.role === 'separator' ? props.vertical ? 'vertical' : 'horizontal' : undefined,
        "role": `${attrs.role || 'separator'}`
      }, null);
      if (!slots.default) return divider;
      return _createVNode$1N("div", {
        "class": ['v-divider__wrapper', {
          'v-divider__wrapper--vertical': props.vertical,
          'v-divider__wrapper--inset': props.inset
        }]
      }, [divider, _createVNode$1N("div", {
        "class": "v-divider__content"
      }, [slots.default()]), divider]);
    });
    return {};
  }
});

const {createVNode:_createVNode$1M,mergeProps:_mergeProps$T} = await importShared('vue');
const makeVListChildrenProps = propsFactory({
  items: Array,
  returnObject: Boolean
}, 'VListChildren');
const VListChildren = genericComponent()({
  name: 'VListChildren',
  props: makeVListChildrenProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    createList();
    return () => slots.default?.() ?? props.items?.map(_ref2 => {
      let {
        children,
        props: itemProps,
        type,
        raw: item
      } = _ref2;
      if (type === 'divider') {
        return slots.divider?.({
          props: itemProps
        }) ?? _createVNode$1M(VDivider, itemProps, null);
      }
      if (type === 'subheader') {
        return slots.subheader?.({
          props: itemProps
        }) ?? _createVNode$1M(VListSubheader, itemProps, null);
      }
      const slotsWithItem = {
        subtitle: slots.subtitle ? slotProps => slots.subtitle?.({
          ...slotProps,
          item
        }) : undefined,
        prepend: slots.prepend ? slotProps => slots.prepend?.({
          ...slotProps,
          item
        }) : undefined,
        append: slots.append ? slotProps => slots.append?.({
          ...slotProps,
          item
        }) : undefined,
        title: slots.title ? slotProps => slots.title?.({
          ...slotProps,
          item
        }) : undefined
      };
      const listGroupProps = VListGroup.filterProps(itemProps);
      return children ? _createVNode$1M(VListGroup, _mergeProps$T({
        "value": itemProps?.value
      }, listGroupProps), {
        activator: _ref3 => {
          let {
            props: activatorProps
          } = _ref3;
          const listItemProps = {
            ...itemProps,
            ...activatorProps,
            value: props.returnObject ? item : itemProps.value
          };
          return slots.header ? slots.header({
            props: listItemProps
          }) : _createVNode$1M(VListItem, listItemProps, slotsWithItem);
        },
        default: () => _createVNode$1M(VListChildren, {
          "items": children,
          "returnObject": props.returnObject
        }, slots)
      }) : slots.item ? slots.item({
        props: itemProps
      }) : _createVNode$1M(VListItem, _mergeProps$T(itemProps, {
        "value": props.returnObject ? item : itemProps.value
      }), slotsWithItem);
    });
  }
});

// Utilities
const {computed: computed$1h,shallowRef: shallowRef$y,watchEffect: watchEffect$g} = await importShared('vue');
// Composables
const makeItemsProps = propsFactory({
  items: {
    type: Array,
    default: () => []
  },
  itemTitle: {
    type: [String, Array, Function],
    default: 'title'
  },
  itemValue: {
    type: [String, Array, Function],
    default: 'value'
  },
  itemChildren: {
    type: [Boolean, String, Array, Function],
    default: 'children'
  },
  itemProps: {
    type: [Boolean, String, Array, Function],
    default: 'props'
  },
  returnObject: Boolean,
  valueComparator: Function
}, 'list-items');
function transformItem$3(props, item) {
  const title = getPropertyFromItem(item, props.itemTitle, item);
  const value = getPropertyFromItem(item, props.itemValue, title);
  const children = getPropertyFromItem(item, props.itemChildren);
  const itemProps = props.itemProps === true ? typeof item === 'object' && item != null && !Array.isArray(item) ? 'children' in item ? omit(item, ['children']) : item : undefined : getPropertyFromItem(item, props.itemProps);
  const _props = {
    title,
    value,
    ...itemProps
  };
  return {
    title: String(_props.title ?? ''),
    value: _props.value,
    props: _props,
    children: Array.isArray(children) ? transformItems$3(props, children) : undefined,
    raw: item
  };
}
function transformItems$3(props, items) {
  const _props = pick(props, ['itemTitle', 'itemValue', 'itemChildren', 'itemProps', 'returnObject', 'valueComparator']);
  const array = [];
  for (const item of items) {
    array.push(transformItem$3(_props, item));
  }
  return array;
}
function useItems(props) {
  const items = computed$1h(() => transformItems$3(props, props.items));
  const hasNullItem = computed$1h(() => items.value.some(item => item.value === null));
  const itemsMap = shallowRef$y(new Map());
  const keylessItems = shallowRef$y([]);
  watchEffect$g(() => {
    const _items = items.value;
    const map = new Map();
    const keyless = [];
    for (let i = 0; i < _items.length; i++) {
      const item = _items[i];
      if (isPrimitive(item.value) || item.value === null) {
        let values = map.get(item.value);
        if (!values) {
          values = [];
          map.set(item.value, values);
        }
        values.push(item);
      } else {
        keyless.push(item);
      }
    }
    itemsMap.value = map;
    keylessItems.value = keyless;
  });
  function transformIn(value) {
    // Cache unrefed values outside the loop,
    // proxy getters can be slow when you call them a billion times
    const _items = itemsMap.value;
    const _allItems = items.value;
    const _keylessItems = keylessItems.value;
    const _hasNullItem = hasNullItem.value;
    const _returnObject = props.returnObject;
    const hasValueComparator = !!props.valueComparator;
    const valueComparator = props.valueComparator || deepEqual;
    const _props = pick(props, ['itemTitle', 'itemValue', 'itemChildren', 'itemProps', 'returnObject', 'valueComparator']);
    const returnValue = [];
    main: for (const v of value) {
      // When the model value is null, return an InternalItem
      // based on null only if null is one of the items
      if (!_hasNullItem && v === null) continue;

      // String model value means value is a custom input value from combobox
      // Don't look up existing items if the model value is a string
      if (_returnObject && typeof v === 'string') {
        returnValue.push(transformItem$3(_props, v));
        continue;
      }

      // Fast path, items with primitive values and no
      // custom valueComparator can use a constant-time
      // map lookup instead of searching the items array
      const fastItems = _items.get(v);

      // Slow path, always use valueComparator.
      // This is O(n^2) so we really don't want to
      // do it for more than a couple hundred items.
      if (hasValueComparator || !fastItems) {
        for (const item of hasValueComparator ? _allItems : _keylessItems) {
          if (valueComparator(v, item.value)) {
            returnValue.push(item);
            continue main;
          }
        }
        // Not an existing item, construct it from the model (#4000)
        returnValue.push(transformItem$3(_props, v));
        continue;
      }
      returnValue.push(...fastItems);
    }
    return returnValue;
  }
  function transformOut(value) {
    return props.returnObject ? value.map(_ref => {
      let {
        raw
      } = _ref;
      return raw;
    }) : value.map(_ref2 => {
      let {
        value
      } = _ref2;
      return value;
    });
  }
  return {
    items,
    transformIn,
    transformOut
  };
}

const {createVNode:_createVNode$1L} = await importShared('vue');
const {computed: computed$1g,ref: ref$F,shallowRef: shallowRef$x,toRef: toRef$D} = await importShared('vue');
function transformItem$2(props, item) {
  const type = getPropertyFromItem(item, props.itemType, 'item');
  const title = isPrimitive(item) ? item : getPropertyFromItem(item, props.itemTitle);
  const value = getPropertyFromItem(item, props.itemValue, undefined);
  const children = getPropertyFromItem(item, props.itemChildren);
  const itemProps = props.itemProps === true ? omit(item, ['children']) : getPropertyFromItem(item, props.itemProps);
  const _props = {
    title,
    value,
    ...itemProps
  };
  return {
    type,
    title: _props.title,
    value: _props.value,
    props: _props,
    children: type === 'item' && children ? transformItems$2(props, children) : undefined,
    raw: item
  };
}
function transformItems$2(props, items) {
  const array = [];
  for (const item of items) {
    array.push(transformItem$2(props, item));
  }
  return array;
}
function useListItems(props) {
  const items = computed$1g(() => transformItems$2(props, props.items));
  return {
    items
  };
}
const makeVListProps = propsFactory({
  baseColor: String,
  /* @deprecated */
  activeColor: String,
  activeClass: String,
  bgColor: String,
  disabled: Boolean,
  expandIcon: IconValue,
  collapseIcon: IconValue,
  lines: {
    type: [Boolean, String],
    default: 'one'
  },
  slim: Boolean,
  nav: Boolean,
  'onClick:open': EventProp(),
  'onClick:select': EventProp(),
  'onUpdate:opened': EventProp(),
  ...makeNestedProps({
    selectStrategy: 'single-leaf',
    openStrategy: 'list'
  }),
  ...makeBorderProps(),
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeDimensionProps(),
  ...makeElevationProps(),
  itemType: {
    type: String,
    default: 'type'
  },
  ...makeItemsProps(),
  ...makeRoundedProps(),
  ...makeTagProps(),
  ...makeThemeProps(),
  ...makeVariantProps({
    variant: 'text'
  })
}, 'VList');
const VList = genericComponent()({
  name: 'VList',
  props: makeVListProps(),
  emits: {
    'update:selected': value => true,
    'update:activated': value => true,
    'update:opened': value => true,
    'click:open': value => true,
    'click:activate': value => true,
    'click:select': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      items
    } = useListItems(props);
    const {
      themeClasses
    } = provideTheme(props);
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.bgColor);
    const {
      borderClasses
    } = useBorder(props);
    const {
      densityClasses
    } = useDensity(props);
    const {
      dimensionStyles
    } = useDimension(props);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      roundedClasses
    } = useRounded(props);
    const {
      children,
      open,
      parents,
      select,
      getPath
    } = useNested(props);
    const lineClasses = toRef$D(() => props.lines ? `v-list--${props.lines}-line` : undefined);
    const activeColor = toRef$D(() => props.activeColor);
    const baseColor = toRef$D(() => props.baseColor);
    const color = toRef$D(() => props.color);
    createList();
    provideDefaults({
      VListGroup: {
        activeColor,
        baseColor,
        color,
        expandIcon: toRef$D(() => props.expandIcon),
        collapseIcon: toRef$D(() => props.collapseIcon)
      },
      VListItem: {
        activeClass: toRef$D(() => props.activeClass),
        activeColor,
        baseColor,
        color,
        density: toRef$D(() => props.density),
        disabled: toRef$D(() => props.disabled),
        lines: toRef$D(() => props.lines),
        nav: toRef$D(() => props.nav),
        slim: toRef$D(() => props.slim),
        variant: toRef$D(() => props.variant)
      }
    });
    const isFocused = shallowRef$x(false);
    const contentRef = ref$F();
    function onFocusin(e) {
      isFocused.value = true;
    }
    function onFocusout(e) {
      isFocused.value = false;
    }
    function onFocus(e) {
      if (!isFocused.value && !(e.relatedTarget && contentRef.value?.contains(e.relatedTarget))) focus();
    }
    function onKeydown(e) {
      const target = e.target;
      if (!contentRef.value || ['INPUT', 'TEXTAREA'].includes(target.tagName)) return;
      if (e.key === 'ArrowDown') {
        focus('next');
      } else if (e.key === 'ArrowUp') {
        focus('prev');
      } else if (e.key === 'Home') {
        focus('first');
      } else if (e.key === 'End') {
        focus('last');
      } else {
        return;
      }
      e.preventDefault();
    }
    function onMousedown(e) {
      isFocused.value = true;
    }
    function focus(location) {
      if (contentRef.value) {
        return focusChild(contentRef.value, location);
      }
    }
    useRender(() => {
      return _createVNode$1L(props.tag, {
        "ref": contentRef,
        "class": ['v-list', {
          'v-list--disabled': props.disabled,
          'v-list--nav': props.nav,
          'v-list--slim': props.slim
        }, themeClasses.value, backgroundColorClasses.value, borderClasses.value, densityClasses.value, elevationClasses.value, lineClasses.value, roundedClasses.value, props.class],
        "style": [backgroundColorStyles.value, dimensionStyles.value, props.style],
        "tabindex": props.disabled ? -1 : 0,
        "role": "listbox",
        "aria-activedescendant": undefined,
        "onFocusin": onFocusin,
        "onFocusout": onFocusout,
        "onFocus": onFocus,
        "onKeydown": onKeydown,
        "onMousedown": onMousedown
      }, {
        default: () => [_createVNode$1L(VListChildren, {
          "items": items.value,
          "returnObject": props.returnObject
        }, slots)]
      });
    });
    return {
      open,
      select,
      focus,
      children,
      parents,
      getPath
    };
  }
});

// Utilities
const VListImg = createSimpleFunctional('v-list-img');

const {createVNode:_createVNode$1K} = await importShared('vue');
const makeVListItemActionProps = propsFactory({
  start: Boolean,
  end: Boolean,
  ...makeComponentProps(),
  ...makeTagProps()
}, 'VListItemAction');
const VListItemAction = genericComponent()({
  name: 'VListItemAction',
  props: makeVListItemActionProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    useRender(() => _createVNode$1K(props.tag, {
      "class": ['v-list-item-action', {
        'v-list-item-action--start': props.start,
        'v-list-item-action--end': props.end
      }, props.class],
      "style": props.style
    }, slots));
    return {};
  }
});

const {createVNode:_createVNode$1J} = await importShared('vue');
const makeVListItemMediaProps = propsFactory({
  start: Boolean,
  end: Boolean,
  ...makeComponentProps(),
  ...makeTagProps()
}, 'VListItemMedia');
const VListItemMedia = genericComponent()({
  name: 'VListItemMedia',
  props: makeVListItemMediaProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    useRender(() => {
      return _createVNode$1J(props.tag, {
        "class": ['v-list-item-media', {
          'v-list-item-media--start': props.start,
          'v-list-item-media--end': props.end
        }, props.class],
        "style": props.style
      }, slots);
    });
    return {};
  }
});

// Types

/** Convert a point in local space to viewport space */
function elementToViewport(point, offset) {
  return {
    x: point.x + offset.x,
    y: point.y + offset.y
  };
}

/** Get the difference between two points */
function getOffset$1(a, b) {
  return {
    x: a.x - b.x,
    y: a.y - b.y
  };
}

/** Convert an anchor object to a point in local space */
function anchorToPoint(anchor, box) {
  if (anchor.side === 'top' || anchor.side === 'bottom') {
    const {
      side,
      align
    } = anchor;
    const x = align === 'left' ? 0 : align === 'center' ? box.width / 2 : align === 'right' ? box.width : align;
    const y = side === 'top' ? 0 : side === 'bottom' ? box.height : side;
    return elementToViewport({
      x,
      y
    }, box);
  } else if (anchor.side === 'left' || anchor.side === 'right') {
    const {
      side,
      align
    } = anchor;
    const x = side === 'left' ? 0 : side === 'right' ? box.width : side;
    const y = align === 'top' ? 0 : align === 'center' ? box.height / 2 : align === 'bottom' ? box.height : align;
    return elementToViewport({
      x,
      y
    }, box);
  }
  return elementToViewport({
    x: box.width / 2,
    y: box.height / 2
  }, box);
}

const {computed: computed$1f,nextTick: nextTick$l,onScopeDispose: onScopeDispose$8,ref: ref$E,watch: watch$w} = await importShared('vue');
const locationStrategies = {
  static: staticLocationStrategy,
  // specific viewport position, usually centered
  connected: connectedLocationStrategy // connected to a certain element
};
const makeLocationStrategyProps = propsFactory({
  locationStrategy: {
    type: [String, Function],
    default: 'static',
    validator: val => typeof val === 'function' || val in locationStrategies
  },
  location: {
    type: String,
    default: 'bottom'
  },
  origin: {
    type: String,
    default: 'auto'
  },
  offset: [Number, String, Array]
}, 'VOverlay-location-strategies');
function useLocationStrategies(props, data) {
  const contentStyles = ref$E({});
  const updateLocation = ref$E();
  if (IN_BROWSER) {
    useToggleScope(() => !!(data.isActive.value && props.locationStrategy), reset => {
      watch$w(() => props.locationStrategy, reset);
      onScopeDispose$8(() => {
        window.removeEventListener('resize', onResize);
        updateLocation.value = undefined;
      });
      window.addEventListener('resize', onResize, {
        passive: true
      });
      if (typeof props.locationStrategy === 'function') {
        updateLocation.value = props.locationStrategy(data, props, contentStyles)?.updateLocation;
      } else {
        updateLocation.value = locationStrategies[props.locationStrategy](data, props, contentStyles)?.updateLocation;
      }
    });
  }
  function onResize(e) {
    updateLocation.value?.(e);
  }
  return {
    contentStyles,
    updateLocation
  };
}
function staticLocationStrategy() {
  // TODO
}

/** Get size of element ignoring max-width/max-height */
function getIntrinsicSize(el, isRtl) {
  // const scrollables = new Map<Element, [number, number]>()
  // el.querySelectorAll('*').forEach(el => {
  //   const x = el.scrollLeft
  //   const y = el.scrollTop
  //   if (x || y) {
  //     scrollables.set(el, [x, y])
  //   }
  // })

  // const initialMaxWidth = el.style.maxWidth
  // const initialMaxHeight = el.style.maxHeight
  // el.style.removeProperty('max-width')
  // el.style.removeProperty('max-height')

  /* eslint-disable-next-line sonarjs/prefer-immediate-return */
  const contentBox = nullifyTransforms(el);
  if (isRtl) {
    contentBox.x += parseFloat(el.style.right || 0);
  } else {
    contentBox.x -= parseFloat(el.style.left || 0);
  }
  contentBox.y -= parseFloat(el.style.top || 0);

  // el.style.maxWidth = initialMaxWidth
  // el.style.maxHeight = initialMaxHeight
  // scrollables.forEach((position, el) => {
  //   el.scrollTo(...position)
  // })

  return contentBox;
}
function connectedLocationStrategy(data, props, contentStyles) {
  const activatorFixed = Array.isArray(data.target.value) || isFixedPosition(data.target.value);
  if (activatorFixed) {
    Object.assign(contentStyles.value, {
      position: 'fixed',
      top: 0,
      [data.isRtl.value ? 'right' : 'left']: 0
    });
  }
  const {
    preferredAnchor,
    preferredOrigin
  } = destructComputed(() => {
    const parsedAnchor = parseAnchor(props.location, data.isRtl.value);
    const parsedOrigin = props.origin === 'overlap' ? parsedAnchor : props.origin === 'auto' ? flipSide(parsedAnchor) : parseAnchor(props.origin, data.isRtl.value);

    // Some combinations of props may produce an invalid origin
    if (parsedAnchor.side === parsedOrigin.side && parsedAnchor.align === flipAlign(parsedOrigin).align) {
      return {
        preferredAnchor: flipCorner(parsedAnchor),
        preferredOrigin: flipCorner(parsedOrigin)
      };
    } else {
      return {
        preferredAnchor: parsedAnchor,
        preferredOrigin: parsedOrigin
      };
    }
  });
  const [minWidth, minHeight, maxWidth, maxHeight] = ['minWidth', 'minHeight', 'maxWidth', 'maxHeight'].map(key => {
    return computed$1f(() => {
      const val = parseFloat(props[key]);
      return isNaN(val) ? Infinity : val;
    });
  });
  const offset = computed$1f(() => {
    if (Array.isArray(props.offset)) {
      return props.offset;
    }
    if (typeof props.offset === 'string') {
      const offset = props.offset.split(' ').map(parseFloat);
      if (offset.length < 2) offset.push(0);
      return offset;
    }
    return typeof props.offset === 'number' ? [props.offset, 0] : [0, 0];
  });
  let observe = false;
  let lastFrame = -1;
  const flipped = new CircularBuffer(4);
  const observer = new ResizeObserver(() => {
    if (!observe) return;

    // Detect consecutive frames
    requestAnimationFrame(newTime => {
      if (newTime !== lastFrame) flipped.clear();
      requestAnimationFrame(newNewTime => {
        lastFrame = newNewTime;
      });
    });
    if (flipped.isFull) {
      const values = flipped.values();
      if (deepEqual(values.at(-1), values.at(-3))) {
        // Flipping is causing a container resize loop
        return;
      }
    }
    const result = updateLocation();
    if (result) flipped.push(result.flipped);
  });
  watch$w([data.target, data.contentEl], (_ref, _ref2) => {
    let [newTarget, newContentEl] = _ref;
    let [oldTarget, oldContentEl] = _ref2;
    if (oldTarget && !Array.isArray(oldTarget)) observer.unobserve(oldTarget);
    if (newTarget && !Array.isArray(newTarget)) observer.observe(newTarget);
    if (oldContentEl) observer.unobserve(oldContentEl);
    if (newContentEl) observer.observe(newContentEl);
  }, {
    immediate: true
  });
  onScopeDispose$8(() => {
    observer.disconnect();
  });
  let targetBox = new Box({
    x: 0,
    y: 0,
    width: 0,
    height: 0
  });

  // eslint-disable-next-line max-statements
  function updateLocation() {
    observe = false;
    requestAnimationFrame(() => observe = true);
    if (!data.target.value || !data.contentEl.value) return;
    if (Array.isArray(data.target.value) || data.target.value.offsetParent || data.target.value.getClientRects().length) {
      targetBox = getTargetBox(data.target.value);
    } // Otherwise target element is hidden, use last known value

    const contentBox = getIntrinsicSize(data.contentEl.value, data.isRtl.value);
    const scrollParents = getScrollParents(data.contentEl.value);
    const viewportMargin = 12;
    if (!scrollParents.length) {
      scrollParents.push(document.documentElement);
      if (!(data.contentEl.value.style.top && data.contentEl.value.style.left)) {
        contentBox.x -= parseFloat(document.documentElement.style.getPropertyValue('--v-body-scroll-x') || 0);
        contentBox.y -= parseFloat(document.documentElement.style.getPropertyValue('--v-body-scroll-y') || 0);
      }
    }
    const viewport = scrollParents.reduce((box, el) => {
      const rect = el.getBoundingClientRect();
      const scrollBox = new Box({
        x: el === document.documentElement ? 0 : rect.x,
        y: el === document.documentElement ? 0 : rect.y,
        width: el.clientWidth,
        height: el.clientHeight
      });
      if (box) {
        return new Box({
          x: Math.max(box.left, scrollBox.left),
          y: Math.max(box.top, scrollBox.top),
          width: Math.min(box.right, scrollBox.right) - Math.max(box.left, scrollBox.left),
          height: Math.min(box.bottom, scrollBox.bottom) - Math.max(box.top, scrollBox.top)
        });
      }
      return scrollBox;
    }, undefined);
    viewport.x += viewportMargin;
    viewport.y += viewportMargin;
    viewport.width -= viewportMargin * 2;
    viewport.height -= viewportMargin * 2;
    let placement = {
      anchor: preferredAnchor.value,
      origin: preferredOrigin.value
    };
    function checkOverflow(_placement) {
      const box = new Box(contentBox);
      const targetPoint = anchorToPoint(_placement.anchor, targetBox);
      const contentPoint = anchorToPoint(_placement.origin, box);
      let {
        x,
        y
      } = getOffset$1(targetPoint, contentPoint);
      switch (_placement.anchor.side) {
        case 'top':
          y -= offset.value[0];
          break;
        case 'bottom':
          y += offset.value[0];
          break;
        case 'left':
          x -= offset.value[0];
          break;
        case 'right':
          x += offset.value[0];
          break;
      }
      switch (_placement.anchor.align) {
        case 'top':
          y -= offset.value[1];
          break;
        case 'bottom':
          y += offset.value[1];
          break;
        case 'left':
          x -= offset.value[1];
          break;
        case 'right':
          x += offset.value[1];
          break;
      }
      box.x += x;
      box.y += y;
      box.width = Math.min(box.width, maxWidth.value);
      box.height = Math.min(box.height, maxHeight.value);
      const overflows = getOverflow(box, viewport);
      return {
        overflows,
        x,
        y
      };
    }
    let x = 0;
    let y = 0;
    const available = {
      x: 0,
      y: 0
    };
    const flipped = {
      x: false,
      y: false
    };
    let resets = -1;
    while (true) {
      if (resets++ > 10) {
        consoleError('Infinite loop detected in connectedLocationStrategy');
        break;
      }
      const {
        x: _x,
        y: _y,
        overflows
      } = checkOverflow(placement);
      x += _x;
      y += _y;
      contentBox.x += _x;
      contentBox.y += _y;

      // flip
      {
        const axis = getAxis(placement.anchor);
        const hasOverflowX = overflows.x.before || overflows.x.after;
        const hasOverflowY = overflows.y.before || overflows.y.after;
        let reset = false;
        ['x', 'y'].forEach(key => {
          if (key === 'x' && hasOverflowX && !flipped.x || key === 'y' && hasOverflowY && !flipped.y) {
            const newPlacement = {
              anchor: {
                ...placement.anchor
              },
              origin: {
                ...placement.origin
              }
            };
            const flip = key === 'x' ? axis === 'y' ? flipAlign : flipSide : axis === 'y' ? flipSide : flipAlign;
            newPlacement.anchor = flip(newPlacement.anchor);
            newPlacement.origin = flip(newPlacement.origin);
            const {
              overflows: newOverflows
            } = checkOverflow(newPlacement);
            if (newOverflows[key].before <= overflows[key].before && newOverflows[key].after <= overflows[key].after || newOverflows[key].before + newOverflows[key].after < (overflows[key].before + overflows[key].after) / 2) {
              placement = newPlacement;
              reset = flipped[key] = true;
            }
          }
        });
        if (reset) continue;
      }

      // shift
      if (overflows.x.before) {
        x += overflows.x.before;
        contentBox.x += overflows.x.before;
      }
      if (overflows.x.after) {
        x -= overflows.x.after;
        contentBox.x -= overflows.x.after;
      }
      if (overflows.y.before) {
        y += overflows.y.before;
        contentBox.y += overflows.y.before;
      }
      if (overflows.y.after) {
        y -= overflows.y.after;
        contentBox.y -= overflows.y.after;
      }

      // size
      {
        const overflows = getOverflow(contentBox, viewport);
        available.x = viewport.width - overflows.x.before - overflows.x.after;
        available.y = viewport.height - overflows.y.before - overflows.y.after;
        x += overflows.x.before;
        contentBox.x += overflows.x.before;
        y += overflows.y.before;
        contentBox.y += overflows.y.before;
      }
      break;
    }
    const axis = getAxis(placement.anchor);
    Object.assign(contentStyles.value, {
      '--v-overlay-anchor-origin': `${placement.anchor.side} ${placement.anchor.align}`,
      transformOrigin: `${placement.origin.side} ${placement.origin.align}`,
      // transform: `translate(${pixelRound(x)}px, ${pixelRound(y)}px)`,
      top: convertToUnit(pixelRound(y)),
      left: data.isRtl.value ? undefined : convertToUnit(pixelRound(x)),
      right: data.isRtl.value ? convertToUnit(pixelRound(-x)) : undefined,
      minWidth: convertToUnit(axis === 'y' ? Math.min(minWidth.value, targetBox.width) : minWidth.value),
      maxWidth: convertToUnit(pixelCeil(clamp(available.x, minWidth.value === Infinity ? 0 : minWidth.value, maxWidth.value))),
      maxHeight: convertToUnit(pixelCeil(clamp(available.y, minHeight.value === Infinity ? 0 : minHeight.value, maxHeight.value)))
    });
    return {
      available,
      contentBox,
      flipped
    };
  }
  watch$w(() => [preferredAnchor.value, preferredOrigin.value, props.offset, props.minWidth, props.minHeight, props.maxWidth, props.maxHeight], () => updateLocation());
  nextTick$l(() => {
    const result = updateLocation();

    // TODO: overflowing content should only require a single updateLocation call
    // Icky hack to make sure the content is positioned consistently
    if (!result) return;
    const {
      available,
      contentBox
    } = result;
    if (contentBox.height > available.y) {
      requestAnimationFrame(() => {
        updateLocation();
        requestAnimationFrame(() => {
          updateLocation();
        });
      });
    }
  });
  return {
    updateLocation
  };
}
function pixelRound(val) {
  return Math.round(val * devicePixelRatio) / devicePixelRatio;
}
function pixelCeil(val) {
  return Math.ceil(val * devicePixelRatio) / devicePixelRatio;
}

let clean = true;
const frames = [];

/**
 * Schedule a task to run in an animation frame on its own
 * This is useful for heavy tasks that may cause jank if all ran together
 */
function requestNewFrame(cb) {
  if (!clean || frames.length) {
    frames.push(cb);
    run();
  } else {
    clean = false;
    cb();
    run();
  }
}
let raf = -1;
function run() {
  cancelAnimationFrame(raf);
  raf = requestAnimationFrame(() => {
    const frame = frames.shift();
    if (frame) frame();
    if (frames.length) run();else clean = true;
  });
}

// Utilities
const {effectScope: effectScope$1,onScopeDispose: onScopeDispose$7,watchEffect: watchEffect$f} = await importShared('vue');
const scrollStrategies = {
  none: null,
  close: closeScrollStrategy,
  block: blockScrollStrategy,
  reposition: repositionScrollStrategy
};
const makeScrollStrategyProps = propsFactory({
  scrollStrategy: {
    type: [String, Function],
    default: 'block',
    validator: val => typeof val === 'function' || val in scrollStrategies
  }
}, 'VOverlay-scroll-strategies');
function useScrollStrategies(props, data) {
  if (!IN_BROWSER) return;
  let scope;
  watchEffect$f(async () => {
    scope?.stop();
    if (!(data.isActive.value && props.scrollStrategy)) return;
    scope = effectScope$1();
    await new Promise(resolve => setTimeout(resolve));
    scope.active && scope.run(() => {
      if (typeof props.scrollStrategy === 'function') {
        props.scrollStrategy(data, props, scope);
      } else {
        scrollStrategies[props.scrollStrategy]?.(data, props, scope);
      }
    });
  });
  onScopeDispose$7(() => {
    scope?.stop();
  });
}
function closeScrollStrategy(data) {
  function onScroll(e) {
    data.isActive.value = false;
  }
  bindScroll(data.targetEl.value ?? data.contentEl.value, onScroll);
}
function blockScrollStrategy(data, props) {
  const offsetParent = data.root.value?.offsetParent;
  const scrollElements = [...new Set([...getScrollParents(data.targetEl.value, props.contained ? offsetParent : undefined), ...getScrollParents(data.contentEl.value, props.contained ? offsetParent : undefined)])].filter(el => !el.classList.contains('v-overlay-scroll-blocked'));
  const scrollbarWidth = window.innerWidth - document.documentElement.offsetWidth;
  const scrollableParent = (el => hasScrollbar(el) && el)(offsetParent || document.documentElement);
  if (scrollableParent) {
    data.root.value.classList.add('v-overlay--scroll-blocked');
  }
  scrollElements.forEach((el, i) => {
    el.style.setProperty('--v-body-scroll-x', convertToUnit(-el.scrollLeft));
    el.style.setProperty('--v-body-scroll-y', convertToUnit(-el.scrollTop));
    if (el !== document.documentElement) {
      el.style.setProperty('--v-scrollbar-offset', convertToUnit(scrollbarWidth));
    }
    el.classList.add('v-overlay-scroll-blocked');
  });
  onScopeDispose$7(() => {
    scrollElements.forEach((el, i) => {
      const x = parseFloat(el.style.getPropertyValue('--v-body-scroll-x'));
      const y = parseFloat(el.style.getPropertyValue('--v-body-scroll-y'));
      const scrollBehavior = el.style.scrollBehavior;
      el.style.scrollBehavior = 'auto';
      el.style.removeProperty('--v-body-scroll-x');
      el.style.removeProperty('--v-body-scroll-y');
      el.style.removeProperty('--v-scrollbar-offset');
      el.classList.remove('v-overlay-scroll-blocked');
      el.scrollLeft = -x;
      el.scrollTop = -y;
      el.style.scrollBehavior = scrollBehavior;
    });
    if (scrollableParent) {
      data.root.value.classList.remove('v-overlay--scroll-blocked');
    }
  });
}
function repositionScrollStrategy(data, props, scope) {
  let slow = false;
  let raf = -1;
  let ric = -1;
  function update(e) {
    requestNewFrame(() => {
      const start = performance.now();
      data.updateLocation.value?.(e);
      const time = performance.now() - start;
      slow = time / (1000 / 60) > 2;
    });
  }
  ric = (typeof requestIdleCallback === 'undefined' ? cb => cb() : requestIdleCallback)(() => {
    scope.run(() => {
      bindScroll(data.targetEl.value ?? data.contentEl.value, e => {
        if (slow) {
          // If the position calculation is slow,
          // defer updates until scrolling is finished.
          // Browsers usually fire one scroll event per frame so
          // we just wait until we've got two frames without an event
          cancelAnimationFrame(raf);
          raf = requestAnimationFrame(() => {
            raf = requestAnimationFrame(() => {
              update(e);
            });
          });
        } else {
          update(e);
        }
      });
    });
  });
  onScopeDispose$7(() => {
    typeof cancelIdleCallback !== 'undefined' && cancelIdleCallback(ric);
    cancelAnimationFrame(raf);
  });
}

/** @private */
function bindScroll(el, onScroll) {
  const scrollElements = [document, ...getScrollParents(el)];
  scrollElements.forEach(el => {
    el.addEventListener('scroll', onScroll, {
      passive: true
    });
  });
  onScopeDispose$7(() => {
    scrollElements.forEach(el => {
      el.removeEventListener('scroll', onScroll);
    });
  });
}

// Types

const VMenuSymbol = Symbol.for('vuetify:v-menu');

// Utilities
// Composables
const makeDelayProps = propsFactory({
  closeDelay: [Number, String],
  openDelay: [Number, String]
}, 'delay');
function useDelay(props, cb) {
  let clearDelay = () => {};
  function runDelay(isOpening) {
    clearDelay?.();
    const delay = Number(isOpening ? props.openDelay : props.closeDelay);
    return new Promise(resolve => {
      clearDelay = defer(delay, () => {
        cb?.(isOpening);
        resolve(isOpening);
      });
    });
  }
  function runOpenDelay() {
    return runDelay(true);
  }
  function runCloseDelay() {
    return runDelay(false);
  }
  return {
    clearDelay,
    runOpenDelay,
    runCloseDelay
  };
}

const {computed: computed$1e,effectScope,inject: inject$g,mergeProps: mergeProps$b,nextTick: nextTick$k,onScopeDispose: onScopeDispose$6,ref: ref$D,watch: watch$v,watchEffect: watchEffect$e} = await importShared('vue');
const makeActivatorProps = propsFactory({
  target: [String, Object],
  activator: [String, Object],
  activatorProps: {
    type: Object,
    default: () => ({})
  },
  openOnClick: {
    type: Boolean,
    default: undefined
  },
  openOnHover: Boolean,
  openOnFocus: {
    type: Boolean,
    default: undefined
  },
  closeOnContentClick: Boolean,
  ...makeDelayProps()
}, 'VOverlay-activator');
function useActivator(props, _ref) {
  let {
    isActive,
    isTop,
    contentEl
  } = _ref;
  const vm = getCurrentInstance('useActivator');
  const activatorEl = ref$D();
  let isHovered = false;
  let isFocused = false;
  let firstEnter = true;
  const openOnFocus = computed$1e(() => props.openOnFocus || props.openOnFocus == null && props.openOnHover);
  const openOnClick = computed$1e(() => props.openOnClick || props.openOnClick == null && !props.openOnHover && !openOnFocus.value);
  const {
    runOpenDelay,
    runCloseDelay
  } = useDelay(props, value => {
    if (value === (props.openOnHover && isHovered || openOnFocus.value && isFocused) && !(props.openOnHover && isActive.value && !isTop.value)) {
      if (isActive.value !== value) {
        firstEnter = true;
      }
      isActive.value = value;
    }
  });
  const cursorTarget = ref$D();
  const availableEvents = {
    onClick: e => {
      e.stopPropagation();
      activatorEl.value = e.currentTarget || e.target;
      if (!isActive.value) {
        cursorTarget.value = [e.clientX, e.clientY];
      }
      isActive.value = !isActive.value;
    },
    onMouseenter: e => {
      if (e.sourceCapabilities?.firesTouchEvents) return;
      isHovered = true;
      activatorEl.value = e.currentTarget || e.target;
      runOpenDelay();
    },
    onMouseleave: e => {
      isHovered = false;
      runCloseDelay();
    },
    onFocus: e => {
      if (matchesSelector(e.target, ':focus-visible') === false) return;
      isFocused = true;
      e.stopPropagation();
      activatorEl.value = e.currentTarget || e.target;
      runOpenDelay();
    },
    onBlur: e => {
      isFocused = false;
      e.stopPropagation();
      runCloseDelay();
    }
  };
  const activatorEvents = computed$1e(() => {
    const events = {};
    if (openOnClick.value) {
      events.onClick = availableEvents.onClick;
    }
    if (props.openOnHover) {
      events.onMouseenter = availableEvents.onMouseenter;
      events.onMouseleave = availableEvents.onMouseleave;
    }
    if (openOnFocus.value) {
      events.onFocus = availableEvents.onFocus;
      events.onBlur = availableEvents.onBlur;
    }
    return events;
  });
  const contentEvents = computed$1e(() => {
    const events = {};
    if (props.openOnHover) {
      events.onMouseenter = () => {
        isHovered = true;
        runOpenDelay();
      };
      events.onMouseleave = () => {
        isHovered = false;
        runCloseDelay();
      };
    }
    if (openOnFocus.value) {
      events.onFocusin = () => {
        isFocused = true;
        runOpenDelay();
      };
      events.onFocusout = () => {
        isFocused = false;
        runCloseDelay();
      };
    }
    if (props.closeOnContentClick) {
      const menu = inject$g(VMenuSymbol, null);
      events.onClick = () => {
        isActive.value = false;
        menu?.closeParents();
      };
    }
    return events;
  });
  const scrimEvents = computed$1e(() => {
    const events = {};
    if (props.openOnHover) {
      events.onMouseenter = () => {
        if (firstEnter) {
          isHovered = true;
          firstEnter = false;
          runOpenDelay();
        }
      };
      events.onMouseleave = () => {
        isHovered = false;
        runCloseDelay();
      };
    }
    return events;
  });
  watch$v(isTop, val => {
    if (val && (props.openOnHover && !isHovered && (!openOnFocus.value || !isFocused) || openOnFocus.value && !isFocused && (!props.openOnHover || !isHovered)) && !contentEl.value?.contains(document.activeElement)) {
      isActive.value = false;
    }
  });
  watch$v(isActive, val => {
    if (!val) {
      setTimeout(() => {
        cursorTarget.value = undefined;
      });
    }
  }, {
    flush: 'post'
  });
  const activatorRef = templateRef();
  watchEffect$e(() => {
    if (!activatorRef.value) return;
    nextTick$k(() => {
      activatorEl.value = activatorRef.el;
    });
  });
  const targetRef = templateRef();
  const target = computed$1e(() => {
    if (props.target === 'cursor' && cursorTarget.value) return cursorTarget.value;
    if (targetRef.value) return targetRef.el;
    return getTarget(props.target, vm) || activatorEl.value;
  });
  const targetEl = computed$1e(() => {
    return Array.isArray(target.value) ? undefined : target.value;
  });
  let scope;
  watch$v(() => !!props.activator, val => {
    if (val && IN_BROWSER) {
      scope = effectScope();
      scope.run(() => {
        _useActivator(props, vm, {
          activatorEl,
          activatorEvents
        });
      });
    } else if (scope) {
      scope.stop();
    }
  }, {
    flush: 'post',
    immediate: true
  });
  onScopeDispose$6(() => {
    scope?.stop();
  });
  return {
    activatorEl,
    activatorRef,
    target,
    targetEl,
    targetRef,
    activatorEvents,
    contentEvents,
    scrimEvents
  };
}
function _useActivator(props, vm, _ref2) {
  let {
    activatorEl,
    activatorEvents
  } = _ref2;
  watch$v(() => props.activator, (val, oldVal) => {
    if (oldVal && val !== oldVal) {
      const activator = getActivator(oldVal);
      activator && unbindActivatorProps(activator);
    }
    if (val) {
      nextTick$k(() => bindActivatorProps());
    }
  }, {
    immediate: true
  });
  watch$v(() => props.activatorProps, () => {
    bindActivatorProps();
  });
  onScopeDispose$6(() => {
    unbindActivatorProps();
  });
  function bindActivatorProps() {
    let el = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : getActivator();
    let _props = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : props.activatorProps;
    if (!el) return;
    bindProps(el, mergeProps$b(activatorEvents.value, _props));
  }
  function unbindActivatorProps() {
    let el = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : getActivator();
    let _props = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : props.activatorProps;
    if (!el) return;
    unbindProps(el, mergeProps$b(activatorEvents.value, _props));
  }
  function getActivator() {
    let selector = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : props.activator;
    const activator = getTarget(selector, vm);

    // The activator should only be a valid element (Ignore comments and text nodes)
    activatorEl.value = activator?.nodeType === Node.ELEMENT_NODE ? activator : undefined;
    return activatorEl.value;
  }
}
function getTarget(selector, vm) {
  if (!selector) return;
  let target;
  if (selector === 'parent') {
    let el = vm?.proxy?.$el?.parentNode;
    while (el?.hasAttribute('data-no-activator')) {
      el = el.parentNode;
    }
    target = el;
  } else if (typeof selector === 'string') {
    // Selector
    target = document.querySelector(selector);
  } else if ('$el' in selector) {
    // Component (ref)
    target = selector.$el;
  } else {
    // HTMLElement | Element | [x, y]
    target = selector;
  }
  return target;
}

const {onMounted: onMounted$a,shallowRef: shallowRef$w} = await importShared('vue');
function useHydration() {
  if (!IN_BROWSER) return shallowRef$w(false);
  const {
    ssr
  } = useDisplay();
  if (ssr) {
    const isMounted = shallowRef$w(false);
    onMounted$a(() => {
      isMounted.value = true;
    });
    return isMounted;
  } else {
    return shallowRef$w(true);
  }
}

// Utilities
const {shallowRef: shallowRef$v,toRef: toRef$C,watch: watch$u} = await importShared('vue');
const makeLazyProps = propsFactory({
  eager: Boolean
}, 'lazy');
function useLazy(props, active) {
  const isBooted = shallowRef$v(false);
  const hasContent = toRef$C(() => isBooted.value || props.eager || active.value);
  watch$u(active, () => isBooted.value = true);
  function onAfterLeave() {
    if (!props.eager) isBooted.value = false;
  }
  return {
    isBooted,
    hasContent,
    onAfterLeave
  };
}

// Utilities
function useScopeId() {
  const vm = getCurrentInstance('useScopeId');
  const scopeId = vm.vnode.scopeId;
  return {
    scopeId: scopeId ? {
      [scopeId]: ''
    } : undefined
  };
}

const {inject: inject$f,onScopeDispose: onScopeDispose$5,provide: provide$b,reactive,readonly: readonly$1,shallowRef: shallowRef$u,toRaw: toRaw$1,toRef: toRef$B,toValue,watchEffect: watchEffect$d} = await importShared('vue');
const StackSymbol = Symbol.for('vuetify:stack');
const globalStack = reactive([]);
function useStack(isActive, zIndex, disableGlobalStack) {
  const vm = getCurrentInstance('useStack');
  const createStackEntry = !disableGlobalStack;
  const parent = inject$f(StackSymbol, undefined);
  const stack = reactive({
    activeChildren: new Set()
  });
  provide$b(StackSymbol, stack);
  const _zIndex = shallowRef$u(Number(toValue(zIndex)));
  useToggleScope(isActive, () => {
    const lastZIndex = globalStack.at(-1)?.[1];
    _zIndex.value = lastZIndex ? lastZIndex + 10 : Number(toValue(zIndex));
    if (createStackEntry) {
      globalStack.push([vm.uid, _zIndex.value]);
    }
    parent?.activeChildren.add(vm.uid);
    onScopeDispose$5(() => {
      if (createStackEntry) {
        const idx = toRaw$1(globalStack).findIndex(v => v[0] === vm.uid);
        globalStack.splice(idx, 1);
      }
      parent?.activeChildren.delete(vm.uid);
    });
  });
  const globalTop = shallowRef$u(true);
  if (createStackEntry) {
    watchEffect$d(() => {
      const _isTop = globalStack.at(-1)?.[0] === vm.uid;
      setTimeout(() => globalTop.value = _isTop);
    });
  }
  const localTop = toRef$B(() => !stack.activeChildren.size);
  return {
    globalTop: readonly$1(globalTop),
    localTop,
    stackStyles: toRef$B(() => ({
      zIndex: _zIndex.value
    }))
  };
}

// Utilities
const {computed: computed$1d,warn} = await importShared('vue');
function useTeleport(target) {
  const teleportTarget = computed$1d(() => {
    const _target = target();
    if (_target === true || !IN_BROWSER) return undefined;
    const targetElement = _target === false ? document.body : typeof _target === 'string' ? document.querySelector(_target) : _target;
    if (targetElement == null) {
      warn(`Unable to locate target ${_target}`);
      return undefined;
    }
    let container = [...targetElement.children].find(el => el.matches('.v-overlay-container'));
    if (!container) {
      container = document.createElement('div');
      container.className = 'v-overlay-container';
      targetElement.appendChild(container);
    }
    return container;
  });
  return {
    teleportTarget
  };
}

// Utilities
function defaultConditional() {
  return true;
}
function checkEvent(e, el, binding) {
  // The include element callbacks below can be expensive
  // so we should avoid calling them when we're not active.
  // Explicitly check for false to allow fallback compatibility
  // with non-toggleable components
  if (!e || checkIsActive(e, binding) === false) return false;

  // If we're clicking inside the shadowroot, then the app root doesn't get the same
  // level of introspection as to _what_ we're clicking. We want to check to see if
  // our target is the shadowroot parent container, and if it is, ignore.
  const root = attachedRoot(el);
  if (typeof ShadowRoot !== 'undefined' && root instanceof ShadowRoot && root.host === e.target) return false;

  // Check if additional elements were passed to be included in check
  // (click must be outside all included elements, if any)
  const elements = (typeof binding.value === 'object' && binding.value.include || (() => []))();
  // Add the root element for the component this directive was defined on
  elements.push(el);

  // Check if it's a click outside our elements, and then if our callback returns true.
  // Non-toggleable components should take action in their callback and return falsy.
  // Toggleable can return true if it wants to deactivate.
  // Note that, because we're in the capture phase, this callback will occur before
  // the bubbling click event on any outside elements.
  return !elements.some(el => el?.contains(e.target));
}
function checkIsActive(e, binding) {
  const isActive = typeof binding.value === 'object' && binding.value.closeConditional || defaultConditional;
  return isActive(e);
}
function directive(e, el, binding) {
  const handler = typeof binding.value === 'function' ? binding.value : binding.value.handler;

  // Clicks in the Shadow DOM change their target while using setTimeout, so the original target is saved here
  e.shadowTarget = e.target;
  el._clickOutside.lastMousedownWasOutside && checkEvent(e, el, binding) && setTimeout(() => {
    checkIsActive(e, binding) && handler && handler(e);
  }, 0);
}
function handleShadow(el, callback) {
  const root = attachedRoot(el);
  callback(document);
  if (typeof ShadowRoot !== 'undefined' && root instanceof ShadowRoot) {
    callback(root);
  }
}
const ClickOutside = {
  // [data-app] may not be found
  // if using bind, inserted makes
  // sure that the root element is
  // available, iOS does not support
  // clicks on body
  mounted(el, binding) {
    const onClick = e => directive(e, el, binding);
    const onMousedown = e => {
      el._clickOutside.lastMousedownWasOutside = checkEvent(e, el, binding);
    };
    handleShadow(el, app => {
      app.addEventListener('click', onClick, true);
      app.addEventListener('mousedown', onMousedown, true);
    });
    if (!el._clickOutside) {
      el._clickOutside = {
        lastMousedownWasOutside: false
      };
    }
    el._clickOutside[binding.instance.$.uid] = {
      onClick,
      onMousedown
    };
  },
  beforeUnmount(el, binding) {
    if (!el._clickOutside) return;
    handleShadow(el, app => {
      if (!app || !el._clickOutside?.[binding.instance.$.uid]) return;
      const {
        onClick,
        onMousedown
      } = el._clickOutside[binding.instance.$.uid];
      app.removeEventListener('click', onClick, true);
      app.removeEventListener('mousedown', onMousedown, true);
    });
    delete el._clickOutside[binding.instance.$.uid];
  }
};

const {mergeProps:_mergeProps$S,createVNode:_createVNode$1I,Fragment:_Fragment$z,vShow:_vShow$7,resolveDirective:_resolveDirective$8,withDirectives:_withDirectives$e} = await importShared('vue');
const {computed: computed$1c,mergeProps: mergeProps$a,onBeforeUnmount: onBeforeUnmount$6,ref: ref$C,Teleport,Transition: Transition$1,watch: watch$t} = await importShared('vue');
function Scrim(props) {
  const {
    modelValue,
    color,
    ...rest
  } = props;
  return _createVNode$1I(Transition$1, {
    "name": "fade-transition",
    "appear": true
  }, {
    default: () => [props.modelValue && _createVNode$1I("div", _mergeProps$S({
      "class": ['v-overlay__scrim', props.color.backgroundColorClasses.value],
      "style": props.color.backgroundColorStyles.value
    }, rest), null)]
  });
}
const makeVOverlayProps = propsFactory({
  absolute: Boolean,
  attach: [Boolean, String, Object],
  closeOnBack: {
    type: Boolean,
    default: true
  },
  contained: Boolean,
  contentClass: null,
  contentProps: null,
  disabled: Boolean,
  opacity: [Number, String],
  noClickAnimation: Boolean,
  modelValue: Boolean,
  persistent: Boolean,
  scrim: {
    type: [Boolean, String],
    default: true
  },
  zIndex: {
    type: [Number, String],
    default: 2000
  },
  ...makeActivatorProps(),
  ...makeComponentProps(),
  ...makeDimensionProps(),
  ...makeLazyProps(),
  ...makeLocationStrategyProps(),
  ...makeScrollStrategyProps(),
  ...makeThemeProps(),
  ...makeTransitionProps()
}, 'VOverlay');
const VOverlay = genericComponent()({
  name: 'VOverlay',
  directives: {
    ClickOutside
  },
  inheritAttrs: false,
  props: {
    _disableGlobalStack: Boolean,
    ...makeVOverlayProps()
  },
  emits: {
    'click:outside': e => true,
    'update:modelValue': value => true,
    keydown: e => true,
    afterEnter: () => true,
    afterLeave: () => true
  },
  setup(props, _ref) {
    let {
      slots,
      attrs,
      emit
    } = _ref;
    const vm = getCurrentInstance('VOverlay');
    const root = ref$C();
    const scrimEl = ref$C();
    const contentEl = ref$C();
    const model = useProxiedModel(props, 'modelValue');
    const isActive = computed$1c({
      get: () => model.value,
      set: v => {
        if (!(v && props.disabled)) model.value = v;
      }
    });
    const {
      themeClasses
    } = provideTheme(props);
    const {
      rtlClasses,
      isRtl
    } = useRtl();
    const {
      hasContent,
      onAfterLeave: _onAfterLeave
    } = useLazy(props, isActive);
    const scrimColor = useBackgroundColor(() => {
      return typeof props.scrim === 'string' ? props.scrim : null;
    });
    const {
      globalTop,
      localTop,
      stackStyles
    } = useStack(isActive, () => props.zIndex, props._disableGlobalStack);
    const {
      activatorEl,
      activatorRef,
      target,
      targetEl,
      targetRef,
      activatorEvents,
      contentEvents,
      scrimEvents
    } = useActivator(props, {
      isActive,
      isTop: localTop,
      contentEl
    });
    const {
      teleportTarget
    } = useTeleport(() => {
      const target = props.attach || props.contained;
      if (target) return target;
      const rootNode = activatorEl?.value?.getRootNode() || vm.proxy?.$el?.getRootNode();
      if (rootNode instanceof ShadowRoot) return rootNode;
      return false;
    });
    const {
      dimensionStyles
    } = useDimension(props);
    const isMounted = useHydration();
    const {
      scopeId
    } = useScopeId();
    watch$t(() => props.disabled, v => {
      if (v) isActive.value = false;
    });
    const {
      contentStyles,
      updateLocation
    } = useLocationStrategies(props, {
      isRtl,
      contentEl,
      target,
      isActive
    });
    useScrollStrategies(props, {
      root,
      contentEl,
      targetEl,
      isActive,
      updateLocation
    });
    function onClickOutside(e) {
      emit('click:outside', e);
      if (!props.persistent) isActive.value = false;else animateClick();
    }
    function closeConditional(e) {
      return isActive.value && globalTop.value && (
      // If using scrim, only close if clicking on it rather than anything opened on top
      !props.scrim || e.target === scrimEl.value || e instanceof MouseEvent && e.shadowTarget === scrimEl.value);
    }
    IN_BROWSER && watch$t(isActive, val => {
      if (val) {
        window.addEventListener('keydown', onKeydown);
      } else {
        window.removeEventListener('keydown', onKeydown);
      }
    }, {
      immediate: true
    });
    onBeforeUnmount$6(() => {
      if (!IN_BROWSER) return;
      window.removeEventListener('keydown', onKeydown);
    });
    function onKeydown(e) {
      if (e.key === 'Escape' && globalTop.value) {
        if (!contentEl.value?.contains(document.activeElement)) {
          emit('keydown', e);
        }
        if (!props.persistent) {
          isActive.value = false;
          if (contentEl.value?.contains(document.activeElement)) {
            activatorEl.value?.focus();
          }
        } else animateClick();
      }
    }
    function onKeydownSelf(e) {
      if (e.key === 'Escape' && !globalTop.value) return;
      emit('keydown', e);
    }
    const router = useRouter();
    useToggleScope(() => props.closeOnBack, () => {
      useBackButton(router, next => {
        if (globalTop.value && isActive.value) {
          next(false);
          if (!props.persistent) isActive.value = false;else animateClick();
        } else {
          next();
        }
      });
    });
    const top = ref$C();
    watch$t(() => isActive.value && (props.absolute || props.contained) && teleportTarget.value == null, val => {
      if (val) {
        const scrollParent = getScrollParent(root.value);
        if (scrollParent && scrollParent !== document.scrollingElement) {
          top.value = scrollParent.scrollTop;
        }
      }
    });

    // Add a quick "bounce" animation to the content
    function animateClick() {
      if (props.noClickAnimation) return;
      contentEl.value && animate(contentEl.value, [{
        transformOrigin: 'center'
      }, {
        transform: 'scale(1.03)'
      }, {
        transformOrigin: 'center'
      }], {
        duration: 150,
        easing: standardEasing
      });
    }
    function onAfterEnter() {
      emit('afterEnter');
    }
    function onAfterLeave() {
      _onAfterLeave();
      emit('afterLeave');
    }
    useRender(() => _createVNode$1I(_Fragment$z, null, [slots.activator?.({
      isActive: isActive.value,
      targetRef,
      props: mergeProps$a({
        ref: activatorRef
      }, activatorEvents.value, props.activatorProps)
    }), isMounted.value && hasContent.value && _createVNode$1I(Teleport, {
      "disabled": !teleportTarget.value,
      "to": teleportTarget.value
    }, {
      default: () => [_createVNode$1I("div", _mergeProps$S({
        "class": ['v-overlay', {
          'v-overlay--absolute': props.absolute || props.contained,
          'v-overlay--active': isActive.value,
          'v-overlay--contained': props.contained
        }, themeClasses.value, rtlClasses.value, props.class],
        "style": [stackStyles.value, {
          '--v-overlay-opacity': props.opacity,
          top: convertToUnit(top.value)
        }, props.style],
        "ref": root,
        "onKeydown": onKeydownSelf
      }, scopeId, attrs), [_createVNode$1I(Scrim, _mergeProps$S({
        "color": scrimColor,
        "modelValue": isActive.value && !!props.scrim,
        "ref": scrimEl
      }, scrimEvents.value), null), _createVNode$1I(MaybeTransition, {
        "appear": true,
        "persisted": true,
        "transition": props.transition,
        "target": target.value,
        "onAfterEnter": onAfterEnter,
        "onAfterLeave": onAfterLeave
      }, {
        default: () => [_withDirectives$e(_createVNode$1I("div", _mergeProps$S({
          "ref": contentEl,
          "class": ['v-overlay__content', props.contentClass],
          "style": [dimensionStyles.value, contentStyles.value]
        }, contentEvents.value, props.contentProps), [slots.default?.({
          isActive
        })]), [[_vShow$7, isActive.value], [_resolveDirective$8("click-outside"), {
          handler: onClickOutside,
          closeConditional,
          include: () => [activatorEl.value]
        }]])]
      })])]
    })]));
    return {
      activatorEl,
      scrimEl,
      target,
      animateClick,
      contentEl,
      globalTop,
      localTop,
      updateLocation
    };
  }
});

// Types

const Refs = Symbol('Forwarded refs');

/** Omit properties starting with P */

/** Omit keyof $props from T */

function getDescriptor(obj, key) {
  let currentObj = obj;
  while (currentObj) {
    const descriptor = Reflect.getOwnPropertyDescriptor(currentObj, key);
    if (descriptor) return descriptor;
    currentObj = Object.getPrototypeOf(currentObj);
  }
  return undefined;
}
function forwardRefs(target) {
  for (var _len = arguments.length, refs = new Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {
    refs[_key - 1] = arguments[_key];
  }
  target[Refs] = refs;
  return new Proxy(target, {
    get(target, key) {
      if (Reflect.has(target, key)) {
        return Reflect.get(target, key);
      }

      // Skip internal properties
      if (typeof key === 'symbol' || key.startsWith('$') || key.startsWith('__')) return;
      for (const ref of refs) {
        if (ref.value && Reflect.has(ref.value, key)) {
          const val = Reflect.get(ref.value, key);
          return typeof val === 'function' ? val.bind(ref.value) : val;
        }
      }
    },
    has(target, key) {
      if (Reflect.has(target, key)) {
        return true;
      }

      // Skip internal properties
      if (typeof key === 'symbol' || key.startsWith('$') || key.startsWith('__')) return false;
      for (const ref of refs) {
        if (ref.value && Reflect.has(ref.value, key)) {
          return true;
        }
      }
      return false;
    },
    set(target, key, value) {
      if (Reflect.has(target, key)) {
        return Reflect.set(target, key, value);
      }

      // Skip internal properties
      if (typeof key === 'symbol' || key.startsWith('$') || key.startsWith('__')) return false;
      for (const ref of refs) {
        if (ref.value && Reflect.has(ref.value, key)) {
          return Reflect.set(ref.value, key, value);
        }
      }
      return false;
    },
    getOwnPropertyDescriptor(target, key) {
      const descriptor = Reflect.getOwnPropertyDescriptor(target, key);
      if (descriptor) return descriptor;

      // Skip internal properties
      if (typeof key === 'symbol' || key.startsWith('$') || key.startsWith('__')) return;

      // Check each ref's own properties
      for (const ref of refs) {
        if (!ref.value) continue;
        const descriptor = getDescriptor(ref.value, key) ?? ('_' in ref.value ? getDescriptor(ref.value._?.setupState, key) : undefined);
        if (descriptor) return descriptor;
      }

      // Recursive search up each ref's prototype
      for (const ref of refs) {
        const childRefs = ref.value && ref.value[Refs];
        if (!childRefs) continue;
        const queue = childRefs.slice();
        while (queue.length) {
          const ref = queue.shift();
          const descriptor = getDescriptor(ref.value, key);
          if (descriptor) return descriptor;
          const childRefs = ref.value && ref.value[Refs];
          if (childRefs) queue.push(...childRefs);
        }
      }
      return undefined;
    }
  });
}

const {createVNode:_createVNode$1H,mergeProps:_mergeProps$R} = await importShared('vue');
const {computed: computed$1b,inject: inject$e,mergeProps: mergeProps$9,nextTick: nextTick$j,onBeforeUnmount: onBeforeUnmount$5,onDeactivated,provide: provide$a,ref: ref$B,shallowRef: shallowRef$t,toRef: toRef$A,useId: useId$7,watch: watch$s} = await importShared('vue');
const makeVMenuProps = propsFactory({
  // TODO
  // disableKeys: Boolean,
  id: String,
  submenu: Boolean,
  ...omit(makeVOverlayProps({
    closeDelay: 250,
    closeOnContentClick: true,
    locationStrategy: 'connected',
    location: undefined,
    openDelay: 300,
    scrim: false,
    scrollStrategy: 'reposition',
    transition: {
      component: VDialogTransition
    }
  }), ['absolute'])
}, 'VMenu');
const VMenu = genericComponent()({
  name: 'VMenu',
  props: makeVMenuProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const isActive = useProxiedModel(props, 'modelValue');
    const {
      scopeId
    } = useScopeId();
    const {
      isRtl
    } = useRtl();
    const uid = useId$7();
    const id = toRef$A(() => props.id || `v-menu-${uid}`);
    const overlay = ref$B();
    const parent = inject$e(VMenuSymbol, null);
    const openChildren = shallowRef$t(new Set());
    provide$a(VMenuSymbol, {
      register() {
        openChildren.value.add(uid);
      },
      unregister() {
        openChildren.value.delete(uid);
      },
      closeParents(e) {
        setTimeout(() => {
          if (!openChildren.value.size && !props.persistent && (e == null || overlay.value?.contentEl && !isClickInsideElement(e, overlay.value.contentEl))) {
            isActive.value = false;
            parent?.closeParents();
          }
        }, 40);
      }
    });
    onBeforeUnmount$5(() => {
      parent?.unregister();
      document.removeEventListener('focusin', onFocusIn);
    });
    onDeactivated(() => isActive.value = false);
    async function onFocusIn(e) {
      const before = e.relatedTarget;
      const after = e.target;
      await nextTick$j();
      if (isActive.value && before !== after && overlay.value?.contentEl &&
      // We're the topmost menu
      overlay.value?.globalTop &&
      // It isn't the document or the menu body
      ![document, overlay.value.contentEl].includes(after) &&
      // It isn't inside the menu body
      !overlay.value.contentEl.contains(after)) {
        const focusable = focusableChildren(overlay.value.contentEl);
        focusable[0]?.focus();
      }
    }
    watch$s(isActive, val => {
      if (val) {
        parent?.register();
        if (IN_BROWSER) {
          document.addEventListener('focusin', onFocusIn, {
            once: true
          });
        }
      } else {
        parent?.unregister();
        if (IN_BROWSER) {
          document.removeEventListener('focusin', onFocusIn);
        }
      }
    }, {
      immediate: true
    });
    function onClickOutside(e) {
      parent?.closeParents(e);
    }
    function onKeydown(e) {
      if (props.disabled) return;
      if (e.key === 'Tab' || e.key === 'Enter' && !props.closeOnContentClick) {
        if (e.key === 'Enter' && (e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLInputElement && !!e.target.closest('form'))) return;
        if (e.key === 'Enter') e.preventDefault();
        const nextElement = getNextElement(focusableChildren(overlay.value?.contentEl, false), e.shiftKey ? 'prev' : 'next', el => el.tabIndex >= 0);
        if (!nextElement) {
          isActive.value = false;
          overlay.value?.activatorEl?.focus();
        }
      } else if (props.submenu && e.key === (isRtl.value ? 'ArrowRight' : 'ArrowLeft')) {
        isActive.value = false;
        overlay.value?.activatorEl?.focus();
      }
    }
    function onActivatorKeydown(e) {
      if (props.disabled) return;
      const el = overlay.value?.contentEl;
      if (el && isActive.value) {
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          e.stopImmediatePropagation();
          focusChild(el, 'next');
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          e.stopImmediatePropagation();
          focusChild(el, 'prev');
        } else if (props.submenu) {
          if (e.key === (isRtl.value ? 'ArrowRight' : 'ArrowLeft')) {
            isActive.value = false;
          } else if (e.key === (isRtl.value ? 'ArrowLeft' : 'ArrowRight')) {
            e.preventDefault();
            focusChild(el, 'first');
          }
        }
      } else if (props.submenu ? e.key === (isRtl.value ? 'ArrowLeft' : 'ArrowRight') : ['ArrowDown', 'ArrowUp'].includes(e.key)) {
        isActive.value = true;
        e.preventDefault();
        setTimeout(() => setTimeout(() => onActivatorKeydown(e)));
      }
    }
    const activatorProps = computed$1b(() => mergeProps$9({
      'aria-haspopup': 'menu',
      'aria-expanded': String(isActive.value),
      'aria-controls': id.value,
      onKeydown: onActivatorKeydown
    }, props.activatorProps));
    useRender(() => {
      const overlayProps = VOverlay.filterProps(props);
      return _createVNode$1H(VOverlay, _mergeProps$R({
        "ref": overlay,
        "id": id.value,
        "class": ['v-menu', props.class],
        "style": props.style
      }, overlayProps, {
        "modelValue": isActive.value,
        "onUpdate:modelValue": $event => isActive.value = $event,
        "absolute": true,
        "activatorProps": activatorProps.value,
        "location": props.location ?? (props.submenu ? 'end' : 'bottom'),
        "onClick:outside": onClickOutside,
        "onKeydown": onKeydown
      }, scopeId), {
        activator: slots.activator,
        default: function () {
          for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
            args[_key] = arguments[_key];
          }
          return _createVNode$1H(VDefaultsProvider, {
            "root": "VMenu"
          }, {
            default: () => [slots.default?.(...args)]
          });
        }
      });
    });
    return forwardRefs({
      id,
      ΨopenChildren: openChildren
    }, overlay);
  }
});

const {vShow:_vShow$6,createVNode:_createVNode$1G,withDirectives:_withDirectives$d} = await importShared('vue');
const {toRef: toRef$z} = await importShared('vue');
const makeVCounterProps = propsFactory({
  active: Boolean,
  disabled: Boolean,
  max: [Number, String],
  value: {
    type: [Number, String],
    default: 0
  },
  ...makeComponentProps(),
  ...makeTransitionProps({
    transition: {
      component: VSlideYTransition
    }
  })
}, 'VCounter');
const VCounter = genericComponent()({
  name: 'VCounter',
  functional: true,
  props: makeVCounterProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const counter = toRef$z(() => {
      return props.max ? `${props.value} / ${props.max}` : String(props.value);
    });
    useRender(() => _createVNode$1G(MaybeTransition, {
      "transition": props.transition
    }, {
      default: () => [_withDirectives$d(_createVNode$1G("div", {
        "class": ['v-counter', {
          'text-error': props.max && !props.disabled && parseFloat(props.value) > parseFloat(props.max)
        }, props.class],
        "style": props.style
      }, [slots.default ? slots.default({
        counter: counter.value,
        max: props.max,
        value: props.value
      }) : counter.value]), [[_vShow$6, props.active]])]
    }));
    return {};
  }
});

const {createVNode:_createVNode$1F} = await importShared('vue');
const makeVFieldLabelProps = propsFactory({
  floating: Boolean,
  ...makeComponentProps()
}, 'VFieldLabel');
const VFieldLabel = genericComponent()({
  name: 'VFieldLabel',
  props: makeVFieldLabelProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    useRender(() => _createVNode$1F(VLabel, {
      "class": ['v-field-label', {
        'v-field-label--floating': props.floating
      }, props.class],
      "style": props.style,
      "aria-hidden": props.floating || undefined
    }, slots));
    return {};
  }
});

const {createVNode:_createVNode$1E,vShow:_vShow$5,withDirectives:_withDirectives$c,Fragment:_Fragment$y,mergeProps:_mergeProps$Q} = await importShared('vue');
const {computed: computed$1a,ref: ref$A,toRef: toRef$y,useId: useId$6,watch: watch$r} = await importShared('vue');
const allowedVariants$1 = ['underlined', 'outlined', 'filled', 'solo', 'solo-inverted', 'solo-filled', 'plain'];
const makeVFieldProps = propsFactory({
  appendInnerIcon: IconValue,
  bgColor: String,
  clearable: Boolean,
  clearIcon: {
    type: IconValue,
    default: '$clear'
  },
  active: Boolean,
  centerAffix: {
    type: Boolean,
    default: undefined
  },
  color: String,
  baseColor: String,
  dirty: Boolean,
  disabled: {
    type: Boolean,
    default: null
  },
  glow: Boolean,
  error: Boolean,
  flat: Boolean,
  iconColor: [Boolean, String],
  label: String,
  persistentClear: Boolean,
  prependInnerIcon: IconValue,
  reverse: Boolean,
  singleLine: Boolean,
  variant: {
    type: String,
    default: 'filled',
    validator: v => allowedVariants$1.includes(v)
  },
  'onClick:clear': EventProp(),
  'onClick:appendInner': EventProp(),
  'onClick:prependInner': EventProp(),
  ...makeComponentProps(),
  ...makeLoaderProps(),
  ...makeRoundedProps(),
  ...makeThemeProps()
}, 'VField');
const VField = genericComponent()({
  name: 'VField',
  inheritAttrs: false,
  props: {
    id: String,
    ...makeFocusProps(),
    ...makeVFieldProps()
  },
  emits: {
    'update:focused': focused => true,
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      attrs,
      emit,
      slots
    } = _ref;
    const {
      themeClasses
    } = provideTheme(props);
    const {
      loaderClasses
    } = useLoader(props);
    const {
      focusClasses,
      isFocused,
      focus,
      blur
    } = useFocus(props);
    const {
      InputIcon
    } = useInputIcon(props);
    const {
      roundedClasses
    } = useRounded(props);
    const {
      rtlClasses
    } = useRtl();
    const isActive = toRef$y(() => props.dirty || props.active);
    const hasLabel = toRef$y(() => !!(props.label || slots.label));
    const hasFloatingLabel = toRef$y(() => !props.singleLine && hasLabel.value);
    const uid = useId$6();
    const id = computed$1a(() => props.id || `input-${uid}`);
    const messagesId = toRef$y(() => `${id.value}-messages`);
    const labelRef = ref$A();
    const floatingLabelRef = ref$A();
    const controlRef = ref$A();
    const isPlainOrUnderlined = computed$1a(() => ['plain', 'underlined'].includes(props.variant));
    const color = computed$1a(() => {
      return props.error || props.disabled ? undefined : isActive.value && isFocused.value ? props.color : props.baseColor;
    });
    const iconColor = computed$1a(() => {
      if (!props.iconColor || props.glow && !isFocused.value) return undefined;
      return props.iconColor === true ? color.value : props.iconColor;
    });
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.bgColor);
    const {
      textColorClasses,
      textColorStyles
    } = useTextColor(color);
    watch$r(isActive, val => {
      if (hasFloatingLabel.value) {
        const el = labelRef.value.$el;
        const targetEl = floatingLabelRef.value.$el;
        requestAnimationFrame(() => {
          const rect = nullifyTransforms(el);
          const targetRect = targetEl.getBoundingClientRect();
          const x = targetRect.x - rect.x;
          const y = targetRect.y - rect.y - (rect.height / 2 - targetRect.height / 2);
          const targetWidth = targetRect.width / 0.75;
          const width = Math.abs(targetWidth - rect.width) > 1 ? {
            maxWidth: convertToUnit(targetWidth)
          } : undefined;
          const style = getComputedStyle(el);
          const targetStyle = getComputedStyle(targetEl);
          const duration = parseFloat(style.transitionDuration) * 1000 || 150;
          const scale = parseFloat(targetStyle.getPropertyValue('--v-field-label-scale'));
          const color = targetStyle.getPropertyValue('color');
          el.style.visibility = 'visible';
          targetEl.style.visibility = 'hidden';
          animate(el, {
            transform: `translate(${x}px, ${y}px) scale(${scale})`,
            color,
            ...width
          }, {
            duration,
            easing: standardEasing,
            direction: val ? 'normal' : 'reverse'
          }).finished.then(() => {
            el.style.removeProperty('visibility');
            targetEl.style.removeProperty('visibility');
          });
        });
      }
    }, {
      flush: 'post'
    });
    const slotProps = computed$1a(() => ({
      isActive,
      isFocused,
      controlRef,
      blur,
      focus
    }));
    function onClick(e) {
      if (e.target !== document.activeElement) {
        e.preventDefault();
      }
    }
    useRender(() => {
      const isOutlined = props.variant === 'outlined';
      const hasPrepend = !!(slots['prepend-inner'] || props.prependInnerIcon);
      const hasClear = !!(props.clearable || slots.clear) && !props.disabled;
      const hasAppend = !!(slots['append-inner'] || props.appendInnerIcon || hasClear);
      const label = () => slots.label ? slots.label({
        ...slotProps.value,
        label: props.label,
        props: {
          for: id.value
        }
      }) : props.label;
      return _createVNode$1E("div", _mergeProps$Q({
        "class": ['v-field', {
          'v-field--active': isActive.value,
          'v-field--appended': hasAppend,
          'v-field--center-affix': props.centerAffix ?? !isPlainOrUnderlined.value,
          'v-field--disabled': props.disabled,
          'v-field--dirty': props.dirty,
          'v-field--error': props.error,
          'v-field--glow': props.glow,
          'v-field--flat': props.flat,
          'v-field--has-background': !!props.bgColor,
          'v-field--persistent-clear': props.persistentClear,
          'v-field--prepended': hasPrepend,
          'v-field--reverse': props.reverse,
          'v-field--single-line': props.singleLine,
          'v-field--no-label': !label(),
          [`v-field--variant-${props.variant}`]: true
        }, themeClasses.value, backgroundColorClasses.value, focusClasses.value, loaderClasses.value, roundedClasses.value, rtlClasses.value, props.class],
        "style": [backgroundColorStyles.value, props.style],
        "onClick": onClick
      }, attrs), [_createVNode$1E("div", {
        "class": "v-field__overlay"
      }, null), _createVNode$1E(LoaderSlot, {
        "name": "v-field",
        "active": !!props.loading,
        "color": props.error ? 'error' : typeof props.loading === 'string' ? props.loading : props.color
      }, {
        default: slots.loader
      }), hasPrepend && _createVNode$1E("div", {
        "key": "prepend",
        "class": "v-field__prepend-inner"
      }, [props.prependInnerIcon && _createVNode$1E(InputIcon, {
        "key": "prepend-icon",
        "name": "prependInner",
        "color": iconColor.value
      }, null), slots['prepend-inner']?.(slotProps.value)]), _createVNode$1E("div", {
        "class": "v-field__field",
        "data-no-activator": ""
      }, [['filled', 'solo', 'solo-inverted', 'solo-filled'].includes(props.variant) && hasFloatingLabel.value && _createVNode$1E(VFieldLabel, {
        "key": "floating-label",
        "ref": floatingLabelRef,
        "class": [textColorClasses.value],
        "floating": true,
        "for": id.value,
        "style": textColorStyles.value
      }, {
        default: () => [label()]
      }), hasLabel.value && _createVNode$1E(VFieldLabel, {
        "key": "label",
        "ref": labelRef,
        "for": id.value
      }, {
        default: () => [label()]
      }), slots.default?.({
        ...slotProps.value,
        props: {
          id: id.value,
          class: 'v-field__input',
          'aria-describedby': messagesId.value
        },
        focus,
        blur
      }) ?? _createVNode$1E("div", {
        "id": id.value,
        "class": "v-field__input",
        "aria-describedby": messagesId.value
      }, null)]), hasClear && _createVNode$1E(VExpandXTransition, {
        "key": "clear"
      }, {
        default: () => [_withDirectives$c(_createVNode$1E("div", {
          "class": "v-field__clearable",
          "onMousedown": e => {
            e.preventDefault();
            e.stopPropagation();
          }
        }, [_createVNode$1E(VDefaultsProvider, {
          "defaults": {
            VIcon: {
              icon: props.clearIcon
            }
          }
        }, {
          default: () => [slots.clear ? slots.clear({
            ...slotProps.value,
            props: {
              onFocus: focus,
              onBlur: blur,
              onClick: props['onClick:clear']
            }
          }) : _createVNode$1E(InputIcon, {
            "name": "clear",
            "onFocus": focus,
            "onBlur": blur
          }, null)]
        })]), [[_vShow$5, props.dirty]])]
      }), hasAppend && _createVNode$1E("div", {
        "key": "append",
        "class": "v-field__append-inner"
      }, [slots['append-inner']?.(slotProps.value), props.appendInnerIcon && _createVNode$1E(InputIcon, {
        "key": "append-icon",
        "name": "appendInner",
        "color": iconColor.value
      }, null)]), _createVNode$1E("div", {
        "class": ['v-field__outline', textColorClasses.value],
        "style": textColorStyles.value
      }, [isOutlined && _createVNode$1E(_Fragment$y, null, [_createVNode$1E("div", {
        "class": "v-field__outline__start"
      }, null), hasFloatingLabel.value && _createVNode$1E("div", {
        "class": "v-field__outline__notch"
      }, [_createVNode$1E(VFieldLabel, {
        "ref": floatingLabelRef,
        "floating": true,
        "for": id.value
      }, {
        default: () => [label()]
      })]), _createVNode$1E("div", {
        "class": "v-field__outline__end"
      }, null)]), isPlainOrUnderlined.value && hasFloatingLabel.value && _createVNode$1E(VFieldLabel, {
        "ref": floatingLabelRef,
        "floating": true,
        "for": id.value
      }, {
        default: () => [label()]
      })])]);
    });
    return {
      controlRef,
      fieldIconColor: iconColor
    };
  }
});

const {resolveDirective:_resolveDirective$7,mergeProps:_mergeProps$P,createVNode:_createVNode$1D,withDirectives:_withDirectives$b,Fragment:_Fragment$x} = await importShared('vue');
const {cloneVNode,computed: computed$19,nextTick: nextTick$i,ref: ref$z} = await importShared('vue');
const activeTypes = ['color', 'file', 'time', 'date', 'datetime-local', 'week', 'month'];
const makeVTextFieldProps = propsFactory({
  autofocus: Boolean,
  counter: [Boolean, Number, String],
  counterValue: [Number, Function],
  prefix: String,
  placeholder: String,
  persistentPlaceholder: Boolean,
  persistentCounter: Boolean,
  suffix: String,
  role: String,
  type: {
    type: String,
    default: 'text'
  },
  modelModifiers: Object,
  ...makeVInputProps(),
  ...makeVFieldProps()
}, 'VTextField');
const VTextField = genericComponent()({
  name: 'VTextField',
  directives: {
    Intersect
  },
  inheritAttrs: false,
  props: makeVTextFieldProps(),
  emits: {
    'click:control': e => true,
    'mousedown:control': e => true,
    'update:focused': focused => true,
    'update:modelValue': val => true
  },
  setup(props, _ref) {
    let {
      attrs,
      emit,
      slots
    } = _ref;
    const model = useProxiedModel(props, 'modelValue');
    const {
      isFocused,
      focus,
      blur
    } = useFocus(props);
    const counterValue = computed$19(() => {
      return typeof props.counterValue === 'function' ? props.counterValue(model.value) : typeof props.counterValue === 'number' ? props.counterValue : (model.value ?? '').toString().length;
    });
    const max = computed$19(() => {
      if (attrs.maxlength) return attrs.maxlength;
      if (!props.counter || typeof props.counter !== 'number' && typeof props.counter !== 'string') return undefined;
      return props.counter;
    });
    const isPlainOrUnderlined = computed$19(() => ['plain', 'underlined'].includes(props.variant));
    function onIntersect(isIntersecting, entries) {
      if (!props.autofocus || !isIntersecting) return;
      entries[0].target?.focus?.();
    }
    const vInputRef = ref$z();
    const vFieldRef = ref$z();
    const inputRef = ref$z();
    const isActive = computed$19(() => activeTypes.includes(props.type) || props.persistentPlaceholder || isFocused.value || props.active);
    function onFocus() {
      if (inputRef.value !== document.activeElement) {
        inputRef.value?.focus();
      }
      if (!isFocused.value) focus();
    }
    function onControlMousedown(e) {
      emit('mousedown:control', e);
      if (e.target === inputRef.value) return;
      onFocus();
      e.preventDefault();
    }
    function onControlClick(e) {
      onFocus();
      emit('click:control', e);
    }
    function onClear(e, reset) {
      e.stopPropagation();
      onFocus();
      nextTick$i(() => {
        model.value = null;
        reset();
        callEvent(props['onClick:clear'], e);
      });
    }
    function onInput(e) {
      const el = e.target;
      model.value = el.value;
      if (props.modelModifiers?.trim && ['text', 'search', 'password', 'tel', 'url'].includes(props.type)) {
        const caretPosition = [el.selectionStart, el.selectionEnd];
        nextTick$i(() => {
          el.selectionStart = caretPosition[0];
          el.selectionEnd = caretPosition[1];
        });
      }
    }
    useRender(() => {
      const hasCounter = !!(slots.counter || props.counter !== false && props.counter != null);
      const hasDetails = !!(hasCounter || slots.details);
      const [rootAttrs, inputAttrs] = filterInputAttrs(attrs);
      const {
        modelValue: _,
        ...inputProps
      } = VInput.filterProps(props);
      const fieldProps = VField.filterProps(props);
      return _createVNode$1D(VInput, _mergeProps$P({
        "ref": vInputRef,
        "modelValue": model.value,
        "onUpdate:modelValue": $event => model.value = $event,
        "class": ['v-text-field', {
          'v-text-field--prefixed': props.prefix,
          'v-text-field--suffixed': props.suffix,
          'v-input--plain-underlined': isPlainOrUnderlined.value
        }, props.class],
        "style": props.style
      }, rootAttrs, inputProps, {
        "centerAffix": !isPlainOrUnderlined.value,
        "focused": isFocused.value
      }), {
        ...slots,
        default: _ref2 => {
          let {
            id,
            isDisabled,
            isDirty,
            isReadonly,
            isValid,
            reset
          } = _ref2;
          return _createVNode$1D(VField, _mergeProps$P({
            "ref": vFieldRef,
            "onMousedown": onControlMousedown,
            "onClick": onControlClick,
            "onClick:clear": e => onClear(e, reset),
            "onClick:prependInner": props['onClick:prependInner'],
            "onClick:appendInner": props['onClick:appendInner'],
            "role": props.role
          }, fieldProps, {
            "id": id.value,
            "active": isActive.value || isDirty.value,
            "dirty": isDirty.value || props.dirty,
            "disabled": isDisabled.value,
            "focused": isFocused.value,
            "error": isValid.value === false
          }), {
            ...slots,
            default: _ref3 => {
              let {
                props: {
                  class: fieldClass,
                  ...slotProps
                }
              } = _ref3;
              const inputNode = _withDirectives$b(_createVNode$1D("input", _mergeProps$P({
                "ref": inputRef,
                "value": model.value,
                "onInput": onInput,
                "autofocus": props.autofocus,
                "readonly": isReadonly.value,
                "disabled": isDisabled.value,
                "name": props.name,
                "placeholder": props.placeholder,
                "size": 1,
                "type": props.type,
                "onFocus": onFocus,
                "onBlur": blur
              }, slotProps, inputAttrs), null), [[_resolveDirective$7("intersect"), {
                handler: onIntersect
              }, null, {
                once: true
              }]]);
              return _createVNode$1D(_Fragment$x, null, [props.prefix && _createVNode$1D("span", {
                "class": "v-text-field__prefix"
              }, [_createVNode$1D("span", {
                "class": "v-text-field__prefix__text"
              }, [props.prefix])]), slots.default ? _createVNode$1D("div", {
                "class": fieldClass,
                "data-no-activator": ""
              }, [slots.default(), inputNode]) : cloneVNode(inputNode, {
                class: fieldClass
              }), props.suffix && _createVNode$1D("span", {
                "class": "v-text-field__suffix"
              }, [_createVNode$1D("span", {
                "class": "v-text-field__suffix__text"
              }, [props.suffix])])]);
            }
          });
        },
        details: hasDetails ? slotProps => _createVNode$1D(_Fragment$x, null, [slots.details?.(slotProps), hasCounter && _createVNode$1D(_Fragment$x, null, [_createVNode$1D("span", null, null), _createVNode$1D(VCounter, {
          "active": props.persistentCounter || isFocused.value,
          "value": counterValue.value,
          "max": max.value,
          "disabled": props.disabled
        }, slots.counter)])]) : undefined
      });
    });
    return forwardRefs({}, vInputRef, vFieldRef, inputRef);
  }
});

const {Fragment:_Fragment$w,createVNode:_createVNode$1C,mergeProps:_mergeProps$O} = await importShared('vue');
const {watch: watch$q} = await importShared('vue');
const makeVVirtualScrollItemProps = propsFactory({
  renderless: Boolean,
  ...makeComponentProps()
}, 'VVirtualScrollItem');
const VVirtualScrollItem = genericComponent()({
  name: 'VVirtualScrollItem',
  inheritAttrs: false,
  props: makeVVirtualScrollItemProps(),
  emits: {
    'update:height': height => true
  },
  setup(props, _ref) {
    let {
      attrs,
      emit,
      slots
    } = _ref;
    const {
      resizeRef,
      contentRect
    } = useResizeObserver(undefined, 'border');
    watch$q(() => contentRect.value?.height, height => {
      if (height != null) emit('update:height', height);
    });
    useRender(() => props.renderless ? _createVNode$1C(_Fragment$w, null, [slots.default?.({
      itemRef: resizeRef
    })]) : _createVNode$1C("div", _mergeProps$O({
      "ref": resizeRef,
      "class": ['v-virtual-scroll__item', props.class],
      "style": props.style
    }, attrs), [slots.default?.()]));
  }
});

const {computed: computed$18,nextTick: nextTick$h,onScopeDispose: onScopeDispose$4,ref: ref$y,shallowRef: shallowRef$s,watch: watch$p,watchEffect: watchEffect$c} = await importShared('vue');
const UP = -1;
const DOWN = 1;

/** Determines how large each batch of items should be */
const BUFFER_PX = 100;
const makeVirtualProps = propsFactory({
  itemHeight: {
    type: [Number, String],
    default: null
  },
  itemKey: {
    type: [String, Array, Function],
    default: null
  },
  height: [Number, String]
}, 'virtual');
function useVirtual(props, items) {
  const display = useDisplay();
  const itemHeight = shallowRef$s(0);
  watchEffect$c(() => {
    itemHeight.value = parseFloat(props.itemHeight || 0);
  });
  const first = shallowRef$s(0);
  const last = shallowRef$s(Math.ceil(
  // Assume 16px items filling the entire screen height if
  // not provided. This is probably incorrect but it minimises
  // the chance of ending up with empty space at the bottom.
  // The default value is set here to avoid poisoning getSize()
  (parseInt(props.height) || display.height.value) / (itemHeight.value || 16)) || 1);
  const paddingTop = shallowRef$s(0);
  const paddingBottom = shallowRef$s(0);

  /** The scrollable element */
  const containerRef = ref$y();
  /** An element marking the top of the scrollable area,
   * used to add an offset if there's padding or other elements above the virtual list */
  const markerRef = ref$y();
  /** markerRef's offsetTop, lazily evaluated */
  let markerOffset = 0;
  const {
    resizeRef,
    contentRect
  } = useResizeObserver();
  watchEffect$c(() => {
    resizeRef.value = containerRef.value;
  });
  const viewportHeight = computed$18(() => {
    return containerRef.value === document.documentElement ? display.height.value : contentRect.value?.height || parseInt(props.height) || 0;
  });
  /** All static elements have been rendered and we have an assumed item height */
  const hasInitialRender = computed$18(() => {
    return !!(containerRef.value && markerRef.value && viewportHeight.value && itemHeight.value);
  });
  let sizes = Array.from({
    length: items.value.length
  });
  let offsets = Array.from({
    length: items.value.length
  });
  const updateTime = shallowRef$s(0);
  let targetScrollIndex = -1;
  function getSize(index) {
    return sizes[index] || itemHeight.value;
  }
  const updateOffsets = debounce(() => {
    const start = performance.now();
    offsets[0] = 0;
    const length = items.value.length;
    for (let i = 1; i <= length - 1; i++) {
      offsets[i] = (offsets[i - 1] || 0) + getSize(i - 1);
    }
    updateTime.value = Math.max(updateTime.value, performance.now() - start);
  }, updateTime);
  const unwatch = watch$p(hasInitialRender, v => {
    if (!v) return;
    // First render is complete, update offsets and visible
    // items in case our assumed item height was incorrect

    unwatch();
    markerOffset = markerRef.value.offsetTop;
    updateOffsets.immediate();
    calculateVisibleItems();
    if (!~targetScrollIndex) return;
    nextTick$h(() => {
      IN_BROWSER && window.requestAnimationFrame(() => {
        scrollToIndex(targetScrollIndex);
        targetScrollIndex = -1;
      });
    });
  });
  onScopeDispose$4(() => {
    updateOffsets.clear();
  });
  function handleItemResize(index, height) {
    const prevHeight = sizes[index];
    const prevMinHeight = itemHeight.value;
    itemHeight.value = prevMinHeight ? Math.min(itemHeight.value, height) : height;
    if (prevHeight !== height || prevMinHeight !== itemHeight.value) {
      sizes[index] = height;
      updateOffsets();
    }
  }
  function calculateOffset(index) {
    index = clamp(index, 0, items.value.length - 1);
    return offsets[index] || 0;
  }
  function calculateIndex(scrollTop) {
    return binaryClosest(offsets, scrollTop);
  }
  let lastScrollTop = 0;
  let scrollVelocity = 0;
  let lastScrollTime = 0;
  watch$p(viewportHeight, (val, oldVal) => {
    if (oldVal) {
      calculateVisibleItems();
      if (val < oldVal) {
        requestAnimationFrame(() => {
          scrollVelocity = 0;
          calculateVisibleItems();
        });
      }
    }
  });
  let scrollTimeout = -1;
  function handleScroll() {
    if (!containerRef.value || !markerRef.value) return;
    const scrollTop = containerRef.value.scrollTop;
    const scrollTime = performance.now();
    const scrollDeltaT = scrollTime - lastScrollTime;
    if (scrollDeltaT > 500) {
      scrollVelocity = Math.sign(scrollTop - lastScrollTop);

      // Not super important, only update at the
      // start of a scroll sequence to avoid reflows
      markerOffset = markerRef.value.offsetTop;
    } else {
      scrollVelocity = scrollTop - lastScrollTop;
    }
    lastScrollTop = scrollTop;
    lastScrollTime = scrollTime;
    window.clearTimeout(scrollTimeout);
    scrollTimeout = window.setTimeout(handleScrollend, 500);
    calculateVisibleItems();
  }
  function handleScrollend() {
    if (!containerRef.value || !markerRef.value) return;
    scrollVelocity = 0;
    lastScrollTime = 0;
    window.clearTimeout(scrollTimeout);
    calculateVisibleItems();
  }
  let raf = -1;
  function calculateVisibleItems() {
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(_calculateVisibleItems);
  }
  function _calculateVisibleItems() {
    if (!containerRef.value || !viewportHeight.value) return;
    const scrollTop = lastScrollTop - markerOffset;
    const direction = Math.sign(scrollVelocity);
    const startPx = Math.max(0, scrollTop - BUFFER_PX);
    const start = clamp(calculateIndex(startPx), 0, items.value.length);
    const endPx = scrollTop + viewportHeight.value + BUFFER_PX;
    const end = clamp(calculateIndex(endPx) + 1, start + 1, items.value.length);
    if (
    // Only update the side we're scrolling towards,
    // the other side will be updated incidentally
    (direction !== UP || start < first.value) && (direction !== DOWN || end > last.value)) {
      const topOverflow = calculateOffset(first.value) - calculateOffset(start);
      const bottomOverflow = calculateOffset(end) - calculateOffset(last.value);
      const bufferOverflow = Math.max(topOverflow, bottomOverflow);
      if (bufferOverflow > BUFFER_PX) {
        first.value = start;
        last.value = end;
      } else {
        // Only update the side that's reached its limit if there's still buffer left
        if (start <= 0) first.value = start;
        if (end >= items.value.length) last.value = end;
      }
    }
    paddingTop.value = calculateOffset(first.value);
    paddingBottom.value = calculateOffset(items.value.length) - calculateOffset(last.value);
  }
  function scrollToIndex(index) {
    const offset = calculateOffset(index);
    if (!containerRef.value || index && !offset) {
      targetScrollIndex = index;
    } else {
      containerRef.value.scrollTop = offset;
    }
  }
  const computedItems = computed$18(() => {
    return items.value.slice(first.value, last.value).map((item, index) => {
      const _index = index + first.value;
      return {
        raw: item,
        index: _index,
        key: getPropertyFromItem(item, props.itemKey, _index)
      };
    });
  });
  watch$p(items, () => {
    sizes = Array.from({
      length: items.value.length
    });
    offsets = Array.from({
      length: items.value.length
    });
    updateOffsets.immediate();
    calculateVisibleItems();
  }, {
    deep: 1
  });
  return {
    calculateVisibleItems,
    containerRef,
    markerRef,
    computedItems,
    paddingTop,
    paddingBottom,
    scrollToIndex,
    handleScroll,
    handleScrollend,
    handleItemResize
  };
}

// https://gist.github.com/robertleeplummerjr/1cc657191d34ecd0a324
function binaryClosest(arr, val) {
  let high = arr.length - 1;
  let low = 0;
  let mid = 0;
  let item = null;
  let target = -1;
  if (arr[high] < val) {
    return high;
  }
  while (low <= high) {
    mid = low + high >> 1;
    item = arr[mid];
    if (item > val) {
      high = mid - 1;
    } else if (item < val) {
      target = mid;
      low = mid + 1;
    } else if (item === val) {
      return mid;
    } else {
      return low;
    }
  }
  return target;
}

const {createVNode:_createVNode$1B,Fragment:_Fragment$v} = await importShared('vue');
const {onMounted: onMounted$9,onScopeDispose: onScopeDispose$3,toRef: toRef$x} = await importShared('vue');
const makeVVirtualScrollProps = propsFactory({
  items: {
    type: Array,
    default: () => []
  },
  renderless: Boolean,
  ...makeVirtualProps(),
  ...makeComponentProps(),
  ...makeDimensionProps()
}, 'VVirtualScroll');
const VVirtualScroll = genericComponent()({
  name: 'VVirtualScroll',
  props: makeVVirtualScrollProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const vm = getCurrentInstance('VVirtualScroll');
    const {
      dimensionStyles
    } = useDimension(props);
    const {
      calculateVisibleItems,
      containerRef,
      markerRef,
      handleScroll,
      handleScrollend,
      handleItemResize,
      scrollToIndex,
      paddingTop,
      paddingBottom,
      computedItems
    } = useVirtual(props, toRef$x(() => props.items));
    useToggleScope(() => props.renderless, () => {
      function handleListeners() {
        let add = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;
        const method = add ? 'addEventListener' : 'removeEventListener';
        if (containerRef.value === document.documentElement) {
          document[method]('scroll', handleScroll, {
            passive: true
          });
          document[method]('scrollend', handleScrollend);
        } else {
          containerRef.value?.[method]('scroll', handleScroll, {
            passive: true
          });
          containerRef.value?.[method]('scrollend', handleScrollend);
        }
      }
      onMounted$9(() => {
        containerRef.value = getScrollParent(vm.vnode.el, true);
        handleListeners(true);
      });
      onScopeDispose$3(handleListeners);
    });
    useRender(() => {
      const children = computedItems.value.map(item => _createVNode$1B(VVirtualScrollItem, {
        "key": item.key,
        "renderless": props.renderless,
        "onUpdate:height": height => handleItemResize(item.index, height)
      }, {
        default: slotProps => slots.default?.({
          item: item.raw,
          index: item.index,
          ...slotProps
        })
      }));
      return props.renderless ? _createVNode$1B(_Fragment$v, null, [_createVNode$1B("div", {
        "ref": markerRef,
        "class": "v-virtual-scroll__spacer",
        "style": {
          paddingTop: convertToUnit(paddingTop.value)
        }
      }, null), children, _createVNode$1B("div", {
        "class": "v-virtual-scroll__spacer",
        "style": {
          paddingBottom: convertToUnit(paddingBottom.value)
        }
      }, null)]) : _createVNode$1B("div", {
        "ref": containerRef,
        "class": ['v-virtual-scroll', props.class],
        "onScrollPassive": handleScroll,
        "onScrollend": handleScrollend,
        "style": [dimensionStyles.value, props.style]
      }, [_createVNode$1B("div", {
        "ref": markerRef,
        "class": "v-virtual-scroll__container",
        "style": {
          paddingTop: convertToUnit(paddingTop.value),
          paddingBottom: convertToUnit(paddingBottom.value)
        }
      }, [children])]);
    });
    return {
      calculateVisibleItems,
      scrollToIndex
    };
  }
});

// Utilities
const {shallowRef: shallowRef$r,watch: watch$o} = await importShared('vue');


// Types

function useScrolling(listRef, textFieldRef) {
  const isScrolling = shallowRef$r(false);
  let scrollTimeout;
  function onListScroll(e) {
    cancelAnimationFrame(scrollTimeout);
    isScrolling.value = true;
    scrollTimeout = requestAnimationFrame(() => {
      scrollTimeout = requestAnimationFrame(() => {
        isScrolling.value = false;
      });
    });
  }
  async function finishScrolling() {
    await new Promise(resolve => requestAnimationFrame(resolve));
    await new Promise(resolve => requestAnimationFrame(resolve));
    await new Promise(resolve => requestAnimationFrame(resolve));
    await new Promise(resolve => {
      if (isScrolling.value) {
        const stop = watch$o(isScrolling, () => {
          stop();
          resolve();
        });
      } else resolve();
    });
  }
  async function onListKeydown(e) {
    if (e.key === 'Tab') {
      textFieldRef.value?.focus();
    }
    if (!['PageDown', 'PageUp', 'Home', 'End'].includes(e.key)) return;
    const el = listRef.value?.$el;
    if (!el) return;
    if (e.key === 'Home' || e.key === 'End') {
      el.scrollTo({
        top: e.key === 'Home' ? 0 : el.scrollHeight,
        behavior: 'smooth'
      });
    }
    await finishScrolling();
    const children = el.querySelectorAll(':scope > :not(.v-virtual-scroll__spacer)');
    if (e.key === 'PageDown' || e.key === 'Home') {
      const top = el.getBoundingClientRect().top;
      for (const child of children) {
        if (child.getBoundingClientRect().top >= top) {
          child.focus();
          break;
        }
      }
    } else {
      const bottom = el.getBoundingClientRect().bottom;
      for (const child of [...children].reverse()) {
        if (child.getBoundingClientRect().bottom <= bottom) {
          child.focus();
          break;
        }
      }
    }
  }
  return {
    onScrollPassive: onListScroll,
    onKeydown: onListKeydown
  }; // typescript doesn't know about vue's event merging
}

const {Fragment:_Fragment$u,createVNode:_createVNode$1A,mergeProps:_mergeProps$N,createTextVNode:_createTextVNode$6} = await importShared('vue');
const {computed: computed$17,mergeProps: mergeProps$8,nextTick: nextTick$g,ref: ref$x,shallowRef: shallowRef$q,toRef: toRef$w,watch: watch$n} = await importShared('vue');
const makeSelectProps = propsFactory({
  chips: Boolean,
  closableChips: Boolean,
  closeText: {
    type: String,
    default: '$vuetify.close'
  },
  openText: {
    type: String,
    default: '$vuetify.open'
  },
  eager: Boolean,
  hideNoData: Boolean,
  hideSelected: Boolean,
  listProps: {
    type: Object
  },
  menu: Boolean,
  menuIcon: {
    type: IconValue,
    default: '$dropdown'
  },
  menuProps: {
    type: Object
  },
  multiple: Boolean,
  noDataText: {
    type: String,
    default: '$vuetify.noDataText'
  },
  openOnClear: Boolean,
  itemColor: String,
  ...makeItemsProps({
    itemChildren: false
  })
}, 'Select');
const makeVSelectProps = propsFactory({
  ...makeSelectProps(),
  ...omit(makeVTextFieldProps({
    modelValue: null,
    role: 'combobox'
  }), ['validationValue', 'dirty', 'appendInnerIcon']),
  ...makeTransitionProps({
    transition: {
      component: VDialogTransition
    }
  })
}, 'VSelect');
const VSelect = genericComponent()({
  name: 'VSelect',
  props: makeVSelectProps(),
  emits: {
    'update:focused': focused => true,
    'update:modelValue': value => true,
    'update:menu': ue => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      t
    } = useLocale();
    const vTextFieldRef = ref$x();
    const vMenuRef = ref$x();
    const vVirtualScrollRef = ref$x();
    const {
      items,
      transformIn,
      transformOut
    } = useItems(props);
    const model = useProxiedModel(props, 'modelValue', [], v => transformIn(v === null ? [null] : wrapInArray(v)), v => {
      const transformed = transformOut(v);
      return props.multiple ? transformed : transformed[0] ?? null;
    });
    const counterValue = computed$17(() => {
      return typeof props.counterValue === 'function' ? props.counterValue(model.value) : typeof props.counterValue === 'number' ? props.counterValue : model.value.length;
    });
    const form = useForm(props);
    const selectedValues = computed$17(() => model.value.map(selection => selection.value));
    const isFocused = shallowRef$q(false);
    let keyboardLookupPrefix = '';
    let keyboardLookupLastTime;
    const displayItems = computed$17(() => {
      if (props.hideSelected) {
        return items.value.filter(item => !model.value.some(s => (props.valueComparator || deepEqual)(s, item)));
      }
      return items.value;
    });
    const menuDisabled = computed$17(() => props.hideNoData && !displayItems.value.length || form.isReadonly.value || form.isDisabled.value);
    const _menu = useProxiedModel(props, 'menu');
    const menu = computed$17({
      get: () => _menu.value,
      set: v => {
        if (_menu.value && !v && vMenuRef.value?.ΨopenChildren.size) return;
        if (v && menuDisabled.value) return;
        _menu.value = v;
      }
    });
    const label = toRef$w(() => menu.value ? props.closeText : props.openText);
    const computedMenuProps = computed$17(() => {
      return {
        ...props.menuProps,
        activatorProps: {
          ...(props.menuProps?.activatorProps || {}),
          'aria-haspopup': 'listbox' // Set aria-haspopup to 'listbox'
        }
      };
    });
    const listRef = ref$x();
    const listEvents = useScrolling(listRef, vTextFieldRef);
    function onClear(e) {
      if (props.openOnClear) {
        menu.value = true;
      }
    }
    function onMousedownControl() {
      if (menuDisabled.value) return;
      menu.value = !menu.value;
    }
    function onListKeydown(e) {
      if (checkPrintable(e)) {
        onKeydown(e);
      }
    }
    function onKeydown(e) {
      if (!e.key || form.isReadonly.value) return;
      if (['Enter', ' ', 'ArrowDown', 'ArrowUp', 'Home', 'End'].includes(e.key)) {
        e.preventDefault();
      }
      if (['Enter', 'ArrowDown', ' '].includes(e.key)) {
        menu.value = true;
      }
      if (['Escape', 'Tab'].includes(e.key)) {
        menu.value = false;
      }
      if (e.key === 'Home') {
        listRef.value?.focus('first');
      } else if (e.key === 'End') {
        listRef.value?.focus('last');
      }

      // html select hotkeys
      const KEYBOARD_LOOKUP_THRESHOLD = 1000; // milliseconds

      if (!checkPrintable(e)) return;
      const now = performance.now();
      if (now - keyboardLookupLastTime > KEYBOARD_LOOKUP_THRESHOLD) {
        keyboardLookupPrefix = '';
      }
      keyboardLookupPrefix += e.key.toLowerCase();
      keyboardLookupLastTime = now;
      const item = items.value.find(item => item.title.toLowerCase().startsWith(keyboardLookupPrefix));
      if (item !== undefined) {
        if (!props.multiple) {
          model.value = [item];
        }
        const index = displayItems.value.indexOf(item);
        if (~index && IN_BROWSER) {
          listRef.value?.focus(index);
        }
      }
    }

    /** @param set - null means toggle */
    function select(item) {
      let set = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : true;
      if (item.props.disabled) return;
      if (props.multiple) {
        const index = model.value.findIndex(selection => (props.valueComparator || deepEqual)(selection.value, item.value));
        const add = set == null ? !~index : set;
        if (~index) {
          const value = add ? [...model.value, item] : [...model.value];
          value.splice(index, 1);
          model.value = value;
        } else if (add) {
          model.value = [...model.value, item];
        }
      } else {
        const add = set !== false;
        model.value = add ? [item] : [];
        nextTick$g(() => {
          menu.value = false;
        });
      }
    }
    function onBlur(e) {
      if (!listRef.value?.$el.contains(e.relatedTarget)) {
        menu.value = false;
      }
    }
    function onAfterEnter() {
      if (props.eager) {
        vVirtualScrollRef.value?.calculateVisibleItems();
      }
    }
    function onAfterLeave() {
      if (isFocused.value) {
        vTextFieldRef.value?.focus();
      }
    }
    function onFocusin(e) {
      isFocused.value = true;
    }
    function onModelUpdate(v) {
      if (v == null) model.value = [];else if (matchesSelector(vTextFieldRef.value, ':autofill') || matchesSelector(vTextFieldRef.value, ':-webkit-autofill')) {
        const item = items.value.find(item => item.title === v);
        if (item) {
          select(item);
        }
      } else if (vTextFieldRef.value) {
        vTextFieldRef.value.value = '';
      }
    }
    watch$n(menu, () => {
      if (!props.hideSelected && menu.value && model.value.length) {
        const index = displayItems.value.findIndex(item => model.value.some(s => (props.valueComparator || deepEqual)(s.value, item.value)));
        IN_BROWSER && window.requestAnimationFrame(() => {
          index >= 0 && vVirtualScrollRef.value?.scrollToIndex(index);
        });
      }
    });
    watch$n(() => props.items, (newVal, oldVal) => {
      if (menu.value) return;
      if (isFocused.value && !oldVal.length && newVal.length) {
        menu.value = true;
      }
    });
    useRender(() => {
      const hasChips = !!(props.chips || slots.chip);
      const hasList = !!(!props.hideNoData || displayItems.value.length || slots['prepend-item'] || slots['append-item'] || slots['no-data']);
      const isDirty = model.value.length > 0;
      const textFieldProps = VTextField.filterProps(props);
      const placeholder = isDirty || !isFocused.value && props.label && !props.persistentPlaceholder ? undefined : props.placeholder;
      return _createVNode$1A(VTextField, _mergeProps$N({
        "ref": vTextFieldRef
      }, textFieldProps, {
        "modelValue": model.value.map(v => v.props.value).join(', '),
        "onUpdate:modelValue": onModelUpdate,
        "focused": isFocused.value,
        "onUpdate:focused": $event => isFocused.value = $event,
        "validationValue": model.externalValue,
        "counterValue": counterValue.value,
        "dirty": isDirty,
        "class": ['v-select', {
          'v-select--active-menu': menu.value,
          'v-select--chips': !!props.chips,
          [`v-select--${props.multiple ? 'multiple' : 'single'}`]: true,
          'v-select--selected': model.value.length,
          'v-select--selection-slot': !!slots.selection
        }, props.class],
        "style": props.style,
        "inputmode": "none",
        "placeholder": placeholder,
        "onClick:clear": onClear,
        "onMousedown:control": onMousedownControl,
        "onBlur": onBlur,
        "onKeydown": onKeydown,
        "aria-label": t(label.value),
        "title": t(label.value)
      }), {
        ...slots,
        default: () => _createVNode$1A(_Fragment$u, null, [_createVNode$1A(VMenu, _mergeProps$N({
          "ref": vMenuRef,
          "modelValue": menu.value,
          "onUpdate:modelValue": $event => menu.value = $event,
          "activator": "parent",
          "contentClass": "v-select__content",
          "disabled": menuDisabled.value,
          "eager": props.eager,
          "maxHeight": 310,
          "openOnClick": false,
          "closeOnContentClick": false,
          "transition": props.transition,
          "onAfterEnter": onAfterEnter,
          "onAfterLeave": onAfterLeave
        }, computedMenuProps.value), {
          default: () => [hasList && _createVNode$1A(VList, _mergeProps$N({
            "ref": listRef,
            "selected": selectedValues.value,
            "selectStrategy": props.multiple ? 'independent' : 'single-independent',
            "onMousedown": e => e.preventDefault(),
            "onKeydown": onListKeydown,
            "onFocusin": onFocusin,
            "tabindex": "-1",
            "aria-live": "polite",
            "aria-label": `${props.label}-list`,
            "color": props.itemColor ?? props.color
          }, listEvents, props.listProps), {
            default: () => [slots['prepend-item']?.(), !displayItems.value.length && !props.hideNoData && (slots['no-data']?.() ?? _createVNode$1A(VListItem, {
              "key": "no-data",
              "title": t(props.noDataText)
            }, null)), _createVNode$1A(VVirtualScroll, {
              "ref": vVirtualScrollRef,
              "renderless": true,
              "items": displayItems.value,
              "itemKey": "value"
            }, {
              default: _ref2 => {
                let {
                  item,
                  index,
                  itemRef
                } = _ref2;
                const itemProps = mergeProps$8(item.props, {
                  ref: itemRef,
                  key: item.value,
                  onClick: () => select(item, null)
                });
                return slots.item?.({
                  item,
                  index,
                  props: itemProps
                }) ?? _createVNode$1A(VListItem, _mergeProps$N(itemProps, {
                  "role": "option"
                }), {
                  prepend: _ref3 => {
                    let {
                      isSelected
                    } = _ref3;
                    return _createVNode$1A(_Fragment$u, null, [props.multiple && !props.hideSelected ? _createVNode$1A(VCheckboxBtn, {
                      "key": item.value,
                      "modelValue": isSelected,
                      "ripple": false,
                      "tabindex": "-1"
                    }, null) : undefined, item.props.prependAvatar && _createVNode$1A(VAvatar, {
                      "image": item.props.prependAvatar
                    }, null), item.props.prependIcon && _createVNode$1A(VIcon, {
                      "icon": item.props.prependIcon
                    }, null)]);
                  }
                });
              }
            }), slots['append-item']?.()]
          })]
        }), model.value.map((item, index) => {
          function onChipClose(e) {
            e.stopPropagation();
            e.preventDefault();
            select(item, false);
          }
          const slotProps = {
            'onClick:close': onChipClose,
            onKeydown(e) {
              if (e.key !== 'Enter' && e.key !== ' ') return;
              e.preventDefault();
              e.stopPropagation();
              onChipClose(e);
            },
            onMousedown(e) {
              e.preventDefault();
              e.stopPropagation();
            },
            modelValue: true,
            'onUpdate:modelValue': undefined
          };
          const hasSlot = hasChips ? !!slots.chip : !!slots.selection;
          const slotContent = hasSlot ? ensureValidVNode(hasChips ? slots.chip({
            item,
            index,
            props: slotProps
          }) : slots.selection({
            item,
            index
          })) : undefined;
          if (hasSlot && !slotContent) return undefined;
          return _createVNode$1A("div", {
            "key": item.value,
            "class": "v-select__selection"
          }, [hasChips ? !slots.chip ? _createVNode$1A(VChip, _mergeProps$N({
            "key": "chip",
            "closable": props.closableChips,
            "size": "small",
            "text": item.title,
            "disabled": item.props.disabled
          }, slotProps), null) : _createVNode$1A(VDefaultsProvider, {
            "key": "chip-defaults",
            "defaults": {
              VChip: {
                closable: props.closableChips,
                size: 'small',
                text: item.title
              }
            }
          }, {
            default: () => [slotContent]
          }) : slotContent ?? _createVNode$1A("span", {
            "class": "v-select__selection-text"
          }, [item.title, props.multiple && index < model.value.length - 1 && _createVNode$1A("span", {
            "class": "v-select__selection-comma"
          }, [_createTextVNode$6(",")])])]);
        })]),
        'append-inner': function () {
          for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
            args[_key] = arguments[_key];
          }
          return _createVNode$1A(_Fragment$u, null, [slots['append-inner']?.(...args), props.menuIcon ? _createVNode$1A(VIcon, {
            "class": "v-select__menu-icon",
            "color": vTextFieldRef.value?.fieldIconColor,
            "icon": props.menuIcon
          }, null) : undefined]);
        }
      });
    });
    return forwardRefs({
      isFocused,
      menu,
      select
    }, vTextFieldRef);
  }
});

/* eslint-disable max-statements */
/* eslint-disable no-labels */

// Utilities
const {computed: computed$16,shallowRef: shallowRef$p,unref,watchEffect: watchEffect$b,createVNode:_createVNode$1z,Fragment:_Fragment$t} = await importShared('vue');
/**
 * - boolean: match without highlight
 * - number: single match (index), length already known
 * - []: single match (start, end)
 * - [][]: multiple matches (start, end), shouldn't overlap
 */
// Composables
const defaultFilter = (value, query, item) => {
  if (value == null || query == null) return -1;
  if (!query.length) return 0;
  value = value.toString().toLocaleLowerCase();
  query = query.toString().toLocaleLowerCase();
  const result = [];
  let idx = value.indexOf(query);
  while (~idx) {
    result.push([idx, idx + query.length]);
    idx = value.indexOf(query, idx + query.length);
  }
  return result.length ? result : -1;
};
function normaliseMatch(match, query) {
  if (match == null || typeof match === 'boolean' || match === -1) return;
  if (typeof match === 'number') return [[match, match + query.length]];
  if (Array.isArray(match[0])) return match;
  return [match];
}
const makeFilterProps = propsFactory({
  customFilter: Function,
  customKeyFilter: Object,
  filterKeys: [Array, String],
  filterMode: {
    type: String,
    default: 'intersection'
  },
  noFilter: Boolean
}, 'filter');
function filterItems(items, query, options) {
  const array = [];
  // always ensure we fall back to a functioning filter
  const filter = options?.default ?? defaultFilter;
  const keys = options?.filterKeys ? wrapInArray(options.filterKeys) : false;
  const customFiltersLength = Object.keys(options?.customKeyFilter ?? {}).length;
  if (!items?.length) return array;
  loop: for (let i = 0; i < items.length; i++) {
    const [item, transformed = item] = wrapInArray(items[i]);
    const customMatches = {};
    const defaultMatches = {};
    let match = -1;
    if ((query || customFiltersLength > 0) && !options?.noFilter) {
      if (typeof item === 'object') {
        const filterKeys = keys || Object.keys(transformed);
        for (const key of filterKeys) {
          const value = getPropertyFromItem(transformed, key);
          const keyFilter = options?.customKeyFilter?.[key];
          match = keyFilter ? keyFilter(value, query, item) : filter(value, query, item);
          if (match !== -1 && match !== false) {
            if (keyFilter) customMatches[key] = normaliseMatch(match, query);else defaultMatches[key] = normaliseMatch(match, query);
          } else if (options?.filterMode === 'every') {
            continue loop;
          }
        }
      } else {
        match = filter(item, query, item);
        if (match !== -1 && match !== false) {
          defaultMatches.title = normaliseMatch(match, query);
        }
      }
      const defaultMatchesLength = Object.keys(defaultMatches).length;
      const customMatchesLength = Object.keys(customMatches).length;
      if (!defaultMatchesLength && !customMatchesLength) continue;
      if (options?.filterMode === 'union' && customMatchesLength !== customFiltersLength && !defaultMatchesLength) continue;
      if (options?.filterMode === 'intersection' && (customMatchesLength !== customFiltersLength || !defaultMatchesLength)) continue;
    }
    array.push({
      index: i,
      matches: {
        ...defaultMatches,
        ...customMatches
      }
    });
  }
  return array;
}
function useFilter(props, items, query, options) {
  const filteredItems = shallowRef$p([]);
  const filteredMatches = shallowRef$p(new Map());
  const transformedItems = computed$16(() => options?.transform ? unref(items).map(item => [item, options.transform(item)]) : unref(items));
  watchEffect$b(() => {
    const _query = typeof query === 'function' ? query() : unref(query);
    const strQuery = typeof _query !== 'string' && typeof _query !== 'number' ? '' : String(_query);
    const results = filterItems(transformedItems.value, strQuery, {
      customKeyFilter: {
        ...props.customKeyFilter,
        ...unref(options?.customKeyFilter)
      },
      default: props.customFilter,
      filterKeys: props.filterKeys,
      filterMode: props.filterMode,
      noFilter: props.noFilter
    });
    const originalItems = unref(items);
    const _filteredItems = [];
    const _filteredMatches = new Map();
    results.forEach(_ref => {
      let {
        index,
        matches
      } = _ref;
      const item = originalItems[index];
      _filteredItems.push(item);
      _filteredMatches.set(item.value, matches);
    });
    filteredItems.value = _filteredItems;
    filteredMatches.value = _filteredMatches;
  });
  function getMatches(item) {
    return filteredMatches.value.get(item.value);
  }
  return {
    filteredItems,
    filteredMatches,
    getMatches
  };
}
function highlightResult(name, text, matches) {
  if (matches == null || !matches.length) return text;
  return matches.map((match, i) => {
    const start = i === 0 ? 0 : matches[i - 1][1];
    const result = [_createVNode$1z("span", {
      "class": `${name}__unmask`
    }, [text.slice(start, match[0])]), _createVNode$1z("span", {
      "class": `${name}__mask`
    }, [text.slice(match[0], match[1])])];
    if (i === matches.length - 1) {
      result.push(_createVNode$1z("span", {
        "class": `${name}__unmask`
      }, [text.slice(match[1])]));
    }
    return _createVNode$1z(_Fragment$t, null, [result]);
  });
}

const {Fragment:_Fragment$s,createVNode:_createVNode$1y,mergeProps:_mergeProps$M,createTextVNode:_createTextVNode$5} = await importShared('vue');
const {computed: computed$15,mergeProps: mergeProps$7,nextTick: nextTick$f,ref: ref$w,shallowRef: shallowRef$o,watch: watch$m} = await importShared('vue');
const makeVAutocompleteProps = propsFactory({
  autoSelectFirst: {
    type: [Boolean, String]
  },
  clearOnSelect: Boolean,
  search: String,
  ...makeFilterProps({
    filterKeys: ['title']
  }),
  ...makeSelectProps(),
  ...omit(makeVTextFieldProps({
    modelValue: null,
    role: 'combobox'
  }), ['validationValue', 'dirty', 'appendInnerIcon']),
  ...makeTransitionProps({
    transition: false
  })
}, 'VAutocomplete');
const VAutocomplete = genericComponent()({
  name: 'VAutocomplete',
  props: makeVAutocompleteProps(),
  emits: {
    'update:focused': focused => true,
    'update:search': value => true,
    'update:modelValue': value => true,
    'update:menu': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      t
    } = useLocale();
    const vTextFieldRef = ref$w();
    const isFocused = shallowRef$o(false);
    const isPristine = shallowRef$o(true);
    const listHasFocus = shallowRef$o(false);
    const vMenuRef = ref$w();
    const vVirtualScrollRef = ref$w();
    const selectionIndex = shallowRef$o(-1);
    const {
      items,
      transformIn,
      transformOut
    } = useItems(props);
    const {
      textColorClasses,
      textColorStyles
    } = useTextColor(() => vTextFieldRef.value?.color);
    const search = useProxiedModel(props, 'search', '');
    const model = useProxiedModel(props, 'modelValue', [], v => transformIn(v === null ? [null] : wrapInArray(v)), v => {
      const transformed = transformOut(v);
      return props.multiple ? transformed : transformed[0] ?? null;
    });
    const counterValue = computed$15(() => {
      return typeof props.counterValue === 'function' ? props.counterValue(model.value) : typeof props.counterValue === 'number' ? props.counterValue : model.value.length;
    });
    const form = useForm(props);
    const {
      filteredItems,
      getMatches
    } = useFilter(props, items, () => isPristine.value ? '' : search.value);
    const displayItems = computed$15(() => {
      if (props.hideSelected) {
        return filteredItems.value.filter(filteredItem => !model.value.some(s => s.value === filteredItem.value));
      }
      return filteredItems.value;
    });
    const hasChips = computed$15(() => !!(props.chips || slots.chip));
    const hasSelectionSlot = computed$15(() => hasChips.value || !!slots.selection);
    const selectedValues = computed$15(() => model.value.map(selection => selection.props.value));
    const highlightFirst = computed$15(() => {
      const selectFirst = props.autoSelectFirst === true || props.autoSelectFirst === 'exact' && search.value === displayItems.value[0]?.title;
      return selectFirst && displayItems.value.length > 0 && !isPristine.value && !listHasFocus.value;
    });
    const menuDisabled = computed$15(() => props.hideNoData && !displayItems.value.length || form.isReadonly.value || form.isDisabled.value);
    const _menu = useProxiedModel(props, 'menu');
    const menu = computed$15({
      get: () => _menu.value,
      set: v => {
        if (_menu.value && !v && vMenuRef.value?.ΨopenChildren.size) return;
        if (v && menuDisabled.value) return;
        _menu.value = v;
      }
    });
    const label = computed$15(() => menu.value ? props.closeText : props.openText);
    const listRef = ref$w();
    const listEvents = useScrolling(listRef, vTextFieldRef);
    function onClear(e) {
      if (props.openOnClear) {
        menu.value = true;
      }
      search.value = '';
    }
    function onMousedownControl() {
      if (menuDisabled.value) return;
      menu.value = true;
    }
    function onMousedownMenuIcon(e) {
      if (menuDisabled.value) return;
      if (isFocused.value) {
        e.preventDefault();
        e.stopPropagation();
      }
      menu.value = !menu.value;
    }
    function onListKeydown(e) {
      if (e.key !== ' ' && checkPrintable(e)) {
        vTextFieldRef.value?.focus();
      }
    }
    function onKeydown(e) {
      if (form.isReadonly.value) return;
      const selectionStart = vTextFieldRef.value?.selectionStart;
      const length = model.value.length;
      if (['Enter', 'ArrowDown', 'ArrowUp'].includes(e.key)) {
        e.preventDefault();
      }
      if (['Enter', 'ArrowDown'].includes(e.key)) {
        menu.value = true;
      }
      if (['Escape'].includes(e.key)) {
        menu.value = false;
      }
      if (highlightFirst.value && ['Enter', 'Tab'].includes(e.key) && !model.value.some(_ref2 => {
        let {
          value
        } = _ref2;
        return value === displayItems.value[0].value;
      })) {
        select(displayItems.value[0]);
      }
      if (e.key === 'ArrowDown' && highlightFirst.value) {
        listRef.value?.focus('next');
      }
      if (['Backspace', 'Delete'].includes(e.key)) {
        if (!props.multiple && hasSelectionSlot.value && model.value.length > 0 && !search.value) return select(model.value[0], false);
        if (~selectionIndex.value) {
          e.preventDefault();
          const originalSelectionIndex = selectionIndex.value;
          select(model.value[selectionIndex.value], false);
          selectionIndex.value = originalSelectionIndex >= length - 1 ? length - 2 : originalSelectionIndex;
        } else if (e.key === 'Backspace' && !search.value) {
          selectionIndex.value = length - 1;
        }
        return;
      }
      if (!props.multiple) return;
      if (e.key === 'ArrowLeft') {
        if (selectionIndex.value < 0 && selectionStart && selectionStart > 0) return;
        const prev = selectionIndex.value > -1 ? selectionIndex.value - 1 : length - 1;
        if (model.value[prev]) {
          selectionIndex.value = prev;
        } else {
          const searchLength = search.value?.length ?? null;
          selectionIndex.value = -1;
          vTextFieldRef.value?.setSelectionRange(searchLength, searchLength);
        }
      } else if (e.key === 'ArrowRight') {
        if (selectionIndex.value < 0) return;
        const next = selectionIndex.value + 1;
        if (model.value[next]) {
          selectionIndex.value = next;
        } else {
          selectionIndex.value = -1;
          vTextFieldRef.value?.setSelectionRange(0, 0);
        }
      } else if (~selectionIndex.value && checkPrintable(e)) {
        selectionIndex.value = -1;
      }
    }
    function onChange(e) {
      if (matchesSelector(vTextFieldRef.value, ':autofill') || matchesSelector(vTextFieldRef.value, ':-webkit-autofill')) {
        const item = items.value.find(item => item.title === e.target.value);
        if (item) {
          select(item);
        }
      }
    }
    function onAfterEnter() {
      if (props.eager) {
        vVirtualScrollRef.value?.calculateVisibleItems();
      }
    }
    function onAfterLeave() {
      if (isFocused.value) {
        isPristine.value = true;
        vTextFieldRef.value?.focus();
      }
    }
    function onFocusin(e) {
      isFocused.value = true;
      setTimeout(() => {
        listHasFocus.value = true;
      });
    }
    function onFocusout(e) {
      listHasFocus.value = false;
    }
    function onUpdateModelValue(v) {
      if (v == null || v === '' && !props.multiple && !hasSelectionSlot.value) model.value = [];
    }
    const isSelecting = shallowRef$o(false);

    /** @param set - null means toggle */
    function select(item) {
      let set = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : true;
      if (!item || item.props.disabled) return;
      if (props.multiple) {
        const index = model.value.findIndex(selection => (props.valueComparator || deepEqual)(selection.value, item.value));
        const add = set == null ? !~index : set;
        if (~index) {
          const value = add ? [...model.value, item] : [...model.value];
          value.splice(index, 1);
          model.value = value;
        } else if (add) {
          model.value = [...model.value, item];
        }
        if (props.clearOnSelect) {
          search.value = '';
        }
      } else {
        const add = set !== false;
        model.value = add ? [item] : [];
        search.value = add && !hasSelectionSlot.value ? item.title : '';

        // watch for search watcher to trigger
        nextTick$f(() => {
          menu.value = false;
          isPristine.value = true;
        });
      }
    }
    watch$m(isFocused, (val, oldVal) => {
      if (val === oldVal) return;
      if (val) {
        isSelecting.value = true;
        search.value = props.multiple || hasSelectionSlot.value ? '' : String(model.value.at(-1)?.props.title ?? '');
        isPristine.value = true;
        nextTick$f(() => isSelecting.value = false);
      } else {
        if (!props.multiple && search.value == null) model.value = [];
        menu.value = false;
        if (props.multiple || hasSelectionSlot.value) search.value = '';
        selectionIndex.value = -1;
      }
    });
    watch$m(search, val => {
      if (!isFocused.value || isSelecting.value) return;
      if (val) menu.value = true;
      isPristine.value = !val;
    });
    watch$m(menu, () => {
      if (!props.hideSelected && menu.value && model.value.length) {
        const index = displayItems.value.findIndex(item => model.value.some(s => item.value === s.value));
        IN_BROWSER && window.requestAnimationFrame(() => {
          index >= 0 && vVirtualScrollRef.value?.scrollToIndex(index);
        });
      }
    });
    watch$m(() => props.items, (newVal, oldVal) => {
      if (menu.value) return;
      if (isFocused.value && !oldVal.length && newVal.length) {
        menu.value = true;
      }
    });
    useRender(() => {
      const hasList = !!(!props.hideNoData || displayItems.value.length || slots['prepend-item'] || slots['append-item'] || slots['no-data']);
      const isDirty = model.value.length > 0;
      const textFieldProps = VTextField.filterProps(props);
      return _createVNode$1y(VTextField, _mergeProps$M({
        "ref": vTextFieldRef
      }, textFieldProps, {
        "modelValue": search.value,
        "onUpdate:modelValue": [$event => search.value = $event, onUpdateModelValue],
        "focused": isFocused.value,
        "onUpdate:focused": $event => isFocused.value = $event,
        "validationValue": model.externalValue,
        "counterValue": counterValue.value,
        "dirty": isDirty,
        "onChange": onChange,
        "class": ['v-autocomplete', `v-autocomplete--${props.multiple ? 'multiple' : 'single'}`, {
          'v-autocomplete--active-menu': menu.value,
          'v-autocomplete--chips': !!props.chips,
          'v-autocomplete--selection-slot': !!hasSelectionSlot.value,
          'v-autocomplete--selecting-index': selectionIndex.value > -1
        }, props.class],
        "style": props.style,
        "readonly": form.isReadonly.value,
        "placeholder": isDirty ? undefined : props.placeholder,
        "onClick:clear": onClear,
        "onMousedown:control": onMousedownControl,
        "onKeydown": onKeydown
      }), {
        ...slots,
        default: () => _createVNode$1y(_Fragment$s, null, [_createVNode$1y(VMenu, _mergeProps$M({
          "ref": vMenuRef,
          "modelValue": menu.value,
          "onUpdate:modelValue": $event => menu.value = $event,
          "activator": "parent",
          "contentClass": "v-autocomplete__content",
          "disabled": menuDisabled.value,
          "eager": props.eager,
          "maxHeight": 310,
          "openOnClick": false,
          "closeOnContentClick": false,
          "transition": props.transition,
          "onAfterEnter": onAfterEnter,
          "onAfterLeave": onAfterLeave
        }, props.menuProps), {
          default: () => [hasList && _createVNode$1y(VList, _mergeProps$M({
            "ref": listRef,
            "selected": selectedValues.value,
            "selectStrategy": props.multiple ? 'independent' : 'single-independent',
            "onMousedown": e => e.preventDefault(),
            "onKeydown": onListKeydown,
            "onFocusin": onFocusin,
            "onFocusout": onFocusout,
            "tabindex": "-1",
            "aria-live": "polite",
            "color": props.itemColor ?? props.color
          }, listEvents, props.listProps), {
            default: () => [slots['prepend-item']?.(), !displayItems.value.length && !props.hideNoData && (slots['no-data']?.() ?? _createVNode$1y(VListItem, {
              "key": "no-data",
              "title": t(props.noDataText)
            }, null)), _createVNode$1y(VVirtualScroll, {
              "ref": vVirtualScrollRef,
              "renderless": true,
              "items": displayItems.value,
              "itemKey": "value"
            }, {
              default: _ref3 => {
                let {
                  item,
                  index,
                  itemRef
                } = _ref3;
                const itemProps = mergeProps$7(item.props, {
                  ref: itemRef,
                  key: item.value,
                  active: highlightFirst.value && index === 0 ? true : undefined,
                  onClick: () => select(item, null)
                });
                return slots.item?.({
                  item,
                  index,
                  props: itemProps
                }) ?? _createVNode$1y(VListItem, _mergeProps$M(itemProps, {
                  "role": "option"
                }), {
                  prepend: _ref4 => {
                    let {
                      isSelected
                    } = _ref4;
                    return _createVNode$1y(_Fragment$s, null, [props.multiple && !props.hideSelected ? _createVNode$1y(VCheckboxBtn, {
                      "key": item.value,
                      "modelValue": isSelected,
                      "ripple": false,
                      "tabindex": "-1"
                    }, null) : undefined, item.props.prependAvatar && _createVNode$1y(VAvatar, {
                      "image": item.props.prependAvatar
                    }, null), item.props.prependIcon && _createVNode$1y(VIcon, {
                      "icon": item.props.prependIcon
                    }, null)]);
                  },
                  title: () => {
                    return isPristine.value ? item.title : highlightResult('v-autocomplete', item.title, getMatches(item)?.title);
                  }
                });
              }
            }), slots['append-item']?.()]
          })]
        }), model.value.map((item, index) => {
          function onChipClose(e) {
            e.stopPropagation();
            e.preventDefault();
            select(item, false);
          }
          const slotProps = {
            'onClick:close': onChipClose,
            onKeydown(e) {
              if (e.key !== 'Enter' && e.key !== ' ') return;
              e.preventDefault();
              e.stopPropagation();
              onChipClose(e);
            },
            onMousedown(e) {
              e.preventDefault();
              e.stopPropagation();
            },
            modelValue: true,
            'onUpdate:modelValue': undefined
          };
          const hasSlot = hasChips.value ? !!slots.chip : !!slots.selection;
          const slotContent = hasSlot ? ensureValidVNode(hasChips.value ? slots.chip({
            item,
            index,
            props: slotProps
          }) : slots.selection({
            item,
            index
          })) : undefined;
          if (hasSlot && !slotContent) return undefined;
          return _createVNode$1y("div", {
            "key": item.value,
            "class": ['v-autocomplete__selection', index === selectionIndex.value && ['v-autocomplete__selection--selected', textColorClasses.value]],
            "style": index === selectionIndex.value ? textColorStyles.value : {}
          }, [hasChips.value ? !slots.chip ? _createVNode$1y(VChip, _mergeProps$M({
            "key": "chip",
            "closable": props.closableChips,
            "size": "small",
            "text": item.title,
            "disabled": item.props.disabled
          }, slotProps), null) : _createVNode$1y(VDefaultsProvider, {
            "key": "chip-defaults",
            "defaults": {
              VChip: {
                closable: props.closableChips,
                size: 'small',
                text: item.title
              }
            }
          }, {
            default: () => [slotContent]
          }) : slotContent ?? _createVNode$1y("span", {
            "class": "v-autocomplete__selection-text"
          }, [item.title, props.multiple && index < model.value.length - 1 && _createVNode$1y("span", {
            "class": "v-autocomplete__selection-comma"
          }, [_createTextVNode$5(",")])])]);
        })]),
        'append-inner': function () {
          for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
            args[_key] = arguments[_key];
          }
          return _createVNode$1y(_Fragment$s, null, [slots['append-inner']?.(...args), props.menuIcon ? _createVNode$1y(VIcon, {
            "class": "v-autocomplete__menu-icon",
            "color": vTextFieldRef.value?.fieldIconColor,
            "icon": props.menuIcon,
            "onMousedown": onMousedownMenuIcon,
            "onClick": noop,
            "aria-label": t(label.value),
            "title": t(label.value),
            "tabindex": "-1"
          }, null) : undefined]);
        }
      });
    });
    return forwardRefs({
      isFocused,
      isPristine,
      menu,
      search,
      filteredItems,
      select
    }, vTextFieldRef);
  }
});

const {createVNode:_createVNode$1x,vShow:_vShow$4,mergeProps:_mergeProps$L,withDirectives:_withDirectives$a} = await importShared('vue');
const makeVBadgeProps = propsFactory({
  bordered: Boolean,
  color: String,
  content: [Number, String],
  dot: Boolean,
  floating: Boolean,
  icon: IconValue,
  inline: Boolean,
  label: {
    type: String,
    default: '$vuetify.badge'
  },
  max: [Number, String],
  modelValue: {
    type: Boolean,
    default: true
  },
  offsetX: [Number, String],
  offsetY: [Number, String],
  textColor: String,
  ...makeComponentProps(),
  ...makeLocationProps({
    location: 'top end'
  }),
  ...makeRoundedProps(),
  ...makeTagProps(),
  ...makeThemeProps(),
  ...makeTransitionProps({
    transition: 'scale-rotate-transition'
  })
}, 'VBadge');
const VBadge = genericComponent()({
  name: 'VBadge',
  inheritAttrs: false,
  props: makeVBadgeProps(),
  setup(props, ctx) {
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.color);
    const {
      roundedClasses
    } = useRounded(props);
    const {
      t
    } = useLocale();
    const {
      textColorClasses,
      textColorStyles
    } = useTextColor(() => props.textColor);
    const {
      themeClasses
    } = useTheme();
    const {
      locationStyles
    } = useLocation(props, true, side => {
      const base = props.floating ? props.dot ? 2 : 4 : props.dot ? 8 : 12;
      return base + (['top', 'bottom'].includes(side) ? Number(props.offsetY ?? 0) : ['left', 'right'].includes(side) ? Number(props.offsetX ?? 0) : 0);
    });
    useRender(() => {
      const value = Number(props.content);
      const content = !props.max || isNaN(value) ? props.content : value <= Number(props.max) ? value : `${props.max}+`;
      const [badgeAttrs, attrs] = pickWithRest(ctx.attrs, ['aria-atomic', 'aria-label', 'aria-live', 'role', 'title']);
      return _createVNode$1x(props.tag, _mergeProps$L({
        "class": ['v-badge', {
          'v-badge--bordered': props.bordered,
          'v-badge--dot': props.dot,
          'v-badge--floating': props.floating,
          'v-badge--inline': props.inline
        }, props.class]
      }, attrs, {
        "style": props.style
      }), {
        default: () => [_createVNode$1x("div", {
          "class": "v-badge__wrapper"
        }, [ctx.slots.default?.(), _createVNode$1x(MaybeTransition, {
          "transition": props.transition
        }, {
          default: () => [_withDirectives$a(_createVNode$1x("span", _mergeProps$L({
            "class": ['v-badge__badge', themeClasses.value, backgroundColorClasses.value, roundedClasses.value, textColorClasses.value],
            "style": [backgroundColorStyles.value, textColorStyles.value, props.inline ? {} : locationStyles.value],
            "aria-atomic": "true",
            "aria-label": t(props.label, value),
            "aria-live": "polite",
            "role": "status"
          }, badgeAttrs), [props.dot ? undefined : ctx.slots.badge ? ctx.slots.badge?.() : props.icon ? _createVNode$1x(VIcon, {
            "icon": props.icon
          }, null) : content]), [[_vShow$4, props.modelValue]])]
        })])]
      });
    });
    return {};
  }
});

const {createVNode:_createVNode$1w} = await importShared('vue');
const makeVBannerActionsProps = propsFactory({
  color: String,
  density: String,
  ...makeComponentProps()
}, 'VBannerActions');
const VBannerActions = genericComponent()({
  name: 'VBannerActions',
  props: makeVBannerActionsProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    provideDefaults({
      VBtn: {
        color: props.color,
        density: props.density,
        slim: true,
        variant: 'text'
      }
    });
    useRender(() => _createVNode$1w("div", {
      "class": ['v-banner-actions', props.class],
      "style": props.style
    }, [slots.default?.()]));
    return {};
  }
});

// Utilities
const VBannerText = createSimpleFunctional('v-banner-text');

const {createVNode:_createVNode$1v} = await importShared('vue');
const {toRef: toRef$v} = await importShared('vue');
const makeVBannerProps = propsFactory({
  avatar: String,
  bgColor: String,
  color: String,
  icon: IconValue,
  lines: String,
  stacked: Boolean,
  sticky: Boolean,
  text: String,
  ...makeBorderProps(),
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeDimensionProps(),
  ...makeDisplayProps({
    mobile: null
  }),
  ...makeElevationProps(),
  ...makeLocationProps(),
  ...makePositionProps(),
  ...makeRoundedProps(),
  ...makeTagProps(),
  ...makeThemeProps()
}, 'VBanner');
const VBanner = genericComponent()({
  name: 'VBanner',
  props: makeVBannerProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.bgColor);
    const {
      borderClasses
    } = useBorder(props);
    const {
      densityClasses
    } = useDensity(props);
    const {
      displayClasses,
      mobile
    } = useDisplay(props);
    const {
      dimensionStyles
    } = useDimension(props);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      locationStyles
    } = useLocation(props);
    const {
      positionClasses
    } = usePosition(props);
    const {
      roundedClasses
    } = useRounded(props);
    const {
      themeClasses
    } = provideTheme(props);
    const color = toRef$v(() => props.color);
    const density = toRef$v(() => props.density);
    provideDefaults({
      VBannerActions: {
        color,
        density
      }
    });
    useRender(() => {
      const hasText = !!(props.text || slots.text);
      const hasPrependMedia = !!(props.avatar || props.icon);
      const hasPrepend = !!(hasPrependMedia || slots.prepend);
      return _createVNode$1v(props.tag, {
        "class": ['v-banner', {
          'v-banner--stacked': props.stacked || mobile.value,
          'v-banner--sticky': props.sticky,
          [`v-banner--${props.lines}-line`]: !!props.lines
        }, themeClasses.value, backgroundColorClasses.value, borderClasses.value, densityClasses.value, displayClasses.value, elevationClasses.value, positionClasses.value, roundedClasses.value, props.class],
        "style": [backgroundColorStyles.value, dimensionStyles.value, locationStyles.value, props.style],
        "role": "banner"
      }, {
        default: () => [hasPrepend && _createVNode$1v("div", {
          "key": "prepend",
          "class": "v-banner__prepend"
        }, [!slots.prepend ? _createVNode$1v(VAvatar, {
          "key": "prepend-avatar",
          "color": color.value,
          "density": density.value,
          "icon": props.icon,
          "image": props.avatar
        }, null) : _createVNode$1v(VDefaultsProvider, {
          "key": "prepend-defaults",
          "disabled": !hasPrependMedia,
          "defaults": {
            VAvatar: {
              color: color.value,
              density: density.value,
              icon: props.icon,
              image: props.avatar
            }
          }
        }, slots.prepend)]), _createVNode$1v("div", {
          "class": "v-banner__content"
        }, [hasText && _createVNode$1v(VBannerText, {
          "key": "text"
        }, {
          default: () => [slots.text?.() ?? props.text]
        }), slots.default?.()]), slots.actions && _createVNode$1v(VBannerActions, {
          "key": "actions"
        }, slots.actions)]
      });
    });
  }
});

const {createVNode:_createVNode$1u} = await importShared('vue');
const {computed: computed$14,toRef: toRef$u} = await importShared('vue');
const makeVBottomNavigationProps = propsFactory({
  baseColor: String,
  bgColor: String,
  color: String,
  grow: Boolean,
  mode: {
    type: String,
    validator: v => !v || ['horizontal', 'shift'].includes(v)
  },
  height: {
    type: [Number, String],
    default: 56
  },
  active: {
    type: Boolean,
    default: true
  },
  ...makeBorderProps(),
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeElevationProps(),
  ...makeRoundedProps(),
  ...makeLayoutItemProps({
    name: 'bottom-navigation'
  }),
  ...makeTagProps({
    tag: 'header'
  }),
  ...makeGroupProps({
    selectedClass: 'v-btn--selected'
  }),
  ...makeThemeProps()
}, 'VBottomNavigation');
const VBottomNavigation = genericComponent()({
  name: 'VBottomNavigation',
  props: makeVBottomNavigationProps(),
  emits: {
    'update:active': value => true,
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      themeClasses
    } = useTheme();
    const {
      borderClasses
    } = useBorder(props);
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.bgColor);
    const {
      densityClasses
    } = useDensity(props);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      roundedClasses
    } = useRounded(props);
    const {
      ssrBootStyles
    } = useSsrBoot();
    const height = computed$14(() => Number(props.height) - (props.density === 'comfortable' ? 8 : 0) - (props.density === 'compact' ? 16 : 0));
    const isActive = useProxiedModel(props, 'active', props.active);
    const {
      layoutItemStyles
    } = useLayoutItem({
      id: props.name,
      order: computed$14(() => parseInt(props.order, 10)),
      position: toRef$u(() => 'bottom'),
      layoutSize: toRef$u(() => isActive.value ? height.value : 0),
      elementSize: height,
      active: isActive,
      absolute: toRef$u(() => props.absolute)
    });
    useGroup(props, VBtnToggleSymbol);
    provideDefaults({
      VBtn: {
        baseColor: toRef$u(() => props.baseColor),
        color: toRef$u(() => props.color),
        density: toRef$u(() => props.density),
        stacked: toRef$u(() => props.mode !== 'horizontal'),
        variant: 'text'
      }
    }, {
      scoped: true
    });
    useRender(() => {
      return _createVNode$1u(props.tag, {
        "class": ['v-bottom-navigation', {
          'v-bottom-navigation--active': isActive.value,
          'v-bottom-navigation--grow': props.grow,
          'v-bottom-navigation--shift': props.mode === 'shift'
        }, themeClasses.value, backgroundColorClasses.value, borderClasses.value, densityClasses.value, elevationClasses.value, roundedClasses.value, props.class],
        "style": [backgroundColorStyles.value, layoutItemStyles.value, {
          height: convertToUnit(height.value)
        }, ssrBootStyles.value, props.style]
      }, {
        default: () => [slots.default && _createVNode$1u("div", {
          "class": "v-bottom-navigation__content"
        }, [slots.default()])]
      });
    });
    return {};
  }
});

const {createVNode:_createVNode$1t,mergeProps:_mergeProps$K} = await importShared('vue');
const {mergeProps: mergeProps$6,nextTick: nextTick$e,onBeforeUnmount: onBeforeUnmount$4,ref: ref$v,watch: watch$l} = await importShared('vue');
const makeVDialogProps = propsFactory({
  fullscreen: Boolean,
  retainFocus: {
    type: Boolean,
    default: true
  },
  scrollable: Boolean,
  ...makeVOverlayProps({
    origin: 'center center',
    scrollStrategy: 'block',
    transition: {
      component: VDialogTransition
    },
    zIndex: 2400
  })
}, 'VDialog');
const VDialog = genericComponent()({
  name: 'VDialog',
  props: makeVDialogProps(),
  emits: {
    'update:modelValue': value => true,
    afterEnter: () => true,
    afterLeave: () => true
  },
  setup(props, _ref) {
    let {
      emit,
      slots
    } = _ref;
    const isActive = useProxiedModel(props, 'modelValue');
    const {
      scopeId
    } = useScopeId();
    const overlay = ref$v();
    function onFocusin(e) {
      const before = e.relatedTarget;
      const after = e.target;
      if (before !== after && overlay.value?.contentEl &&
      // We're the topmost dialog
      overlay.value?.globalTop &&
      // It isn't the document or the dialog body
      ![document, overlay.value.contentEl].includes(after) &&
      // It isn't inside the dialog body
      !overlay.value.contentEl.contains(after)) {
        const focusable = focusableChildren(overlay.value.contentEl);
        if (!focusable.length) return;
        const firstElement = focusable[0];
        const lastElement = focusable[focusable.length - 1];
        if (before === firstElement) {
          lastElement.focus();
        } else {
          firstElement.focus();
        }
      }
    }
    onBeforeUnmount$4(() => {
      document.removeEventListener('focusin', onFocusin);
    });
    if (IN_BROWSER) {
      watch$l(() => isActive.value && props.retainFocus, val => {
        val ? document.addEventListener('focusin', onFocusin) : document.removeEventListener('focusin', onFocusin);
      }, {
        immediate: true
      });
    }
    function onAfterEnter() {
      emit('afterEnter');
      if ((props.scrim || props.retainFocus) && overlay.value?.contentEl && !overlay.value.contentEl.contains(document.activeElement)) {
        overlay.value.contentEl.focus({
          preventScroll: true
        });
      }
    }
    function onAfterLeave() {
      emit('afterLeave');
    }
    watch$l(isActive, async val => {
      if (!val) {
        await nextTick$e();
        overlay.value.activatorEl?.focus({
          preventScroll: true
        });
      }
    });
    useRender(() => {
      const overlayProps = VOverlay.filterProps(props);
      const activatorProps = mergeProps$6({
        'aria-haspopup': 'dialog'
      }, props.activatorProps);
      const contentProps = mergeProps$6({
        tabindex: -1
      }, props.contentProps);
      return _createVNode$1t(VOverlay, _mergeProps$K({
        "ref": overlay,
        "class": ['v-dialog', {
          'v-dialog--fullscreen': props.fullscreen,
          'v-dialog--scrollable': props.scrollable
        }, props.class],
        "style": props.style
      }, overlayProps, {
        "modelValue": isActive.value,
        "onUpdate:modelValue": $event => isActive.value = $event,
        "aria-modal": "true",
        "activatorProps": activatorProps,
        "contentProps": contentProps,
        "height": !props.fullscreen ? props.height : undefined,
        "width": !props.fullscreen ? props.width : undefined,
        "maxHeight": !props.fullscreen ? props.maxHeight : undefined,
        "maxWidth": !props.fullscreen ? props.maxWidth : undefined,
        "role": "dialog",
        "onAfterEnter": onAfterEnter,
        "onAfterLeave": onAfterLeave
      }, scopeId), {
        activator: slots.activator,
        default: function () {
          for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
            args[_key] = arguments[_key];
          }
          return _createVNode$1t(VDefaultsProvider, {
            "root": "VDialog"
          }, {
            default: () => [slots.default?.(...args)]
          });
        }
      });
    });
    return forwardRefs({}, overlay);
  }
});

const {mergeProps:_mergeProps$J,createVNode:_createVNode$1s} = await importShared('vue');
const makeVBottomSheetProps = propsFactory({
  inset: Boolean,
  ...makeVDialogProps({
    transition: 'bottom-sheet-transition'
  })
}, 'VBottomSheet');
const VBottomSheet = genericComponent()({
  name: 'VBottomSheet',
  props: makeVBottomSheetProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const isActive = useProxiedModel(props, 'modelValue');
    useRender(() => {
      const dialogProps = VDialog.filterProps(props);
      return _createVNode$1s(VDialog, _mergeProps$J(dialogProps, {
        "contentClass": ['v-bottom-sheet__content', props.contentClass],
        "modelValue": isActive.value,
        "onUpdate:modelValue": $event => isActive.value = $event,
        "class": ['v-bottom-sheet', {
          'v-bottom-sheet--inset': props.inset
        }, props.class],
        "style": props.style
      }), slots);
    });
    return {};
  }
});

const {createVNode:_createVNode$1r} = await importShared('vue');
const makeVBreadcrumbsDividerProps = propsFactory({
  divider: [Number, String],
  ...makeComponentProps()
}, 'VBreadcrumbsDivider');
const VBreadcrumbsDivider = genericComponent()({
  name: 'VBreadcrumbsDivider',
  props: makeVBreadcrumbsDividerProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    useRender(() => _createVNode$1r("li", {
      "aria-hidden": "true",
      "class": ['v-breadcrumbs-divider', props.class],
      "style": props.style
    }, [slots?.default?.() ?? props.divider]));
    return {};
  }
});

const {mergeProps:_mergeProps$I,createVNode:_createVNode$1q} = await importShared('vue');
const {computed: computed$13} = await importShared('vue');
const makeVBreadcrumbsItemProps = propsFactory({
  active: Boolean,
  activeClass: String,
  activeColor: String,
  color: String,
  disabled: Boolean,
  title: String,
  ...makeComponentProps(),
  ...makeRouterProps(),
  ...makeTagProps({
    tag: 'li'
  })
}, 'VBreadcrumbsItem');
const VBreadcrumbsItem = genericComponent()({
  name: 'VBreadcrumbsItem',
  props: makeVBreadcrumbsItemProps(),
  setup(props, _ref) {
    let {
      slots,
      attrs
    } = _ref;
    const link = useLink(props, attrs);
    const isActive = computed$13(() => props.active || link.isActive?.value);
    const {
      textColorClasses,
      textColorStyles
    } = useTextColor(() => isActive.value ? props.activeColor : props.color);
    useRender(() => {
      return _createVNode$1q(props.tag, {
        "class": ['v-breadcrumbs-item', {
          'v-breadcrumbs-item--active': isActive.value,
          'v-breadcrumbs-item--disabled': props.disabled,
          [`${props.activeClass}`]: isActive.value && props.activeClass
        }, textColorClasses.value, props.class],
        "style": [textColorStyles.value, props.style],
        "aria-current": isActive.value ? 'page' : undefined
      }, {
        default: () => [!link.isLink.value ? slots.default?.() ?? props.title : _createVNode$1q("a", _mergeProps$I({
          "class": "v-breadcrumbs-item--link",
          "onClick": link.navigate
        }, link.linkProps), [slots.default?.() ?? props.title])]
      });
    });
    return {};
  }
});

const {createVNode:_createVNode$1p,Fragment:_Fragment$r,mergeProps:_mergeProps$H} = await importShared('vue');
const {computed: computed$12,toRef: toRef$t} = await importShared('vue');
const makeVBreadcrumbsProps = propsFactory({
  activeClass: String,
  activeColor: String,
  bgColor: String,
  color: String,
  disabled: Boolean,
  divider: {
    type: String,
    default: '/'
  },
  icon: IconValue,
  items: {
    type: Array,
    default: () => []
  },
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeRoundedProps(),
  ...makeTagProps({
    tag: 'ul'
  })
}, 'VBreadcrumbs');
const VBreadcrumbs = genericComponent()({
  name: 'VBreadcrumbs',
  props: makeVBreadcrumbsProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.bgColor);
    const {
      densityClasses
    } = useDensity(props);
    const {
      roundedClasses
    } = useRounded(props);
    provideDefaults({
      VBreadcrumbsDivider: {
        divider: toRef$t(() => props.divider)
      },
      VBreadcrumbsItem: {
        activeClass: toRef$t(() => props.activeClass),
        activeColor: toRef$t(() => props.activeColor),
        color: toRef$t(() => props.color),
        disabled: toRef$t(() => props.disabled)
      }
    });
    const items = computed$12(() => props.items.map(item => {
      return typeof item === 'string' ? {
        item: {
          title: item
        },
        raw: item
      } : {
        item,
        raw: item
      };
    }));
    useRender(() => {
      const hasPrepend = !!(slots.prepend || props.icon);
      return _createVNode$1p(props.tag, {
        "class": ['v-breadcrumbs', backgroundColorClasses.value, densityClasses.value, roundedClasses.value, props.class],
        "style": [backgroundColorStyles.value, props.style]
      }, {
        default: () => [hasPrepend && _createVNode$1p("li", {
          "key": "prepend",
          "class": "v-breadcrumbs__prepend"
        }, [!slots.prepend ? _createVNode$1p(VIcon, {
          "key": "prepend-icon",
          "start": true,
          "icon": props.icon
        }, null) : _createVNode$1p(VDefaultsProvider, {
          "key": "prepend-defaults",
          "disabled": !props.icon,
          "defaults": {
            VIcon: {
              icon: props.icon,
              start: true
            }
          }
        }, slots.prepend)]), items.value.map((_ref2, index, array) => {
          let {
            item,
            raw
          } = _ref2;
          return _createVNode$1p(_Fragment$r, null, [slots.item?.({
            item,
            index
          }) ?? _createVNode$1p(VBreadcrumbsItem, _mergeProps$H({
            "key": index,
            "disabled": index >= array.length - 1
          }, typeof item === 'string' ? {
            title: item
          } : item), {
            default: slots.title ? () => slots.title?.({
              item,
              index
            }) : undefined
          }), index < array.length - 1 && _createVNode$1p(VBreadcrumbsDivider, null, {
            default: slots.divider ? () => slots.divider?.({
              item: raw,
              index
            }) : undefined
          })]);
        }), slots.default?.()]
      });
    });
    return {};
  }
});

const {createVNode:_createVNode$1o} = await importShared('vue');
const VCardActions = genericComponent()({
  name: 'VCardActions',
  props: makeComponentProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    provideDefaults({
      VBtn: {
        slim: true,
        variant: 'text'
      }
    });
    useRender(() => _createVNode$1o("div", {
      "class": ['v-card-actions', props.class],
      "style": props.style
    }, [slots.default?.()]));
    return {};
  }
});

const {createVNode:_createVNode$1n} = await importShared('vue');
const makeVCardSubtitleProps = propsFactory({
  opacity: [Number, String],
  ...makeComponentProps(),
  ...makeTagProps()
}, 'VCardSubtitle');
const VCardSubtitle = genericComponent()({
  name: 'VCardSubtitle',
  props: makeVCardSubtitleProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    useRender(() => _createVNode$1n(props.tag, {
      "class": ['v-card-subtitle', props.class],
      "style": [{
        '--v-card-subtitle-opacity': props.opacity
      }, props.style]
    }, slots));
    return {};
  }
});

// Utilities
const VCardTitle = createSimpleFunctional('v-card-title');

const {Fragment:_Fragment$q,createVNode:_createVNode$1m} = await importShared('vue');
const {toDisplayString: toDisplayString$1} = await importShared('vue');
const makeCardItemProps = propsFactory({
  appendAvatar: String,
  appendIcon: IconValue,
  prependAvatar: String,
  prependIcon: IconValue,
  subtitle: {
    type: [String, Number, Boolean],
    default: undefined
  },
  title: {
    type: [String, Number, Boolean],
    default: undefined
  },
  ...makeComponentProps(),
  ...makeDensityProps()
}, 'VCardItem');
const VCardItem = genericComponent()({
  name: 'VCardItem',
  props: makeCardItemProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    useRender(() => {
      const hasPrependMedia = !!(props.prependAvatar || props.prependIcon);
      const hasPrepend = !!(hasPrependMedia || slots.prepend);
      const hasAppendMedia = !!(props.appendAvatar || props.appendIcon);
      const hasAppend = !!(hasAppendMedia || slots.append);
      const hasTitle = !!(props.title != null || slots.title);
      const hasSubtitle = !!(props.subtitle != null || slots.subtitle);
      return _createVNode$1m("div", {
        "class": ['v-card-item', props.class],
        "style": props.style
      }, [hasPrepend && _createVNode$1m("div", {
        "key": "prepend",
        "class": "v-card-item__prepend"
      }, [!slots.prepend ? _createVNode$1m(_Fragment$q, null, [props.prependAvatar && _createVNode$1m(VAvatar, {
        "key": "prepend-avatar",
        "density": props.density,
        "image": props.prependAvatar
      }, null), props.prependIcon && _createVNode$1m(VIcon, {
        "key": "prepend-icon",
        "density": props.density,
        "icon": props.prependIcon
      }, null)]) : _createVNode$1m(VDefaultsProvider, {
        "key": "prepend-defaults",
        "disabled": !hasPrependMedia,
        "defaults": {
          VAvatar: {
            density: props.density,
            image: props.prependAvatar
          },
          VIcon: {
            density: props.density,
            icon: props.prependIcon
          }
        }
      }, slots.prepend)]), _createVNode$1m("div", {
        "class": "v-card-item__content"
      }, [hasTitle && _createVNode$1m(VCardTitle, {
        "key": "title"
      }, {
        default: () => [slots.title?.() ?? toDisplayString$1(props.title)]
      }), hasSubtitle && _createVNode$1m(VCardSubtitle, {
        "key": "subtitle"
      }, {
        default: () => [slots.subtitle?.() ?? toDisplayString$1(props.subtitle)]
      }), slots.default?.()]), hasAppend && _createVNode$1m("div", {
        "key": "append",
        "class": "v-card-item__append"
      }, [!slots.append ? _createVNode$1m(_Fragment$q, null, [props.appendIcon && _createVNode$1m(VIcon, {
        "key": "append-icon",
        "density": props.density,
        "icon": props.appendIcon
      }, null), props.appendAvatar && _createVNode$1m(VAvatar, {
        "key": "append-avatar",
        "density": props.density,
        "image": props.appendAvatar
      }, null)]) : _createVNode$1m(VDefaultsProvider, {
        "key": "append-defaults",
        "disabled": !hasAppendMedia,
        "defaults": {
          VAvatar: {
            density: props.density,
            image: props.appendAvatar
          },
          VIcon: {
            density: props.density,
            icon: props.appendIcon
          }
        }
      }, slots.append)])]);
    });
    return {};
  }
});

const {createVNode:_createVNode$1l} = await importShared('vue');
const makeVCardTextProps = propsFactory({
  opacity: [Number, String],
  ...makeComponentProps(),
  ...makeTagProps()
}, 'VCardText');
const VCardText = genericComponent()({
  name: 'VCardText',
  props: makeVCardTextProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    useRender(() => _createVNode$1l(props.tag, {
      "class": ['v-card-text', props.class],
      "style": [{
        '--v-card-text-opacity': props.opacity
      }, props.style]
    }, slots));
    return {};
  }
});

const {createVNode:_createVNode$1k,resolveDirective:_resolveDirective$6,mergeProps:_mergeProps$G,withDirectives:_withDirectives$9} = await importShared('vue');
const makeVCardProps = propsFactory({
  appendAvatar: String,
  appendIcon: IconValue,
  disabled: Boolean,
  flat: Boolean,
  hover: Boolean,
  image: String,
  link: {
    type: Boolean,
    default: undefined
  },
  prependAvatar: String,
  prependIcon: IconValue,
  ripple: {
    type: [Boolean, Object],
    default: true
  },
  subtitle: {
    type: [String, Number, Boolean],
    default: undefined
  },
  text: {
    type: [String, Number, Boolean],
    default: undefined
  },
  title: {
    type: [String, Number, Boolean],
    default: undefined
  },
  ...makeBorderProps(),
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeDimensionProps(),
  ...makeElevationProps(),
  ...makeLoaderProps(),
  ...makeLocationProps(),
  ...makePositionProps(),
  ...makeRoundedProps(),
  ...makeRouterProps(),
  ...makeTagProps(),
  ...makeThemeProps(),
  ...makeVariantProps({
    variant: 'elevated'
  })
}, 'VCard');
const VCard = genericComponent()({
  name: 'VCard',
  directives: {
    Ripple
  },
  props: makeVCardProps(),
  setup(props, _ref) {
    let {
      attrs,
      slots
    } = _ref;
    const {
      themeClasses
    } = provideTheme(props);
    const {
      borderClasses
    } = useBorder(props);
    const {
      colorClasses,
      colorStyles,
      variantClasses
    } = useVariant(props);
    const {
      densityClasses
    } = useDensity(props);
    const {
      dimensionStyles
    } = useDimension(props);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      loaderClasses
    } = useLoader(props);
    const {
      locationStyles
    } = useLocation(props);
    const {
      positionClasses
    } = usePosition(props);
    const {
      roundedClasses
    } = useRounded(props);
    const link = useLink(props, attrs);
    useRender(() => {
      const isLink = props.link !== false && link.isLink.value;
      const isClickable = !props.disabled && props.link !== false && (props.link || link.isClickable.value);
      const Tag = isLink ? 'a' : props.tag;
      const hasTitle = !!(slots.title || props.title != null);
      const hasSubtitle = !!(slots.subtitle || props.subtitle != null);
      const hasHeader = hasTitle || hasSubtitle;
      const hasAppend = !!(slots.append || props.appendAvatar || props.appendIcon);
      const hasPrepend = !!(slots.prepend || props.prependAvatar || props.prependIcon);
      const hasImage = !!(slots.image || props.image);
      const hasCardItem = hasHeader || hasPrepend || hasAppend;
      const hasText = !!(slots.text || props.text != null);
      return _withDirectives$9(_createVNode$1k(Tag, _mergeProps$G({
        "class": ['v-card', {
          'v-card--disabled': props.disabled,
          'v-card--flat': props.flat,
          'v-card--hover': props.hover && !(props.disabled || props.flat),
          'v-card--link': isClickable
        }, themeClasses.value, borderClasses.value, colorClasses.value, densityClasses.value, elevationClasses.value, loaderClasses.value, positionClasses.value, roundedClasses.value, variantClasses.value, props.class],
        "style": [colorStyles.value, dimensionStyles.value, locationStyles.value, props.style],
        "onClick": isClickable && link.navigate,
        "tabindex": props.disabled ? -1 : undefined
      }, link.linkProps), {
        default: () => [hasImage && _createVNode$1k("div", {
          "key": "image",
          "class": "v-card__image"
        }, [!slots.image ? _createVNode$1k(VImg, {
          "key": "image-img",
          "cover": true,
          "src": props.image
        }, null) : _createVNode$1k(VDefaultsProvider, {
          "key": "image-defaults",
          "disabled": !props.image,
          "defaults": {
            VImg: {
              cover: true,
              src: props.image
            }
          }
        }, slots.image)]), _createVNode$1k(LoaderSlot, {
          "name": "v-card",
          "active": !!props.loading,
          "color": typeof props.loading === 'boolean' ? undefined : props.loading
        }, {
          default: slots.loader
        }), hasCardItem && _createVNode$1k(VCardItem, {
          "key": "item",
          "prependAvatar": props.prependAvatar,
          "prependIcon": props.prependIcon,
          "title": props.title,
          "subtitle": props.subtitle,
          "appendAvatar": props.appendAvatar,
          "appendIcon": props.appendIcon
        }, {
          default: slots.item,
          prepend: slots.prepend,
          title: slots.title,
          subtitle: slots.subtitle,
          append: slots.append
        }), hasText && _createVNode$1k(VCardText, {
          "key": "text"
        }, {
          default: () => [slots.text?.() ?? props.text]
        }), slots.default?.(), slots.actions && _createVNode$1k(VCardActions, null, {
          default: slots.actions
        }), genOverlays(isClickable, 'v-card')]
      }), [[_resolveDirective$6("ripple"), isClickable && props.ripple]]);
    });
    return {};
  }
});

// Utilities
const handleGesture = wrapper => {
  const {
    touchstartX,
    touchendX,
    touchstartY,
    touchendY
  } = wrapper;
  const dirRatio = 0.5;
  const minDistance = 16;
  wrapper.offsetX = touchendX - touchstartX;
  wrapper.offsetY = touchendY - touchstartY;
  if (Math.abs(wrapper.offsetY) < dirRatio * Math.abs(wrapper.offsetX)) {
    wrapper.left && touchendX < touchstartX - minDistance && wrapper.left(wrapper);
    wrapper.right && touchendX > touchstartX + minDistance && wrapper.right(wrapper);
  }
  if (Math.abs(wrapper.offsetX) < dirRatio * Math.abs(wrapper.offsetY)) {
    wrapper.up && touchendY < touchstartY - minDistance && wrapper.up(wrapper);
    wrapper.down && touchendY > touchstartY + minDistance && wrapper.down(wrapper);
  }
};
function touchstart(event, wrapper) {
  const touch = event.changedTouches[0];
  wrapper.touchstartX = touch.clientX;
  wrapper.touchstartY = touch.clientY;
  wrapper.start?.({
    originalEvent: event,
    ...wrapper
  });
}
function touchend(event, wrapper) {
  const touch = event.changedTouches[0];
  wrapper.touchendX = touch.clientX;
  wrapper.touchendY = touch.clientY;
  wrapper.end?.({
    originalEvent: event,
    ...wrapper
  });
  handleGesture(wrapper);
}
function touchmove(event, wrapper) {
  const touch = event.changedTouches[0];
  wrapper.touchmoveX = touch.clientX;
  wrapper.touchmoveY = touch.clientY;
  wrapper.move?.({
    originalEvent: event,
    ...wrapper
  });
}
function createHandlers() {
  let value = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
  const wrapper = {
    touchstartX: 0,
    touchstartY: 0,
    touchendX: 0,
    touchendY: 0,
    touchmoveX: 0,
    touchmoveY: 0,
    offsetX: 0,
    offsetY: 0,
    left: value.left,
    right: value.right,
    up: value.up,
    down: value.down,
    start: value.start,
    move: value.move,
    end: value.end
  };
  return {
    touchstart: e => touchstart(e, wrapper),
    touchend: e => touchend(e, wrapper),
    touchmove: e => touchmove(e, wrapper)
  };
}
function mounted$3(el, binding) {
  const value = binding.value;
  const target = value?.parent ? el.parentElement : el;
  const options = value?.options ?? {
    passive: true
  };
  const uid = binding.instance?.$.uid; // TODO: use custom uid generator

  if (!target || !uid) return;
  const handlers = createHandlers(binding.value);
  target._touchHandlers = target._touchHandlers ?? Object.create(null);
  target._touchHandlers[uid] = handlers;
  keys(handlers).forEach(eventName => {
    target.addEventListener(eventName, handlers[eventName], options);
  });
}
function unmounted$3(el, binding) {
  const target = binding.value?.parent ? el.parentElement : el;
  const uid = binding.instance?.$.uid;
  if (!target?._touchHandlers || !uid) return;
  const handlers = target._touchHandlers[uid];
  keys(handlers).forEach(eventName => {
    target.removeEventListener(eventName, handlers[eventName]);
  });
  delete target._touchHandlers[uid];
}
const Touch = {
  mounted: mounted$3,
  unmounted: unmounted$3
};

const {createVNode:_createVNode$1j,resolveDirective:_resolveDirective$5,withDirectives:_withDirectives$8} = await importShared('vue');
const {computed: computed$11,provide: provide$9,ref: ref$u,shallowRef: shallowRef$n,toRef: toRef$s,watch: watch$k} = await importShared('vue');
const VWindowSymbol = Symbol.for('vuetify:v-window');
const VWindowGroupSymbol = Symbol.for('vuetify:v-window-group');
const makeVWindowProps = propsFactory({
  continuous: Boolean,
  nextIcon: {
    type: [Boolean, String, Function, Object],
    default: '$next'
  },
  prevIcon: {
    type: [Boolean, String, Function, Object],
    default: '$prev'
  },
  reverse: Boolean,
  showArrows: {
    type: [Boolean, String],
    validator: v => typeof v === 'boolean' || v === 'hover'
  },
  touch: {
    type: [Object, Boolean],
    default: undefined
  },
  direction: {
    type: String,
    default: 'horizontal'
  },
  modelValue: null,
  disabled: Boolean,
  selectedClass: {
    type: String,
    default: 'v-window-item--active'
  },
  // TODO: mandatory should probably not be exposed but do this for now
  mandatory: {
    type: [Boolean, String],
    default: 'force'
  },
  ...makeComponentProps(),
  ...makeTagProps(),
  ...makeThemeProps()
}, 'VWindow');
const VWindow = genericComponent()({
  name: 'VWindow',
  directives: {
    Touch
  },
  props: makeVWindowProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      themeClasses
    } = provideTheme(props);
    const {
      isRtl
    } = useRtl();
    const {
      t
    } = useLocale();
    const group = useGroup(props, VWindowGroupSymbol);
    const rootRef = ref$u();
    const isRtlReverse = computed$11(() => isRtl.value ? !props.reverse : props.reverse);
    const isReversed = shallowRef$n(false);
    const transition = computed$11(() => {
      const axis = props.direction === 'vertical' ? 'y' : 'x';
      const reverse = isRtlReverse.value ? !isReversed.value : isReversed.value;
      const direction = reverse ? '-reverse' : '';
      return `v-window-${axis}${direction}-transition`;
    });
    const transitionCount = shallowRef$n(0);
    const transitionHeight = ref$u(undefined);
    const activeIndex = computed$11(() => {
      return group.items.value.findIndex(item => group.selected.value.includes(item.id));
    });
    watch$k(activeIndex, (newVal, oldVal) => {
      const itemsLength = group.items.value.length;
      const lastIndex = itemsLength - 1;
      if (itemsLength <= 2) {
        isReversed.value = newVal < oldVal;
      } else if (newVal === lastIndex && oldVal === 0) {
        isReversed.value = true;
      } else if (newVal === 0 && oldVal === lastIndex) {
        isReversed.value = false;
      } else {
        isReversed.value = newVal < oldVal;
      }
    });
    provide$9(VWindowSymbol, {
      transition,
      isReversed,
      transitionCount,
      transitionHeight,
      rootRef
    });
    const canMoveBack = toRef$s(() => props.continuous || activeIndex.value !== 0);
    const canMoveForward = toRef$s(() => props.continuous || activeIndex.value !== group.items.value.length - 1);
    function prev() {
      canMoveBack.value && group.prev();
    }
    function next() {
      canMoveForward.value && group.next();
    }
    const arrows = computed$11(() => {
      const arrows = [];
      const prevProps = {
        icon: isRtl.value ? props.nextIcon : props.prevIcon,
        class: `v-window__${isRtlReverse.value ? 'right' : 'left'}`,
        onClick: group.prev,
        'aria-label': t('$vuetify.carousel.prev')
      };
      arrows.push(canMoveBack.value ? slots.prev ? slots.prev({
        props: prevProps
      }) : _createVNode$1j(VBtn, prevProps, null) : _createVNode$1j("div", null, null));
      const nextProps = {
        icon: isRtl.value ? props.prevIcon : props.nextIcon,
        class: `v-window__${isRtlReverse.value ? 'left' : 'right'}`,
        onClick: group.next,
        'aria-label': t('$vuetify.carousel.next')
      };
      arrows.push(canMoveForward.value ? slots.next ? slots.next({
        props: nextProps
      }) : _createVNode$1j(VBtn, nextProps, null) : _createVNode$1j("div", null, null));
      return arrows;
    });
    const touchOptions = computed$11(() => {
      if (props.touch === false) return props.touch;
      const options = {
        left: () => {
          isRtlReverse.value ? prev() : next();
        },
        right: () => {
          isRtlReverse.value ? next() : prev();
        },
        start: _ref2 => {
          let {
            originalEvent
          } = _ref2;
          originalEvent.stopPropagation();
        }
      };
      return {
        ...options,
        ...(props.touch === true ? {} : props.touch)
      };
    });
    useRender(() => _withDirectives$8(_createVNode$1j(props.tag, {
      "ref": rootRef,
      "class": ['v-window', {
        'v-window--show-arrows-on-hover': props.showArrows === 'hover'
      }, themeClasses.value, props.class],
      "style": props.style
    }, {
      default: () => [_createVNode$1j("div", {
        "class": "v-window__container",
        "style": {
          height: transitionHeight.value
        }
      }, [slots.default?.({
        group
      }), props.showArrows !== false && _createVNode$1j("div", {
        "class": "v-window__controls"
      }, [arrows.value])]), slots.additional?.({
        group
      })]
    }), [[_resolveDirective$5("touch"), touchOptions.value]]));
    return {
      group
    };
  }
});

const {Fragment:_Fragment$p,mergeProps:_mergeProps$F,createVNode:_createVNode$1i} = await importShared('vue');
const {onMounted: onMounted$8,ref: ref$t,watch: watch$j} = await importShared('vue');
const makeVCarouselProps = propsFactory({
  color: String,
  cycle: Boolean,
  delimiterIcon: {
    type: IconValue,
    default: '$delimiter'
  },
  height: {
    type: [Number, String],
    default: 500
  },
  hideDelimiters: Boolean,
  hideDelimiterBackground: Boolean,
  interval: {
    type: [Number, String],
    default: 6000,
    validator: value => Number(value) > 0
  },
  progress: [Boolean, String],
  verticalDelimiters: [Boolean, String],
  ...makeVWindowProps({
    continuous: true,
    mandatory: 'force',
    showArrows: true
  })
}, 'VCarousel');
const VCarousel = genericComponent()({
  name: 'VCarousel',
  props: makeVCarouselProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const model = useProxiedModel(props, 'modelValue');
    const {
      t
    } = useLocale();
    const windowRef = ref$t();
    let slideTimeout = -1;
    watch$j(model, restartTimeout);
    watch$j(() => props.interval, restartTimeout);
    watch$j(() => props.cycle, val => {
      if (val) restartTimeout();else window.clearTimeout(slideTimeout);
    });
    onMounted$8(startTimeout);
    function startTimeout() {
      if (!props.cycle || !windowRef.value) return;
      slideTimeout = window.setTimeout(windowRef.value.group.next, Number(props.interval) > 0 ? Number(props.interval) : 6000);
    }
    function restartTimeout() {
      window.clearTimeout(slideTimeout);
      window.requestAnimationFrame(startTimeout);
    }
    useRender(() => {
      const windowProps = VWindow.filterProps(props);
      return _createVNode$1i(VWindow, _mergeProps$F({
        "ref": windowRef
      }, windowProps, {
        "modelValue": model.value,
        "onUpdate:modelValue": $event => model.value = $event,
        "class": ['v-carousel', {
          'v-carousel--hide-delimiter-background': props.hideDelimiterBackground,
          'v-carousel--vertical-delimiters': props.verticalDelimiters
        }, props.class],
        "style": [{
          height: convertToUnit(props.height)
        }, props.style]
      }), {
        default: slots.default,
        additional: _ref2 => {
          let {
            group
          } = _ref2;
          return _createVNode$1i(_Fragment$p, null, [!props.hideDelimiters && _createVNode$1i("div", {
            "class": "v-carousel__controls",
            "style": {
              left: props.verticalDelimiters === 'left' && props.verticalDelimiters ? 0 : 'auto',
              right: props.verticalDelimiters === 'right' ? 0 : 'auto'
            }
          }, [group.items.value.length > 0 && _createVNode$1i(VDefaultsProvider, {
            "defaults": {
              VBtn: {
                color: props.color,
                icon: props.delimiterIcon,
                size: 'x-small',
                variant: 'text'
              }
            },
            "scoped": true
          }, {
            default: () => [group.items.value.map((item, index) => {
              const props = {
                id: `carousel-item-${item.id}`,
                'aria-label': t('$vuetify.carousel.ariaLabel.delimiter', index + 1, group.items.value.length),
                class: ['v-carousel__controls__item', group.isSelected(item.id) && 'v-btn--active'],
                onClick: () => group.select(item.id, true)
              };
              return slots.item ? slots.item({
                props,
                item
              }) : _createVNode$1i(VBtn, _mergeProps$F(item, props), null);
            })]
          })]), props.progress && _createVNode$1i(VProgressLinear, {
            "class": "v-carousel__progress",
            "color": typeof props.progress === 'string' ? props.progress : undefined,
            "modelValue": (group.getItemIndex(model.value) + 1) / group.items.value.length * 100
          }, null)]);
        },
        prev: slots.prev,
        next: slots.next
      });
    });
    return {};
  }
});

const {vShow:_vShow$3,createVNode:_createVNode$1h,withDirectives:_withDirectives$7} = await importShared('vue');
const {computed: computed$10,inject: inject$d,nextTick: nextTick$d,shallowRef: shallowRef$m} = await importShared('vue');
const makeVWindowItemProps = propsFactory({
  reverseTransition: {
    type: [Boolean, String],
    default: undefined
  },
  transition: {
    type: [Boolean, String],
    default: undefined
  },
  ...makeComponentProps(),
  ...makeGroupItemProps(),
  ...makeLazyProps()
}, 'VWindowItem');
const VWindowItem = genericComponent()({
  name: 'VWindowItem',
  directives: {
    Touch
  },
  props: makeVWindowItemProps(),
  emits: {
    'group:selected': val => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const window = inject$d(VWindowSymbol);
    const groupItem = useGroupItem(props, VWindowGroupSymbol);
    const {
      isBooted
    } = useSsrBoot();
    if (!window || !groupItem) throw new Error('[Vuetify] VWindowItem must be used inside VWindow');
    const isTransitioning = shallowRef$m(false);
    const hasTransition = computed$10(() => isBooted.value && (window.isReversed.value ? props.reverseTransition !== false : props.transition !== false));
    function onAfterTransition() {
      if (!isTransitioning.value || !window) {
        return;
      }

      // Finalize transition state.
      isTransitioning.value = false;
      if (window.transitionCount.value > 0) {
        window.transitionCount.value -= 1;

        // Remove container height if we are out of transition.
        if (window.transitionCount.value === 0) {
          window.transitionHeight.value = undefined;
        }
      }
    }
    function onBeforeTransition() {
      if (isTransitioning.value || !window) {
        return;
      }

      // Initialize transition state here.
      isTransitioning.value = true;
      if (window.transitionCount.value === 0) {
        // Set initial height for height transition.
        window.transitionHeight.value = convertToUnit(window.rootRef.value?.clientHeight);
      }
      window.transitionCount.value += 1;
    }
    function onTransitionCancelled() {
      onAfterTransition(); // This should have the same path as normal transition end.
    }
    function onEnterTransition(el) {
      if (!isTransitioning.value) {
        return;
      }
      nextTick$d(() => {
        // Do not set height if no transition or cancelled.
        if (!hasTransition.value || !isTransitioning.value || !window) {
          return;
        }

        // Set transition target height.
        window.transitionHeight.value = convertToUnit(el.clientHeight);
      });
    }
    const transition = computed$10(() => {
      const name = window.isReversed.value ? props.reverseTransition : props.transition;
      return !hasTransition.value ? false : {
        name: typeof name !== 'string' ? window.transition.value : name,
        onBeforeEnter: onBeforeTransition,
        onAfterEnter: onAfterTransition,
        onEnterCancelled: onTransitionCancelled,
        onBeforeLeave: onBeforeTransition,
        onAfterLeave: onAfterTransition,
        onLeaveCancelled: onTransitionCancelled,
        onEnter: onEnterTransition
      };
    });
    const {
      hasContent
    } = useLazy(props, groupItem.isSelected);
    useRender(() => _createVNode$1h(MaybeTransition, {
      "transition": transition.value,
      "disabled": !isBooted.value
    }, {
      default: () => [_withDirectives$7(_createVNode$1h("div", {
        "class": ['v-window-item', groupItem.selectedClass.value, props.class],
        "style": props.style
      }, [hasContent.value && slots.default?.()]), [[_vShow$3, groupItem.isSelected.value]])]
    }));
    return {
      groupItem
    };
  }
});

const {mergeProps:_mergeProps$E,createVNode:_createVNode$1g} = await importShared('vue');
const makeVCarouselItemProps = propsFactory({
  ...makeVImgProps(),
  ...makeVWindowItemProps()
}, 'VCarouselItem');
const VCarouselItem = genericComponent()({
  name: 'VCarouselItem',
  inheritAttrs: false,
  props: makeVCarouselItemProps(),
  setup(props, _ref) {
    let {
      slots,
      attrs
    } = _ref;
    useRender(() => {
      const imgProps = VImg.filterProps(props);
      const windowItemProps = VWindowItem.filterProps(props);
      return _createVNode$1g(VWindowItem, _mergeProps$E({
        "class": ['v-carousel-item', props.class]
      }, windowItemProps), {
        default: () => [_createVNode$1g(VImg, _mergeProps$E(attrs, imgProps), slots)]
      });
    });
  }
});

// Styles
const VCode = createSimpleFunctional('v-code', 'code');

const {createVNode:_createVNode$1f} = await importShared('vue');
const {computed: computed$$,onMounted: onMounted$7,ref: ref$s,shallowRef: shallowRef$l,watch: watch$i} = await importShared('vue');
const makeVColorPickerCanvasProps = propsFactory({
  color: {
    type: Object
  },
  disabled: Boolean,
  dotSize: {
    type: [Number, String],
    default: 10
  },
  height: {
    type: [Number, String],
    default: 150
  },
  width: {
    type: [Number, String],
    default: 300
  },
  ...makeComponentProps()
}, 'VColorPickerCanvas');
const VColorPickerCanvas = defineComponent({
  name: 'VColorPickerCanvas',
  props: makeVColorPickerCanvasProps(),
  emits: {
    'update:color': color => true,
    'update:position': hue => true
  },
  setup(props, _ref) {
    let {
      emit
    } = _ref;
    const isInteracting = shallowRef$l(false);
    const canvasRef = ref$s();
    const canvasWidth = shallowRef$l(parseFloat(props.width));
    const canvasHeight = shallowRef$l(parseFloat(props.height));
    const _dotPosition = ref$s({
      x: 0,
      y: 0
    });
    const dotPosition = computed$$({
      get: () => _dotPosition.value,
      set(val) {
        if (!canvasRef.value) return;
        const {
          x,
          y
        } = val;
        _dotPosition.value = val;
        emit('update:color', {
          h: props.color?.h ?? 0,
          s: clamp(x, 0, canvasWidth.value) / canvasWidth.value,
          v: 1 - clamp(y, 0, canvasHeight.value) / canvasHeight.value,
          a: props.color?.a ?? 1
        });
      }
    });
    const dotStyles = computed$$(() => {
      const {
        x,
        y
      } = dotPosition.value;
      const radius = parseInt(props.dotSize, 10) / 2;
      return {
        width: convertToUnit(props.dotSize),
        height: convertToUnit(props.dotSize),
        transform: `translate(${convertToUnit(x - radius)}, ${convertToUnit(y - radius)})`
      };
    });
    const {
      resizeRef
    } = useResizeObserver(entries => {
      if (!resizeRef.el?.offsetParent) return;
      const {
        width,
        height
      } = entries[0].contentRect;
      canvasWidth.value = width;
      canvasHeight.value = height;
    });
    function updateDotPosition(x, y, rect) {
      const {
        left,
        top,
        width,
        height
      } = rect;
      dotPosition.value = {
        x: clamp(x - left, 0, width),
        y: clamp(y - top, 0, height)
      };
    }
    function handleMouseDown(e) {
      if (e.type === 'mousedown') {
        // Prevent text selection while dragging
        e.preventDefault();
      }
      if (props.disabled) return;
      handleMouseMove(e);
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      window.addEventListener('touchmove', handleMouseMove);
      window.addEventListener('touchend', handleMouseUp);
    }
    function handleMouseMove(e) {
      if (props.disabled || !canvasRef.value) return;
      isInteracting.value = true;
      const coords = getEventCoordinates(e);
      updateDotPosition(coords.clientX, coords.clientY, canvasRef.value.getBoundingClientRect());
    }
    function handleMouseUp() {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('touchmove', handleMouseMove);
      window.removeEventListener('touchend', handleMouseUp);
    }
    function updateCanvas() {
      if (!canvasRef.value) return;
      const canvas = canvasRef.value;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      const saturationGradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
      saturationGradient.addColorStop(0, 'hsla(0, 0%, 100%, 1)'); // white
      saturationGradient.addColorStop(1, `hsla(${props.color?.h ?? 0}, 100%, 50%, 1)`);
      ctx.fillStyle = saturationGradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      const valueGradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
      valueGradient.addColorStop(0, 'hsla(0, 0%, 0%, 0)'); // transparent
      valueGradient.addColorStop(1, 'hsla(0, 0%, 0%, 1)'); // black
      ctx.fillStyle = valueGradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    watch$i(() => props.color?.h, updateCanvas, {
      immediate: true
    });
    watch$i(() => [canvasWidth.value, canvasHeight.value], (newVal, oldVal) => {
      updateCanvas();
      _dotPosition.value = {
        x: dotPosition.value.x * newVal[0] / oldVal[0],
        y: dotPosition.value.y * newVal[1] / oldVal[1]
      };
    }, {
      flush: 'post'
    });
    watch$i(() => props.color, () => {
      if (isInteracting.value) {
        isInteracting.value = false;
        return;
      }
      _dotPosition.value = props.color ? {
        x: props.color.s * canvasWidth.value,
        y: (1 - props.color.v) * canvasHeight.value
      } : {
        x: 0,
        y: 0
      };
    }, {
      deep: true,
      immediate: true
    });
    onMounted$7(() => updateCanvas());
    useRender(() => _createVNode$1f("div", {
      "ref": resizeRef,
      "class": ['v-color-picker-canvas', props.class],
      "style": props.style,
      "onMousedown": handleMouseDown,
      "onTouchstartPassive": handleMouseDown
    }, [_createVNode$1f("canvas", {
      "ref": canvasRef,
      "width": canvasWidth.value,
      "height": canvasHeight.value
    }, null), props.color && _createVNode$1f("div", {
      "class": ['v-color-picker-canvas__dot', {
        'v-color-picker-canvas__dot--disabled': props.disabled
      }],
      "style": dotStyles.value
    }, null)]));
    return {};
  }
});

// Utilities
function stripAlpha(color, stripAlpha) {
  if (stripAlpha) {
    const {
      a,
      ...rest
    } = color;
    return rest;
  }
  return color;
}
function extractColor(color, input) {
  if (input == null || typeof input === 'string') {
    const hasA = color.a !== 1;
    if (input?.startsWith('rgb(')) {
      const {
        r,
        g,
        b,
        a
      } = HSVtoRGB(color);
      return `rgb(${r} ${g} ${b}` + (hasA ? ` / ${a})` : ')');
    } else if (input?.startsWith('hsl(')) {
      const {
        h,
        s,
        l,
        a
      } = HSVtoHSL(color);
      return `hsl(${h} ${Math.round(s * 100)} ${Math.round(l * 100)}` + (hasA ? ` / ${a})` : ')');
    }
    const hex = HSVtoHex(color);
    if (color.a === 1) return hex.slice(0, 7);else return hex;
  }
  if (typeof input === 'object') {
    let converted;
    if (has(input, ['r', 'g', 'b'])) converted = HSVtoRGB(color);else if (has(input, ['h', 's', 'l'])) converted = HSVtoHSL(color);else if (has(input, ['h', 's', 'v'])) converted = color;
    return stripAlpha(converted, !has(input, ['a']) && color.a === 1);
  }
  return color;
}
const nullColor = {
  h: 0,
  s: 0,
  v: 0,
  a: 1
};
const rgba = {
  inputProps: {
    type: 'number',
    min: 0
  },
  inputs: [{
    label: 'R',
    max: 255,
    step: 1,
    getValue: c => Math.round(c.r),
    getColor: (c, v) => ({
      ...c,
      r: Number(v)
    })
  }, {
    label: 'G',
    max: 255,
    step: 1,
    getValue: c => Math.round(c.g),
    getColor: (c, v) => ({
      ...c,
      g: Number(v)
    })
  }, {
    label: 'B',
    max: 255,
    step: 1,
    getValue: c => Math.round(c.b),
    getColor: (c, v) => ({
      ...c,
      b: Number(v)
    })
  }, {
    label: 'A',
    max: 1,
    step: 0.01,
    getValue: _ref => {
      let {
        a
      } = _ref;
      return a != null ? Math.round(a * 100) / 100 : 1;
    },
    getColor: (c, v) => ({
      ...c,
      a: Number(v)
    })
  }],
  to: HSVtoRGB,
  from: RGBtoHSV
};
const rgb = {
  ...rgba,
  inputs: rgba.inputs?.slice(0, 3)
};
const hsla = {
  inputProps: {
    type: 'number',
    min: 0
  },
  inputs: [{
    label: 'H',
    max: 360,
    step: 1,
    getValue: c => Math.round(c.h),
    getColor: (c, v) => ({
      ...c,
      h: Number(v)
    })
  }, {
    label: 'S',
    max: 1,
    step: 0.01,
    getValue: c => Math.round(c.s * 100) / 100,
    getColor: (c, v) => ({
      ...c,
      s: Number(v)
    })
  }, {
    label: 'L',
    max: 1,
    step: 0.01,
    getValue: c => Math.round(c.l * 100) / 100,
    getColor: (c, v) => ({
      ...c,
      l: Number(v)
    })
  }, {
    label: 'A',
    max: 1,
    step: 0.01,
    getValue: _ref2 => {
      let {
        a
      } = _ref2;
      return a != null ? Math.round(a * 100) / 100 : 1;
    },
    getColor: (c, v) => ({
      ...c,
      a: Number(v)
    })
  }],
  to: HSVtoHSL,
  from: HSLtoHSV
};
const hsl = {
  ...hsla,
  inputs: hsla.inputs.slice(0, 3)
};
const hexa = {
  inputProps: {
    type: 'text'
  },
  inputs: [{
    label: 'HEXA',
    getValue: c => c,
    getColor: (c, v) => v
  }],
  to: HSVtoHex,
  from: HexToHSV
};
const hex = {
  ...hexa,
  inputs: [{
    label: 'HEX',
    getValue: c => c.slice(0, 7),
    getColor: (c, v) => v
  }]
};
const modes = {
  rgb,
  rgba,
  hsl,
  hsla,
  hex,
  hexa
};

const {createVNode:_createVNode$1e} = await importShared('vue');
const {computed: computed$_} = await importShared('vue');
const VColorPickerInput = _ref => {
  let {
    label,
    ...rest
  } = _ref;
  return _createVNode$1e("div", {
    "class": "v-color-picker-edit__input"
  }, [_createVNode$1e("input", rest, null), _createVNode$1e("span", null, [label])]);
};
const makeVColorPickerEditProps = propsFactory({
  color: Object,
  disabled: Boolean,
  mode: {
    type: String,
    default: 'rgba',
    validator: v => Object.keys(modes).includes(v)
  },
  modes: {
    type: Array,
    default: () => Object.keys(modes),
    validator: v => Array.isArray(v) && v.every(m => Object.keys(modes).includes(m))
  },
  ...makeComponentProps()
}, 'VColorPickerEdit');
const VColorPickerEdit = defineComponent({
  name: 'VColorPickerEdit',
  props: makeVColorPickerEditProps(),
  emits: {
    'update:color': color => true,
    'update:mode': mode => true
  },
  setup(props, _ref2) {
    let {
      emit
    } = _ref2;
    const enabledModes = computed$_(() => {
      return props.modes.map(key => ({
        ...modes[key],
        name: key
      }));
    });
    const inputs = computed$_(() => {
      const mode = enabledModes.value.find(m => m.name === props.mode);
      if (!mode) return [];
      const color = props.color ? mode.to(props.color) : null;
      return mode.inputs?.map(_ref3 => {
        let {
          getValue,
          getColor,
          ...inputProps
        } = _ref3;
        return {
          ...mode.inputProps,
          ...inputProps,
          disabled: props.disabled,
          value: color && getValue(color),
          onChange: e => {
            const target = e.target;
            if (!target) return;
            emit('update:color', mode.from(getColor(color ?? mode.to(nullColor), target.value)));
          }
        };
      });
    });
    useRender(() => _createVNode$1e("div", {
      "class": ['v-color-picker-edit', props.class],
      "style": props.style
    }, [inputs.value?.map(props => _createVNode$1e(VColorPickerInput, props, null)), enabledModes.value.length > 1 && _createVNode$1e(VBtn, {
      "icon": "$unfold",
      "size": "x-small",
      "variant": "plain",
      "onClick": () => {
        const mi = enabledModes.value.findIndex(m => m.name === props.mode);
        emit('update:mode', enabledModes.value[(mi + 1) % enabledModes.value.length].name);
      }
    }, null)]));
    return {};
  }
});

const {computed: computed$Z,nextTick: nextTick$c,provide: provide$8,ref: ref$r,shallowRef: shallowRef$k,toRef: toRef$r} = await importShared('vue');
const VSliderSymbol = Symbol.for('vuetify:v-slider');
function getOffset(e, el, direction) {
  const vertical = direction === 'vertical';
  const rect = el.getBoundingClientRect();
  const touch = 'touches' in e ? e.touches[0] : e;
  return vertical ? touch.clientY - (rect.top + rect.height / 2) : touch.clientX - (rect.left + rect.width / 2);
}
function getPosition(e, position) {
  if ('touches' in e && e.touches.length) return e.touches[0][position];else if ('changedTouches' in e && e.changedTouches.length) return e.changedTouches[0][position];else return e[position];
}
const makeSliderProps = propsFactory({
  disabled: {
    type: Boolean,
    default: null
  },
  error: Boolean,
  readonly: {
    type: Boolean,
    default: null
  },
  max: {
    type: [Number, String],
    default: 100
  },
  min: {
    type: [Number, String],
    default: 0
  },
  step: {
    type: [Number, String],
    default: 0
  },
  thumbColor: String,
  thumbLabel: {
    type: [Boolean, String],
    default: undefined,
    validator: v => typeof v === 'boolean' || v === 'always'
  },
  thumbSize: {
    type: [Number, String],
    default: 20
  },
  showTicks: {
    type: [Boolean, String],
    default: false,
    validator: v => typeof v === 'boolean' || v === 'always'
  },
  ticks: {
    type: [Array, Object]
  },
  tickSize: {
    type: [Number, String],
    default: 2
  },
  color: String,
  trackColor: String,
  trackFillColor: String,
  trackSize: {
    type: [Number, String],
    default: 4
  },
  direction: {
    type: String,
    default: 'horizontal',
    validator: v => ['vertical', 'horizontal'].includes(v)
  },
  reverse: Boolean,
  ...makeRoundedProps(),
  ...makeElevationProps({
    elevation: 2
  }),
  ripple: {
    type: Boolean,
    default: true
  }
}, 'Slider');
const useSteps = props => {
  const min = computed$Z(() => parseFloat(props.min));
  const max = computed$Z(() => parseFloat(props.max));
  const step = computed$Z(() => Number(props.step) > 0 ? parseFloat(props.step) : 0);
  const decimals = computed$Z(() => Math.max(getDecimals(step.value), getDecimals(min.value)));
  function roundValue(value) {
    value = parseFloat(value);
    if (step.value <= 0) return value;
    const clamped = clamp(value, min.value, max.value);
    const offset = min.value % step.value;
    const newValue = Math.round((clamped - offset) / step.value) * step.value + offset;
    return parseFloat(Math.min(newValue, max.value).toFixed(decimals.value));
  }
  return {
    min,
    max,
    step,
    decimals,
    roundValue
  };
};
const useSlider = _ref => {
  let {
    props,
    steps,
    onSliderStart,
    onSliderMove,
    onSliderEnd,
    getActiveThumb
  } = _ref;
  const {
    isRtl
  } = useRtl();
  const isReversed = toRef$r(() => props.reverse);
  const vertical = computed$Z(() => props.direction === 'vertical');
  const indexFromEnd = computed$Z(() => vertical.value !== isReversed.value);
  const {
    min,
    max,
    step,
    decimals,
    roundValue
  } = steps;
  const thumbSize = computed$Z(() => parseInt(props.thumbSize, 10));
  const tickSize = computed$Z(() => parseInt(props.tickSize, 10));
  const trackSize = computed$Z(() => parseInt(props.trackSize, 10));
  const numTicks = computed$Z(() => (max.value - min.value) / step.value);
  const disabled = toRef$r(() => props.disabled);
  const thumbColor = computed$Z(() => props.error || props.disabled ? undefined : props.thumbColor ?? props.color);
  const trackColor = computed$Z(() => props.error || props.disabled ? undefined : props.trackColor ?? props.color);
  const trackFillColor = computed$Z(() => props.error || props.disabled ? undefined : props.trackFillColor ?? props.color);
  const mousePressed = shallowRef$k(false);
  const startOffset = shallowRef$k(0);
  const trackContainerRef = ref$r();
  const activeThumbRef = ref$r();
  function parseMouseMove(e) {
    const el = trackContainerRef.value?.$el;
    if (!el) return;
    const vertical = props.direction === 'vertical';
    const start = vertical ? 'top' : 'left';
    const length = vertical ? 'height' : 'width';
    const position = vertical ? 'clientY' : 'clientX';
    const {
      [start]: trackStart,
      [length]: trackLength
    } = el.getBoundingClientRect();
    const clickOffset = getPosition(e, position);

    // It is possible for left to be NaN, force to number
    let clickPos = Math.min(Math.max((clickOffset - trackStart - startOffset.value) / trackLength, 0), 1) || 0;
    if (vertical ? indexFromEnd.value : indexFromEnd.value !== isRtl.value) clickPos = 1 - clickPos;
    return roundValue(min.value + clickPos * (max.value - min.value));
  }
  const handleStop = e => {
    const value = parseMouseMove(e);
    if (value != null) {
      onSliderEnd({
        value
      });
    }
    mousePressed.value = false;
    startOffset.value = 0;
  };
  const handleStart = e => {
    const value = parseMouseMove(e);
    activeThumbRef.value = getActiveThumb(e);
    if (!activeThumbRef.value) return;
    mousePressed.value = true;
    if (activeThumbRef.value.contains(e.target)) {
      startOffset.value = getOffset(e, activeThumbRef.value, props.direction);
    } else {
      startOffset.value = 0;
      if (value != null) {
        onSliderMove({
          value
        });
      }
    }
    if (value != null) {
      onSliderStart({
        value
      });
    }
    nextTick$c(() => activeThumbRef.value?.focus());
  };
  const moveListenerOptions = {
    passive: true,
    capture: true
  };
  function onMouseMove(e) {
    const value = parseMouseMove(e);
    if (value != null) {
      onSliderMove({
        value
      });
    }
  }
  function onSliderMouseUp(e) {
    e.stopPropagation();
    e.preventDefault();
    handleStop(e);
    window.removeEventListener('mousemove', onMouseMove, moveListenerOptions);
    window.removeEventListener('mouseup', onSliderMouseUp);
  }
  function onSliderTouchend(e) {
    handleStop(e);
    window.removeEventListener('touchmove', onMouseMove, moveListenerOptions);
    e.target?.removeEventListener('touchend', onSliderTouchend);
  }
  function onSliderTouchstart(e) {
    handleStart(e);
    window.addEventListener('touchmove', onMouseMove, moveListenerOptions);
    e.target?.addEventListener('touchend', onSliderTouchend, {
      passive: false
    });
  }
  function onSliderMousedown(e) {
    if (e.button !== 0) return;
    e.preventDefault();
    handleStart(e);
    window.addEventListener('mousemove', onMouseMove, moveListenerOptions);
    window.addEventListener('mouseup', onSliderMouseUp, {
      passive: false
    });
  }
  const position = val => {
    const percentage = (val - min.value) / (max.value - min.value) * 100;
    return clamp(isNaN(percentage) ? 0 : percentage, 0, 100);
  };
  const showTicks = toRef$r(() => props.showTicks);
  const parsedTicks = computed$Z(() => {
    if (!showTicks.value) return [];
    if (!props.ticks) {
      return numTicks.value !== Infinity ? createRange(numTicks.value + 1).map(t => {
        const value = min.value + t * step.value;
        return {
          value,
          position: position(value)
        };
      }) : [];
    }
    if (Array.isArray(props.ticks)) return props.ticks.map(t => ({
      value: t,
      position: position(t),
      label: t.toString()
    }));
    return Object.keys(props.ticks).map(key => ({
      value: parseFloat(key),
      position: position(parseFloat(key)),
      label: props.ticks[key]
    }));
  });
  const hasLabels = computed$Z(() => parsedTicks.value.some(_ref2 => {
    let {
      label
    } = _ref2;
    return !!label;
  }));
  const data = {
    activeThumbRef,
    color: toRef$r(() => props.color),
    decimals,
    disabled,
    direction: toRef$r(() => props.direction),
    elevation: toRef$r(() => props.elevation),
    hasLabels,
    isReversed,
    indexFromEnd,
    min,
    max,
    mousePressed,
    numTicks,
    onSliderMousedown,
    onSliderTouchstart,
    parsedTicks,
    parseMouseMove,
    position,
    readonly: toRef$r(() => props.readonly),
    rounded: toRef$r(() => props.rounded),
    roundValue,
    showTicks,
    startOffset,
    step,
    thumbSize,
    thumbColor,
    thumbLabel: toRef$r(() => props.thumbLabel),
    ticks: toRef$r(() => props.ticks),
    tickSize,
    trackColor,
    trackContainerRef,
    trackFillColor,
    trackSize,
    vertical
  };
  provide$8(VSliderSymbol, data);
  return data;
};

const {createVNode:_createVNode$1d,resolveDirective:_resolveDirective$4,withDirectives:_withDirectives$6,vShow:_vShow$2} = await importShared('vue');
const {computed: computed$Y,inject: inject$c} = await importShared('vue');
const makeVSliderThumbProps = propsFactory({
  focused: Boolean,
  max: {
    type: Number,
    required: true
  },
  min: {
    type: Number,
    required: true
  },
  modelValue: {
    type: Number,
    required: true
  },
  position: {
    type: Number,
    required: true
  },
  ripple: {
    type: [Boolean, Object],
    default: true
  },
  name: String,
  ...makeComponentProps()
}, 'VSliderThumb');
const VSliderThumb = genericComponent()({
  name: 'VSliderThumb',
  directives: {
    Ripple
  },
  props: makeVSliderThumbProps(),
  emits: {
    'update:modelValue': v => true
  },
  setup(props, _ref) {
    let {
      slots,
      emit
    } = _ref;
    const slider = inject$c(VSliderSymbol);
    const {
      isRtl,
      rtlClasses
    } = useRtl();
    if (!slider) throw new Error('[Vuetify] v-slider-thumb must be used inside v-slider or v-range-slider');
    const {
      thumbColor,
      step,
      disabled,
      thumbSize,
      thumbLabel,
      direction,
      isReversed,
      vertical,
      readonly,
      elevation,
      mousePressed,
      decimals,
      indexFromEnd
    } = slider;
    const elevationProps = computed$Y(() => !disabled.value ? elevation.value : undefined);
    const {
      elevationClasses
    } = useElevation(elevationProps);
    const {
      textColorClasses,
      textColorStyles
    } = useTextColor(thumbColor);
    const {
      pageup,
      pagedown,
      end,
      home,
      left,
      right,
      down,
      up
    } = keyValues;
    const relevantKeys = [pageup, pagedown, end, home, left, right, down, up];
    const multipliers = computed$Y(() => {
      if (step.value) return [1, 2, 3];else return [1, 5, 10];
    });
    function parseKeydown(e, value) {
      if (!relevantKeys.includes(e.key)) return;
      e.preventDefault();
      const _step = step.value || 0.1;
      const steps = (props.max - props.min) / _step;
      if ([left, right, down, up].includes(e.key)) {
        const increase = vertical.value ? [isRtl.value ? left : right, isReversed.value ? down : up] : indexFromEnd.value !== isRtl.value ? [left, up] : [right, up];
        const direction = increase.includes(e.key) ? 1 : -1;
        const multiplier = e.shiftKey ? 2 : e.ctrlKey ? 1 : 0;
        value = value + direction * _step * multipliers.value[multiplier];
      } else if (e.key === home) {
        value = props.min;
      } else if (e.key === end) {
        value = props.max;
      } else {
        const direction = e.key === pagedown ? 1 : -1;
        value = value - direction * _step * (steps > 100 ? steps / 10 : 10);
      }
      return Math.max(props.min, Math.min(props.max, value));
    }
    function onKeydown(e) {
      const newValue = parseKeydown(e, props.modelValue);
      newValue != null && emit('update:modelValue', newValue);
    }
    useRender(() => {
      const positionPercentage = convertToUnit(indexFromEnd.value ? 100 - props.position : props.position, '%');
      return _createVNode$1d("div", {
        "class": ['v-slider-thumb', {
          'v-slider-thumb--focused': props.focused,
          'v-slider-thumb--pressed': props.focused && mousePressed.value
        }, props.class, rtlClasses.value],
        "style": [{
          '--v-slider-thumb-position': positionPercentage,
          '--v-slider-thumb-size': convertToUnit(thumbSize.value)
        }, props.style],
        "role": "slider",
        "tabindex": disabled.value ? -1 : 0,
        "aria-label": props.name,
        "aria-valuemin": props.min,
        "aria-valuemax": props.max,
        "aria-valuenow": props.modelValue,
        "aria-readonly": !!readonly.value,
        "aria-orientation": direction.value,
        "onKeydown": !readonly.value ? onKeydown : undefined
      }, [_createVNode$1d("div", {
        "class": ['v-slider-thumb__surface', textColorClasses.value, elevationClasses.value],
        "style": {
          ...textColorStyles.value
        }
      }, null), _withDirectives$6(_createVNode$1d("div", {
        "class": ['v-slider-thumb__ripple', textColorClasses.value],
        "style": textColorStyles.value
      }, null), [[_resolveDirective$4("ripple"), props.ripple, null, {
        circle: true,
        center: true
      }]]), _createVNode$1d(VScaleTransition, {
        "origin": "bottom center"
      }, {
        default: () => [_withDirectives$6(_createVNode$1d("div", {
          "class": "v-slider-thumb__label-container"
        }, [_createVNode$1d("div", {
          "class": ['v-slider-thumb__label']
        }, [_createVNode$1d("div", null, [slots['thumb-label']?.({
          modelValue: props.modelValue
        }) ?? props.modelValue.toFixed(step.value ? decimals.value : 1)])])]), [[_vShow$2, thumbLabel.value && props.focused || thumbLabel.value === 'always']])]
      })]);
    });
    return {};
  }
});

const {createVNode:_createVNode$1c} = await importShared('vue');
const {computed: computed$X,inject: inject$b} = await importShared('vue');
const makeVSliderTrackProps = propsFactory({
  start: {
    type: Number,
    required: true
  },
  stop: {
    type: Number,
    required: true
  },
  ...makeComponentProps()
}, 'VSliderTrack');
const VSliderTrack = genericComponent()({
  name: 'VSliderTrack',
  props: makeVSliderTrackProps(),
  emits: {},
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const slider = inject$b(VSliderSymbol);
    if (!slider) throw new Error('[Vuetify] v-slider-track must be inside v-slider or v-range-slider');
    const {
      color,
      parsedTicks,
      rounded,
      showTicks,
      tickSize,
      trackColor,
      trackFillColor,
      trackSize,
      vertical,
      min,
      max,
      indexFromEnd
    } = slider;
    const {
      roundedClasses
    } = useRounded(rounded);
    const {
      backgroundColorClasses: trackFillColorClasses,
      backgroundColorStyles: trackFillColorStyles
    } = useBackgroundColor(trackFillColor);
    const {
      backgroundColorClasses: trackColorClasses,
      backgroundColorStyles: trackColorStyles
    } = useBackgroundColor(trackColor);
    const startDir = computed$X(() => `inset-${vertical.value ? 'block' : 'inline'}-${indexFromEnd.value ? 'end' : 'start'}`);
    const endDir = computed$X(() => vertical.value ? 'height' : 'width');
    const backgroundStyles = computed$X(() => {
      return {
        [startDir.value]: '0%',
        [endDir.value]: '100%'
      };
    });
    const trackFillWidth = computed$X(() => props.stop - props.start);
    const trackFillStyles = computed$X(() => {
      return {
        [startDir.value]: convertToUnit(props.start, '%'),
        [endDir.value]: convertToUnit(trackFillWidth.value, '%')
      };
    });
    const computedTicks = computed$X(() => {
      if (!showTicks.value) return [];
      const ticks = vertical.value ? parsedTicks.value.slice().reverse() : parsedTicks.value;
      return ticks.map((tick, index) => {
        const directionValue = tick.value !== min.value && tick.value !== max.value ? convertToUnit(tick.position, '%') : undefined;
        return _createVNode$1c("div", {
          "key": tick.value,
          "class": ['v-slider-track__tick', {
            'v-slider-track__tick--filled': tick.position >= props.start && tick.position <= props.stop,
            'v-slider-track__tick--first': tick.value === min.value,
            'v-slider-track__tick--last': tick.value === max.value
          }],
          "style": {
            [startDir.value]: directionValue
          }
        }, [(tick.label || slots['tick-label']) && _createVNode$1c("div", {
          "class": "v-slider-track__tick-label"
        }, [slots['tick-label']?.({
          tick,
          index
        }) ?? tick.label])]);
      });
    });
    useRender(() => {
      return _createVNode$1c("div", {
        "class": ['v-slider-track', roundedClasses.value, props.class],
        "style": [{
          '--v-slider-track-size': convertToUnit(trackSize.value),
          '--v-slider-tick-size': convertToUnit(tickSize.value)
        }, props.style]
      }, [_createVNode$1c("div", {
        "class": ['v-slider-track__background', trackColorClasses.value, {
          'v-slider-track__background--opacity': !!color.value || !trackFillColor.value
        }],
        "style": {
          ...backgroundStyles.value,
          ...trackColorStyles.value
        }
      }, null), _createVNode$1c("div", {
        "class": ['v-slider-track__fill', trackFillColorClasses.value],
        "style": {
          ...trackFillStyles.value,
          ...trackFillColorStyles.value
        }
      }, null), showTicks.value && _createVNode$1c("div", {
        "class": ['v-slider-track__ticks', {
          'v-slider-track__ticks--always-show': showTicks.value === 'always'
        }]
      }, [computedTicks.value])]);
    });
    return {};
  }
});

const {Fragment:_Fragment$o,createVNode:_createVNode$1b,mergeProps:_mergeProps$D} = await importShared('vue');
const {computed: computed$W,ref: ref$q} = await importShared('vue');
const makeVSliderProps = propsFactory({
  ...makeFocusProps(),
  ...makeSliderProps(),
  ...makeVInputProps(),
  modelValue: {
    type: [Number, String],
    default: 0
  }
}, 'VSlider');
const VSlider = genericComponent()({
  name: 'VSlider',
  props: makeVSliderProps(),
  emits: {
    'update:focused': value => true,
    'update:modelValue': v => true,
    start: value => true,
    end: value => true
  },
  setup(props, _ref) {
    let {
      slots,
      emit
    } = _ref;
    const thumbContainerRef = ref$q();
    const {
      rtlClasses
    } = useRtl();
    const steps = useSteps(props);
    const model = useProxiedModel(props, 'modelValue', undefined, value => {
      return steps.roundValue(value == null ? steps.min.value : value);
    });
    const {
      min,
      max,
      mousePressed,
      roundValue,
      onSliderMousedown,
      onSliderTouchstart,
      trackContainerRef,
      position,
      hasLabels,
      readonly
    } = useSlider({
      props,
      steps,
      onSliderStart: () => {
        emit('start', model.value);
      },
      onSliderEnd: _ref2 => {
        let {
          value
        } = _ref2;
        const roundedValue = roundValue(value);
        model.value = roundedValue;
        emit('end', roundedValue);
      },
      onSliderMove: _ref3 => {
        let {
          value
        } = _ref3;
        return model.value = roundValue(value);
      },
      getActiveThumb: () => thumbContainerRef.value?.$el
    });
    const {
      isFocused,
      focus,
      blur
    } = useFocus(props);
    const trackStop = computed$W(() => position(model.value));
    useRender(() => {
      const inputProps = VInput.filterProps(props);
      const hasPrepend = !!(props.label || slots.label || slots.prepend);
      return _createVNode$1b(VInput, _mergeProps$D({
        "class": ['v-slider', {
          'v-slider--has-labels': !!slots['tick-label'] || hasLabels.value,
          'v-slider--focused': isFocused.value,
          'v-slider--pressed': mousePressed.value,
          'v-slider--disabled': props.disabled
        }, rtlClasses.value, props.class],
        "style": props.style
      }, inputProps, {
        "focused": isFocused.value
      }), {
        ...slots,
        prepend: hasPrepend ? slotProps => _createVNode$1b(_Fragment$o, null, [slots.label?.(slotProps) ?? (props.label ? _createVNode$1b(VLabel, {
          "id": slotProps.id.value,
          "class": "v-slider__label",
          "text": props.label
        }, null) : undefined), slots.prepend?.(slotProps)]) : undefined,
        default: _ref4 => {
          let {
            id,
            messagesId
          } = _ref4;
          return _createVNode$1b("div", {
            "class": "v-slider__container",
            "onMousedown": !readonly.value ? onSliderMousedown : undefined,
            "onTouchstartPassive": !readonly.value ? onSliderTouchstart : undefined
          }, [_createVNode$1b("input", {
            "id": id.value,
            "name": props.name || id.value,
            "disabled": !!props.disabled,
            "readonly": !!props.readonly,
            "tabindex": "-1",
            "value": model.value
          }, null), _createVNode$1b(VSliderTrack, {
            "ref": trackContainerRef,
            "start": 0,
            "stop": trackStop.value
          }, {
            'tick-label': slots['tick-label']
          }), _createVNode$1b(VSliderThumb, {
            "ref": thumbContainerRef,
            "aria-describedby": messagesId.value,
            "focused": isFocused.value,
            "min": min.value,
            "max": max.value,
            "modelValue": model.value,
            "onUpdate:modelValue": v => model.value = v,
            "position": trackStop.value,
            "elevation": props.elevation,
            "onFocus": focus,
            "onBlur": blur,
            "ripple": props.ripple,
            "name": props.name
          }, {
            'thumb-label': slots['thumb-label']
          })]);
        }
      });
    });
    return {};
  }
});

const {createVNode:_createVNode$1a} = await importShared('vue');
const {onUnmounted} = await importShared('vue');
const makeVColorPickerPreviewProps = propsFactory({
  color: {
    type: Object
  },
  disabled: Boolean,
  hideAlpha: Boolean,
  ...makeComponentProps()
}, 'VColorPickerPreview');
const VColorPickerPreview = defineComponent({
  name: 'VColorPickerPreview',
  props: makeVColorPickerPreviewProps(),
  emits: {
    'update:color': color => true
  },
  setup(props, _ref) {
    let {
      emit
    } = _ref;
    const abortController = new AbortController();
    onUnmounted(() => abortController.abort());
    async function openEyeDropper() {
      if (!SUPPORTS_EYE_DROPPER || props.disabled) return;
      const eyeDropper = new window.EyeDropper();
      try {
        const result = await eyeDropper.open({
          signal: abortController.signal
        });
        const colorHexValue = RGBtoHSV(parseColor(result.sRGBHex));
        emit('update:color', {
          ...(props.color ?? nullColor),
          ...colorHexValue
        });
      } catch (e) {}
    }
    useRender(() => _createVNode$1a("div", {
      "class": ['v-color-picker-preview', {
        'v-color-picker-preview--hide-alpha': props.hideAlpha
      }, props.class],
      "style": props.style
    }, [SUPPORTS_EYE_DROPPER && _createVNode$1a("div", {
      "class": "v-color-picker-preview__eye-dropper",
      "key": "eyeDropper"
    }, [_createVNode$1a(VBtn, {
      "density": "comfortable",
      "disabled": props.disabled,
      "icon": "$eyeDropper",
      "variant": "plain",
      "onClick": openEyeDropper
    }, null)]), _createVNode$1a("div", {
      "class": "v-color-picker-preview__dot"
    }, [_createVNode$1a("div", {
      "style": {
        background: HSVtoCSS(props.color ?? nullColor)
      }
    }, null)]), _createVNode$1a("div", {
      "class": "v-color-picker-preview__sliders"
    }, [_createVNode$1a(VSlider, {
      "class": "v-color-picker-preview__track v-color-picker-preview__hue",
      "modelValue": props.color?.h,
      "onUpdate:modelValue": h => emit('update:color', {
        ...(props.color ?? nullColor),
        h
      }),
      "step": 0,
      "min": 0,
      "max": 360,
      "disabled": props.disabled,
      "thumbSize": 14,
      "trackSize": 8,
      "trackFillColor": "white",
      "hideDetails": true
    }, null), !props.hideAlpha && _createVNode$1a(VSlider, {
      "class": "v-color-picker-preview__track v-color-picker-preview__alpha",
      "modelValue": props.color?.a ?? 1,
      "onUpdate:modelValue": a => emit('update:color', {
        ...(props.color ?? nullColor),
        a
      }),
      "step": 1 / 256,
      "min": 0,
      "max": 1,
      "disabled": props.disabled,
      "thumbSize": 14,
      "trackSize": 8,
      "trackFillColor": "white",
      "hideDetails": true
    }, null)])]));
    return {};
  }
});

const red = {
  base: '#f44336',
  lighten5: '#ffebee',
  lighten4: '#ffcdd2',
  lighten3: '#ef9a9a',
  lighten2: '#e57373',
  lighten1: '#ef5350',
  darken1: '#e53935',
  darken2: '#d32f2f',
  darken3: '#c62828',
  darken4: '#b71c1c',
  accent1: '#ff8a80',
  accent2: '#ff5252',
  accent3: '#ff1744',
  accent4: '#d50000'
};
const pink = {
  base: '#e91e63',
  lighten5: '#fce4ec',
  lighten4: '#f8bbd0',
  lighten3: '#f48fb1',
  lighten2: '#f06292',
  lighten1: '#ec407a',
  darken1: '#d81b60',
  darken2: '#c2185b',
  darken3: '#ad1457',
  darken4: '#880e4f',
  accent1: '#ff80ab',
  accent2: '#ff4081',
  accent3: '#f50057',
  accent4: '#c51162'
};
const purple = {
  base: '#9c27b0',
  lighten5: '#f3e5f5',
  lighten4: '#e1bee7',
  lighten3: '#ce93d8',
  lighten2: '#ba68c8',
  lighten1: '#ab47bc',
  darken1: '#8e24aa',
  darken2: '#7b1fa2',
  darken3: '#6a1b9a',
  darken4: '#4a148c',
  accent1: '#ea80fc',
  accent2: '#e040fb',
  accent3: '#d500f9',
  accent4: '#aa00ff'
};
const deepPurple = {
  base: '#673ab7',
  lighten5: '#ede7f6',
  lighten4: '#d1c4e9',
  lighten3: '#b39ddb',
  lighten2: '#9575cd',
  lighten1: '#7e57c2',
  darken1: '#5e35b1',
  darken2: '#512da8',
  darken3: '#4527a0',
  darken4: '#311b92',
  accent1: '#b388ff',
  accent2: '#7c4dff',
  accent3: '#651fff',
  accent4: '#6200ea'
};
const indigo = {
  base: '#3f51b5',
  lighten5: '#e8eaf6',
  lighten4: '#c5cae9',
  lighten3: '#9fa8da',
  lighten2: '#7986cb',
  lighten1: '#5c6bc0',
  darken1: '#3949ab',
  darken2: '#303f9f',
  darken3: '#283593',
  darken4: '#1a237e',
  accent1: '#8c9eff',
  accent2: '#536dfe',
  accent3: '#3d5afe',
  accent4: '#304ffe'
};
const blue = {
  base: '#2196f3',
  lighten5: '#e3f2fd',
  lighten4: '#bbdefb',
  lighten3: '#90caf9',
  lighten2: '#64b5f6',
  lighten1: '#42a5f5',
  darken1: '#1e88e5',
  darken2: '#1976d2',
  darken3: '#1565c0',
  darken4: '#0d47a1',
  accent1: '#82b1ff',
  accent2: '#448aff',
  accent3: '#2979ff',
  accent4: '#2962ff'
};
const lightBlue = {
  base: '#03a9f4',
  lighten5: '#e1f5fe',
  lighten4: '#b3e5fc',
  lighten3: '#81d4fa',
  lighten2: '#4fc3f7',
  lighten1: '#29b6f6',
  darken1: '#039be5',
  darken2: '#0288d1',
  darken3: '#0277bd',
  darken4: '#01579b',
  accent1: '#80d8ff',
  accent2: '#40c4ff',
  accent3: '#00b0ff',
  accent4: '#0091ea'
};
const cyan = {
  base: '#00bcd4',
  lighten5: '#e0f7fa',
  lighten4: '#b2ebf2',
  lighten3: '#80deea',
  lighten2: '#4dd0e1',
  lighten1: '#26c6da',
  darken1: '#00acc1',
  darken2: '#0097a7',
  darken3: '#00838f',
  darken4: '#006064',
  accent1: '#84ffff',
  accent2: '#18ffff',
  accent3: '#00e5ff',
  accent4: '#00b8d4'
};
const teal = {
  base: '#009688',
  lighten5: '#e0f2f1',
  lighten4: '#b2dfdb',
  lighten3: '#80cbc4',
  lighten2: '#4db6ac',
  lighten1: '#26a69a',
  darken1: '#00897b',
  darken2: '#00796b',
  darken3: '#00695c',
  darken4: '#004d40',
  accent1: '#a7ffeb',
  accent2: '#64ffda',
  accent3: '#1de9b6',
  accent4: '#00bfa5'
};
const green = {
  base: '#4caf50',
  lighten5: '#e8f5e9',
  lighten4: '#c8e6c9',
  lighten3: '#a5d6a7',
  lighten2: '#81c784',
  lighten1: '#66bb6a',
  darken1: '#43a047',
  darken2: '#388e3c',
  darken3: '#2e7d32',
  darken4: '#1b5e20',
  accent1: '#b9f6ca',
  accent2: '#69f0ae',
  accent3: '#00e676',
  accent4: '#00c853'
};
const lightGreen = {
  base: '#8bc34a',
  lighten5: '#f1f8e9',
  lighten4: '#dcedc8',
  lighten3: '#c5e1a5',
  lighten2: '#aed581',
  lighten1: '#9ccc65',
  darken1: '#7cb342',
  darken2: '#689f38',
  darken3: '#558b2f',
  darken4: '#33691e',
  accent1: '#ccff90',
  accent2: '#b2ff59',
  accent3: '#76ff03',
  accent4: '#64dd17'
};
const lime = {
  base: '#cddc39',
  lighten5: '#f9fbe7',
  lighten4: '#f0f4c3',
  lighten3: '#e6ee9c',
  lighten2: '#dce775',
  lighten1: '#d4e157',
  darken1: '#c0ca33',
  darken2: '#afb42b',
  darken3: '#9e9d24',
  darken4: '#827717',
  accent1: '#f4ff81',
  accent2: '#eeff41',
  accent3: '#c6ff00',
  accent4: '#aeea00'
};
const yellow = {
  base: '#ffeb3b',
  lighten5: '#fffde7',
  lighten4: '#fff9c4',
  lighten3: '#fff59d',
  lighten2: '#fff176',
  lighten1: '#ffee58',
  darken1: '#fdd835',
  darken2: '#fbc02d',
  darken3: '#f9a825',
  darken4: '#f57f17',
  accent1: '#ffff8d',
  accent2: '#ffff00',
  accent3: '#ffea00',
  accent4: '#ffd600'
};
const amber = {
  base: '#ffc107',
  lighten5: '#fff8e1',
  lighten4: '#ffecb3',
  lighten3: '#ffe082',
  lighten2: '#ffd54f',
  lighten1: '#ffca28',
  darken1: '#ffb300',
  darken2: '#ffa000',
  darken3: '#ff8f00',
  darken4: '#ff6f00',
  accent1: '#ffe57f',
  accent2: '#ffd740',
  accent3: '#ffc400',
  accent4: '#ffab00'
};
const orange = {
  base: '#ff9800',
  lighten5: '#fff3e0',
  lighten4: '#ffe0b2',
  lighten3: '#ffcc80',
  lighten2: '#ffb74d',
  lighten1: '#ffa726',
  darken1: '#fb8c00',
  darken2: '#f57c00',
  darken3: '#ef6c00',
  darken4: '#e65100',
  accent1: '#ffd180',
  accent2: '#ffab40',
  accent3: '#ff9100',
  accent4: '#ff6d00'
};
const deepOrange = {
  base: '#ff5722',
  lighten5: '#fbe9e7',
  lighten4: '#ffccbc',
  lighten3: '#ffab91',
  lighten2: '#ff8a65',
  lighten1: '#ff7043',
  darken1: '#f4511e',
  darken2: '#e64a19',
  darken3: '#d84315',
  darken4: '#bf360c',
  accent1: '#ff9e80',
  accent2: '#ff6e40',
  accent3: '#ff3d00',
  accent4: '#dd2c00'
};
const brown = {
  base: '#795548',
  lighten5: '#efebe9',
  lighten4: '#d7ccc8',
  lighten3: '#bcaaa4',
  lighten2: '#a1887f',
  lighten1: '#8d6e63',
  darken1: '#6d4c41',
  darken2: '#5d4037',
  darken3: '#4e342e',
  darken4: '#3e2723'
};
const blueGrey = {
  base: '#607d8b',
  lighten5: '#eceff1',
  lighten4: '#cfd8dc',
  lighten3: '#b0bec5',
  lighten2: '#90a4ae',
  lighten1: '#78909c',
  darken1: '#546e7a',
  darken2: '#455a64',
  darken3: '#37474f',
  darken4: '#263238'
};
const grey = {
  base: '#9e9e9e',
  lighten5: '#fafafa',
  lighten4: '#f5f5f5',
  lighten3: '#eeeeee',
  lighten2: '#e0e0e0',
  lighten1: '#bdbdbd',
  darken1: '#757575',
  darken2: '#616161',
  darken3: '#424242',
  darken4: '#212121'
};
const shades = {
  black: '#000000',
  white: '#ffffff',
  transparent: '#ffffff00'
};
const colors = {
  red,
  pink,
  purple,
  deepPurple,
  indigo,
  blue,
  lightBlue,
  cyan,
  teal,
  green,
  lightGreen,
  lime,
  yellow,
  amber,
  orange,
  deepOrange,
  brown,
  blueGrey,
  grey,
  shades
};

const {createVNode:_createVNode$19} = await importShared('vue');
const makeVColorPickerSwatchesProps = propsFactory({
  swatches: {
    type: Array,
    default: () => parseDefaultColors(colors)
  },
  disabled: Boolean,
  color: Object,
  maxHeight: [Number, String],
  ...makeComponentProps()
}, 'VColorPickerSwatches');
function parseDefaultColors(colors) {
  return Object.keys(colors).map(key => {
    const color = colors[key];
    return color.base ? [color.base, color.darken4, color.darken3, color.darken2, color.darken1, color.lighten1, color.lighten2, color.lighten3, color.lighten4, color.lighten5] : [color.black, color.white, color.transparent];
  });
}
const VColorPickerSwatches = defineComponent({
  name: 'VColorPickerSwatches',
  props: makeVColorPickerSwatchesProps(),
  emits: {
    'update:color': color => true
  },
  setup(props, _ref) {
    let {
      emit
    } = _ref;
    useRender(() => _createVNode$19("div", {
      "class": ['v-color-picker-swatches', props.class],
      "style": [{
        maxHeight: convertToUnit(props.maxHeight)
      }, props.style]
    }, [_createVNode$19("div", null, [props.swatches.map(swatch => _createVNode$19("div", {
      "class": "v-color-picker-swatches__swatch"
    }, [swatch.map(color => {
      const rgba = parseColor(color);
      const hsva = RGBtoHSV(rgba);
      const background = RGBtoCSS(rgba);
      return _createVNode$19("div", {
        "class": "v-color-picker-swatches__color",
        "onClick": () => hsva && emit('update:color', hsva)
      }, [_createVNode$19("div", {
        "style": {
          background
        }
      }, [props.color && deepEqual(props.color, hsva) ? _createVNode$19(VIcon, {
        "size": "x-small",
        "icon": "$success",
        "color": getContrast(color, '#FFFFFF') > 2 ? 'white' : 'black'
      }, null) : undefined])]);
    })]))])]));
    return {};
  }
});

// Utilities
const VPickerTitle = createSimpleFunctional('v-picker-title');

const {createVNode:_createVNode$18} = await importShared('vue');
const makeVSheetProps = propsFactory({
  color: String,
  ...makeBorderProps(),
  ...makeComponentProps(),
  ...makeDimensionProps(),
  ...makeElevationProps(),
  ...makeLocationProps(),
  ...makePositionProps(),
  ...makeRoundedProps(),
  ...makeTagProps(),
  ...makeThemeProps()
}, 'VSheet');
const VSheet = genericComponent()({
  name: 'VSheet',
  props: makeVSheetProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      themeClasses
    } = provideTheme(props);
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.color);
    const {
      borderClasses
    } = useBorder(props);
    const {
      dimensionStyles
    } = useDimension(props);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      locationStyles
    } = useLocation(props);
    const {
      positionClasses
    } = usePosition(props);
    const {
      roundedClasses
    } = useRounded(props);
    useRender(() => _createVNode$18(props.tag, {
      "class": ['v-sheet', themeClasses.value, backgroundColorClasses.value, borderClasses.value, elevationClasses.value, positionClasses.value, roundedClasses.value, props.class],
      "style": [backgroundColorStyles.value, dimensionStyles.value, locationStyles.value, props.style]
    }, slots));
    return {};
  }
});

const {createVNode:_createVNode$17,mergeProps:_mergeProps$C} = await importShared('vue');
const makeVPickerProps = propsFactory({
  bgColor: String,
  divided: Boolean,
  landscape: Boolean,
  title: String,
  hideHeader: Boolean,
  ...makeVSheetProps()
}, 'VPicker');
const VPicker = genericComponent()({
  name: 'VPicker',
  props: makeVPickerProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.color);
    useRender(() => {
      const sheetProps = VSheet.filterProps(props);
      const hasTitle = !!(props.title || slots.title);
      return _createVNode$17(VSheet, _mergeProps$C(sheetProps, {
        "color": props.bgColor,
        "class": ['v-picker', {
          'v-picker--divided': props.divided,
          'v-picker--landscape': props.landscape,
          'v-picker--with-actions': !!slots.actions
        }, props.class],
        "style": props.style
      }), {
        default: () => [!props.hideHeader && _createVNode$17("div", {
          "key": "header",
          "class": [backgroundColorClasses.value],
          "style": [backgroundColorStyles.value]
        }, [hasTitle && _createVNode$17(VPickerTitle, {
          "key": "picker-title"
        }, {
          default: () => [slots.title?.() ?? props.title]
        }), slots.header && _createVNode$17("div", {
          "class": "v-picker__header"
        }, [slots.header()])]), _createVNode$17("div", {
          "class": "v-picker__body"
        }, [slots.default?.()]), slots.actions && _createVNode$17(VDefaultsProvider, {
          "defaults": {
            VBtn: {
              slim: true,
              variant: 'text'
            }
          }
        }, {
          default: () => [_createVNode$17("div", {
            "class": "v-picker__actions"
          }, [slots.actions()])]
        })]
      });
    });
    return {};
  }
});

const {Fragment:_Fragment$n,createVNode:_createVNode$16,mergeProps:_mergeProps$B} = await importShared('vue');
const {computed: computed$V,onBeforeMount,ref: ref$p,watch: watch$h} = await importShared('vue');
const makeVColorPickerProps = propsFactory({
  canvasHeight: {
    type: [String, Number],
    default: 150
  },
  disabled: Boolean,
  dotSize: {
    type: [Number, String],
    default: 10
  },
  hideCanvas: Boolean,
  hideSliders: Boolean,
  hideInputs: Boolean,
  mode: {
    type: String,
    default: 'rgba',
    validator: v => Object.keys(modes).includes(v)
  },
  modes: {
    type: Array,
    default: () => Object.keys(modes),
    validator: v => Array.isArray(v) && v.every(m => Object.keys(modes).includes(m))
  },
  showSwatches: Boolean,
  swatches: Array,
  swatchesMaxHeight: {
    type: [Number, String],
    default: 150
  },
  modelValue: {
    type: [Object, String]
  },
  ...makeVPickerProps({
    hideHeader: true
  })
}, 'VColorPicker');
const VColorPicker = defineComponent({
  name: 'VColorPicker',
  props: makeVColorPickerProps(),
  emits: {
    'update:modelValue': color => true,
    'update:mode': mode => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const mode = useProxiedModel(props, 'mode');
    const hue = ref$p(null);
    const model = useProxiedModel(props, 'modelValue', undefined, v => {
      if (v == null || v === '') return null;
      let c;
      try {
        c = RGBtoHSV(parseColor(v));
      } catch (err) {
        consoleWarn(err);
        return null;
      }
      return c;
    }, v => {
      if (!v) return null;
      return extractColor(v, props.modelValue);
    });
    const currentColor = computed$V(() => {
      return model.value ? {
        ...model.value,
        h: hue.value ?? model.value.h
      } : null;
    });
    const {
      rtlClasses
    } = useRtl();
    let externalChange = true;
    watch$h(model, v => {
      if (!externalChange) {
        // prevent hue shift from rgb conversion inaccuracy
        externalChange = true;
        return;
      }
      if (!v) return;
      hue.value = v.h;
    }, {
      immediate: true
    });
    const updateColor = hsva => {
      externalChange = false;
      hue.value = hsva.h;
      model.value = hsva;
    };
    onBeforeMount(() => {
      if (!props.modes.includes(mode.value)) mode.value = props.modes[0];
    });
    provideDefaults({
      VSlider: {
        color: undefined,
        trackColor: undefined,
        trackFillColor: undefined
      }
    });
    useRender(() => {
      const pickerProps = VPicker.filterProps(props);
      return _createVNode$16(VPicker, _mergeProps$B(pickerProps, {
        "class": ['v-color-picker', rtlClasses.value, props.class],
        "style": [{
          '--v-color-picker-color-hsv': HSVtoCSS({
            ...(currentColor.value ?? nullColor),
            a: 1
          })
        }, props.style]
      }), {
        ...slots,
        default: () => _createVNode$16(_Fragment$n, null, [!props.hideCanvas && _createVNode$16(VColorPickerCanvas, {
          "key": "canvas",
          "color": currentColor.value,
          "onUpdate:color": updateColor,
          "disabled": props.disabled,
          "dotSize": props.dotSize,
          "width": props.width,
          "height": props.canvasHeight
        }, null), (!props.hideSliders || !props.hideInputs) && _createVNode$16("div", {
          "key": "controls",
          "class": "v-color-picker__controls"
        }, [!props.hideSliders && _createVNode$16(VColorPickerPreview, {
          "key": "preview",
          "color": currentColor.value,
          "onUpdate:color": updateColor,
          "hideAlpha": !mode.value.endsWith('a'),
          "disabled": props.disabled
        }, null), !props.hideInputs && _createVNode$16(VColorPickerEdit, {
          "key": "edit",
          "modes": props.modes,
          "mode": mode.value,
          "onUpdate:mode": m => mode.value = m,
          "color": currentColor.value,
          "onUpdate:color": updateColor,
          "disabled": props.disabled
        }, null)]), props.showSwatches && _createVNode$16(VColorPickerSwatches, {
          "key": "swatches",
          "color": currentColor.value,
          "onUpdate:color": updateColor,
          "maxHeight": props.swatchesMaxHeight,
          "swatches": props.swatches,
          "disabled": props.disabled
        }, null)])
      });
    });
    return {};
  }
});

const {Fragment:_Fragment$m,createVNode:_createVNode$15,mergeProps:_mergeProps$A,createTextVNode:_createTextVNode$4} = await importShared('vue');
const {computed: computed$U,mergeProps: mergeProps$5,nextTick: nextTick$b,ref: ref$o,shallowRef: shallowRef$j,toRef: toRef$q,watch: watch$g} = await importShared('vue');
const makeVComboboxProps = propsFactory({
  autoSelectFirst: {
    type: [Boolean, String]
  },
  clearOnSelect: {
    type: Boolean,
    default: true
  },
  delimiters: Array,
  ...makeFilterProps({
    filterKeys: ['title']
  }),
  ...makeSelectProps({
    hideNoData: true,
    returnObject: true
  }),
  ...omit(makeVTextFieldProps({
    modelValue: null,
    role: 'combobox'
  }), ['validationValue', 'dirty', 'appendInnerIcon']),
  ...makeTransitionProps({
    transition: false
  })
}, 'VCombobox');
const VCombobox = genericComponent()({
  name: 'VCombobox',
  props: makeVComboboxProps(),
  emits: {
    'update:focused': focused => true,
    'update:modelValue': value => true,
    'update:search': value => true,
    'update:menu': value => true
  },
  setup(props, _ref) {
    let {
      emit,
      slots
    } = _ref;
    const {
      t
    } = useLocale();
    const vTextFieldRef = ref$o();
    const isFocused = shallowRef$j(false);
    const isPristine = shallowRef$j(true);
    const listHasFocus = shallowRef$j(false);
    const vMenuRef = ref$o();
    const vVirtualScrollRef = ref$o();
    const selectionIndex = shallowRef$j(-1);
    let cleared = false;
    const {
      items,
      transformIn,
      transformOut
    } = useItems(props);
    const {
      textColorClasses,
      textColorStyles
    } = useTextColor(() => vTextFieldRef.value?.color);
    const model = useProxiedModel(props, 'modelValue', [], v => transformIn(wrapInArray(v)), v => {
      const transformed = transformOut(v);
      return props.multiple ? transformed : transformed[0] ?? null;
    });
    const form = useForm(props);
    const hasChips = computed$U(() => !!(props.chips || slots.chip));
    const hasSelectionSlot = computed$U(() => hasChips.value || !!slots.selection);
    const _search = shallowRef$j(!props.multiple && !hasSelectionSlot.value ? model.value[0]?.title ?? '' : '');
    const search = computed$U({
      get: () => {
        return _search.value;
      },
      set: val => {
        _search.value = val ?? '';
        if (!props.multiple && !hasSelectionSlot.value) {
          model.value = [transformItem$3(props, val)];
        }
        if (val && props.multiple && props.delimiters?.length) {
          const values = val.split(new RegExp(`(?:${props.delimiters.join('|')})+`));
          if (values.length > 1) {
            values.forEach(v => {
              v = v.trim();
              if (v) select(transformItem$3(props, v));
            });
            _search.value = '';
          }
        }
        if (!val) selectionIndex.value = -1;
        isPristine.value = !val;
      }
    });
    const counterValue = computed$U(() => {
      return typeof props.counterValue === 'function' ? props.counterValue(model.value) : typeof props.counterValue === 'number' ? props.counterValue : props.multiple ? model.value.length : search.value.length;
    });
    const {
      filteredItems,
      getMatches
    } = useFilter(props, items, () => isPristine.value ? '' : search.value);
    const displayItems = computed$U(() => {
      if (props.hideSelected) {
        return filteredItems.value.filter(filteredItem => !model.value.some(s => s.value === filteredItem.value));
      }
      return filteredItems.value;
    });
    const menuDisabled = computed$U(() => props.hideNoData && !displayItems.value.length || form.isReadonly.value || form.isDisabled.value);
    const _menu = useProxiedModel(props, 'menu');
    const menu = computed$U({
      get: () => _menu.value,
      set: v => {
        if (_menu.value && !v && vMenuRef.value?.ΨopenChildren.size) return;
        if (v && menuDisabled.value) return;
        _menu.value = v;
      }
    });
    const label = toRef$q(() => menu.value ? props.closeText : props.openText);
    watch$g(_search, value => {
      if (cleared) {
        // wait for clear to finish, VTextField sets _search to null
        // then search computed triggers and updates _search to ''
        nextTick$b(() => cleared = false);
      } else if (isFocused.value && !menu.value) {
        menu.value = true;
      }
      emit('update:search', value);
    });
    watch$g(model, value => {
      if (!props.multiple && !hasSelectionSlot.value) {
        _search.value = value[0]?.title ?? '';
      }
    });
    const selectedValues = computed$U(() => model.value.map(selection => selection.value));
    const highlightFirst = computed$U(() => {
      const selectFirst = props.autoSelectFirst === true || props.autoSelectFirst === 'exact' && search.value === displayItems.value[0]?.title;
      return selectFirst && displayItems.value.length > 0 && !isPristine.value && !listHasFocus.value;
    });
    const listRef = ref$o();
    const listEvents = useScrolling(listRef, vTextFieldRef);
    function onClear(e) {
      cleared = true;
      if (props.openOnClear) {
        menu.value = true;
      }
    }
    function onMousedownControl() {
      if (menuDisabled.value) return;
      menu.value = true;
    }
    function onMousedownMenuIcon(e) {
      if (menuDisabled.value) return;
      if (isFocused.value) {
        e.preventDefault();
        e.stopPropagation();
      }
      menu.value = !menu.value;
    }
    function onListKeydown(e) {
      if (e.key !== ' ' && checkPrintable(e)) {
        vTextFieldRef.value?.focus();
      }
    }
    // eslint-disable-next-line complexity
    function onKeydown(e) {
      if (isComposingIgnoreKey(e) || form.isReadonly.value) return;
      const selectionStart = vTextFieldRef.value?.selectionStart;
      const length = model.value.length;
      if (['Enter', 'ArrowDown', 'ArrowUp'].includes(e.key)) {
        e.preventDefault();
      }
      if (['Enter', 'ArrowDown'].includes(e.key)) {
        menu.value = true;
      }
      if (['Escape'].includes(e.key)) {
        menu.value = false;
      }
      if (['Enter', 'Escape', 'Tab'].includes(e.key)) {
        if (highlightFirst.value && ['Enter', 'Tab'].includes(e.key) && !model.value.some(_ref2 => {
          let {
            value
          } = _ref2;
          return value === displayItems.value[0].value;
        })) {
          select(filteredItems.value[0]);
        }
        isPristine.value = true;
      }
      if (e.key === 'ArrowDown' && highlightFirst.value) {
        listRef.value?.focus('next');
      }
      if (e.key === 'Enter' && search.value) {
        select(transformItem$3(props, search.value));
        if (hasSelectionSlot.value) _search.value = '';
      }
      if (['Backspace', 'Delete'].includes(e.key)) {
        if (!props.multiple && hasSelectionSlot.value && model.value.length > 0 && !search.value) return select(model.value[0], false);
        if (~selectionIndex.value) {
          e.preventDefault();
          const originalSelectionIndex = selectionIndex.value;
          select(model.value[selectionIndex.value], false);
          selectionIndex.value = originalSelectionIndex >= length - 1 ? length - 2 : originalSelectionIndex;
        } else if (e.key === 'Backspace' && !search.value) {
          selectionIndex.value = length - 1;
        }
        return;
      }
      if (!props.multiple) return;
      if (e.key === 'ArrowLeft') {
        if (selectionIndex.value < 0 && selectionStart && selectionStart > 0) return;
        const prev = selectionIndex.value > -1 ? selectionIndex.value - 1 : length - 1;
        if (model.value[prev]) {
          selectionIndex.value = prev;
        } else {
          selectionIndex.value = -1;
          vTextFieldRef.value?.setSelectionRange(search.value.length, search.value.length);
        }
      } else if (e.key === 'ArrowRight') {
        if (selectionIndex.value < 0) return;
        const next = selectionIndex.value + 1;
        if (model.value[next]) {
          selectionIndex.value = next;
        } else {
          selectionIndex.value = -1;
          vTextFieldRef.value?.setSelectionRange(0, 0);
        }
      } else if (~selectionIndex.value && checkPrintable(e)) {
        selectionIndex.value = -1;
      }
    }
    function onAfterEnter() {
      if (props.eager) {
        vVirtualScrollRef.value?.calculateVisibleItems();
      }
    }
    function onAfterLeave() {
      if (isFocused.value) {
        isPristine.value = true;
        vTextFieldRef.value?.focus();
      }
    }
    /** @param set - null means toggle */
    function select(item) {
      let set = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : true;
      if (!item || item.props.disabled) return;
      if (props.multiple) {
        const index = model.value.findIndex(selection => (props.valueComparator || deepEqual)(selection.value, item.value));
        const add = set == null ? !~index : set;
        if (~index) {
          const value = add ? [...model.value, item] : [...model.value];
          value.splice(index, 1);
          model.value = value;
        } else if (add) {
          model.value = [...model.value, item];
        }
        if (props.clearOnSelect) {
          search.value = '';
        }
      } else {
        const add = set !== false;
        model.value = add ? [item] : [];
        _search.value = add && !hasSelectionSlot.value ? item.title : '';

        // watch for search watcher to trigger
        nextTick$b(() => {
          menu.value = false;
          isPristine.value = true;
        });
      }
    }
    function onFocusin(e) {
      isFocused.value = true;
      setTimeout(() => {
        listHasFocus.value = true;
      });
    }
    function onFocusout(e) {
      listHasFocus.value = false;
    }
    function onUpdateModelValue(v) {
      if (v == null || v === '' && !props.multiple && !hasSelectionSlot.value) model.value = [];
    }
    watch$g(isFocused, (val, oldVal) => {
      if (val || val === oldVal) return;
      selectionIndex.value = -1;
      menu.value = false;
      if (search.value) {
        if (props.multiple) {
          select(transformItem$3(props, search.value));
          return;
        }
        if (!hasSelectionSlot.value) return;
        if (model.value.some(_ref3 => {
          let {
            title
          } = _ref3;
          return title === search.value;
        })) {
          _search.value = '';
        } else {
          select(transformItem$3(props, search.value));
        }
      }
    });
    watch$g(menu, () => {
      if (!props.hideSelected && menu.value && model.value.length) {
        const index = displayItems.value.findIndex(item => model.value.some(s => (props.valueComparator || deepEqual)(s.value, item.value)));
        IN_BROWSER && window.requestAnimationFrame(() => {
          index >= 0 && vVirtualScrollRef.value?.scrollToIndex(index);
        });
      }
    });
    watch$g(() => props.items, (newVal, oldVal) => {
      if (menu.value) return;
      if (isFocused.value && !oldVal.length && newVal.length) {
        menu.value = true;
      }
    });
    useRender(() => {
      const hasList = !!(!props.hideNoData || displayItems.value.length || slots['prepend-item'] || slots['append-item'] || slots['no-data']);
      const isDirty = model.value.length > 0;
      const textFieldProps = VTextField.filterProps(props);
      return _createVNode$15(VTextField, _mergeProps$A({
        "ref": vTextFieldRef
      }, textFieldProps, {
        "modelValue": search.value,
        "onUpdate:modelValue": [$event => search.value = $event, onUpdateModelValue],
        "focused": isFocused.value,
        "onUpdate:focused": $event => isFocused.value = $event,
        "validationValue": model.externalValue,
        "counterValue": counterValue.value,
        "dirty": isDirty,
        "class": ['v-combobox', {
          'v-combobox--active-menu': menu.value,
          'v-combobox--chips': !!props.chips,
          'v-combobox--selection-slot': !!hasSelectionSlot.value,
          'v-combobox--selecting-index': selectionIndex.value > -1,
          [`v-combobox--${props.multiple ? 'multiple' : 'single'}`]: true
        }, props.class],
        "style": props.style,
        "readonly": form.isReadonly.value,
        "placeholder": isDirty ? undefined : props.placeholder,
        "onClick:clear": onClear,
        "onMousedown:control": onMousedownControl,
        "onKeydown": onKeydown
      }), {
        ...slots,
        default: () => _createVNode$15(_Fragment$m, null, [_createVNode$15(VMenu, _mergeProps$A({
          "ref": vMenuRef,
          "modelValue": menu.value,
          "onUpdate:modelValue": $event => menu.value = $event,
          "activator": "parent",
          "contentClass": "v-combobox__content",
          "disabled": menuDisabled.value,
          "eager": props.eager,
          "maxHeight": 310,
          "openOnClick": false,
          "closeOnContentClick": false,
          "transition": props.transition,
          "onAfterEnter": onAfterEnter,
          "onAfterLeave": onAfterLeave
        }, props.menuProps), {
          default: () => [hasList && _createVNode$15(VList, _mergeProps$A({
            "ref": listRef,
            "selected": selectedValues.value,
            "selectStrategy": props.multiple ? 'independent' : 'single-independent',
            "onMousedown": e => e.preventDefault(),
            "onKeydown": onListKeydown,
            "onFocusin": onFocusin,
            "onFocusout": onFocusout,
            "tabindex": "-1",
            "aria-live": "polite",
            "color": props.itemColor ?? props.color
          }, listEvents, props.listProps), {
            default: () => [slots['prepend-item']?.(), !displayItems.value.length && !props.hideNoData && (slots['no-data']?.() ?? _createVNode$15(VListItem, {
              "key": "no-data",
              "title": t(props.noDataText)
            }, null)), _createVNode$15(VVirtualScroll, {
              "ref": vVirtualScrollRef,
              "renderless": true,
              "items": displayItems.value,
              "itemKey": "value"
            }, {
              default: _ref4 => {
                let {
                  item,
                  index,
                  itemRef
                } = _ref4;
                const itemProps = mergeProps$5(item.props, {
                  ref: itemRef,
                  key: item.value,
                  active: highlightFirst.value && index === 0 ? true : undefined,
                  onClick: () => select(item, null)
                });
                return slots.item?.({
                  item,
                  index,
                  props: itemProps
                }) ?? _createVNode$15(VListItem, _mergeProps$A(itemProps, {
                  "role": "option"
                }), {
                  prepend: _ref5 => {
                    let {
                      isSelected
                    } = _ref5;
                    return _createVNode$15(_Fragment$m, null, [props.multiple && !props.hideSelected ? _createVNode$15(VCheckboxBtn, {
                      "key": item.value,
                      "modelValue": isSelected,
                      "ripple": false,
                      "tabindex": "-1"
                    }, null) : undefined, item.props.prependAvatar && _createVNode$15(VAvatar, {
                      "image": item.props.prependAvatar
                    }, null), item.props.prependIcon && _createVNode$15(VIcon, {
                      "icon": item.props.prependIcon
                    }, null)]);
                  },
                  title: () => {
                    return isPristine.value ? item.title : highlightResult('v-combobox', item.title, getMatches(item)?.title);
                  }
                });
              }
            }), slots['append-item']?.()]
          })]
        }), model.value.map((item, index) => {
          function onChipClose(e) {
            e.stopPropagation();
            e.preventDefault();
            select(item, false);
          }
          const slotProps = {
            'onClick:close': onChipClose,
            onKeydown(e) {
              if (e.key !== 'Enter' && e.key !== ' ') return;
              e.preventDefault();
              e.stopPropagation();
              onChipClose(e);
            },
            onMousedown(e) {
              e.preventDefault();
              e.stopPropagation();
            },
            modelValue: true,
            'onUpdate:modelValue': undefined
          };
          const hasSlot = hasChips.value ? !!slots.chip : !!slots.selection;
          const slotContent = hasSlot ? ensureValidVNode(hasChips.value ? slots.chip({
            item,
            index,
            props: slotProps
          }) : slots.selection({
            item,
            index
          })) : undefined;
          if (hasSlot && !slotContent) return undefined;
          return _createVNode$15("div", {
            "key": item.value,
            "class": ['v-combobox__selection', index === selectionIndex.value && ['v-combobox__selection--selected', textColorClasses.value]],
            "style": index === selectionIndex.value ? textColorStyles.value : {}
          }, [hasChips.value ? !slots.chip ? _createVNode$15(VChip, _mergeProps$A({
            "key": "chip",
            "closable": props.closableChips,
            "size": "small",
            "text": item.title,
            "disabled": item.props.disabled
          }, slotProps), null) : _createVNode$15(VDefaultsProvider, {
            "key": "chip-defaults",
            "defaults": {
              VChip: {
                closable: props.closableChips,
                size: 'small',
                text: item.title
              }
            }
          }, {
            default: () => [slotContent]
          }) : slotContent ?? _createVNode$15("span", {
            "class": "v-combobox__selection-text"
          }, [item.title, props.multiple && index < model.value.length - 1 && _createVNode$15("span", {
            "class": "v-combobox__selection-comma"
          }, [_createTextVNode$4(",")])])]);
        })]),
        'append-inner': function () {
          for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
            args[_key] = arguments[_key];
          }
          return _createVNode$15(_Fragment$m, null, [slots['append-inner']?.(...args), (!props.hideNoData || props.items.length) && props.menuIcon ? _createVNode$15(VIcon, {
            "class": "v-combobox__menu-icon",
            "color": vTextFieldRef.value?.fieldIconColor,
            "icon": props.menuIcon,
            "onMousedown": onMousedownMenuIcon,
            "onClick": noop,
            "aria-label": t(label.value),
            "title": t(label.value),
            "tabindex": "-1"
          }, null) : undefined]);
        }
      });
    });
    return forwardRefs({
      isFocused,
      isPristine,
      menu,
      search,
      selectionIndex,
      filteredItems,
      select
    }, vTextFieldRef);
  }
});

const {Fragment:_Fragment$l,mergeProps:_mergeProps$z,createVNode:_createVNode$14} = await importShared('vue');
const {computed: computed$T,ref: ref$n,toRaw,watchEffect: watchEffect$a} = await importShared('vue');
const makeVConfirmEditProps = propsFactory({
  modelValue: null,
  color: String,
  cancelText: {
    type: String,
    default: '$vuetify.confirmEdit.cancel'
  },
  okText: {
    type: String,
    default: '$vuetify.confirmEdit.ok'
  },
  disabled: {
    type: [Boolean, Array],
    default: undefined
  },
  hideActions: Boolean
}, 'VConfirmEdit');
const VConfirmEdit = genericComponent()({
  name: 'VConfirmEdit',
  props: makeVConfirmEditProps(),
  emits: {
    cancel: () => true,
    save: value => true,
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      emit,
      slots
    } = _ref;
    const model = useProxiedModel(props, 'modelValue');
    const internalModel = ref$n();
    watchEffect$a(() => {
      internalModel.value = structuredClone(toRaw(model.value));
    });
    const {
      t
    } = useLocale();
    const isPristine = computed$T(() => {
      return deepEqual(model.value, internalModel.value);
    });
    function isActionDisabled(action) {
      if (typeof props.disabled === 'boolean') {
        return props.disabled;
      }
      if (Array.isArray(props.disabled)) {
        return props.disabled.includes(action);
      }
      return isPristine.value;
    }
    const isSaveDisabled = computed$T(() => isActionDisabled('save'));
    const isCancelDisabled = computed$T(() => isActionDisabled('cancel'));
    function save() {
      model.value = internalModel.value;
      emit('save', internalModel.value);
    }
    function cancel() {
      internalModel.value = structuredClone(toRaw(model.value));
      emit('cancel');
    }
    function actions(actionsProps) {
      return _createVNode$14(_Fragment$l, null, [_createVNode$14(VBtn, _mergeProps$z({
        "disabled": isCancelDisabled.value,
        "variant": "text",
        "color": props.color,
        "onClick": cancel,
        "text": t(props.cancelText)
      }, actionsProps), null), _createVNode$14(VBtn, _mergeProps$z({
        "disabled": isSaveDisabled.value,
        "variant": "text",
        "color": props.color,
        "onClick": save,
        "text": t(props.okText)
      }, actionsProps), null)]);
    }
    let actionsUsed = false;
    useRender(() => {
      return _createVNode$14(_Fragment$l, null, [slots.default?.({
        model: internalModel,
        save,
        cancel,
        isPristine: isPristine.value,
        get actions() {
          actionsUsed = true;
          return actions;
        }
      }), !props.hideActions && !actionsUsed && actions()]);
    });
    return {
      save,
      cancel,
      isPristine
    };
  }
});

const {inject: inject$a,provide: provide$7,toRef: toRef$p} = await importShared('vue');
const makeDataTableExpandProps = propsFactory({
  expandOnClick: Boolean,
  showExpand: Boolean,
  expanded: {
    type: Array,
    default: () => []
  }
}, 'DataTable-expand');
const VDataTableExpandedKey = Symbol.for('vuetify:datatable:expanded');
function provideExpanded(props) {
  const expandOnClick = toRef$p(() => props.expandOnClick);
  const expanded = useProxiedModel(props, 'expanded', props.expanded, v => {
    return new Set(v);
  }, v => {
    return [...v.values()];
  });
  function expand(item, value) {
    const newExpanded = new Set(expanded.value);
    if (!value) {
      newExpanded.delete(item.value);
    } else {
      newExpanded.add(item.value);
    }
    expanded.value = newExpanded;
  }
  function isExpanded(item) {
    return expanded.value.has(item.value);
  }
  function toggleExpand(item) {
    expand(item, !isExpanded(item));
  }
  const data = {
    expand,
    expanded,
    expandOnClick,
    isExpanded,
    toggleExpand
  };
  provide$7(VDataTableExpandedKey, data);
  return data;
}
function useExpanded() {
  const data = inject$a(VDataTableExpandedKey);
  if (!data) throw new Error('foo');
  return data;
}

const {computed: computed$S,inject: inject$9,provide: provide$6,ref: ref$m} = await importShared('vue');
const makeDataTableGroupProps = propsFactory({
  groupBy: {
    type: Array,
    default: () => []
  }
}, 'DataTable-group');
const VDataTableGroupSymbol = Symbol.for('vuetify:data-table-group');
function createGroupBy(props) {
  const groupBy = useProxiedModel(props, 'groupBy');
  return {
    groupBy
  };
}
function provideGroupBy(options) {
  const {
    disableSort,
    groupBy,
    sortBy
  } = options;
  const opened = ref$m(new Set());
  const sortByWithGroups = computed$S(() => {
    return groupBy.value.map(val => ({
      ...val,
      order: val.order ?? false
    })).concat(disableSort?.value ? [] : sortBy.value);
  });
  function isGroupOpen(group) {
    return opened.value.has(group.id);
  }
  function toggleGroup(group) {
    const newOpened = new Set(opened.value);
    if (!isGroupOpen(group)) newOpened.add(group.id);else newOpened.delete(group.id);
    opened.value = newOpened;
  }
  function extractRows(items) {
    function dive(group) {
      const arr = [];
      for (const item of group.items) {
        if ('type' in item && item.type === 'group') {
          arr.push(...dive(item));
        } else {
          arr.push(item);
        }
      }
      return [...new Set(arr)];
    }
    return dive({
      items});
  }

  // onBeforeMount(() => {
  //   for (const key of groupedItems.value.keys()) {
  //     opened.value.add(key)
  //   }
  // })

  const data = {
    sortByWithGroups,
    toggleGroup,
    opened,
    groupBy,
    extractRows,
    isGroupOpen
  };
  provide$6(VDataTableGroupSymbol, data);
  return data;
}
function useGroupBy() {
  const data = inject$9(VDataTableGroupSymbol);
  if (!data) throw new Error('Missing group!');
  return data;
}
function groupItemsByProperty(items, groupBy) {
  if (!items.length) return [];
  const groups = new Map();
  for (const item of items) {
    const value = getObjectValueByPath(item.raw, groupBy);
    if (!groups.has(value)) {
      groups.set(value, []);
    }
    groups.get(value).push(item);
  }
  return groups;
}
function groupItems(items, groupBy) {
  let depth = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : 0;
  let prefix = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : 'root';
  if (!groupBy.length) return [];
  const groupedItems = groupItemsByProperty(items, groupBy[0]);
  const groups = [];
  const rest = groupBy.slice(1);
  groupedItems.forEach((items, value) => {
    const key = groupBy[0];
    const id = `${prefix}_${key}_${value}`;
    groups.push({
      depth,
      id,
      key,
      value,
      items: rest.length ? groupItems(items, rest, depth + 1, id) : items,
      type: 'group'
    });
  });
  return groups;
}
function flattenItems(items, opened) {
  const flatItems = [];
  for (const item of items) {
    // TODO: make this better
    if ('type' in item && item.type === 'group') {
      if (item.value != null) {
        flatItems.push(item);
      }
      if (opened.has(item.id) || item.value == null) {
        flatItems.push(...flattenItems(item.items, opened));
      }
    } else {
      flatItems.push(item);
    }
  }
  return flatItems;
}
function useGroupedItems(items, groupBy, opened) {
  const flatItems = computed$S(() => {
    if (!groupBy.value.length) return items.value;
    const groupedItems = groupItems(items.value, groupBy.value.map(item => item.key));
    return flattenItems(groupedItems, opened.value);
  });
  return {
    flatItems
  };
}

// Utilities
const {watch: watch$f} = await importShared('vue');
function useOptions(_ref) {
  let {
    page,
    itemsPerPage,
    sortBy,
    groupBy,
    search
  } = _ref;
  const vm = getCurrentInstance('VDataTable');
  const options = () => ({
    page: page.value,
    itemsPerPage: itemsPerPage.value,
    sortBy: sortBy.value,
    groupBy: groupBy.value,
    search: search.value
  });
  let oldOptions = null;
  watch$f(options, value => {
    if (deepEqual(oldOptions, value)) return;

    // Reset page when searching
    if (oldOptions && oldOptions.search !== value.search) {
      page.value = 1;
    }
    vm.emit('update:options', value);
    oldOptions = value;
  }, {
    deep: true,
    immediate: true
  });
}

const {computed: computed$R,inject: inject$8,provide: provide$5,watch: watch$e} = await importShared('vue');
const makeDataTablePaginateProps = propsFactory({
  page: {
    type: [Number, String],
    default: 1
  },
  itemsPerPage: {
    type: [Number, String],
    default: 10
  }
}, 'DataTable-paginate');
const VDataTablePaginationSymbol = Symbol.for('vuetify:data-table-pagination');
function createPagination(props) {
  const page = useProxiedModel(props, 'page', undefined, value => Number(value ?? 1));
  const itemsPerPage = useProxiedModel(props, 'itemsPerPage', undefined, value => Number(value ?? 10));
  return {
    page,
    itemsPerPage
  };
}
function providePagination(options) {
  const {
    page,
    itemsPerPage,
    itemsLength
  } = options;
  const startIndex = computed$R(() => {
    if (itemsPerPage.value === -1) return 0;
    return itemsPerPage.value * (page.value - 1);
  });
  const stopIndex = computed$R(() => {
    if (itemsPerPage.value === -1) return itemsLength.value;
    return Math.min(itemsLength.value, startIndex.value + itemsPerPage.value);
  });
  const pageCount = computed$R(() => {
    if (itemsPerPage.value === -1 || itemsLength.value === 0) return 1;
    return Math.ceil(itemsLength.value / itemsPerPage.value);
  });

  // Don't run immediately, items may not have been loaded yet: #17966
  watch$e([page, pageCount], () => {
    if (page.value > pageCount.value) {
      page.value = pageCount.value;
    }
  });
  function setItemsPerPage(value) {
    itemsPerPage.value = value;
    page.value = 1;
  }
  function nextPage() {
    page.value = clamp(page.value + 1, 1, pageCount.value);
  }
  function prevPage() {
    page.value = clamp(page.value - 1, 1, pageCount.value);
  }
  function setPage(value) {
    page.value = clamp(value, 1, pageCount.value);
  }
  const data = {
    page,
    itemsPerPage,
    startIndex,
    stopIndex,
    pageCount,
    itemsLength,
    nextPage,
    prevPage,
    setPage,
    setItemsPerPage
  };
  provide$5(VDataTablePaginationSymbol, data);
  return data;
}
function usePagination() {
  const data = inject$8(VDataTablePaginationSymbol);
  if (!data) throw new Error('Missing pagination!');
  return data;
}
function usePaginatedItems(options) {
  const vm = getCurrentInstance('usePaginatedItems');
  const {
    items,
    startIndex,
    stopIndex,
    itemsPerPage
  } = options;
  const paginatedItems = computed$R(() => {
    if (itemsPerPage.value <= 0) return items.value;
    return items.value.slice(startIndex.value, stopIndex.value);
  });
  watch$e(paginatedItems, val => {
    vm.emit('update:currentItems', val);
  }, {
    immediate: true
  });
  return {
    paginatedItems
  };
}

const {computed: computed$Q,inject: inject$7,provide: provide$4,shallowRef: shallowRef$i,toRef: toRef$o} = await importShared('vue');
const singleSelectStrategy = {
  showSelectAll: false,
  allSelected: () => [],
  select: _ref => {
    let {
      items,
      value
    } = _ref;
    return new Set(value ? [items[0]?.value] : []);
  },
  selectAll: _ref2 => {
    let {
      selected
    } = _ref2;
    return selected;
  }
};
const pageSelectStrategy = {
  showSelectAll: true,
  allSelected: _ref3 => {
    let {
      currentPage
    } = _ref3;
    return currentPage;
  },
  select: _ref4 => {
    let {
      items,
      value,
      selected
    } = _ref4;
    for (const item of items) {
      if (value) selected.add(item.value);else selected.delete(item.value);
    }
    return selected;
  },
  selectAll: _ref5 => {
    let {
      value,
      currentPage,
      selected
    } = _ref5;
    return pageSelectStrategy.select({
      items: currentPage,
      value,
      selected
    });
  }
};
const allSelectStrategy = {
  showSelectAll: true,
  allSelected: _ref6 => {
    let {
      allItems
    } = _ref6;
    return allItems;
  },
  select: _ref7 => {
    let {
      items,
      value,
      selected
    } = _ref7;
    for (const item of items) {
      if (value) selected.add(item.value);else selected.delete(item.value);
    }
    return selected;
  },
  selectAll: _ref8 => {
    let {
      value,
      allItems,
      selected
    } = _ref8;
    return allSelectStrategy.select({
      items: allItems,
      value,
      selected
    });
  }
};
const makeDataTableSelectProps = propsFactory({
  showSelect: Boolean,
  selectStrategy: {
    type: [String, Object],
    default: 'page'
  },
  modelValue: {
    type: Array,
    default: () => []
  },
  valueComparator: {
    type: Function,
    default: deepEqual
  }
}, 'DataTable-select');
const VDataTableSelectionSymbol = Symbol.for('vuetify:data-table-selection');
function provideSelection(props, _ref9) {
  let {
    allItems,
    currentPage
  } = _ref9;
  const selected = useProxiedModel(props, 'modelValue', props.modelValue, v => {
    return new Set(wrapInArray(v).map(v => {
      return allItems.value.find(item => props.valueComparator(v, item.value))?.value ?? v;
    }));
  }, v => {
    return [...v.values()];
  });
  const allSelectable = computed$Q(() => allItems.value.filter(item => item.selectable));
  const currentPageSelectable = computed$Q(() => currentPage.value.filter(item => item.selectable));
  const selectStrategy = computed$Q(() => {
    if (typeof props.selectStrategy === 'object') return props.selectStrategy;
    switch (props.selectStrategy) {
      case 'single':
        return singleSelectStrategy;
      case 'all':
        return allSelectStrategy;
      case 'page':
      default:
        return pageSelectStrategy;
    }
  });
  const lastSelectedIndex = shallowRef$i(null);
  function isSelected(items) {
    return wrapInArray(items).every(item => selected.value.has(item.value));
  }
  function isSomeSelected(items) {
    return wrapInArray(items).some(item => selected.value.has(item.value));
  }
  function select(items, value) {
    const newSelected = selectStrategy.value.select({
      items,
      value,
      selected: new Set(selected.value)
    });
    selected.value = newSelected;
  }
  function toggleSelect(item, index, event) {
    const items = [];
    index = index ?? currentPage.value.findIndex(i => i.value === item.value);
    if (props.selectStrategy !== 'single' && event?.shiftKey && lastSelectedIndex.value !== null) {
      const [start, end] = [lastSelectedIndex.value, index].sort((a, b) => a - b);
      items.push(...currentPage.value.slice(start, end + 1).filter(item => item.selectable));
    } else {
      items.push(item);
      lastSelectedIndex.value = index;
    }
    select(items, !isSelected([item]));
  }
  function selectAll(value) {
    const newSelected = selectStrategy.value.selectAll({
      value,
      allItems: allSelectable.value,
      currentPage: currentPageSelectable.value,
      selected: new Set(selected.value)
    });
    selected.value = newSelected;
  }
  const someSelected = computed$Q(() => selected.value.size > 0);
  const allSelected = computed$Q(() => {
    const items = selectStrategy.value.allSelected({
      allItems: allSelectable.value,
      currentPage: currentPageSelectable.value
    });
    return !!items.length && isSelected(items);
  });
  const showSelectAll = toRef$o(() => selectStrategy.value.showSelectAll);
  const data = {
    toggleSelect,
    select,
    selectAll,
    isSelected,
    isSomeSelected,
    someSelected,
    allSelected,
    showSelectAll,
    lastSelectedIndex,
    selectStrategy
  };
  provide$4(VDataTableSelectionSymbol, data);
  return data;
}
function useSelection() {
  const data = inject$7(VDataTableSelectionSymbol);
  if (!data) throw new Error('Missing selection!');
  return data;
}

const {computed: computed$P,inject: inject$6,provide: provide$3,toRef: toRef$n} = await importShared('vue');
const makeDataTableSortProps = propsFactory({
  sortBy: {
    type: Array,
    default: () => []
  },
  customKeySort: Object,
  multiSort: Boolean,
  mustSort: Boolean
}, 'DataTable-sort');
const VDataTableSortSymbol = Symbol.for('vuetify:data-table-sort');
function createSort(props) {
  const sortBy = useProxiedModel(props, 'sortBy');
  const mustSort = toRef$n(() => props.mustSort);
  const multiSort = toRef$n(() => props.multiSort);
  return {
    sortBy,
    mustSort,
    multiSort
  };
}
function provideSort(options) {
  const {
    sortBy,
    mustSort,
    multiSort,
    page
  } = options;
  const toggleSort = column => {
    if (column.key == null) return;
    let newSortBy = sortBy.value.map(x => ({
      ...x
    })) ?? [];
    const item = newSortBy.find(x => x.key === column.key);
    if (!item) {
      if (multiSort.value) {
        newSortBy.push({
          key: column.key,
          order: 'asc'
        });
      } else {
        newSortBy = [{
          key: column.key,
          order: 'asc'
        }];
      }
    } else if (item.order === 'desc') {
      if (mustSort.value && newSortBy.length === 1) {
        item.order = 'asc';
      } else {
        newSortBy = newSortBy.filter(x => x.key !== column.key);
      }
    } else {
      item.order = 'desc';
    }
    sortBy.value = newSortBy;
    if (page) page.value = 1;
  };
  function isSorted(column) {
    return !!sortBy.value.find(item => item.key === column.key);
  }
  const data = {
    sortBy,
    toggleSort,
    isSorted
  };
  provide$3(VDataTableSortSymbol, data);
  return data;
}
function useSort() {
  const data = inject$6(VDataTableSortSymbol);
  if (!data) throw new Error('Missing sort!');
  return data;
}

// TODO: abstract into project composable
function useSortedItems(props, items, sortBy, options) {
  const locale = useLocale();
  const sortedItems = computed$P(() => {
    if (!sortBy.value.length) return items.value;
    return sortItems(items.value, sortBy.value, locale.current.value, {
      transform: options?.transform,
      sortFunctions: {
        ...props.customKeySort,
        ...options?.sortFunctions?.value
      },
      sortRawFunctions: options?.sortRawFunctions?.value
    });
  });
  return {
    sortedItems
  };
}
function sortItems(items, sortByItems, locale, options) {
  const stringCollator = new Intl.Collator(locale, {
    sensitivity: 'accent',
    usage: 'sort'
  });
  const transformedItems = items.map(item => [item, options?.transform ? options.transform(item) : item]);
  return transformedItems.sort((a, b) => {
    for (let i = 0; i < sortByItems.length; i++) {
      let hasCustomResult = false;
      const sortKey = sortByItems[i].key;
      const sortOrder = sortByItems[i].order ?? 'asc';
      if (sortOrder === false) continue;
      let sortA = getObjectValueByPath(a[1], sortKey);
      let sortB = getObjectValueByPath(b[1], sortKey);
      let sortARaw = a[0].raw;
      let sortBRaw = b[0].raw;
      if (sortOrder === 'desc') {
        [sortA, sortB] = [sortB, sortA];
        [sortARaw, sortBRaw] = [sortBRaw, sortARaw];
      }
      if (options?.sortRawFunctions?.[sortKey]) {
        const customResult = options.sortRawFunctions[sortKey](sortARaw, sortBRaw);
        if (customResult == null) continue;
        hasCustomResult = true;
        if (customResult) return customResult;
      }
      if (options?.sortFunctions?.[sortKey]) {
        const customResult = options.sortFunctions[sortKey](sortA, sortB);
        if (customResult == null) continue;
        hasCustomResult = true;
        if (customResult) return customResult;
      }
      if (hasCustomResult) continue;

      // Dates should be compared numerically
      if (sortA instanceof Date && sortB instanceof Date) {
        return sortA.getTime() - sortB.getTime();
      }
      [sortA, sortB] = [sortA, sortB].map(s => s != null ? s.toString().toLocaleLowerCase() : s);
      if (sortA !== sortB) {
        if (isEmpty(sortA) && isEmpty(sortB)) return 0;
        if (isEmpty(sortA)) return -1;
        if (isEmpty(sortB)) return 1;
        if (!isNaN(sortA) && !isNaN(sortB)) return Number(sortA) - Number(sortB);
        return stringCollator.compare(sortA, sortB);
      }
    }
    return 0;
  }).map(_ref => {
    let [item] = _ref;
    return item;
  });
}

// Utilities
const {computed: computed$O} = await importShared('vue');
// Composables
const makeDataIteratorItemsProps = propsFactory({
  items: {
    type: Array,
    default: () => []
  },
  itemValue: {
    type: [String, Array, Function],
    default: 'id'
  },
  itemSelectable: {
    type: [String, Array, Function],
    default: null
  },
  returnObject: Boolean
}, 'DataIterator-items');
function transformItem$1(props, item) {
  const value = props.returnObject ? item : getPropertyFromItem(item, props.itemValue);
  const selectable = getPropertyFromItem(item, props.itemSelectable, true);
  return {
    type: 'item',
    value,
    selectable,
    raw: item
  };
}
function transformItems$1(props, items) {
  const array = [];
  for (const item of items) {
    array.push(transformItem$1(props, item));
  }
  return array;
}
function useDataIteratorItems(props) {
  const items = computed$O(() => transformItems$1(props, props.items));
  return {
    items
  };
}

const {createVNode:_createVNode$13} = await importShared('vue');
const {computed: computed$N,toRef: toRef$m} = await importShared('vue');
const makeVDataIteratorProps = propsFactory({
  search: String,
  loading: Boolean,
  ...makeComponentProps(),
  ...makeDataIteratorItemsProps(),
  ...makeDataTableSelectProps(),
  ...makeDataTableSortProps(),
  ...makeDataTablePaginateProps({
    itemsPerPage: 5
  }),
  ...makeDataTableExpandProps(),
  ...makeDataTableGroupProps(),
  ...makeFilterProps(),
  ...makeTagProps(),
  ...makeTransitionProps({
    transition: {
      component: VFadeTransition,
      hideOnLeave: true
    }
  })
}, 'VDataIterator');
const VDataIterator = genericComponent()({
  name: 'VDataIterator',
  props: makeVDataIteratorProps(),
  emits: {
    'update:modelValue': value => true,
    'update:groupBy': value => true,
    'update:page': value => true,
    'update:itemsPerPage': value => true,
    'update:sortBy': value => true,
    'update:options': value => true,
    'update:expanded': value => true,
    'update:currentItems': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const groupBy = useProxiedModel(props, 'groupBy');
    const search = toRef$m(() => props.search);
    const {
      items
    } = useDataIteratorItems(props);
    const {
      filteredItems
    } = useFilter(props, items, search, {
      transform: item => item.raw
    });
    const {
      sortBy,
      multiSort,
      mustSort
    } = createSort(props);
    const {
      page,
      itemsPerPage
    } = createPagination(props);
    const {
      toggleSort
    } = provideSort({
      sortBy,
      multiSort,
      mustSort,
      page
    });
    const {
      sortByWithGroups,
      opened,
      extractRows,
      isGroupOpen,
      toggleGroup
    } = provideGroupBy({
      groupBy,
      sortBy
    });
    const {
      sortedItems
    } = useSortedItems(props, filteredItems, sortByWithGroups, {
      transform: item => item.raw
    });
    const {
      flatItems
    } = useGroupedItems(sortedItems, groupBy, opened);
    const itemsLength = toRef$m(() => flatItems.value.length);
    const {
      startIndex,
      stopIndex,
      pageCount,
      prevPage,
      nextPage,
      setItemsPerPage,
      setPage
    } = providePagination({
      page,
      itemsPerPage,
      itemsLength
    });
    const {
      paginatedItems
    } = usePaginatedItems({
      items: flatItems,
      startIndex,
      stopIndex,
      itemsPerPage
    });
    const paginatedItemsWithoutGroups = computed$N(() => extractRows(paginatedItems.value));
    const {
      isSelected,
      select,
      selectAll,
      toggleSelect
    } = provideSelection(props, {
      allItems: items,
      currentPage: paginatedItemsWithoutGroups
    });
    const {
      isExpanded,
      toggleExpand
    } = provideExpanded(props);
    useOptions({
      page,
      itemsPerPage,
      sortBy,
      groupBy,
      search
    });
    const slotProps = computed$N(() => ({
      page: page.value,
      itemsPerPage: itemsPerPage.value,
      sortBy: sortBy.value,
      pageCount: pageCount.value,
      toggleSort,
      prevPage,
      nextPage,
      setPage,
      setItemsPerPage,
      isSelected,
      select,
      selectAll,
      toggleSelect,
      isExpanded,
      toggleExpand,
      isGroupOpen,
      toggleGroup,
      items: paginatedItemsWithoutGroups.value,
      groupedItems: paginatedItems.value
    }));
    useRender(() => _createVNode$13(props.tag, {
      "class": ['v-data-iterator', {
        'v-data-iterator--loading': props.loading
      }, props.class],
      "style": props.style
    }, {
      default: () => [slots.header?.(slotProps.value), _createVNode$13(MaybeTransition, {
        "transition": props.transition
      }, {
        default: () => [props.loading ? _createVNode$13(LoaderSlot, {
          "key": "loader",
          "name": "v-data-iterator",
          "active": true
        }, {
          default: slotProps => slots.loader?.(slotProps)
        }) : _createVNode$13("div", {
          "key": "items"
        }, [!paginatedItems.value.length ? slots['no-data']?.() : slots.default?.(slotProps.value)])]
      }), slots.footer?.(slotProps.value)]
    }));
    return {};
  }
});

// Utilities
const {onBeforeUpdate,ref: ref$l} = await importShared('vue');


// Types

function useRefs() {
  const refs = ref$l([]);
  onBeforeUpdate(() => refs.value = []);
  function updateRef(e, i) {
    refs.value[i] = e;
  }
  return {
    refs,
    updateRef
  };
}

const {mergeProps:_mergeProps$y,createVNode:_createVNode$12} = await importShared('vue');
const {computed: computed$M,nextTick: nextTick$a,shallowRef: shallowRef$h,toRef: toRef$l} = await importShared('vue');
const makeVPaginationProps = propsFactory({
  activeColor: String,
  start: {
    type: [Number, String],
    default: 1
  },
  modelValue: {
    type: Number,
    default: props => props.start
  },
  disabled: Boolean,
  length: {
    type: [Number, String],
    default: 1,
    validator: val => val % 1 === 0
  },
  totalVisible: [Number, String],
  firstIcon: {
    type: IconValue,
    default: '$first'
  },
  prevIcon: {
    type: IconValue,
    default: '$prev'
  },
  nextIcon: {
    type: IconValue,
    default: '$next'
  },
  lastIcon: {
    type: IconValue,
    default: '$last'
  },
  ariaLabel: {
    type: String,
    default: '$vuetify.pagination.ariaLabel.root'
  },
  pageAriaLabel: {
    type: String,
    default: '$vuetify.pagination.ariaLabel.page'
  },
  currentPageAriaLabel: {
    type: String,
    default: '$vuetify.pagination.ariaLabel.currentPage'
  },
  firstAriaLabel: {
    type: String,
    default: '$vuetify.pagination.ariaLabel.first'
  },
  previousAriaLabel: {
    type: String,
    default: '$vuetify.pagination.ariaLabel.previous'
  },
  nextAriaLabel: {
    type: String,
    default: '$vuetify.pagination.ariaLabel.next'
  },
  lastAriaLabel: {
    type: String,
    default: '$vuetify.pagination.ariaLabel.last'
  },
  ellipsis: {
    type: String,
    default: '...'
  },
  showFirstLastPage: Boolean,
  ...makeBorderProps(),
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeElevationProps(),
  ...makeRoundedProps(),
  ...makeSizeProps(),
  ...makeTagProps({
    tag: 'nav'
  }),
  ...makeThemeProps(),
  ...makeVariantProps({
    variant: 'text'
  })
}, 'VPagination');
const VPagination = genericComponent()({
  name: 'VPagination',
  props: makeVPaginationProps(),
  emits: {
    'update:modelValue': value => true,
    first: value => true,
    prev: value => true,
    next: value => true,
    last: value => true
  },
  setup(props, _ref) {
    let {
      slots,
      emit
    } = _ref;
    const page = useProxiedModel(props, 'modelValue');
    const {
      t,
      n
    } = useLocale();
    const {
      isRtl
    } = useRtl();
    const {
      themeClasses
    } = provideTheme(props);
    const {
      width
    } = useDisplay();
    const maxButtons = shallowRef$h(-1);
    provideDefaults(undefined, {
      scoped: true
    });
    const {
      resizeRef
    } = useResizeObserver(entries => {
      if (!entries.length) return;
      const {
        target,
        contentRect
      } = entries[0];
      const firstItem = target.querySelector('.v-pagination__list > *');
      if (!firstItem) return;
      const totalWidth = contentRect.width;
      const itemWidth = firstItem.offsetWidth + parseFloat(getComputedStyle(firstItem).marginRight) * 2;
      maxButtons.value = getMax(totalWidth, itemWidth);
    });
    const length = computed$M(() => parseInt(props.length, 10));
    const start = computed$M(() => parseInt(props.start, 10));
    const totalVisible = computed$M(() => {
      if (props.totalVisible != null) return parseInt(props.totalVisible, 10);else if (maxButtons.value >= 0) return maxButtons.value;
      return getMax(width.value, 58);
    });
    function getMax(totalWidth, itemWidth) {
      const minButtons = props.showFirstLastPage ? 5 : 3;
      return Math.max(0, Math.floor(
      // Round to two decimal places to avoid floating point errors
      Number(((totalWidth - itemWidth * minButtons) / itemWidth).toFixed(2))));
    }
    const range = computed$M(() => {
      if (length.value <= 0 || isNaN(length.value) || length.value > Number.MAX_SAFE_INTEGER) return [];
      if (totalVisible.value <= 0) return [];else if (totalVisible.value === 1) return [page.value];
      if (length.value <= totalVisible.value) {
        return createRange(length.value, start.value);
      }
      const even = totalVisible.value % 2 === 0;
      const middle = even ? totalVisible.value / 2 : Math.floor(totalVisible.value / 2);
      const left = even ? middle : middle + 1;
      const right = length.value - middle;
      if (left - page.value >= 0) {
        return [...createRange(Math.max(1, totalVisible.value - 1), start.value), props.ellipsis, length.value];
      } else if (page.value - right >= (even ? 1 : 0)) {
        const rangeLength = totalVisible.value - 1;
        const rangeStart = length.value - rangeLength + start.value;
        return [start.value, props.ellipsis, ...createRange(rangeLength, rangeStart)];
      } else {
        const rangeLength = Math.max(1, totalVisible.value - 2);
        const rangeStart = rangeLength === 1 ? page.value : page.value - Math.ceil(rangeLength / 2) + start.value;
        return [start.value, props.ellipsis, ...createRange(rangeLength, rangeStart), props.ellipsis, length.value];
      }
    });

    // TODO: 'first' | 'prev' | 'next' | 'last' does not work here?
    function setValue(e, value, event) {
      e.preventDefault();
      page.value = value;
      event && emit(event, value);
    }
    const {
      refs,
      updateRef
    } = useRefs();
    provideDefaults({
      VPaginationBtn: {
        color: toRef$l(() => props.color),
        border: toRef$l(() => props.border),
        density: toRef$l(() => props.density),
        size: toRef$l(() => props.size),
        variant: toRef$l(() => props.variant),
        rounded: toRef$l(() => props.rounded),
        elevation: toRef$l(() => props.elevation)
      }
    });
    const items = computed$M(() => {
      return range.value.map((item, index) => {
        const ref = e => updateRef(e, index);
        if (typeof item === 'string') {
          return {
            isActive: false,
            key: `ellipsis-${index}`,
            page: item,
            props: {
              ref,
              ellipsis: true,
              icon: true,
              disabled: true
            }
          };
        } else {
          const isActive = item === page.value;
          return {
            isActive,
            key: item,
            page: n(item),
            props: {
              ref,
              ellipsis: false,
              icon: true,
              disabled: !!props.disabled || Number(props.length) < 2,
              color: isActive ? props.activeColor : props.color,
              'aria-current': isActive,
              'aria-label': t(isActive ? props.currentPageAriaLabel : props.pageAriaLabel, item),
              onClick: e => setValue(e, item)
            }
          };
        }
      });
    });
    const controls = computed$M(() => {
      const prevDisabled = !!props.disabled || page.value <= start.value;
      const nextDisabled = !!props.disabled || page.value >= start.value + length.value - 1;
      return {
        first: props.showFirstLastPage ? {
          icon: isRtl.value ? props.lastIcon : props.firstIcon,
          onClick: e => setValue(e, start.value, 'first'),
          disabled: prevDisabled,
          'aria-label': t(props.firstAriaLabel),
          'aria-disabled': prevDisabled
        } : undefined,
        prev: {
          icon: isRtl.value ? props.nextIcon : props.prevIcon,
          onClick: e => setValue(e, page.value - 1, 'prev'),
          disabled: prevDisabled,
          'aria-label': t(props.previousAriaLabel),
          'aria-disabled': prevDisabled
        },
        next: {
          icon: isRtl.value ? props.prevIcon : props.nextIcon,
          onClick: e => setValue(e, page.value + 1, 'next'),
          disabled: nextDisabled,
          'aria-label': t(props.nextAriaLabel),
          'aria-disabled': nextDisabled
        },
        last: props.showFirstLastPage ? {
          icon: isRtl.value ? props.firstIcon : props.lastIcon,
          onClick: e => setValue(e, start.value + length.value - 1, 'last'),
          disabled: nextDisabled,
          'aria-label': t(props.lastAriaLabel),
          'aria-disabled': nextDisabled
        } : undefined
      };
    });
    function updateFocus() {
      const currentIndex = page.value - start.value;
      refs.value[currentIndex]?.$el.focus();
    }
    function onKeydown(e) {
      if (e.key === keyValues.left && !props.disabled && page.value > Number(props.start)) {
        page.value = page.value - 1;
        nextTick$a(updateFocus);
      } else if (e.key === keyValues.right && !props.disabled && page.value < start.value + length.value - 1) {
        page.value = page.value + 1;
        nextTick$a(updateFocus);
      }
    }
    useRender(() => _createVNode$12(props.tag, {
      "ref": resizeRef,
      "class": ['v-pagination', themeClasses.value, props.class],
      "style": props.style,
      "role": "navigation",
      "aria-label": t(props.ariaLabel),
      "onKeydown": onKeydown,
      "data-test": "v-pagination-root"
    }, {
      default: () => [_createVNode$12("ul", {
        "class": "v-pagination__list"
      }, [props.showFirstLastPage && _createVNode$12("li", {
        "key": "first",
        "class": "v-pagination__first",
        "data-test": "v-pagination-first"
      }, [slots.first ? slots.first(controls.value.first) : _createVNode$12(VBtn, _mergeProps$y({
        "_as": "VPaginationBtn"
      }, controls.value.first), null)]), _createVNode$12("li", {
        "key": "prev",
        "class": "v-pagination__prev",
        "data-test": "v-pagination-prev"
      }, [slots.prev ? slots.prev(controls.value.prev) : _createVNode$12(VBtn, _mergeProps$y({
        "_as": "VPaginationBtn"
      }, controls.value.prev), null)]), items.value.map((item, index) => _createVNode$12("li", {
        "key": item.key,
        "class": ['v-pagination__item', {
          'v-pagination__item--is-active': item.isActive
        }],
        "data-test": "v-pagination-item"
      }, [slots.item ? slots.item(item) : _createVNode$12(VBtn, _mergeProps$y({
        "_as": "VPaginationBtn"
      }, item.props), {
        default: () => [item.page]
      })])), _createVNode$12("li", {
        "key": "next",
        "class": "v-pagination__next",
        "data-test": "v-pagination-next"
      }, [slots.next ? slots.next(controls.value.next) : _createVNode$12(VBtn, _mergeProps$y({
        "_as": "VPaginationBtn"
      }, controls.value.next), null)]), props.showFirstLastPage && _createVNode$12("li", {
        "key": "last",
        "class": "v-pagination__last",
        "data-test": "v-pagination-last"
      }, [slots.last ? slots.last(controls.value.last) : _createVNode$12(VBtn, _mergeProps$y({
        "_as": "VPaginationBtn"
      }, controls.value.last), null)])])]
    }));
    return {};
  }
});

const {createVNode:_createVNode$11,mergeProps:_mergeProps$x} = await importShared('vue');
const {computed: computed$L} = await importShared('vue');
const makeVDataTableFooterProps = propsFactory({
  prevIcon: {
    type: IconValue,
    default: '$prev'
  },
  nextIcon: {
    type: IconValue,
    default: '$next'
  },
  firstIcon: {
    type: IconValue,
    default: '$first'
  },
  lastIcon: {
    type: IconValue,
    default: '$last'
  },
  itemsPerPageText: {
    type: String,
    default: '$vuetify.dataFooter.itemsPerPageText'
  },
  pageText: {
    type: String,
    default: '$vuetify.dataFooter.pageText'
  },
  firstPageLabel: {
    type: String,
    default: '$vuetify.dataFooter.firstPage'
  },
  prevPageLabel: {
    type: String,
    default: '$vuetify.dataFooter.prevPage'
  },
  nextPageLabel: {
    type: String,
    default: '$vuetify.dataFooter.nextPage'
  },
  lastPageLabel: {
    type: String,
    default: '$vuetify.dataFooter.lastPage'
  },
  itemsPerPageOptions: {
    type: Array,
    default: () => [{
      value: 10,
      title: '10'
    }, {
      value: 25,
      title: '25'
    }, {
      value: 50,
      title: '50'
    }, {
      value: 100,
      title: '100'
    }, {
      value: -1,
      title: '$vuetify.dataFooter.itemsPerPageAll'
    }]
  },
  showCurrentPage: Boolean
}, 'VDataTableFooter');
const VDataTableFooter = genericComponent()({
  name: 'VDataTableFooter',
  props: makeVDataTableFooterProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      t
    } = useLocale();
    const {
      page,
      pageCount,
      startIndex,
      stopIndex,
      itemsLength,
      itemsPerPage,
      setItemsPerPage
    } = usePagination();
    const itemsPerPageOptions = computed$L(() => props.itemsPerPageOptions.map(option => {
      if (typeof option === 'number') {
        return {
          value: option,
          title: option === -1 ? t('$vuetify.dataFooter.itemsPerPageAll') : String(option)
        };
      }
      return {
        ...option,
        title: !isNaN(Number(option.title)) ? option.title : t(option.title)
      };
    }));
    useRender(() => {
      const paginationProps = VPagination.filterProps(props);
      return _createVNode$11("div", {
        "class": "v-data-table-footer"
      }, [slots.prepend?.(), _createVNode$11("div", {
        "class": "v-data-table-footer__items-per-page"
      }, [_createVNode$11("span", null, [t(props.itemsPerPageText)]), _createVNode$11(VSelect, {
        "items": itemsPerPageOptions.value,
        "modelValue": itemsPerPage.value,
        "onUpdate:modelValue": v => setItemsPerPage(Number(v)),
        "density": "compact",
        "variant": "outlined",
        "hide-details": true
      }, null)]), _createVNode$11("div", {
        "class": "v-data-table-footer__info"
      }, [_createVNode$11("div", null, [t(props.pageText, !itemsLength.value ? 0 : startIndex.value + 1, stopIndex.value, itemsLength.value)])]), _createVNode$11("div", {
        "class": "v-data-table-footer__pagination"
      }, [_createVNode$11(VPagination, _mergeProps$x({
        "modelValue": page.value,
        "onUpdate:modelValue": $event => page.value = $event,
        "density": "comfortable",
        "first-aria-label": props.firstPageLabel,
        "last-aria-label": props.lastPageLabel,
        "length": pageCount.value,
        "next-aria-label": props.nextPageLabel,
        "previous-aria-label": props.prevPageLabel,
        "rounded": true,
        "show-first-last-page": true,
        "total-visible": props.showCurrentPage ? 1 : 0,
        "variant": "plain"
      }, paginationProps), null)])]);
    });
    return {};
  }
});

const {createVNode:_createVNode$10} = await importShared('vue');
const VDataTableColumn = defineFunctionalComponent({
  align: {
    type: String,
    default: 'start'
  },
  fixed: Boolean,
  fixedOffset: [Number, String],
  height: [Number, String],
  lastFixed: Boolean,
  noPadding: Boolean,
  tag: String,
  width: [Number, String],
  maxWidth: [Number, String],
  nowrap: Boolean
}, (props, _ref) => {
  let {
    slots
  } = _ref;
  const Tag = props.tag ?? 'td';
  return _createVNode$10(Tag, {
    "class": ['v-data-table__td', {
      'v-data-table-column--fixed': props.fixed,
      'v-data-table-column--last-fixed': props.lastFixed,
      'v-data-table-column--no-padding': props.noPadding,
      'v-data-table-column--nowrap': props.nowrap
    }, `v-data-table-column--align-${props.align}`],
    "style": {
      height: convertToUnit(props.height),
      width: convertToUnit(props.width),
      maxWidth: convertToUnit(props.maxWidth),
      left: convertToUnit(props.fixedOffset || null)
    }
  }, {
    default: () => [slots.default?.()]
  });
});

// Utilities
const {capitalize: capitalize$2,inject: inject$5,provide: provide$2,ref: ref$k,watchEffect: watchEffect$9} = await importShared('vue');
const makeDataTableHeaderProps = propsFactory({
  headers: Array
}, 'DataTable-header');
const VDataTableHeadersSymbol = Symbol.for('vuetify:data-table-headers');
const defaultHeader = {
  title: '',
  sortable: false
};
const defaultActionHeader = {
  ...defaultHeader,
  width: 48
};
function priorityQueue() {
  let arr = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];
  const queue = arr.map(element => ({
    element,
    priority: 0
  }));
  return {
    enqueue: (element, priority) => {
      let added = false;
      for (let i = 0; i < queue.length; i++) {
        const item = queue[i];
        if (item.priority > priority) {
          queue.splice(i, 0, {
            element,
            priority
          });
          added = true;
          break;
        }
      }
      if (!added) queue.push({
        element,
        priority
      });
    },
    size: () => queue.length,
    count: () => {
      let count = 0;
      if (!queue.length) return 0;
      const whole = Math.floor(queue[0].priority);
      for (let i = 0; i < queue.length; i++) {
        if (Math.floor(queue[i].priority) === whole) count += 1;
      }
      return count;
    },
    dequeue: () => {
      return queue.shift();
    }
  };
}
function extractLeaves(item) {
  let columns = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];
  if (!item.children) {
    columns.push(item);
  } else {
    for (const child of item.children) {
      extractLeaves(child, columns);
    }
  }
  return columns;
}
function extractKeys(headers) {
  let keys = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : new Set();
  for (const item of headers) {
    if (item.key) keys.add(item.key);
    if (item.children) {
      extractKeys(item.children, keys);
    }
  }
  return keys;
}
function getDefaultItem(item) {
  if (!item.key) return undefined;
  if (item.key === 'data-table-group') return defaultHeader;
  if (['data-table-expand', 'data-table-select'].includes(item.key)) return defaultActionHeader;
  return undefined;
}
function getDepth(item) {
  let depth = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 0;
  if (!item.children) return depth;
  return Math.max(depth, ...item.children.map(child => getDepth(child, depth + 1)));
}
function parseFixedColumns(items) {
  let seenFixed = false;
  function setFixed(item) {
    let parentFixed = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
    if (!item) return;
    if (parentFixed) {
      item.fixed = true;
    }
    if (item.fixed) {
      if (item.children) {
        for (let i = item.children.length - 1; i >= 0; i--) {
          setFixed(item.children[i], true);
        }
      } else {
        if (!seenFixed) {
          item.lastFixed = true;
        } else if (isNaN(Number(item.width))) {
          consoleError(`Multiple fixed columns should have a static width (key: ${item.key})`);
        } else {
          item.minWidth = Math.max(Number(item.width) || 0, Number(item.minWidth) || 0);
        }
        seenFixed = true;
      }
    } else {
      if (item.children) {
        for (let i = item.children.length - 1; i >= 0; i--) {
          setFixed(item.children[i]);
        }
      } else {
        seenFixed = false;
      }
    }
  }
  for (let i = items.length - 1; i >= 0; i--) {
    setFixed(items[i]);
  }
  function setFixedOffset(item) {
    let fixedOffset = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 0;
    if (!item) return fixedOffset;
    if (item.children) {
      item.fixedOffset = fixedOffset;
      for (const child of item.children) {
        fixedOffset = setFixedOffset(child, fixedOffset);
      }
    } else if (item.fixed) {
      item.fixedOffset = fixedOffset;
      fixedOffset += parseFloat(item.width || '0') || 0;
    }
    return fixedOffset;
  }
  let fixedOffset = 0;
  for (const item of items) {
    fixedOffset = setFixedOffset(item, fixedOffset);
  }
}
function parse(items, maxDepth) {
  const headers = [];
  let currentDepth = 0;
  const queue = priorityQueue(items);
  while (queue.size() > 0) {
    let rowSize = queue.count();
    const row = [];
    let fraction = 1;
    while (rowSize > 0) {
      const {
        element: item,
        priority
      } = queue.dequeue();
      const diff = maxDepth - currentDepth - getDepth(item);
      row.push({
        ...item,
        rowspan: diff ?? 1,
        colspan: item.children ? extractLeaves(item).length : 1
      });
      if (item.children) {
        for (const child of item.children) {
          // This internally sorts items that are on the same priority "row"
          const sort = priority % 1 + fraction / Math.pow(10, currentDepth + 2);
          queue.enqueue(child, currentDepth + diff + sort);
        }
      }
      fraction += 1;
      rowSize -= 1;
    }
    currentDepth += 1;
    headers.push(row);
  }
  const columns = items.map(item => extractLeaves(item)).flat();
  return {
    columns,
    headers
  };
}
function convertToInternalHeaders(items) {
  const internalHeaders = [];
  for (const item of items) {
    const defaultItem = {
      ...getDefaultItem(item),
      ...item
    };
    const key = defaultItem.key ?? (typeof defaultItem.value === 'string' ? defaultItem.value : null);
    const value = defaultItem.value ?? key ?? null;
    const internalItem = {
      ...defaultItem,
      key,
      value,
      sortable: defaultItem.sortable ?? (defaultItem.key != null || !!defaultItem.sort),
      children: defaultItem.children ? convertToInternalHeaders(defaultItem.children) : undefined
    };
    internalHeaders.push(internalItem);
  }
  return internalHeaders;
}
function createHeaders(props, options) {
  const headers = ref$k([]);
  const columns = ref$k([]);
  const sortFunctions = ref$k({});
  const sortRawFunctions = ref$k({});
  const filterFunctions = ref$k({});
  watchEffect$9(() => {
    const _headers = props.headers || Object.keys(props.items[0] ?? {}).map(key => ({
      key,
      title: capitalize$2(key)
    }));
    const items = _headers.slice();
    const keys = extractKeys(items);
    if (options?.groupBy?.value.length && !keys.has('data-table-group')) {
      items.unshift({
        key: 'data-table-group',
        title: 'Group'
      });
    }
    if (options?.showSelect?.value && !keys.has('data-table-select')) {
      items.unshift({
        key: 'data-table-select'
      });
    }
    if (options?.showExpand?.value && !keys.has('data-table-expand')) {
      items.push({
        key: 'data-table-expand'
      });
    }
    const internalHeaders = convertToInternalHeaders(items);
    parseFixedColumns(internalHeaders);
    const maxDepth = Math.max(...internalHeaders.map(item => getDepth(item))) + 1;
    const parsed = parse(internalHeaders, maxDepth);
    headers.value = parsed.headers;
    columns.value = parsed.columns;
    const flatHeaders = parsed.headers.flat(1);
    for (const header of flatHeaders) {
      if (!header.key) continue;
      if (header.sortable) {
        if (header.sort) {
          sortFunctions.value[header.key] = header.sort;
        }
        if (header.sortRaw) {
          sortRawFunctions.value[header.key] = header.sortRaw;
        }
      }
      if (header.filter) {
        filterFunctions.value[header.key] = header.filter;
      }
    }
  });
  const data = {
    headers,
    columns,
    sortFunctions,
    sortRawFunctions,
    filterFunctions
  };
  provide$2(VDataTableHeadersSymbol, data);
  return data;
}
function useHeaders() {
  const data = inject$5(VDataTableHeadersSymbol);
  if (!data) throw new Error('Missing headers!');
  return data;
}

const {createVNode:_createVNode$$,mergeProps:_mergeProps$w,Fragment:_Fragment$k} = await importShared('vue');
const {computed: computed$K,mergeProps: mergeProps$4} = await importShared('vue');
const makeVDataTableHeadersProps = propsFactory({
  color: String,
  disableSort: Boolean,
  fixedHeader: Boolean,
  multiSort: Boolean,
  sortAscIcon: {
    type: IconValue,
    default: '$sortAsc'
  },
  sortDescIcon: {
    type: IconValue,
    default: '$sortDesc'
  },
  headerProps: {
    type: Object
  },
  /** @deprecated */
  sticky: Boolean,
  ...makeDisplayProps(),
  ...makeLoaderProps()
}, 'VDataTableHeaders');
const VDataTableHeaders = genericComponent()({
  name: 'VDataTableHeaders',
  props: makeVDataTableHeadersProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      t
    } = useLocale();
    const {
      toggleSort,
      sortBy,
      isSorted
    } = useSort();
    const {
      someSelected,
      allSelected,
      selectAll,
      showSelectAll
    } = useSelection();
    const {
      columns,
      headers
    } = useHeaders();
    const {
      loaderClasses
    } = useLoader(props);
    function getFixedStyles(column, y) {
      if (!(props.sticky || props.fixedHeader) && !column.fixed) return undefined;
      return {
        position: 'sticky',
        left: column.fixed ? convertToUnit(column.fixedOffset) : undefined,
        top: props.sticky || props.fixedHeader ? `calc(var(--v-table-header-height) * ${y})` : undefined
      };
    }
    function getSortIcon(column) {
      const item = sortBy.value.find(item => item.key === column.key);
      if (!item) return props.sortAscIcon;
      return item.order === 'asc' ? props.sortAscIcon : props.sortDescIcon;
    }
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.color);
    const {
      displayClasses,
      mobile
    } = useDisplay(props);
    const slotProps = computed$K(() => ({
      headers: headers.value,
      columns: columns.value,
      toggleSort,
      isSorted,
      sortBy: sortBy.value,
      someSelected: someSelected.value,
      allSelected: allSelected.value,
      selectAll,
      getSortIcon
    }));
    const headerCellClasses = computed$K(() => ['v-data-table__th', {
      'v-data-table__th--sticky': props.sticky || props.fixedHeader
    }, displayClasses.value, loaderClasses.value]);
    const VDataTableHeaderCell = _ref2 => {
      let {
        column,
        x,
        y
      } = _ref2;
      const noPadding = column.key === 'data-table-select' || column.key === 'data-table-expand';
      const headerProps = mergeProps$4(props.headerProps ?? {}, column.headerProps ?? {});
      return _createVNode$$(VDataTableColumn, _mergeProps$w({
        "tag": "th",
        "align": column.align,
        "class": [{
          'v-data-table__th--sortable': column.sortable && !props.disableSort,
          'v-data-table__th--sorted': isSorted(column),
          'v-data-table__th--fixed': column.fixed
        }, ...headerCellClasses.value],
        "style": {
          width: convertToUnit(column.width),
          minWidth: convertToUnit(column.minWidth),
          maxWidth: convertToUnit(column.maxWidth),
          ...getFixedStyles(column, y)
        },
        "colspan": column.colspan,
        "rowspan": column.rowspan,
        "onClick": column.sortable ? () => toggleSort(column) : undefined,
        "fixed": column.fixed,
        "nowrap": column.nowrap,
        "lastFixed": column.lastFixed,
        "noPadding": noPadding
      }, headerProps), {
        default: () => {
          const columnSlotName = `header.${column.key}`;
          const columnSlotProps = {
            column,
            selectAll,
            isSorted,
            toggleSort,
            sortBy: sortBy.value,
            someSelected: someSelected.value,
            allSelected: allSelected.value,
            getSortIcon
          };
          if (slots[columnSlotName]) return slots[columnSlotName](columnSlotProps);
          if (column.key === 'data-table-select') {
            return slots['header.data-table-select']?.(columnSlotProps) ?? (showSelectAll.value && _createVNode$$(VCheckboxBtn, {
              "modelValue": allSelected.value,
              "indeterminate": someSelected.value && !allSelected.value,
              "onUpdate:modelValue": selectAll
            }, null));
          }
          return _createVNode$$("div", {
            "class": "v-data-table-header__content"
          }, [_createVNode$$("span", null, [column.title]), column.sortable && !props.disableSort && _createVNode$$(VIcon, {
            "key": "icon",
            "class": "v-data-table-header__sort-icon",
            "icon": getSortIcon(column)
          }, null), props.multiSort && isSorted(column) && _createVNode$$("div", {
            "key": "badge",
            "class": ['v-data-table-header__sort-badge', ...backgroundColorClasses.value],
            "style": backgroundColorStyles.value
          }, [sortBy.value.findIndex(x => x.key === column.key) + 1])]);
        }
      });
    };
    const VDataTableMobileHeaderCell = () => {
      const displayItems = computed$K(() => {
        return columns.value.filter(column => column?.sortable && !props.disableSort);
      });
      const appendIcon = computed$K(() => {
        const showSelectColumn = columns.value.find(column => column.key === 'data-table-select');
        if (showSelectColumn == null) return;
        return allSelected.value ? '$checkboxOn' : someSelected.value ? '$checkboxIndeterminate' : '$checkboxOff';
      });
      return _createVNode$$(VDataTableColumn, _mergeProps$w({
        "tag": "th",
        "class": [...headerCellClasses.value],
        "colspan": headers.value.length + 1
      }, props.headerProps), {
        default: () => [_createVNode$$("div", {
          "class": "v-data-table-header__content"
        }, [_createVNode$$(VSelect, {
          "chips": true,
          "class": "v-data-table__td-sort-select",
          "clearable": true,
          "density": "default",
          "items": displayItems.value,
          "label": t('$vuetify.dataTable.sortBy'),
          "multiple": props.multiSort,
          "variant": "underlined",
          "onClick:clear": () => sortBy.value = [],
          "appendIcon": appendIcon.value,
          "onClick:append": () => selectAll(!allSelected.value)
        }, {
          ...slots,
          chip: props => _createVNode$$(VChip, {
            "onClick": props.item.raw?.sortable ? () => toggleSort(props.item.raw) : undefined,
            "onMousedown": e => {
              e.preventDefault();
              e.stopPropagation();
            }
          }, {
            default: () => [props.item.title, _createVNode$$(VIcon, {
              "class": ['v-data-table__td-sort-icon', isSorted(props.item.raw) && 'v-data-table__td-sort-icon-active'],
              "icon": getSortIcon(props.item.raw),
              "size": "small"
            }, null)]
          })
        })])]
      });
    };
    useRender(() => {
      return mobile.value ? _createVNode$$("tr", null, [_createVNode$$(VDataTableMobileHeaderCell, null, null)]) : _createVNode$$(_Fragment$k, null, [slots.headers ? slots.headers(slotProps.value) : headers.value.map((row, y) => _createVNode$$("tr", null, [row.map((column, x) => _createVNode$$(VDataTableHeaderCell, {
        "column": column,
        "x": x,
        "y": y
      }, null))])), props.loading && _createVNode$$("tr", {
        "class": "v-data-table-progress"
      }, [_createVNode$$("th", {
        "colspan": columns.value.length
      }, [_createVNode$$(LoaderSlot, {
        "name": "v-data-table-progress",
        "absolute": true,
        "active": true,
        "color": typeof props.loading === 'boolean' ? undefined : props.loading,
        "indeterminate": true
      }, {
        default: slots.loader
      })])])]);
    });
  }
});

const {createVNode:_createVNode$_,createTextVNode:_createTextVNode$3} = await importShared('vue');
const {computed: computed$J} = await importShared('vue');
const makeVDataTableGroupHeaderRowProps = propsFactory({
  item: {
    type: Object,
    required: true
  }
}, 'VDataTableGroupHeaderRow');
const VDataTableGroupHeaderRow = genericComponent()({
  name: 'VDataTableGroupHeaderRow',
  props: makeVDataTableGroupHeaderRowProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      isGroupOpen,
      toggleGroup,
      extractRows
    } = useGroupBy();
    const {
      isSelected,
      isSomeSelected,
      select
    } = useSelection();
    const {
      columns
    } = useHeaders();
    const rows = computed$J(() => {
      return extractRows([props.item]);
    });
    return () => _createVNode$_("tr", {
      "class": "v-data-table-group-header-row",
      "style": {
        '--v-data-table-group-header-row-depth': props.item.depth
      }
    }, [columns.value.map(column => {
      if (column.key === 'data-table-group') {
        const icon = isGroupOpen(props.item) ? '$expand' : '$next';
        const onClick = () => toggleGroup(props.item);
        return slots['data-table-group']?.({
          item: props.item,
          count: rows.value.length,
          props: {
            icon,
            onClick
          }
        }) ?? _createVNode$_(VDataTableColumn, {
          "class": "v-data-table-group-header-row__column"
        }, {
          default: () => [_createVNode$_(VBtn, {
            "size": "small",
            "variant": "text",
            "icon": icon,
            "onClick": onClick
          }, null), _createVNode$_("span", null, [props.item.value]), _createVNode$_("span", null, [_createTextVNode$3("("), rows.value.length, _createTextVNode$3(")")])]
        });
      }
      if (column.key === 'data-table-select') {
        const modelValue = isSelected(rows.value);
        const indeterminate = isSomeSelected(rows.value) && !modelValue;
        const selectGroup = v => select(rows.value, v);
        return slots['data-table-select']?.({
          props: {
            modelValue,
            indeterminate,
            'onUpdate:modelValue': selectGroup
          }
        }) ?? _createVNode$_("td", null, [_createVNode$_(VCheckboxBtn, {
          "modelValue": modelValue,
          "indeterminate": indeterminate,
          "onUpdate:modelValue": selectGroup
        }, null)]);
      }
      return _createVNode$_("td", null, null);
    })]);
  }
});

const {createVNode:_createVNode$Z,Fragment:_Fragment$j,mergeProps:_mergeProps$v} = await importShared('vue');
const {toDisplayString,withModifiers} = await importShared('vue');
const makeVDataTableRowProps = propsFactory({
  index: Number,
  item: Object,
  cellProps: [Object, Function],
  onClick: EventProp(),
  onContextmenu: EventProp(),
  onDblclick: EventProp(),
  ...makeDisplayProps()
}, 'VDataTableRow');
const VDataTableRow = genericComponent()({
  name: 'VDataTableRow',
  props: makeVDataTableRowProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      displayClasses,
      mobile
    } = useDisplay(props, 'v-data-table__tr');
    const {
      isSelected,
      toggleSelect,
      someSelected,
      allSelected,
      selectAll
    } = useSelection();
    const {
      isExpanded,
      toggleExpand
    } = useExpanded();
    const {
      toggleSort,
      sortBy,
      isSorted
    } = useSort();
    const {
      columns
    } = useHeaders();
    useRender(() => _createVNode$Z("tr", {
      "class": ['v-data-table__tr', {
        'v-data-table__tr--clickable': !!(props.onClick || props.onContextmenu || props.onDblclick)
      }, displayClasses.value],
      "onClick": props.onClick,
      "onContextmenu": props.onContextmenu,
      "onDblclick": props.onDblclick
    }, [props.item && columns.value.map((column, i) => {
      const item = props.item;
      const slotName = `item.${column.key}`;
      const headerSlotName = `header.${column.key}`;
      const slotProps = {
        index: props.index,
        item: item.raw,
        internalItem: item,
        value: getObjectValueByPath(item.columns, column.key),
        column,
        isSelected,
        toggleSelect,
        isExpanded,
        toggleExpand
      };
      const columnSlotProps = {
        column,
        selectAll,
        isSorted,
        toggleSort,
        sortBy: sortBy.value,
        someSelected: someSelected.value,
        allSelected: allSelected.value,
        getSortIcon: () => ''
      };
      const cellProps = typeof props.cellProps === 'function' ? props.cellProps({
        index: slotProps.index,
        item: slotProps.item,
        internalItem: slotProps.internalItem,
        value: slotProps.value,
        column
      }) : props.cellProps;
      const columnCellProps = typeof column.cellProps === 'function' ? column.cellProps({
        index: slotProps.index,
        item: slotProps.item,
        internalItem: slotProps.internalItem,
        value: slotProps.value
      }) : column.cellProps;
      return _createVNode$Z(VDataTableColumn, _mergeProps$v({
        "align": column.align,
        "class": {
          'v-data-table__td--expanded-row': column.key === 'data-table-expand',
          'v-data-table__td--select-row': column.key === 'data-table-select'
        },
        "fixed": column.fixed,
        "fixedOffset": column.fixedOffset,
        "lastFixed": column.lastFixed,
        "maxWidth": !mobile.value ? column.maxWidth : undefined,
        "noPadding": column.key === 'data-table-select' || column.key === 'data-table-expand',
        "nowrap": column.nowrap,
        "width": !mobile.value ? column.width : undefined
      }, cellProps, columnCellProps), {
        default: () => {
          if (column.key === 'data-table-select') {
            return slots['item.data-table-select']?.({
              ...slotProps,
              props: {
                disabled: !item.selectable,
                modelValue: isSelected([item]),
                onClick: withModifiers(() => toggleSelect(item), ['stop'])
              }
            }) ?? _createVNode$Z(VCheckboxBtn, {
              "disabled": !item.selectable,
              "modelValue": isSelected([item]),
              "onClick": withModifiers(event => toggleSelect(item, props.index, event), ['stop'])
            }, null);
          }
          if (column.key === 'data-table-expand') {
            return slots['item.data-table-expand']?.({
              ...slotProps,
              props: {
                icon: isExpanded(item) ? '$collapse' : '$expand',
                size: 'small',
                variant: 'text',
                onClick: withModifiers(() => toggleExpand(item), ['stop'])
              }
            }) ?? _createVNode$Z(VBtn, {
              "icon": isExpanded(item) ? '$collapse' : '$expand',
              "size": "small",
              "variant": "text",
              "onClick": withModifiers(() => toggleExpand(item), ['stop'])
            }, null);
          }
          if (slots[slotName] && !mobile.value) return slots[slotName](slotProps);
          const displayValue = toDisplayString(slotProps.value);
          return !mobile.value ? displayValue : _createVNode$Z(_Fragment$j, null, [_createVNode$Z("div", {
            "class": "v-data-table__td-title"
          }, [slots[headerSlotName]?.(columnSlotProps) ?? column.title]), _createVNode$Z("div", {
            "class": "v-data-table__td-value"
          }, [slots[slotName]?.(slotProps) ?? displayValue])]);
        }
      });
    })]));
  }
});

const {createVNode:_createVNode$Y,Fragment:_Fragment$i,mergeProps:_mergeProps$u} = await importShared('vue');
const {Fragment,mergeProps: mergeProps$3} = await importShared('vue');
const makeVDataTableRowsProps = propsFactory({
  loading: [Boolean, String],
  loadingText: {
    type: String,
    default: '$vuetify.dataIterator.loadingText'
  },
  hideNoData: Boolean,
  items: {
    type: Array,
    default: () => []
  },
  noDataText: {
    type: String,
    default: '$vuetify.noDataText'
  },
  rowProps: [Object, Function],
  cellProps: [Object, Function],
  ...makeDisplayProps()
}, 'VDataTableRows');
const VDataTableRows = genericComponent()({
  name: 'VDataTableRows',
  inheritAttrs: false,
  props: makeVDataTableRowsProps(),
  setup(props, _ref) {
    let {
      attrs,
      slots
    } = _ref;
    const {
      columns
    } = useHeaders();
    const {
      expandOnClick,
      toggleExpand,
      isExpanded
    } = useExpanded();
    const {
      isSelected,
      toggleSelect
    } = useSelection();
    const {
      toggleGroup,
      isGroupOpen
    } = useGroupBy();
    const {
      t
    } = useLocale();
    const {
      mobile
    } = useDisplay(props);
    useRender(() => {
      if (props.loading && (!props.items.length || slots.loading)) {
        return _createVNode$Y("tr", {
          "class": "v-data-table-rows-loading",
          "key": "loading"
        }, [_createVNode$Y("td", {
          "colspan": columns.value.length
        }, [slots.loading?.() ?? t(props.loadingText)])]);
      }
      if (!props.loading && !props.items.length && !props.hideNoData) {
        return _createVNode$Y("tr", {
          "class": "v-data-table-rows-no-data",
          "key": "no-data"
        }, [_createVNode$Y("td", {
          "colspan": columns.value.length
        }, [slots['no-data']?.() ?? t(props.noDataText)])]);
      }
      return _createVNode$Y(_Fragment$i, null, [props.items.map((item, index) => {
        if (item.type === 'group') {
          const slotProps = {
            index,
            item,
            columns: columns.value,
            isExpanded,
            toggleExpand,
            isSelected,
            toggleSelect,
            toggleGroup,
            isGroupOpen
          };
          return slots['group-header'] ? slots['group-header'](slotProps) : _createVNode$Y(VDataTableGroupHeaderRow, _mergeProps$u({
            "key": `group-header_${item.id}`,
            "item": item
          }, getPrefixedEventHandlers(attrs, ':group-header', () => slotProps)), slots);
        }
        const slotProps = {
          index,
          item: item.raw,
          internalItem: item,
          columns: columns.value,
          isExpanded,
          toggleExpand,
          isSelected,
          toggleSelect
        };
        const itemSlotProps = {
          ...slotProps,
          props: mergeProps$3({
            key: `item_${item.key ?? item.index}`,
            onClick: expandOnClick.value ? () => {
              toggleExpand(item);
            } : undefined,
            index,
            item,
            cellProps: props.cellProps,
            mobile: mobile.value
          }, getPrefixedEventHandlers(attrs, ':row', () => slotProps), typeof props.rowProps === 'function' ? props.rowProps({
            item: slotProps.item,
            index: slotProps.index,
            internalItem: slotProps.internalItem
          }) : props.rowProps)
        };
        return _createVNode$Y(_Fragment$i, {
          "key": itemSlotProps.props.key
        }, [slots.item ? slots.item(itemSlotProps) : _createVNode$Y(VDataTableRow, itemSlotProps.props, slots), isExpanded(item) && slots['expanded-row']?.(slotProps)]);
      })]);
    });
    return {};
  }
});

const {createVNode:_createVNode$X} = await importShared('vue');
const makeVTableProps = propsFactory({
  fixedHeader: Boolean,
  fixedFooter: Boolean,
  height: [Number, String],
  hover: Boolean,
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeTagProps(),
  ...makeThemeProps()
}, 'VTable');
const VTable = genericComponent()({
  name: 'VTable',
  props: makeVTableProps(),
  setup(props, _ref) {
    let {
      slots,
      emit
    } = _ref;
    const {
      themeClasses
    } = provideTheme(props);
    const {
      densityClasses
    } = useDensity(props);
    useRender(() => _createVNode$X(props.tag, {
      "class": ['v-table', {
        'v-table--fixed-height': !!props.height,
        'v-table--fixed-header': props.fixedHeader,
        'v-table--fixed-footer': props.fixedFooter,
        'v-table--has-top': !!slots.top,
        'v-table--has-bottom': !!slots.bottom,
        'v-table--hover': props.hover
      }, themeClasses.value, densityClasses.value, props.class],
      "style": props.style
    }, {
      default: () => [slots.top?.(), slots.default ? _createVNode$X("div", {
        "class": "v-table__wrapper",
        "style": {
          height: convertToUnit(props.height)
        }
      }, [_createVNode$X("table", null, [slots.default()])]) : slots.wrapper?.(), slots.bottom?.()]
    }));
    return {};
  }
});

// Utilities
const {computed: computed$I} = await importShared('vue');
// Composables
const makeDataTableItemsProps = propsFactory({
  items: {
    type: Array,
    default: () => []
  },
  itemValue: {
    type: [String, Array, Function],
    default: 'id'
  },
  itemSelectable: {
    type: [String, Array, Function],
    default: null
  },
  rowProps: [Object, Function],
  cellProps: [Object, Function],
  returnObject: Boolean
}, 'DataTable-items');
function transformItem(props, item, index, columns) {
  const value = props.returnObject ? item : getPropertyFromItem(item, props.itemValue);
  const selectable = getPropertyFromItem(item, props.itemSelectable, true);
  const itemColumns = columns.reduce((obj, column) => {
    if (column.key != null) obj[column.key] = getPropertyFromItem(item, column.value);
    return obj;
  }, {});
  return {
    type: 'item',
    key: props.returnObject ? getPropertyFromItem(item, props.itemValue) : value,
    index,
    value,
    selectable,
    columns: itemColumns,
    raw: item
  };
}
function transformItems(props, items, columns) {
  return items.map((item, index) => transformItem(props, item, index, columns));
}
function useDataTableItems(props, columns) {
  const items = computed$I(() => transformItems(props, props.items, columns.value));
  return {
    items
  };
}

const {Fragment:_Fragment$h,createVNode:_createVNode$W,mergeProps:_mergeProps$t} = await importShared('vue');
const {computed: computed$H,toRef: toRef$k,toRefs: toRefs$3} = await importShared('vue');
const makeDataTableProps = propsFactory({
  ...makeVDataTableRowsProps(),
  hideDefaultBody: Boolean,
  hideDefaultFooter: Boolean,
  hideDefaultHeader: Boolean,
  width: [String, Number],
  search: String,
  ...makeDataTableExpandProps(),
  ...makeDataTableGroupProps(),
  ...makeDataTableHeaderProps(),
  ...makeDataTableItemsProps(),
  ...makeDataTableSelectProps(),
  ...makeDataTableSortProps(),
  ...makeVDataTableHeadersProps(),
  ...makeVTableProps()
}, 'DataTable');
const makeVDataTableProps = propsFactory({
  ...makeDataTablePaginateProps(),
  ...makeDataTableProps(),
  ...makeFilterProps(),
  ...makeVDataTableFooterProps()
}, 'VDataTable');
const VDataTable = genericComponent()({
  name: 'VDataTable',
  props: makeVDataTableProps(),
  emits: {
    'update:modelValue': value => true,
    'update:page': value => true,
    'update:itemsPerPage': value => true,
    'update:sortBy': value => true,
    'update:options': value => true,
    'update:groupBy': value => true,
    'update:expanded': value => true,
    'update:currentItems': value => true
  },
  setup(props, _ref) {
    let {
      attrs,
      slots
    } = _ref;
    const {
      groupBy
    } = createGroupBy(props);
    const {
      sortBy,
      multiSort,
      mustSort
    } = createSort(props);
    const {
      page,
      itemsPerPage
    } = createPagination(props);
    const {
      disableSort
    } = toRefs$3(props);
    const {
      columns,
      headers,
      sortFunctions,
      sortRawFunctions,
      filterFunctions
    } = createHeaders(props, {
      groupBy,
      showSelect: toRef$k(() => props.showSelect),
      showExpand: toRef$k(() => props.showExpand)
    });
    const {
      items
    } = useDataTableItems(props, columns);
    const search = toRef$k(() => props.search);
    const {
      filteredItems
    } = useFilter(props, items, search, {
      transform: item => item.columns,
      customKeyFilter: filterFunctions
    });
    const {
      toggleSort
    } = provideSort({
      sortBy,
      multiSort,
      mustSort,
      page
    });
    const {
      sortByWithGroups,
      opened,
      extractRows,
      isGroupOpen,
      toggleGroup
    } = provideGroupBy({
      groupBy,
      sortBy,
      disableSort
    });
    const {
      sortedItems
    } = useSortedItems(props, filteredItems, sortByWithGroups, {
      transform: item => ({
        ...item.raw,
        ...item.columns
      }),
      sortFunctions,
      sortRawFunctions
    });
    const {
      flatItems
    } = useGroupedItems(sortedItems, groupBy, opened);
    const itemsLength = computed$H(() => flatItems.value.length);
    const {
      startIndex,
      stopIndex,
      pageCount,
      setItemsPerPage
    } = providePagination({
      page,
      itemsPerPage,
      itemsLength
    });
    const {
      paginatedItems
    } = usePaginatedItems({
      items: flatItems,
      startIndex,
      stopIndex,
      itemsPerPage
    });
    const paginatedItemsWithoutGroups = computed$H(() => extractRows(paginatedItems.value));
    const {
      isSelected,
      select,
      selectAll,
      toggleSelect,
      someSelected,
      allSelected
    } = provideSelection(props, {
      allItems: items,
      currentPage: paginatedItemsWithoutGroups
    });
    const {
      isExpanded,
      toggleExpand
    } = provideExpanded(props);
    useOptions({
      page,
      itemsPerPage,
      sortBy,
      groupBy,
      search
    });
    provideDefaults({
      VDataTableRows: {
        hideNoData: toRef$k(() => props.hideNoData),
        noDataText: toRef$k(() => props.noDataText),
        loading: toRef$k(() => props.loading),
        loadingText: toRef$k(() => props.loadingText)
      }
    });
    const slotProps = computed$H(() => ({
      page: page.value,
      itemsPerPage: itemsPerPage.value,
      sortBy: sortBy.value,
      pageCount: pageCount.value,
      toggleSort,
      setItemsPerPage,
      someSelected: someSelected.value,
      allSelected: allSelected.value,
      isSelected,
      select,
      selectAll,
      toggleSelect,
      isExpanded,
      toggleExpand,
      isGroupOpen,
      toggleGroup,
      items: paginatedItemsWithoutGroups.value.map(item => item.raw),
      internalItems: paginatedItemsWithoutGroups.value,
      groupedItems: paginatedItems.value,
      columns: columns.value,
      headers: headers.value
    }));
    useRender(() => {
      const dataTableFooterProps = VDataTableFooter.filterProps(props);
      const dataTableHeadersProps = VDataTableHeaders.filterProps(props);
      const dataTableRowsProps = VDataTableRows.filterProps(props);
      const tableProps = VTable.filterProps(props);
      return _createVNode$W(VTable, _mergeProps$t({
        "class": ['v-data-table', {
          'v-data-table--show-select': props.showSelect,
          'v-data-table--loading': props.loading
        }, props.class],
        "style": props.style
      }, tableProps, {
        "fixedHeader": props.fixedHeader || props.sticky
      }), {
        top: () => slots.top?.(slotProps.value),
        default: () => slots.default ? slots.default(slotProps.value) : _createVNode$W(_Fragment$h, null, [slots.colgroup?.(slotProps.value), !props.hideDefaultHeader && _createVNode$W("thead", {
          "key": "thead"
        }, [_createVNode$W(VDataTableHeaders, dataTableHeadersProps, slots)]), slots.thead?.(slotProps.value), !props.hideDefaultBody && _createVNode$W("tbody", null, [slots['body.prepend']?.(slotProps.value), slots.body ? slots.body(slotProps.value) : _createVNode$W(VDataTableRows, _mergeProps$t(attrs, dataTableRowsProps, {
          "items": paginatedItems.value
        }), slots), slots['body.append']?.(slotProps.value)]), slots.tbody?.(slotProps.value), slots.tfoot?.(slotProps.value)]),
        bottom: () => slots.bottom ? slots.bottom(slotProps.value) : !props.hideDefaultFooter && _createVNode$W(_Fragment$h, null, [_createVNode$W(VDivider, null, null), _createVNode$W(VDataTableFooter, dataTableFooterProps, {
          prepend: slots['footer.prepend']
        })])
      });
    });
    return {};
  }
});

const {createVNode:_createVNode$V,mergeProps:_mergeProps$s} = await importShared('vue');
const {computed: computed$G,shallowRef: shallowRef$g,toRef: toRef$j,toRefs: toRefs$2} = await importShared('vue');
const makeVDataTableVirtualProps = propsFactory({
  ...omit(makeDataTableProps(), ['hideDefaultFooter']),
  ...makeDataTableGroupProps(),
  ...makeVirtualProps(),
  ...makeFilterProps()
}, 'VDataTableVirtual');
const VDataTableVirtual = genericComponent()({
  name: 'VDataTableVirtual',
  props: makeVDataTableVirtualProps(),
  emits: {
    'update:modelValue': value => true,
    'update:sortBy': value => true,
    'update:options': value => true,
    'update:groupBy': value => true,
    'update:expanded': value => true
  },
  setup(props, _ref) {
    let {
      attrs,
      slots
    } = _ref;
    const {
      groupBy
    } = createGroupBy(props);
    const {
      sortBy,
      multiSort,
      mustSort
    } = createSort(props);
    const {
      disableSort
    } = toRefs$2(props);
    const {
      columns,
      headers,
      filterFunctions,
      sortFunctions,
      sortRawFunctions
    } = createHeaders(props, {
      groupBy,
      showSelect: toRef$j(() => props.showSelect),
      showExpand: toRef$j(() => props.showExpand)
    });
    const {
      items
    } = useDataTableItems(props, columns);
    const search = toRef$j(() => props.search);
    const {
      filteredItems
    } = useFilter(props, items, search, {
      transform: item => item.columns,
      customKeyFilter: filterFunctions
    });
    const {
      toggleSort
    } = provideSort({
      sortBy,
      multiSort,
      mustSort
    });
    const {
      sortByWithGroups,
      opened,
      extractRows,
      isGroupOpen,
      toggleGroup
    } = provideGroupBy({
      groupBy,
      sortBy,
      disableSort
    });
    const {
      sortedItems
    } = useSortedItems(props, filteredItems, sortByWithGroups, {
      transform: item => ({
        ...item.raw,
        ...item.columns
      }),
      sortFunctions,
      sortRawFunctions
    });
    const {
      flatItems
    } = useGroupedItems(sortedItems, groupBy, opened);
    const allItems = computed$G(() => extractRows(flatItems.value));
    const {
      isSelected,
      select,
      selectAll,
      toggleSelect,
      someSelected,
      allSelected
    } = provideSelection(props, {
      allItems,
      currentPage: allItems
    });
    const {
      isExpanded,
      toggleExpand
    } = provideExpanded(props);
    const {
      containerRef,
      markerRef,
      paddingTop,
      paddingBottom,
      computedItems,
      handleItemResize,
      handleScroll,
      handleScrollend,
      calculateVisibleItems,
      scrollToIndex
    } = useVirtual(props, flatItems);
    const displayItems = computed$G(() => computedItems.value.map(item => item.raw));
    useOptions({
      sortBy,
      page: shallowRef$g(1),
      itemsPerPage: shallowRef$g(-1),
      groupBy,
      search
    });
    provideDefaults({
      VDataTableRows: {
        hideNoData: toRef$j(() => props.hideNoData),
        noDataText: toRef$j(() => props.noDataText),
        loading: toRef$j(() => props.loading),
        loadingText: toRef$j(() => props.loadingText)
      }
    });
    const slotProps = computed$G(() => ({
      sortBy: sortBy.value,
      toggleSort,
      someSelected: someSelected.value,
      allSelected: allSelected.value,
      isSelected,
      select,
      selectAll,
      toggleSelect,
      isExpanded,
      toggleExpand,
      isGroupOpen,
      toggleGroup,
      items: allItems.value.map(item => item.raw),
      internalItems: allItems.value,
      groupedItems: flatItems.value,
      columns: columns.value,
      headers: headers.value
    }));
    useRender(() => {
      const dataTableHeadersProps = VDataTableHeaders.filterProps(props);
      const dataTableRowsProps = VDataTableRows.filterProps(props);
      const tableProps = VTable.filterProps(props);
      return _createVNode$V(VTable, _mergeProps$s({
        "class": ['v-data-table', {
          'v-data-table--loading': props.loading
        }, props.class],
        "style": props.style
      }, tableProps, {
        "fixedHeader": props.fixedHeader || props.sticky
      }), {
        top: () => slots.top?.(slotProps.value),
        wrapper: () => _createVNode$V("div", {
          "ref": containerRef,
          "onScrollPassive": handleScroll,
          "onScrollend": handleScrollend,
          "class": "v-table__wrapper",
          "style": {
            height: convertToUnit(props.height)
          }
        }, [_createVNode$V("table", null, [slots.colgroup?.(slotProps.value), !props.hideDefaultHeader && _createVNode$V("thead", {
          "key": "thead"
        }, [_createVNode$V(VDataTableHeaders, dataTableHeadersProps, slots)]), slots.thead?.(slotProps.value), !props.hideDefaultBody && _createVNode$V("tbody", {
          "key": "tbody"
        }, [_createVNode$V("tr", {
          "ref": markerRef,
          "style": {
            height: convertToUnit(paddingTop.value),
            border: 0
          }
        }, [_createVNode$V("td", {
          "colspan": columns.value.length,
          "style": {
            height: 0,
            border: 0
          }
        }, null)]), slots['body.prepend']?.(slotProps.value), _createVNode$V(VDataTableRows, _mergeProps$s(attrs, dataTableRowsProps, {
          "items": displayItems.value
        }), {
          ...slots,
          item: itemSlotProps => _createVNode$V(VVirtualScrollItem, {
            "key": itemSlotProps.internalItem.index,
            "renderless": true,
            "onUpdate:height": height => handleItemResize(itemSlotProps.internalItem.index, height)
          }, {
            default: _ref2 => {
              let {
                itemRef
              } = _ref2;
              return slots.item?.({
                ...itemSlotProps,
                itemRef
              }) ?? _createVNode$V(VDataTableRow, _mergeProps$s(itemSlotProps.props, {
                "ref": itemRef,
                "key": itemSlotProps.internalItem.index,
                "index": itemSlotProps.internalItem.index
              }), slots);
            }
          })
        }), slots['body.append']?.(slotProps.value), _createVNode$V("tr", {
          "style": {
            height: convertToUnit(paddingBottom.value),
            border: 0
          }
        }, [_createVNode$V("td", {
          "colspan": columns.value.length,
          "style": {
            height: 0,
            border: 0
          }
        }, null)])]), slots.tbody?.(slotProps.value), slots.tfoot?.(slotProps.value)])]),
        bottom: () => slots.bottom?.(slotProps.value)
      });
    });
    return {
      calculateVisibleItems,
      scrollToIndex
    };
  }
});

const {Fragment:_Fragment$g,createVNode:_createVNode$U,mergeProps:_mergeProps$r} = await importShared('vue');
const {computed: computed$F,provide: provide$1,toRef: toRef$i,toRefs: toRefs$1} = await importShared('vue');
const makeVDataTableServerProps = propsFactory({
  itemsLength: {
    type: [Number, String],
    required: true
  },
  ...makeDataTablePaginateProps(),
  ...makeDataTableProps(),
  ...makeVDataTableFooterProps()
}, 'VDataTableServer');
const VDataTableServer = genericComponent()({
  name: 'VDataTableServer',
  props: makeVDataTableServerProps(),
  emits: {
    'update:modelValue': value => true,
    'update:page': page => true,
    'update:itemsPerPage': page => true,
    'update:sortBy': sortBy => true,
    'update:options': options => true,
    'update:expanded': options => true,
    'update:groupBy': value => true
  },
  setup(props, _ref) {
    let {
      attrs,
      slots
    } = _ref;
    const {
      groupBy
    } = createGroupBy(props);
    const {
      sortBy,
      multiSort,
      mustSort
    } = createSort(props);
    const {
      page,
      itemsPerPage
    } = createPagination(props);
    const {
      disableSort
    } = toRefs$1(props);
    const itemsLength = computed$F(() => parseInt(props.itemsLength, 10));
    const {
      columns,
      headers
    } = createHeaders(props, {
      groupBy,
      showSelect: toRef$i(() => props.showSelect),
      showExpand: toRef$i(() => props.showExpand)
    });
    const {
      items
    } = useDataTableItems(props, columns);
    const {
      toggleSort
    } = provideSort({
      sortBy,
      multiSort,
      mustSort,
      page
    });
    const {
      opened,
      isGroupOpen,
      toggleGroup,
      extractRows
    } = provideGroupBy({
      groupBy,
      sortBy,
      disableSort
    });
    const {
      pageCount,
      setItemsPerPage
    } = providePagination({
      page,
      itemsPerPage,
      itemsLength
    });
    const {
      flatItems
    } = useGroupedItems(items, groupBy, opened);
    const {
      isSelected,
      select,
      selectAll,
      toggleSelect,
      someSelected,
      allSelected
    } = provideSelection(props, {
      allItems: items,
      currentPage: items
    });
    const {
      isExpanded,
      toggleExpand
    } = provideExpanded(props);
    const itemsWithoutGroups = computed$F(() => extractRows(items.value));
    useOptions({
      page,
      itemsPerPage,
      sortBy,
      groupBy,
      search: toRef$i(() => props.search)
    });
    provide$1('v-data-table', {
      toggleSort,
      sortBy
    });
    provideDefaults({
      VDataTableRows: {
        hideNoData: toRef$i(() => props.hideNoData),
        noDataText: toRef$i(() => props.noDataText),
        loading: toRef$i(() => props.loading),
        loadingText: toRef$i(() => props.loadingText)
      }
    });
    const slotProps = computed$F(() => ({
      page: page.value,
      itemsPerPage: itemsPerPage.value,
      sortBy: sortBy.value,
      pageCount: pageCount.value,
      toggleSort,
      setItemsPerPage,
      someSelected: someSelected.value,
      allSelected: allSelected.value,
      isSelected,
      select,
      selectAll,
      toggleSelect,
      isExpanded,
      toggleExpand,
      isGroupOpen,
      toggleGroup,
      items: itemsWithoutGroups.value.map(item => item.raw),
      internalItems: itemsWithoutGroups.value,
      groupedItems: flatItems.value,
      columns: columns.value,
      headers: headers.value
    }));
    useRender(() => {
      const dataTableFooterProps = VDataTableFooter.filterProps(props);
      const dataTableHeadersProps = VDataTableHeaders.filterProps(props);
      const dataTableRowsProps = VDataTableRows.filterProps(props);
      const tableProps = VTable.filterProps(props);
      return _createVNode$U(VTable, _mergeProps$r({
        "class": ['v-data-table', {
          'v-data-table--loading': props.loading
        }, props.class],
        "style": props.style
      }, tableProps, {
        "fixedHeader": props.fixedHeader || props.sticky
      }), {
        top: () => slots.top?.(slotProps.value),
        default: () => slots.default ? slots.default(slotProps.value) : _createVNode$U(_Fragment$g, null, [slots.colgroup?.(slotProps.value), !props.hideDefaultHeader && _createVNode$U("thead", {
          "key": "thead",
          "class": "v-data-table__thead",
          "role": "rowgroup"
        }, [_createVNode$U(VDataTableHeaders, dataTableHeadersProps, slots)]), slots.thead?.(slotProps.value), !props.hideDefaultBody && _createVNode$U("tbody", {
          "class": "v-data-table__tbody",
          "role": "rowgroup"
        }, [slots['body.prepend']?.(slotProps.value), slots.body ? slots.body(slotProps.value) : _createVNode$U(VDataTableRows, _mergeProps$r(attrs, dataTableRowsProps, {
          "items": flatItems.value
        }), slots), slots['body.append']?.(slotProps.value)]), slots.tbody?.(slotProps.value), slots.tfoot?.(slotProps.value)]),
        bottom: () => slots.bottom ? slots.bottom(slotProps.value) : !props.hideDefaultFooter && _createVNode$U(_Fragment$g, null, [_createVNode$U(VDivider, null, null), _createVNode$U(VDataTableFooter, dataTableFooterProps, {
          prepend: slots['footer.prepend']
        })])
      });
    });
  }
});

const {createVNode:_createVNode$T} = await importShared('vue');
const makeVContainerProps = propsFactory({
  fluid: {
    type: Boolean,
    default: false
  },
  ...makeComponentProps(),
  ...makeDimensionProps(),
  ...makeTagProps()
}, 'VContainer');
const VContainer = genericComponent()({
  name: 'VContainer',
  props: makeVContainerProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      rtlClasses
    } = useRtl();
    const {
      dimensionStyles
    } = useDimension(props);
    useRender(() => _createVNode$T(props.tag, {
      "class": ['v-container', {
        'v-container--fluid': props.fluid
      }, rtlClasses.value, props.class],
      "style": [dimensionStyles.value, props.style]
    }, slots));
    return {};
  }
});

const {capitalize: capitalize$1,computed: computed$E,h: h$2} = await importShared('vue');
const breakpointProps = (() => {
  return breakpoints.reduce((props, val) => {
    props[val] = {
      type: [Boolean, String, Number],
      default: false
    };
    return props;
  }, {});
})();
const offsetProps = (() => {
  return breakpoints.reduce((props, val) => {
    const offsetKey = 'offset' + capitalize$1(val);
    props[offsetKey] = {
      type: [String, Number],
      default: null
    };
    return props;
  }, {});
})();
const orderProps = (() => {
  return breakpoints.reduce((props, val) => {
    const orderKey = 'order' + capitalize$1(val);
    props[orderKey] = {
      type: [String, Number],
      default: null
    };
    return props;
  }, {});
})();
const propMap$1 = {
  col: Object.keys(breakpointProps),
  offset: Object.keys(offsetProps),
  order: Object.keys(orderProps)
};
function breakpointClass$1(type, prop, val) {
  let className = type;
  if (val == null || val === false) {
    return undefined;
  }
  if (prop) {
    const breakpoint = prop.replace(type, '');
    className += `-${breakpoint}`;
  }
  if (type === 'col') {
    className = 'v-' + className;
  }
  // Handling the boolean style prop when accepting [Boolean, String, Number]
  // means Vue will not convert <v-col sm></v-col> to sm: true for us.
  // Since the default is false, an empty string indicates the prop's presence.
  if (type === 'col' && (val === '' || val === true)) {
    // .v-col-md
    return className.toLowerCase();
  }
  // .order-md-6
  className += `-${val}`;
  return className.toLowerCase();
}
const ALIGN_SELF_VALUES = ['auto', 'start', 'end', 'center', 'baseline', 'stretch'];
const makeVColProps = propsFactory({
  cols: {
    type: [Boolean, String, Number],
    default: false
  },
  ...breakpointProps,
  offset: {
    type: [String, Number],
    default: null
  },
  ...offsetProps,
  order: {
    type: [String, Number],
    default: null
  },
  ...orderProps,
  alignSelf: {
    type: String,
    default: null,
    validator: str => ALIGN_SELF_VALUES.includes(str)
  },
  ...makeComponentProps(),
  ...makeTagProps()
}, 'VCol');
const VCol = genericComponent()({
  name: 'VCol',
  props: makeVColProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const classes = computed$E(() => {
      const classList = [];

      // Loop through `col`, `offset`, `order` breakpoint props
      let type;
      for (type in propMap$1) {
        propMap$1[type].forEach(prop => {
          const value = props[prop];
          const className = breakpointClass$1(type, prop, value);
          if (className) classList.push(className);
        });
      }
      const hasColClasses = classList.some(className => className.startsWith('v-col-'));
      classList.push({
        // Default to .v-col if no other col-{bp}-* classes generated nor `cols` specified.
        'v-col': !hasColClasses || !props.cols,
        [`v-col-${props.cols}`]: props.cols,
        [`offset-${props.offset}`]: props.offset,
        [`order-${props.order}`]: props.order,
        [`align-self-${props.alignSelf}`]: props.alignSelf
      });
      return classList;
    });
    return () => h$2(props.tag, {
      class: [classes.value, props.class],
      style: props.style
    }, slots.default?.());
  }
});

const {capitalize,computed: computed$D,h: h$1} = await importShared('vue');
const ALIGNMENT = ['start', 'end', 'center'];
const SPACE = ['space-between', 'space-around', 'space-evenly'];
function makeRowProps(prefix, def) {
  return breakpoints.reduce((props, val) => {
    const prefixKey = prefix + capitalize(val);
    props[prefixKey] = def();
    return props;
  }, {});
}
const ALIGN_VALUES = [...ALIGNMENT, 'baseline', 'stretch'];
const alignValidator = str => ALIGN_VALUES.includes(str);
const alignProps = makeRowProps('align', () => ({
  type: String,
  default: null,
  validator: alignValidator
}));
const JUSTIFY_VALUES = [...ALIGNMENT, ...SPACE];
const justifyValidator = str => JUSTIFY_VALUES.includes(str);
const justifyProps = makeRowProps('justify', () => ({
  type: String,
  default: null,
  validator: justifyValidator
}));
const ALIGN_CONTENT_VALUES = [...ALIGNMENT, ...SPACE, 'stretch'];
const alignContentValidator = str => ALIGN_CONTENT_VALUES.includes(str);
const alignContentProps = makeRowProps('alignContent', () => ({
  type: String,
  default: null,
  validator: alignContentValidator
}));
const propMap = {
  align: Object.keys(alignProps),
  justify: Object.keys(justifyProps),
  alignContent: Object.keys(alignContentProps)
};
const classMap = {
  align: 'align',
  justify: 'justify',
  alignContent: 'align-content'
};
function breakpointClass(type, prop, val) {
  let className = classMap[type];
  if (val == null) {
    return undefined;
  }
  if (prop) {
    // alignSm -> Sm
    const breakpoint = prop.replace(type, '');
    className += `-${breakpoint}`;
  }
  // .align-items-sm-center
  className += `-${val}`;
  return className.toLowerCase();
}
const makeVRowProps = propsFactory({
  dense: Boolean,
  noGutters: Boolean,
  align: {
    type: String,
    default: null,
    validator: alignValidator
  },
  ...alignProps,
  justify: {
    type: String,
    default: null,
    validator: justifyValidator
  },
  ...justifyProps,
  alignContent: {
    type: String,
    default: null,
    validator: alignContentValidator
  },
  ...alignContentProps,
  ...makeComponentProps(),
  ...makeTagProps()
}, 'VRow');
const VRow = genericComponent()({
  name: 'VRow',
  props: makeVRowProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const classes = computed$D(() => {
      const classList = [];

      // Loop through `align`, `justify`, `alignContent` breakpoint props
      let type;
      for (type in propMap) {
        propMap[type].forEach(prop => {
          const value = props[prop];
          const className = breakpointClass(type, prop, value);
          if (className) classList.push(className);
        });
      }
      classList.push({
        'v-row--no-gutters': props.noGutters,
        'v-row--dense': props.dense,
        [`align-${props.align}`]: props.align,
        [`justify-${props.justify}`]: props.justify,
        [`align-content-${props.alignContent}`]: props.alignContent
      });
      return classList;
    });
    return () => h$1(props.tag, {
      class: ['v-row', classes.value, props.class],
      style: props.style
    }, slots.default?.());
  }
});

// Styles
const VSpacer = createSimpleFunctional('v-spacer', 'div', 'VSpacer');

const {createVNode:_createVNode$S} = await importShared('vue');
const {computed: computed$C} = await importShared('vue');
const makeVDatePickerControlsProps = propsFactory({
  active: {
    type: [String, Array],
    default: undefined
  },
  controlHeight: [Number, String],
  disabled: {
    type: [Boolean, String, Array],
    default: null
  },
  nextIcon: {
    type: IconValue,
    default: '$next'
  },
  prevIcon: {
    type: IconValue,
    default: '$prev'
  },
  modeIcon: {
    type: IconValue,
    default: '$subgroup'
  },
  text: String,
  viewMode: {
    type: String,
    default: 'month'
  }
}, 'VDatePickerControls');
const VDatePickerControls = genericComponent()({
  name: 'VDatePickerControls',
  props: makeVDatePickerControlsProps(),
  emits: {
    'click:year': () => true,
    'click:month': () => true,
    'click:prev': () => true,
    'click:next': () => true,
    'click:text': () => true
  },
  setup(props, _ref) {
    let {
      emit
    } = _ref;
    const disableMonth = computed$C(() => {
      return Array.isArray(props.disabled) ? props.disabled.includes('text') : !!props.disabled;
    });
    const disableYear = computed$C(() => {
      return Array.isArray(props.disabled) ? props.disabled.includes('mode') : !!props.disabled;
    });
    const disablePrev = computed$C(() => {
      return Array.isArray(props.disabled) ? props.disabled.includes('prev') : !!props.disabled;
    });
    const disableNext = computed$C(() => {
      return Array.isArray(props.disabled) ? props.disabled.includes('next') : !!props.disabled;
    });
    function onClickPrev() {
      emit('click:prev');
    }
    function onClickNext() {
      emit('click:next');
    }
    function onClickYear() {
      emit('click:year');
    }
    function onClickMonth() {
      emit('click:month');
    }
    useRender(() => {
      // TODO: add slot support and scope defaults
      return _createVNode$S("div", {
        "class": ['v-date-picker-controls'],
        "style": {
          '--v-date-picker-controls-height': convertToUnit(props.controlHeight)
        }
      }, [_createVNode$S(VBtn, {
        "class": "v-date-picker-controls__month-btn",
        "data-testid": "month-btn",
        "disabled": disableMonth.value,
        "text": props.text,
        "variant": "text",
        "rounded": true,
        "onClick": onClickMonth
      }, null), _createVNode$S(VBtn, {
        "class": "v-date-picker-controls__mode-btn",
        "data-testid": "year-btn",
        "disabled": disableYear.value,
        "density": "comfortable",
        "icon": props.modeIcon,
        "variant": "text",
        "onClick": onClickYear
      }, null), _createVNode$S(VSpacer, null, null), _createVNode$S("div", {
        "class": "v-date-picker-controls__month"
      }, [_createVNode$S(VBtn, {
        "data-testid": "prev-month",
        "disabled": disablePrev.value,
        "density": "comfortable",
        "icon": props.prevIcon,
        "variant": "text",
        "onClick": onClickPrev
      }, null), _createVNode$S(VBtn, {
        "data-testid": "next-month",
        "disabled": disableNext.value,
        "icon": props.nextIcon,
        "density": "comfortable",
        "variant": "text",
        "onClick": onClickNext
      }, null)])]);
    });
    return {};
  }
});

const {createVNode:_createVNode$R} = await importShared('vue');
const makeVDatePickerHeaderProps = propsFactory({
  appendIcon: IconValue,
  color: String,
  header: String,
  transition: String,
  onClick: EventProp()
}, 'VDatePickerHeader');
const VDatePickerHeader = genericComponent()({
  name: 'VDatePickerHeader',
  props: makeVDatePickerHeaderProps(),
  emits: {
    click: () => true,
    'click:append': () => true
  },
  setup(props, _ref) {
    let {
      emit,
      slots
    } = _ref;
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.color);
    function onClick() {
      emit('click');
    }
    function onClickAppend() {
      emit('click:append');
    }
    useRender(() => {
      const hasContent = !!(slots.default || props.header);
      const hasAppend = !!(slots.append || props.appendIcon);
      return _createVNode$R("div", {
        "class": ['v-date-picker-header', {
          'v-date-picker-header--clickable': !!props.onClick
        }, backgroundColorClasses.value],
        "style": backgroundColorStyles.value,
        "onClick": onClick
      }, [slots.prepend && _createVNode$R("div", {
        "key": "prepend",
        "class": "v-date-picker-header__prepend"
      }, [slots.prepend()]), hasContent && _createVNode$R(MaybeTransition, {
        "key": "content",
        "name": props.transition
      }, {
        default: () => [_createVNode$R("div", {
          "key": props.header,
          "class": "v-date-picker-header__content"
        }, [slots.default?.() ?? props.header])]
      }), hasAppend && _createVNode$R("div", {
        "class": "v-date-picker-header__append"
      }, [!slots.append ? _createVNode$R(VBtn, {
        "key": "append-btn",
        "icon": props.appendIcon,
        "variant": "text",
        "onClick": onClickAppend
      }, null) : _createVNode$R(VDefaultsProvider, {
        "key": "append-defaults",
        "disabled": !props.appendIcon,
        "defaults": {
          VBtn: {
            icon: props.appendIcon,
            variant: 'text'
          }
        }
      }, {
        default: () => [slots.append?.()]
      })])]);
    });
    return {};
  }
});

const {computed: computed$B} = await importShared('vue');
// Types
// Composables
const makeCalendarProps = propsFactory({
  allowedDates: [Array, Function],
  disabled: {
    type: Boolean,
    default: null
  },
  displayValue: null,
  modelValue: Array,
  month: [Number, String],
  max: null,
  min: null,
  showAdjacentMonths: Boolean,
  year: [Number, String],
  weekdays: {
    type: Array,
    default: () => [0, 1, 2, 3, 4, 5, 6]
  },
  weeksInMonth: {
    type: String,
    default: 'dynamic'
  },
  firstDayOfWeek: {
    type: [Number, String],
    default: undefined
  }
}, 'calendar');
function useCalendar(props) {
  const adapter = useDate();
  const model = useProxiedModel(props, 'modelValue', [], v => wrapInArray(v).map(i => adapter.date(i)));
  const displayValue = computed$B(() => {
    if (props.displayValue) return adapter.date(props.displayValue);
    if (model.value.length > 0) return adapter.date(model.value[0]);
    if (props.min) return adapter.date(props.min);
    if (Array.isArray(props.allowedDates)) return adapter.date(props.allowedDates[0]);
    return adapter.date();
  });
  const year = useProxiedModel(props, 'year', undefined, v => {
    const value = v != null ? Number(v) : adapter.getYear(displayValue.value);
    return adapter.startOfYear(adapter.setYear(adapter.date(), value));
  }, v => adapter.getYear(v));
  const month = useProxiedModel(props, 'month', undefined, v => {
    const value = v != null ? Number(v) : adapter.getMonth(displayValue.value);
    const date = adapter.setYear(adapter.startOfMonth(adapter.date()), adapter.getYear(year.value));
    return adapter.setMonth(date, value);
  }, v => adapter.getMonth(v));
  const weekDays = computed$B(() => {
    const firstDayOfWeek = adapter.toJsDate(adapter.startOfWeek(adapter.date(), props.firstDayOfWeek)).getDay();
    // Always generate all days, regardless of props.weekdays
    return [0, 1, 2, 3, 4, 5, 6].map(day => (day + firstDayOfWeek) % 7);
  });
  const weeksInMonth = computed$B(() => {
    const weeks = adapter.getWeekArray(month.value, props.firstDayOfWeek);
    const days = weeks.flat();

    // Make sure there's always 6 weeks in month (6 * 7 days)
    // if weeksInMonth is 'static'
    const daysInMonth = 6 * 7;
    if (props.weeksInMonth === 'static' && days.length < daysInMonth) {
      const lastDay = days[days.length - 1];
      let week = [];
      for (let day = 1; day <= daysInMonth - days.length; day++) {
        week.push(adapter.addDays(lastDay, day));
        if (day % 7 === 0) {
          weeks.push(week);
          week = [];
        }
      }
    }
    return weeks;
  });
  function genDays(days, today) {
    return days.filter(date => {
      return weekDays.value.includes(adapter.toJsDate(date).getDay());
    }).map((date, index) => {
      const isoDate = adapter.toISO(date);
      const isAdjacent = !adapter.isSameMonth(date, month.value);
      const isStart = adapter.isSameDay(date, adapter.startOfMonth(month.value));
      const isEnd = adapter.isSameDay(date, adapter.endOfMonth(month.value));
      const isSame = adapter.isSameDay(date, month.value);
      return {
        date,
        formatted: adapter.format(date, 'keyboardDate'),
        isAdjacent,
        isDisabled: isDisabled(date),
        isEnd,
        isHidden: isAdjacent && !props.showAdjacentMonths,
        isSame,
        isSelected: model.value.some(value => adapter.isSameDay(date, value)),
        isStart,
        isToday: adapter.isSameDay(date, today),
        isWeekEnd: index % 7 === 6,
        isWeekStart: index % 7 === 0,
        isoDate,
        localized: adapter.format(date, 'dayOfMonth'),
        month: adapter.getMonth(date),
        year: adapter.getYear(date)
      };
    });
  }
  const daysInWeek = computed$B(() => {
    const lastDay = adapter.startOfWeek(displayValue.value, props.firstDayOfWeek);
    const week = [];
    for (let day = 0; day <= 6; day++) {
      week.push(adapter.addDays(lastDay, day));
    }
    const today = adapter.date();
    return genDays(week, today);
  });
  const daysInMonth = computed$B(() => {
    const days = weeksInMonth.value.flat();
    const today = adapter.date();
    return genDays(days, today);
  });
  const weekNumbers = computed$B(() => {
    return weeksInMonth.value.map(week => {
      return week.length ? adapter.getWeek(week[0], props.firstDayOfWeek) : null;
    });
  });
  function isDisabled(value) {
    if (props.disabled) return true;
    const date = adapter.date(value);
    if (props.min && adapter.isAfter(adapter.date(props.min), date)) return true;
    if (props.max && adapter.isAfter(date, adapter.date(props.max))) return true;
    if (Array.isArray(props.allowedDates) && props.allowedDates.length > 0) {
      return !props.allowedDates.some(d => adapter.isSameDay(adapter.date(d), date));
    }
    if (typeof props.allowedDates === 'function') {
      return !props.allowedDates(date);
    }
    return !props.weekdays.includes(adapter.toJsDate(date).getDay());
  }
  return {
    displayValue,
    daysInMonth,
    daysInWeek,
    genDays,
    model,
    weeksInMonth,
    weekDays,
    weekNumbers
  };
}

const {createTextVNode:_createTextVNode$2,createVNode:_createVNode$Q} = await importShared('vue');
const {computed: computed$A,ref: ref$j,shallowRef: shallowRef$f,toRef: toRef$h,watch: watch$d} = await importShared('vue');
const makeVDatePickerMonthProps = propsFactory({
  color: String,
  hideWeekdays: Boolean,
  multiple: [Boolean, Number, String],
  showWeek: Boolean,
  transition: {
    type: String,
    default: 'picker-transition'
  },
  reverseTransition: {
    type: String,
    default: 'picker-reverse-transition'
  },
  ...omit(makeCalendarProps(), ['displayValue'])
}, 'VDatePickerMonth');
const VDatePickerMonth = genericComponent()({
  name: 'VDatePickerMonth',
  props: makeVDatePickerMonthProps(),
  emits: {
    'update:modelValue': date => true,
    'update:month': date => true,
    'update:year': date => true
  },
  setup(props, _ref) {
    let {
      emit,
      slots
    } = _ref;
    const daysRef = ref$j();
    const {
      daysInMonth,
      model,
      weekNumbers
    } = useCalendar(props);
    const adapter = useDate();
    const rangeStart = shallowRef$f();
    const rangeStop = shallowRef$f();
    const isReverse = shallowRef$f(false);
    const transition = toRef$h(() => {
      return !isReverse.value ? props.transition : props.reverseTransition;
    });
    if (props.multiple === 'range' && model.value.length > 0) {
      rangeStart.value = model.value[0];
      if (model.value.length > 1) {
        rangeStop.value = model.value[model.value.length - 1];
      }
    }
    const atMax = computed$A(() => {
      const max = ['number', 'string'].includes(typeof props.multiple) ? Number(props.multiple) : Infinity;
      return model.value.length >= max;
    });
    watch$d(daysInMonth, (val, oldVal) => {
      if (!oldVal) return;
      isReverse.value = adapter.isBefore(val[0].date, oldVal[0].date);
    });
    function onRangeClick(value) {
      const _value = adapter.startOfDay(value);
      if (model.value.length === 0) {
        rangeStart.value = undefined;
      } else if (model.value.length === 1) {
        rangeStart.value = model.value[0];
        rangeStop.value = undefined;
      }
      if (!rangeStart.value) {
        rangeStart.value = _value;
        model.value = [rangeStart.value];
      } else if (!rangeStop.value) {
        if (adapter.isSameDay(_value, rangeStart.value)) {
          rangeStart.value = undefined;
          model.value = [];
          return;
        } else if (adapter.isBefore(_value, rangeStart.value)) {
          rangeStop.value = adapter.endOfDay(rangeStart.value);
          rangeStart.value = _value;
        } else {
          rangeStop.value = adapter.endOfDay(_value);
        }
        const diff = adapter.getDiff(rangeStop.value, rangeStart.value, 'days');
        const datesInRange = [rangeStart.value];
        for (let i = 1; i < diff; i++) {
          const nextDate = adapter.addDays(rangeStart.value, i);
          datesInRange.push(nextDate);
        }
        datesInRange.push(rangeStop.value);
        model.value = datesInRange;
      } else {
        rangeStart.value = value;
        rangeStop.value = undefined;
        model.value = [rangeStart.value];
      }
    }
    function onMultipleClick(value) {
      const index = model.value.findIndex(selection => adapter.isSameDay(selection, value));
      if (index === -1) {
        model.value = [...model.value, value];
      } else {
        const value = [...model.value];
        value.splice(index, 1);
        model.value = value;
      }
    }
    function onClick(value) {
      if (props.multiple === 'range') {
        onRangeClick(value);
      } else if (props.multiple) {
        onMultipleClick(value);
      } else {
        model.value = [value];
      }
    }
    useRender(() => _createVNode$Q("div", {
      "class": "v-date-picker-month"
    }, [props.showWeek && _createVNode$Q("div", {
      "key": "weeks",
      "class": "v-date-picker-month__weeks"
    }, [!props.hideWeekdays && _createVNode$Q("div", {
      "key": "hide-week-days",
      "class": "v-date-picker-month__day"
    }, [_createTextVNode$2("\xA0")]), weekNumbers.value.map(week => _createVNode$Q("div", {
      "class": ['v-date-picker-month__day', 'v-date-picker-month__day--adjacent']
    }, [week]))]), _createVNode$Q(MaybeTransition, {
      "name": transition.value
    }, {
      default: () => [_createVNode$Q("div", {
        "ref": daysRef,
        "key": daysInMonth.value[0].date?.toString(),
        "class": "v-date-picker-month__days"
      }, [!props.hideWeekdays && adapter.getWeekdays(props.firstDayOfWeek).map(weekDay => _createVNode$Q("div", {
        "class": ['v-date-picker-month__day', 'v-date-picker-month__weekday']
      }, [weekDay])), daysInMonth.value.map((item, i) => {
        const slotProps = {
          props: {
            class: 'v-date-picker-month__day-btn',
            color: item.isSelected || item.isToday ? props.color : undefined,
            disabled: item.isDisabled,
            icon: true,
            ripple: false,
            text: item.localized,
            variant: item.isSelected ? 'flat' : item.isToday ? 'outlined' : 'text',
            onClick: () => onClick(item.date)
          },
          item,
          i
        };
        if (atMax.value && !item.isSelected) {
          item.isDisabled = true;
        }
        return _createVNode$Q("div", {
          "class": ['v-date-picker-month__day', {
            'v-date-picker-month__day--adjacent': item.isAdjacent,
            'v-date-picker-month__day--hide-adjacent': item.isHidden,
            'v-date-picker-month__day--selected': item.isSelected,
            'v-date-picker-month__day--week-end': item.isWeekEnd,
            'v-date-picker-month__day--week-start': item.isWeekStart
          }],
          "data-v-date": !item.isDisabled ? item.isoDate : undefined
        }, [(props.showAdjacentMonths || !item.isAdjacent) && (slots.day?.(slotProps) ?? _createVNode$Q(VBtn, slotProps.props, null))]);
      })])]
    })]));
  }
});

const {mergeProps:_mergeProps$q,createVNode:_createVNode$P} = await importShared('vue');
const {computed: computed$z,watchEffect: watchEffect$8} = await importShared('vue');
const makeVDatePickerMonthsProps = propsFactory({
  color: String,
  height: [String, Number],
  min: null,
  max: null,
  modelValue: Number,
  year: Number
}, 'VDatePickerMonths');
const VDatePickerMonths = genericComponent()({
  name: 'VDatePickerMonths',
  props: makeVDatePickerMonthsProps(),
  emits: {
    'update:modelValue': date => true
  },
  setup(props, _ref) {
    let {
      emit,
      slots
    } = _ref;
    const adapter = useDate();
    const model = useProxiedModel(props, 'modelValue');
    const months = computed$z(() => {
      let date = adapter.startOfYear(adapter.date());
      if (props.year) {
        date = adapter.setYear(date, props.year);
      }
      return createRange(12).map(i => {
        const text = adapter.format(date, 'monthShort');
        const isDisabled = !!(props.min && adapter.isAfter(adapter.startOfMonth(adapter.date(props.min)), date) || props.max && adapter.isAfter(date, adapter.startOfMonth(adapter.date(props.max))));
        date = adapter.getNextMonth(date);
        return {
          isDisabled,
          text,
          value: i
        };
      });
    });
    watchEffect$8(() => {
      model.value = model.value ?? adapter.getMonth(adapter.date());
    });
    useRender(() => _createVNode$P("div", {
      "class": "v-date-picker-months",
      "style": {
        height: convertToUnit(props.height)
      }
    }, [_createVNode$P("div", {
      "class": "v-date-picker-months__content"
    }, [months.value.map((month, i) => {
      const btnProps = {
        active: model.value === i,
        color: model.value === i ? props.color : undefined,
        disabled: month.isDisabled,
        rounded: true,
        text: month.text,
        variant: model.value === month.value ? 'flat' : 'text',
        onClick: () => onClick(i)
      };
      function onClick(i) {
        if (model.value === i) {
          emit('update:modelValue', model.value);
          return;
        }
        model.value = i;
      }
      return slots.month?.({
        month,
        i,
        props: btnProps
      }) ?? _createVNode$P(VBtn, _mergeProps$q({
        "key": "month"
      }, btnProps), null);
    })])]));
    return {};
  }
});

const {mergeProps:_mergeProps$p,createVNode:_createVNode$O} = await importShared('vue');
const {computed: computed$y,nextTick: nextTick$9,onMounted: onMounted$6,watchEffect: watchEffect$7} = await importShared('vue');
// Types
const makeVDatePickerYearsProps = propsFactory({
  color: String,
  height: [String, Number],
  min: null,
  max: null,
  modelValue: Number
}, 'VDatePickerYears');
const VDatePickerYears = genericComponent()({
  name: 'VDatePickerYears',
  props: makeVDatePickerYearsProps(),
  emits: {
    'update:modelValue': year => true
  },
  setup(props, _ref) {
    let {
      emit,
      slots
    } = _ref;
    const adapter = useDate();
    const model = useProxiedModel(props, 'modelValue');
    const years = computed$y(() => {
      const year = adapter.getYear(adapter.date());
      let min = year - 100;
      let max = year + 52;
      if (props.min) {
        min = adapter.getYear(adapter.date(props.min));
      }
      if (props.max) {
        max = adapter.getYear(adapter.date(props.max));
      }
      let date = adapter.startOfYear(adapter.date());
      date = adapter.setYear(date, min);
      return createRange(max - min + 1, min).map(i => {
        const text = adapter.format(date, 'year');
        date = adapter.setYear(date, adapter.getYear(date) + 1);
        return {
          text,
          value: i
        };
      });
    });
    watchEffect$7(() => {
      model.value = model.value ?? adapter.getYear(adapter.date());
    });
    const yearRef = templateRef();
    onMounted$6(async () => {
      await nextTick$9();
      yearRef.el?.scrollIntoView({
        block: 'center'
      });
    });
    useRender(() => _createVNode$O("div", {
      "class": "v-date-picker-years",
      "style": {
        height: convertToUnit(props.height)
      }
    }, [_createVNode$O("div", {
      "class": "v-date-picker-years__content"
    }, [years.value.map((year, i) => {
      const btnProps = {
        ref: model.value === year.value ? yearRef : undefined,
        active: model.value === year.value,
        color: model.value === year.value ? props.color : undefined,
        rounded: true,
        text: year.text,
        variant: model.value === year.value ? 'flat' : 'text',
        onClick: () => {
          if (model.value === year.value) {
            emit('update:modelValue', model.value);
            return;
          }
          model.value = year.value;
        }
      };
      return slots.year?.({
        year,
        i,
        props: btnProps
      }) ?? _createVNode$O(VBtn, _mergeProps$p({
        "key": "month"
      }, btnProps), null);
    })])]));
    return {};
  }
});

const {createVNode:_createVNode$N,mergeProps:_mergeProps$o,Fragment:_Fragment$f} = await importShared('vue');
const {computed: computed$x,ref: ref$i,shallowRef: shallowRef$e,toRef: toRef$g,watch: watch$c} = await importShared('vue');
// Types
const makeVDatePickerProps = propsFactory({
  // TODO: implement in v3.5
  // calendarIcon: {
  //   type: String,
  //   default: '$calendar',
  // },
  // keyboardIcon: {
  //   type: String,
  //   default: '$edit',
  // },
  // inputMode: {
  //   type: String as PropType<'calendar' | 'keyboard'>,
  //   default: 'calendar',
  // },
  // inputText: {
  //   type: String,
  //   default: '$vuetify.datePicker.input.placeholder',
  // },
  // inputPlaceholder: {
  //   type: String,
  //   default: 'dd/mm/yyyy',
  // },
  header: {
    type: String,
    default: '$vuetify.datePicker.header'
  },
  headerColor: String,
  ...makeVDatePickerControlsProps(),
  ...makeVDatePickerMonthProps({
    weeksInMonth: 'static'
  }),
  ...omit(makeVDatePickerMonthsProps(), ['modelValue']),
  ...omit(makeVDatePickerYearsProps(), ['modelValue']),
  ...makeVPickerProps({
    title: '$vuetify.datePicker.title'
  }),
  modelValue: null
}, 'VDatePicker');
const VDatePicker = genericComponent()({
  name: 'VDatePicker',
  props: makeVDatePickerProps(),
  emits: {
    'update:modelValue': date => true,
    'update:month': date => true,
    'update:year': date => true,
    // 'update:inputMode': (date: any) => true,
    'update:viewMode': date => true
  },
  setup(props, _ref) {
    let {
      emit,
      slots
    } = _ref;
    const adapter = useDate();
    const {
      t
    } = useLocale();
    const {
      rtlClasses
    } = useRtl();
    const model = useProxiedModel(props, 'modelValue', undefined, v => wrapInArray(v).map(i => adapter.date(i)), v => props.multiple ? v : v[0]);
    const viewMode = useProxiedModel(props, 'viewMode');
    // const inputMode = useProxiedModel(props, 'inputMode')

    const minDate = computed$x(() => {
      const date = adapter.date(props.min);
      return props.min && adapter.isValid(date) ? date : null;
    });
    const maxDate = computed$x(() => {
      const date = adapter.date(props.max);
      return props.max && adapter.isValid(date) ? date : null;
    });
    const internal = computed$x(() => {
      const today = adapter.date();
      let value = today;
      if (model.value?.[0]) {
        value = adapter.date(model.value[0]);
      } else if (minDate.value && adapter.isBefore(today, minDate.value)) {
        value = minDate.value;
      } else if (maxDate.value && adapter.isAfter(today, maxDate.value)) {
        value = maxDate.value;
      }
      return value && adapter.isValid(value) ? value : today;
    });
    const headerColor = toRef$g(() => props.headerColor ?? props.color);
    const month = ref$i(Number(props.month ?? adapter.getMonth(adapter.startOfMonth(internal.value))));
    const year = ref$i(Number(props.year ?? adapter.getYear(adapter.startOfYear(adapter.setMonth(internal.value, month.value)))));
    const isReversing = shallowRef$e(false);
    const header = computed$x(() => {
      if (props.multiple && model.value.length > 1) {
        return t('$vuetify.datePicker.itemsSelected', model.value.length);
      }
      return model.value[0] && adapter.isValid(model.value[0]) ? adapter.format(adapter.date(model.value[0]), 'normalDateWithWeekday') : t(props.header);
    });
    const text = computed$x(() => {
      let date = adapter.date();
      date = adapter.setDate(date, 1);
      date = adapter.setMonth(date, month.value);
      date = adapter.setYear(date, year.value);
      return adapter.format(date, 'monthAndYear');
    });
    // const headerIcon = toRef(() => props.inputMode === 'calendar' ? props.keyboardIcon : props.calendarIcon)
    const headerTransition = toRef$g(() => `date-picker-header${isReversing.value ? '-reverse' : ''}-transition`);
    const disabled = computed$x(() => {
      if (props.disabled) return true;
      const targets = [];
      if (viewMode.value !== 'month') {
        targets.push(...['prev', 'next']);
      } else {
        let _date = adapter.date();
        _date = adapter.startOfMonth(_date);
        _date = adapter.setMonth(_date, month.value);
        _date = adapter.setYear(_date, year.value);
        if (minDate.value) {
          const date = adapter.addDays(adapter.startOfMonth(_date), -1);
          adapter.isAfter(minDate.value, date) && targets.push('prev');
        }
        if (maxDate.value) {
          const date = adapter.addDays(adapter.endOfMonth(_date), 1);
          adapter.isAfter(date, maxDate.value) && targets.push('next');
        }
      }
      return targets;
    });

    // function onClickAppend () {
    //   inputMode.value = inputMode.value === 'calendar' ? 'keyboard' : 'calendar'
    // }

    function onClickNext() {
      if (month.value < 11) {
        month.value++;
      } else {
        year.value++;
        month.value = 0;
        onUpdateYear(year.value);
      }
      onUpdateMonth(month.value);
    }
    function onClickPrev() {
      if (month.value > 0) {
        month.value--;
      } else {
        year.value--;
        month.value = 11;
        onUpdateYear(year.value);
      }
      onUpdateMonth(month.value);
    }
    function onClickDate() {
      viewMode.value = 'month';
    }
    function onClickMonth() {
      viewMode.value = viewMode.value === 'months' ? 'month' : 'months';
    }
    function onClickYear() {
      viewMode.value = viewMode.value === 'year' ? 'month' : 'year';
    }
    function onUpdateMonth(value) {
      if (viewMode.value === 'months') onClickMonth();
      emit('update:month', value);
    }
    function onUpdateYear(value) {
      if (viewMode.value === 'year') onClickYear();
      emit('update:year', value);
    }
    watch$c(model, (val, oldVal) => {
      const arrBefore = wrapInArray(oldVal);
      const arrAfter = wrapInArray(val);
      if (!arrAfter.length) return;
      const before = adapter.date(arrBefore[arrBefore.length - 1]);
      const after = adapter.date(arrAfter[arrAfter.length - 1]);
      const newMonth = adapter.getMonth(after);
      const newYear = adapter.getYear(after);
      if (newMonth !== month.value) {
        month.value = newMonth;
        onUpdateMonth(month.value);
      }
      if (newYear !== year.value) {
        year.value = newYear;
        onUpdateYear(year.value);
      }
      isReversing.value = adapter.isBefore(before, after);
    });
    useRender(() => {
      const pickerProps = VPicker.filterProps(props);
      const datePickerControlsProps = VDatePickerControls.filterProps(props);
      const datePickerHeaderProps = VDatePickerHeader.filterProps(props);
      const datePickerMonthProps = VDatePickerMonth.filterProps(props);
      const datePickerMonthsProps = omit(VDatePickerMonths.filterProps(props), ['modelValue']);
      const datePickerYearsProps = omit(VDatePickerYears.filterProps(props), ['modelValue']);
      const headerProps = {
        color: headerColor.value,
        header: header.value,
        transition: headerTransition.value
      };
      return _createVNode$N(VPicker, _mergeProps$o(pickerProps, {
        "color": headerColor.value,
        "class": ['v-date-picker', `v-date-picker--${viewMode.value}`, {
          'v-date-picker--show-week': props.showWeek
        }, rtlClasses.value, props.class],
        "style": props.style
      }), {
        title: () => slots.title?.() ?? _createVNode$N("div", {
          "class": "v-date-picker__title"
        }, [t(props.title)]),
        header: () => slots.header ? _createVNode$N(VDefaultsProvider, {
          "defaults": {
            VDatePickerHeader: {
              ...headerProps
            }
          }
        }, {
          default: () => [slots.header?.(headerProps)]
        }) : _createVNode$N(VDatePickerHeader, _mergeProps$o({
          "key": "header"
        }, datePickerHeaderProps, headerProps, {
          "onClick": viewMode.value !== 'month' ? onClickDate : undefined
        }), {
          ...slots,
          default: undefined
        }),
        default: () => _createVNode$N(_Fragment$f, null, [_createVNode$N(VDatePickerControls, _mergeProps$o(datePickerControlsProps, {
          "disabled": disabled.value,
          "text": text.value,
          "onClick:next": onClickNext,
          "onClick:prev": onClickPrev,
          "onClick:month": onClickMonth,
          "onClick:year": onClickYear
        }), null), _createVNode$N(VFadeTransition, {
          "hideOnLeave": true
        }, {
          default: () => [viewMode.value === 'months' ? _createVNode$N(VDatePickerMonths, _mergeProps$o({
            "key": "date-picker-months"
          }, datePickerMonthsProps, {
            "modelValue": month.value,
            "onUpdate:modelValue": [$event => month.value = $event, onUpdateMonth],
            "min": minDate.value,
            "max": maxDate.value,
            "year": year.value
          }), null) : viewMode.value === 'year' ? _createVNode$N(VDatePickerYears, _mergeProps$o({
            "key": "date-picker-years"
          }, datePickerYearsProps, {
            "modelValue": year.value,
            "onUpdate:modelValue": [$event => year.value = $event, onUpdateYear],
            "min": minDate.value,
            "max": maxDate.value
          }), null) : _createVNode$N(VDatePickerMonth, _mergeProps$o({
            "key": "date-picker-month"
          }, datePickerMonthProps, {
            "modelValue": model.value,
            "onUpdate:modelValue": $event => model.value = $event,
            "month": month.value,
            "onUpdate:month": [$event => month.value = $event, onUpdateMonth],
            "year": year.value,
            "onUpdate:year": [$event => year.value = $event, onUpdateYear],
            "min": minDate.value,
            "max": maxDate.value
          }), null)]
        })]),
        actions: slots.actions
      });
    });
    return {};
  }
});

const {Fragment:_Fragment$e,createVNode:_createVNode$M} = await importShared('vue');
// Types
const makeVEmptyStateProps = propsFactory({
  actionText: String,
  bgColor: String,
  color: String,
  icon: IconValue,
  image: String,
  justify: {
    type: String,
    default: 'center'
  },
  headline: String,
  title: String,
  text: String,
  textWidth: {
    type: [Number, String],
    default: 500
  },
  href: String,
  to: String,
  ...makeComponentProps(),
  ...makeDimensionProps(),
  ...makeSizeProps({
    size: undefined
  }),
  ...makeThemeProps()
}, 'VEmptyState');
const VEmptyState = genericComponent()({
  name: 'VEmptyState',
  props: makeVEmptyStateProps(),
  emits: {
    'click:action': e => true
  },
  setup(props, _ref) {
    let {
      emit,
      slots
    } = _ref;
    const {
      themeClasses
    } = provideTheme(props);
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.bgColor);
    const {
      dimensionStyles
    } = useDimension(props);
    const {
      displayClasses
    } = useDisplay();
    function onClickAction(e) {
      emit('click:action', e);
    }
    useRender(() => {
      const hasActions = !!(slots.actions || props.actionText);
      const hasHeadline = !!(slots.headline || props.headline);
      const hasTitle = !!(slots.title || props.title);
      const hasText = !!(slots.text || props.text);
      const hasMedia = !!(slots.media || props.image || props.icon);
      const size = props.size || (props.image ? 200 : 96);
      return _createVNode$M("div", {
        "class": ['v-empty-state', {
          [`v-empty-state--${props.justify}`]: true
        }, themeClasses.value, backgroundColorClasses.value, displayClasses.value, props.class],
        "style": [backgroundColorStyles.value, dimensionStyles.value, props.style]
      }, [hasMedia && _createVNode$M("div", {
        "key": "media",
        "class": "v-empty-state__media"
      }, [!slots.media ? _createVNode$M(_Fragment$e, null, [props.image ? _createVNode$M(VImg, {
        "key": "image",
        "src": props.image,
        "height": size
      }, null) : props.icon ? _createVNode$M(VIcon, {
        "key": "icon",
        "color": props.color,
        "size": size,
        "icon": props.icon
      }, null) : undefined]) : _createVNode$M(VDefaultsProvider, {
        "key": "media-defaults",
        "defaults": {
          VImg: {
            src: props.image,
            height: size
          },
          VIcon: {
            size,
            icon: props.icon
          }
        }
      }, {
        default: () => [slots.media()]
      })]), hasHeadline && _createVNode$M("div", {
        "key": "headline",
        "class": "v-empty-state__headline"
      }, [slots.headline?.() ?? props.headline]), hasTitle && _createVNode$M("div", {
        "key": "title",
        "class": "v-empty-state__title"
      }, [slots.title?.() ?? props.title]), hasText && _createVNode$M("div", {
        "key": "text",
        "class": "v-empty-state__text",
        "style": {
          maxWidth: convertToUnit(props.textWidth)
        }
      }, [slots.text?.() ?? props.text]), slots.default && _createVNode$M("div", {
        "key": "content",
        "class": "v-empty-state__content"
      }, [slots.default()]), hasActions && _createVNode$M("div", {
        "key": "actions",
        "class": "v-empty-state__actions"
      }, [_createVNode$M(VDefaultsProvider, {
        "defaults": {
          VBtn: {
            class: 'v-empty-state__action-btn',
            color: props.color ?? 'surface-variant',
            href: props.href,
            text: props.actionText,
            to: props.to
          }
        }
      }, {
        default: () => [slots.actions?.({
          props: {
            onClick: onClickAction
          }
        }) ?? _createVNode$M(VBtn, {
          "onClick": onClickAction
        }, null)]
      })])]);
    });
    return {};
  }
});

// Types

const VExpansionPanelSymbol = Symbol.for('vuetify:v-expansion-panel');

const {createVNode:_createVNode$L,vShow:_vShow$1,withDirectives:_withDirectives$5} = await importShared('vue');
const {inject: inject$4} = await importShared('vue');
const makeVExpansionPanelTextProps = propsFactory({
  ...makeComponentProps(),
  ...makeLazyProps()
}, 'VExpansionPanelText');
const VExpansionPanelText = genericComponent()({
  name: 'VExpansionPanelText',
  props: makeVExpansionPanelTextProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const expansionPanel = inject$4(VExpansionPanelSymbol);
    if (!expansionPanel) throw new Error('[Vuetify] v-expansion-panel-text needs to be placed inside v-expansion-panel');
    const {
      hasContent,
      onAfterLeave
    } = useLazy(props, expansionPanel.isSelected);
    useRender(() => _createVNode$L(VExpandTransition, {
      "onAfterLeave": onAfterLeave
    }, {
      default: () => [_withDirectives$5(_createVNode$L("div", {
        "class": ['v-expansion-panel-text', props.class],
        "style": props.style
      }, [slots.default && hasContent.value && _createVNode$L("div", {
        "class": "v-expansion-panel-text__wrapper"
      }, [slots.default?.()])]), [[_vShow$1, expansionPanel.isSelected.value]])]
    }));
    return {};
  }
});

const {createVNode:_createVNode$K,resolveDirective:_resolveDirective$3,withDirectives:_withDirectives$4} = await importShared('vue');
const {computed: computed$w,inject: inject$3,toRef: toRef$f} = await importShared('vue');
const makeVExpansionPanelTitleProps = propsFactory({
  color: String,
  expandIcon: {
    type: IconValue,
    default: '$expand'
  },
  collapseIcon: {
    type: IconValue,
    default: '$collapse'
  },
  hideActions: Boolean,
  focusable: Boolean,
  static: Boolean,
  ripple: {
    type: [Boolean, Object],
    default: false
  },
  readonly: Boolean,
  ...makeComponentProps(),
  ...makeDimensionProps()
}, 'VExpansionPanelTitle');
const VExpansionPanelTitle = genericComponent()({
  name: 'VExpansionPanelTitle',
  directives: {
    Ripple
  },
  props: makeVExpansionPanelTitleProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const expansionPanel = inject$3(VExpansionPanelSymbol);
    if (!expansionPanel) throw new Error('[Vuetify] v-expansion-panel-title needs to be placed inside v-expansion-panel');
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.color);
    const {
      dimensionStyles
    } = useDimension(props);
    const slotProps = computed$w(() => ({
      collapseIcon: props.collapseIcon,
      disabled: expansionPanel.disabled.value,
      expanded: expansionPanel.isSelected.value,
      expandIcon: props.expandIcon,
      readonly: props.readonly
    }));
    const icon = toRef$f(() => expansionPanel.isSelected.value ? props.collapseIcon : props.expandIcon);
    useRender(() => _withDirectives$4(_createVNode$K("button", {
      "class": ['v-expansion-panel-title', {
        'v-expansion-panel-title--active': expansionPanel.isSelected.value,
        'v-expansion-panel-title--focusable': props.focusable,
        'v-expansion-panel-title--static': props.static
      }, backgroundColorClasses.value, props.class],
      "style": [backgroundColorStyles.value, dimensionStyles.value, props.style],
      "type": "button",
      "tabindex": expansionPanel.disabled.value ? -1 : undefined,
      "disabled": expansionPanel.disabled.value,
      "aria-expanded": expansionPanel.isSelected.value,
      "onClick": !props.readonly ? expansionPanel.toggle : undefined
    }, [_createVNode$K("span", {
      "class": "v-expansion-panel-title__overlay"
    }, null), slots.default?.(slotProps.value), !props.hideActions && _createVNode$K(VDefaultsProvider, {
      "defaults": {
        VIcon: {
          icon: icon.value
        }
      }
    }, {
      default: () => [_createVNode$K("span", {
        "class": "v-expansion-panel-title__icon"
      }, [slots.actions?.(slotProps.value) ?? _createVNode$K(VIcon, null, null)])]
    })]), [[_resolveDirective$3("ripple"), props.ripple]]));
    return {};
  }
});

const {createVNode:_createVNode$J} = await importShared('vue');
const {computed: computed$v,provide,toRef: toRef$e} = await importShared('vue');
const makeVExpansionPanelProps = propsFactory({
  title: String,
  text: String,
  bgColor: String,
  ...makeElevationProps(),
  ...makeGroupItemProps(),
  ...makeRoundedProps(),
  ...makeTagProps(),
  ...makeVExpansionPanelTitleProps(),
  ...makeVExpansionPanelTextProps()
}, 'VExpansionPanel');
const VExpansionPanel = genericComponent()({
  name: 'VExpansionPanel',
  props: makeVExpansionPanelProps(),
  emits: {
    'group:selected': val => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const groupItem = useGroupItem(props, VExpansionPanelSymbol);
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.bgColor);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      roundedClasses
    } = useRounded(props);
    const isDisabled = toRef$e(() => groupItem?.disabled.value || props.disabled);
    const selectedIndices = computed$v(() => groupItem.group.items.value.reduce((arr, item, index) => {
      if (groupItem.group.selected.value.includes(item.id)) arr.push(index);
      return arr;
    }, []));
    const isBeforeSelected = computed$v(() => {
      const index = groupItem.group.items.value.findIndex(item => item.id === groupItem.id);
      return !groupItem.isSelected.value && selectedIndices.value.some(selectedIndex => selectedIndex - index === 1);
    });
    const isAfterSelected = computed$v(() => {
      const index = groupItem.group.items.value.findIndex(item => item.id === groupItem.id);
      return !groupItem.isSelected.value && selectedIndices.value.some(selectedIndex => selectedIndex - index === -1);
    });
    provide(VExpansionPanelSymbol, groupItem);
    useRender(() => {
      const hasText = !!(slots.text || props.text);
      const hasTitle = !!(slots.title || props.title);
      const expansionPanelTitleProps = VExpansionPanelTitle.filterProps(props);
      const expansionPanelTextProps = VExpansionPanelText.filterProps(props);
      return _createVNode$J(props.tag, {
        "class": ['v-expansion-panel', {
          'v-expansion-panel--active': groupItem.isSelected.value,
          'v-expansion-panel--before-active': isBeforeSelected.value,
          'v-expansion-panel--after-active': isAfterSelected.value,
          'v-expansion-panel--disabled': isDisabled.value
        }, roundedClasses.value, backgroundColorClasses.value, props.class],
        "style": [backgroundColorStyles.value, props.style]
      }, {
        default: () => [_createVNode$J("div", {
          "class": ['v-expansion-panel__shadow', ...elevationClasses.value]
        }, null), _createVNode$J(VDefaultsProvider, {
          "defaults": {
            VExpansionPanelTitle: {
              ...expansionPanelTitleProps
            },
            VExpansionPanelText: {
              ...expansionPanelTextProps
            }
          }
        }, {
          default: () => [hasTitle && _createVNode$J(VExpansionPanelTitle, {
            "key": "title"
          }, {
            default: () => [slots.title ? slots.title() : props.title]
          }), hasText && _createVNode$J(VExpansionPanelText, {
            "key": "text"
          }, {
            default: () => [slots.text ? slots.text() : props.text]
          }), slots.default?.()]
        })]
      });
    });
    return {
      groupItem
    };
  }
});

const {createVNode:_createVNode$I} = await importShared('vue');
const {toRef: toRef$d} = await importShared('vue');
const allowedVariants = ['default', 'accordion', 'inset', 'popout'];
const makeVExpansionPanelsProps = propsFactory({
  flat: Boolean,
  ...makeGroupProps(),
  ...pick(makeVExpansionPanelProps(), ['bgColor', 'collapseIcon', 'color', 'eager', 'elevation', 'expandIcon', 'focusable', 'hideActions', 'readonly', 'ripple', 'rounded', 'tile', 'static']),
  ...makeThemeProps(),
  ...makeComponentProps(),
  ...makeTagProps(),
  variant: {
    type: String,
    default: 'default',
    validator: v => allowedVariants.includes(v)
  }
}, 'VExpansionPanels');
const VExpansionPanels = genericComponent()({
  name: 'VExpansionPanels',
  props: makeVExpansionPanelsProps(),
  emits: {
    'update:modelValue': val => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      next,
      prev
    } = useGroup(props, VExpansionPanelSymbol);
    const {
      themeClasses
    } = provideTheme(props);
    const variantClass = toRef$d(() => props.variant && `v-expansion-panels--variant-${props.variant}`);
    provideDefaults({
      VExpansionPanel: {
        bgColor: toRef$d(() => props.bgColor),
        collapseIcon: toRef$d(() => props.collapseIcon),
        color: toRef$d(() => props.color),
        eager: toRef$d(() => props.eager),
        elevation: toRef$d(() => props.elevation),
        expandIcon: toRef$d(() => props.expandIcon),
        focusable: toRef$d(() => props.focusable),
        hideActions: toRef$d(() => props.hideActions),
        readonly: toRef$d(() => props.readonly),
        ripple: toRef$d(() => props.ripple),
        rounded: toRef$d(() => props.rounded),
        static: toRef$d(() => props.static)
      }
    });
    useRender(() => _createVNode$I(props.tag, {
      "class": ['v-expansion-panels', {
        'v-expansion-panels--flat': props.flat,
        'v-expansion-panels--tile': props.tile
      }, themeClasses.value, variantClass.value, props.class],
      "style": props.style
    }, {
      default: () => [slots.default?.({
        prev,
        next
      })]
    }));
    return {
      next,
      prev
    };
  }
});

const {vShow:_vShow,mergeProps:_mergeProps$n,createVNode:_createVNode$H,withDirectives:_withDirectives$3} = await importShared('vue');
const {computed: computed$u,ref: ref$h,shallowRef: shallowRef$d,toRef: toRef$c,watchEffect: watchEffect$6} = await importShared('vue');
const makeVFabProps = propsFactory({
  app: Boolean,
  appear: Boolean,
  extended: Boolean,
  layout: Boolean,
  offset: Boolean,
  modelValue: {
    type: Boolean,
    default: true
  },
  ...omit(makeVBtnProps({
    active: true
  }), ['location']),
  ...makeLayoutItemProps(),
  ...makeLocationProps(),
  ...makeTransitionProps({
    transition: 'fab-transition'
  })
}, 'VFab');
const VFab = genericComponent()({
  name: 'VFab',
  props: makeVFabProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const model = useProxiedModel(props, 'modelValue');
    const height = shallowRef$d(56);
    const layoutItemStyles = ref$h();
    const {
      resizeRef
    } = useResizeObserver(entries => {
      if (!entries.length) return;
      height.value = entries[0].target.clientHeight;
    });
    const hasPosition = toRef$c(() => props.app || props.absolute);
    const position = computed$u(() => {
      if (!hasPosition.value) return false;
      return props.location?.split(' ').shift() ?? 'bottom';
    });
    const orientation = computed$u(() => {
      if (!hasPosition.value) return false;
      return props.location?.split(' ')[1] ?? 'end';
    });
    useToggleScope(() => props.app, () => {
      const layout = useLayoutItem({
        id: props.name,
        order: computed$u(() => parseInt(props.order, 10)),
        position,
        layoutSize: computed$u(() => props.layout ? height.value + 24 : 0),
        elementSize: computed$u(() => height.value + 24),
        active: computed$u(() => props.app && model.value),
        absolute: toRef$c(() => props.absolute)
      });
      watchEffect$6(() => {
        layoutItemStyles.value = layout.layoutItemStyles.value;
      });
    });
    const vFabRef = ref$h();
    useRender(() => {
      const btnProps = VBtn.filterProps(props);
      return _createVNode$H("div", {
        "ref": vFabRef,
        "class": ['v-fab', {
          'v-fab--absolute': props.absolute,
          'v-fab--app': !!props.app,
          'v-fab--extended': props.extended,
          'v-fab--offset': props.offset,
          [`v-fab--${position.value}`]: hasPosition.value,
          [`v-fab--${orientation.value}`]: hasPosition.value
        }, props.class],
        "style": [props.app ? {
          ...layoutItemStyles.value
        } : {
          height: props.absolute ? '100%' : 'inherit'
        }, props.style]
      }, [_createVNode$H("div", {
        "class": "v-fab__container"
      }, [_createVNode$H(MaybeTransition, {
        "appear": props.appear,
        "transition": props.transition
      }, {
        default: () => [_withDirectives$3(_createVNode$H(VBtn, _mergeProps$n({
          "ref": resizeRef
        }, btnProps, {
          "active": undefined,
          "location": undefined
        }), slots), [[_vShow, props.active]])]
      })])]);
    });
    return {};
  }
});

const {Fragment:_Fragment$d,mergeProps:_mergeProps$m,createVNode:_createVNode$G} = await importShared('vue');
const {computed: computed$t,nextTick: nextTick$8,ref: ref$g,shallowRef: shallowRef$c,toRef: toRef$b,watch: watch$b} = await importShared('vue');
const makeVFileInputProps = propsFactory({
  chips: Boolean,
  counter: Boolean,
  counterSizeString: {
    type: String,
    default: '$vuetify.fileInput.counterSize'
  },
  counterString: {
    type: String,
    default: '$vuetify.fileInput.counter'
  },
  hideInput: Boolean,
  multiple: Boolean,
  showSize: {
    type: [Boolean, Number, String],
    default: false,
    validator: v => {
      return typeof v === 'boolean' || [1000, 1024].includes(Number(v));
    }
  },
  ...makeVInputProps({
    prependIcon: '$file'
  }),
  modelValue: {
    type: [Array, Object],
    default: props => props.multiple ? [] : null,
    validator: val => {
      return wrapInArray(val).every(v => v != null && typeof v === 'object');
    }
  },
  ...makeVFieldProps({
    clearable: true
  })
}, 'VFileInput');
const VFileInput = genericComponent()({
  name: 'VFileInput',
  inheritAttrs: false,
  props: makeVFileInputProps(),
  emits: {
    'click:control': e => true,
    'mousedown:control': e => true,
    'update:focused': focused => true,
    'update:modelValue': files => true
  },
  setup(props, _ref) {
    let {
      attrs,
      emit,
      slots
    } = _ref;
    const {
      t
    } = useLocale();
    const model = useProxiedModel(props, 'modelValue', props.modelValue, val => wrapInArray(val), val => !props.multiple && Array.isArray(val) ? val[0] : val);
    const {
      isFocused,
      focus,
      blur
    } = useFocus(props);
    const base = computed$t(() => typeof props.showSize !== 'boolean' ? props.showSize : undefined);
    const totalBytes = computed$t(() => (model.value ?? []).reduce((bytes, _ref2) => {
      let {
        size = 0
      } = _ref2;
      return bytes + size;
    }, 0));
    const totalBytesReadable = computed$t(() => humanReadableFileSize(totalBytes.value, base.value));
    const fileNames = computed$t(() => (model.value ?? []).map(file => {
      const {
        name = '',
        size = 0
      } = file;
      return !props.showSize ? name : `${name} (${humanReadableFileSize(size, base.value)})`;
    }));
    const counterValue = computed$t(() => {
      const fileCount = model.value?.length ?? 0;
      if (props.showSize) return t(props.counterSizeString, fileCount, totalBytesReadable.value);else return t(props.counterString, fileCount);
    });
    const vInputRef = ref$g();
    const vFieldRef = ref$g();
    const inputRef = ref$g();
    const isActive = toRef$b(() => isFocused.value || props.active);
    const isPlainOrUnderlined = computed$t(() => ['plain', 'underlined'].includes(props.variant));
    const isDragging = shallowRef$c(false);
    function onFocus() {
      if (inputRef.value !== document.activeElement) {
        inputRef.value?.focus();
      }
      if (!isFocused.value) focus();
    }
    function onClickPrepend(e) {
      inputRef.value?.click();
    }
    function onControlMousedown(e) {
      emit('mousedown:control', e);
    }
    function onControlClick(e) {
      inputRef.value?.click();
      emit('click:control', e);
    }
    function onClear(e) {
      e.stopPropagation();
      onFocus();
      nextTick$8(() => {
        model.value = [];
        callEvent(props['onClick:clear'], e);
      });
    }
    function onDragover(e) {
      e.preventDefault();
      e.stopImmediatePropagation();
      isDragging.value = true;
    }
    function onDragleave(e) {
      e.preventDefault();
      isDragging.value = false;
    }
    function onDrop(e) {
      e.preventDefault();
      e.stopImmediatePropagation();
      isDragging.value = false;
      if (!e.dataTransfer?.files?.length || !inputRef.value) return;
      const dataTransfer = new DataTransfer();
      for (const file of e.dataTransfer.files) {
        dataTransfer.items.add(file);
      }
      inputRef.value.files = dataTransfer.files;
      inputRef.value.dispatchEvent(new Event('change', {
        bubbles: true
      }));
    }
    watch$b(model, newValue => {
      const hasModelReset = !Array.isArray(newValue) || !newValue.length;
      if (hasModelReset && inputRef.value) {
        inputRef.value.value = '';
      }
    });
    useRender(() => {
      const hasCounter = !!(slots.counter || props.counter);
      const hasDetails = !!(hasCounter || slots.details);
      const [rootAttrs, inputAttrs] = filterInputAttrs(attrs);
      const {
        modelValue: _,
        ...inputProps
      } = VInput.filterProps(props);
      const fieldProps = VField.filterProps(props);
      return _createVNode$G(VInput, _mergeProps$m({
        "ref": vInputRef,
        "modelValue": props.multiple ? model.value : model.value[0],
        "class": ['v-file-input', {
          'v-file-input--chips': !!props.chips,
          'v-file-input--dragging': isDragging.value,
          'v-file-input--hide': props.hideInput,
          'v-input--plain-underlined': isPlainOrUnderlined.value
        }, props.class],
        "style": props.style,
        "onClick:prepend": onClickPrepend
      }, rootAttrs, inputProps, {
        "centerAffix": !isPlainOrUnderlined.value,
        "focused": isFocused.value
      }), {
        ...slots,
        default: _ref3 => {
          let {
            id,
            isDisabled,
            isDirty,
            isReadonly,
            isValid
          } = _ref3;
          return _createVNode$G(VField, _mergeProps$m({
            "ref": vFieldRef,
            "prepend-icon": props.prependIcon,
            "onMousedown": onControlMousedown,
            "onClick": onControlClick,
            "onClick:clear": onClear,
            "onClick:prependInner": props['onClick:prependInner'],
            "onClick:appendInner": props['onClick:appendInner']
          }, fieldProps, {
            "id": id.value,
            "active": isActive.value || isDirty.value,
            "dirty": isDirty.value || props.dirty,
            "disabled": isDisabled.value,
            "focused": isFocused.value,
            "error": isValid.value === false,
            "onDragover": onDragover,
            "onDrop": onDrop
          }), {
            ...slots,
            default: _ref4 => {
              let {
                props: {
                  class: fieldClass,
                  ...slotProps
                }
              } = _ref4;
              return _createVNode$G(_Fragment$d, null, [_createVNode$G("input", _mergeProps$m({
                "ref": inputRef,
                "type": "file",
                "readonly": isReadonly.value,
                "disabled": isDisabled.value,
                "multiple": props.multiple,
                "name": props.name,
                "onClick": e => {
                  e.stopPropagation();
                  if (isReadonly.value) e.preventDefault();
                  onFocus();
                },
                "onChange": e => {
                  if (!e.target) return;
                  const target = e.target;
                  model.value = [...(target.files ?? [])];
                },
                "onDragleave": onDragleave,
                "onFocus": onFocus,
                "onBlur": blur
              }, slotProps, inputAttrs), null), _createVNode$G("div", {
                "class": fieldClass
              }, [!!model.value?.length && !props.hideInput && (slots.selection ? slots.selection({
                fileNames: fileNames.value,
                totalBytes: totalBytes.value,
                totalBytesReadable: totalBytesReadable.value
              }) : props.chips ? fileNames.value.map(text => _createVNode$G(VChip, {
                "key": text,
                "size": "small",
                "text": text
              }, null)) : fileNames.value.join(', '))])]);
            }
          });
        },
        details: hasDetails ? slotProps => _createVNode$G(_Fragment$d, null, [slots.details?.(slotProps), hasCounter && _createVNode$G(_Fragment$d, null, [_createVNode$G("span", null, null), _createVNode$G(VCounter, {
          "active": !!model.value?.length,
          "value": counterValue.value,
          "disabled": props.disabled
        }, slots.counter)])]) : undefined
      });
    });
    return forwardRefs({}, vInputRef, vFieldRef, inputRef);
  }
});

const {createVNode:_createVNode$F} = await importShared('vue');
const {computed: computed$s,ref: ref$f,shallowRef: shallowRef$b,toRef: toRef$a,watchEffect: watchEffect$5} = await importShared('vue');
const makeVFooterProps = propsFactory({
  app: Boolean,
  color: String,
  height: {
    type: [Number, String],
    default: 'auto'
  },
  ...makeBorderProps(),
  ...makeComponentProps(),
  ...makeElevationProps(),
  ...makeLayoutItemProps(),
  ...makeRoundedProps(),
  ...makeTagProps({
    tag: 'footer'
  }),
  ...makeThemeProps()
}, 'VFooter');
const VFooter = genericComponent()({
  name: 'VFooter',
  props: makeVFooterProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const layoutItemStyles = ref$f();
    const {
      themeClasses
    } = provideTheme(props);
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.color);
    const {
      borderClasses
    } = useBorder(props);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      roundedClasses
    } = useRounded(props);
    const autoHeight = shallowRef$b(32);
    const {
      resizeRef
    } = useResizeObserver(entries => {
      if (!entries.length) return;
      autoHeight.value = entries[0].target.clientHeight;
    });
    const height = computed$s(() => props.height === 'auto' ? autoHeight.value : parseInt(props.height, 10));
    useToggleScope(() => props.app, () => {
      const layout = useLayoutItem({
        id: props.name,
        order: computed$s(() => parseInt(props.order, 10)),
        position: toRef$a(() => 'bottom'),
        layoutSize: height,
        elementSize: computed$s(() => props.height === 'auto' ? undefined : height.value),
        active: toRef$a(() => props.app),
        absolute: toRef$a(() => props.absolute)
      });
      watchEffect$5(() => {
        layoutItemStyles.value = layout.layoutItemStyles.value;
      });
    });
    useRender(() => _createVNode$F(props.tag, {
      "ref": resizeRef,
      "class": ['v-footer', themeClasses.value, backgroundColorClasses.value, borderClasses.value, elevationClasses.value, roundedClasses.value, props.class],
      "style": [backgroundColorStyles.value, props.app ? layoutItemStyles.value : {
        height: convertToUnit(props.height)
      }, props.style]
    }, slots));
    return {};
  }
});

const {createVNode:_createVNode$E} = await importShared('vue');
const {ref: ref$e} = await importShared('vue');
const makeVFormProps = propsFactory({
  ...makeComponentProps(),
  ...makeFormProps()
}, 'VForm');
const VForm = genericComponent()({
  name: 'VForm',
  props: makeVFormProps(),
  emits: {
    'update:modelValue': val => true,
    submit: e => true
  },
  setup(props, _ref) {
    let {
      slots,
      emit
    } = _ref;
    const form = createForm(props);
    const formRef = ref$e();
    function onReset(e) {
      e.preventDefault();
      form.reset();
    }
    function onSubmit(_e) {
      const e = _e;
      const ready = form.validate();
      e.then = ready.then.bind(ready);
      e.catch = ready.catch.bind(ready);
      e.finally = ready.finally.bind(ready);
      emit('submit', e);
      if (!e.defaultPrevented) {
        ready.then(_ref2 => {
          let {
            valid
          } = _ref2;
          if (valid) {
            formRef.value?.submit();
          }
        });
      }
      e.preventDefault();
    }
    useRender(() => _createVNode$E("form", {
      "ref": formRef,
      "class": ['v-form', props.class],
      "style": props.style,
      "novalidate": true,
      "onReset": onReset,
      "onSubmit": onSubmit
    }, [slots.default?.(form)]));
    return forwardRefs(form, formRef);
  }
});

// Composables
const makeVHoverProps = propsFactory({
  disabled: Boolean,
  modelValue: {
    type: Boolean,
    default: null
  },
  ...makeDelayProps()
}, 'VHover');
const VHover = genericComponent()({
  name: 'VHover',
  props: makeVHoverProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const isHovering = useProxiedModel(props, 'modelValue');
    const {
      runOpenDelay,
      runCloseDelay
    } = useDelay(props, value => !props.disabled && (isHovering.value = value));
    return () => slots.default?.({
      isHovering: isHovering.value,
      props: {
        onMouseenter: runOpenDelay,
        onMouseleave: runCloseDelay
      }
    });
  }
});

const {createTextVNode:_createTextVNode$1,createVNode:_createVNode$D} = await importShared('vue');
const {computed: computed$r,nextTick: nextTick$7,onMounted: onMounted$5,ref: ref$d,shallowRef: shallowRef$a,watch: watch$a} = await importShared('vue');
const makeVInfiniteScrollProps = propsFactory({
  color: String,
  direction: {
    type: String,
    default: 'vertical',
    validator: v => ['vertical', 'horizontal'].includes(v)
  },
  side: {
    type: String,
    default: 'end',
    validator: v => ['start', 'end', 'both'].includes(v)
  },
  mode: {
    type: String,
    default: 'intersect',
    validator: v => ['intersect', 'manual'].includes(v)
  },
  margin: [Number, String],
  loadMoreText: {
    type: String,
    default: '$vuetify.infiniteScroll.loadMore'
  },
  emptyText: {
    type: String,
    default: '$vuetify.infiniteScroll.empty'
  },
  ...makeDimensionProps(),
  ...makeTagProps()
}, 'VInfiniteScroll');
const VInfiniteScrollIntersect = defineComponent({
  name: 'VInfiniteScrollIntersect',
  props: {
    side: {
      type: String,
      required: true
    },
    rootMargin: String
  },
  emits: {
    intersect: (side, isIntersecting) => true
  },
  setup(props, _ref) {
    let {
      emit
    } = _ref;
    const {
      intersectionRef,
      isIntersecting
    } = useIntersectionObserver();
    watch$a(isIntersecting, async val => {
      emit('intersect', props.side, val);
    });
    useRender(() => _createVNode$D("div", {
      "class": "v-infinite-scroll-intersect",
      "style": {
        '--v-infinite-margin-size': props.rootMargin
      },
      "ref": intersectionRef
    }, [_createTextVNode$1("\xA0")]));
    return {};
  }
});
const VInfiniteScroll = genericComponent()({
  name: 'VInfiniteScroll',
  props: makeVInfiniteScrollProps(),
  emits: {
    load: options => true
  },
  setup(props, _ref2) {
    let {
      slots,
      emit
    } = _ref2;
    const rootEl = ref$d();
    const startStatus = shallowRef$a('ok');
    const endStatus = shallowRef$a('ok');
    const margin = computed$r(() => convertToUnit(props.margin));
    const isIntersecting = shallowRef$a(false);
    function setScrollAmount(amount) {
      if (!rootEl.value) return;
      const property = props.direction === 'vertical' ? 'scrollTop' : 'scrollLeft';
      rootEl.value[property] = amount;
    }
    function getScrollAmount() {
      if (!rootEl.value) return 0;
      const property = props.direction === 'vertical' ? 'scrollTop' : 'scrollLeft';
      return rootEl.value[property];
    }
    function getScrollSize() {
      if (!rootEl.value) return 0;
      const property = props.direction === 'vertical' ? 'scrollHeight' : 'scrollWidth';
      return rootEl.value[property];
    }
    function getContainerSize() {
      if (!rootEl.value) return 0;
      const property = props.direction === 'vertical' ? 'clientHeight' : 'clientWidth';
      return rootEl.value[property];
    }
    onMounted$5(() => {
      if (!rootEl.value) return;
      if (props.side === 'start') {
        setScrollAmount(getScrollSize());
      } else if (props.side === 'both') {
        setScrollAmount(getScrollSize() / 2 - getContainerSize() / 2);
      }
    });
    function setStatus(side, status) {
      if (side === 'start') {
        startStatus.value = status;
      } else if (side === 'end') {
        endStatus.value = status;
      }
    }
    function getStatus(side) {
      return side === 'start' ? startStatus.value : endStatus.value;
    }
    let previousScrollSize = 0;
    function handleIntersect(side, _isIntersecting) {
      isIntersecting.value = _isIntersecting;
      if (isIntersecting.value) {
        intersecting(side);
      }
    }
    function intersecting(side) {
      if (props.mode !== 'manual' && !isIntersecting.value) return;
      const status = getStatus(side);
      if (!rootEl.value || ['empty', 'loading'].includes(status)) return;
      previousScrollSize = getScrollSize();
      setStatus(side, 'loading');
      function done(status) {
        setStatus(side, status);
        nextTick$7(() => {
          if (status === 'empty' || status === 'error') return;
          if (status === 'ok' && side === 'start') {
            setScrollAmount(getScrollSize() - previousScrollSize + getScrollAmount());
          }
          if (props.mode !== 'manual') {
            nextTick$7(() => {
              window.requestAnimationFrame(() => {
                window.requestAnimationFrame(() => {
                  window.requestAnimationFrame(() => {
                    intersecting(side);
                  });
                });
              });
            });
          }
        });
      }
      emit('load', {
        side,
        done
      });
    }
    const {
      t
    } = useLocale();
    function renderSide(side, status) {
      if (props.side !== side && props.side !== 'both') return;
      const onClick = () => intersecting(side);
      const slotProps = {
        side,
        props: {
          onClick,
          color: props.color
        }
      };
      if (status === 'error') return slots.error?.(slotProps);
      if (status === 'empty') return slots.empty?.(slotProps) ?? _createVNode$D("div", null, [t(props.emptyText)]);
      if (props.mode === 'manual') {
        if (status === 'loading') {
          return slots.loading?.(slotProps) ?? _createVNode$D(VProgressCircular, {
            "indeterminate": true,
            "color": props.color
          }, null);
        }
        return slots['load-more']?.(slotProps) ?? _createVNode$D(VBtn, {
          "variant": "outlined",
          "color": props.color,
          "onClick": onClick
        }, {
          default: () => [t(props.loadMoreText)]
        });
      }
      return slots.loading?.(slotProps) ?? _createVNode$D(VProgressCircular, {
        "indeterminate": true,
        "color": props.color
      }, null);
    }
    const {
      dimensionStyles
    } = useDimension(props);
    useRender(() => {
      const Tag = props.tag;
      const hasStartIntersect = props.side === 'start' || props.side === 'both';
      const hasEndIntersect = props.side === 'end' || props.side === 'both';
      const intersectMode = props.mode === 'intersect';
      return _createVNode$D(Tag, {
        "ref": rootEl,
        "class": ['v-infinite-scroll', `v-infinite-scroll--${props.direction}`, {
          'v-infinite-scroll--start': hasStartIntersect,
          'v-infinite-scroll--end': hasEndIntersect
        }],
        "style": dimensionStyles.value
      }, {
        default: () => [_createVNode$D("div", {
          "class": "v-infinite-scroll__side"
        }, [renderSide('start', startStatus.value)]), hasStartIntersect && intersectMode && _createVNode$D(VInfiniteScrollIntersect, {
          "key": "start",
          "side": "start",
          "onIntersect": handleIntersect,
          "rootMargin": margin.value
        }, null), slots.default?.(), hasEndIntersect && intersectMode && _createVNode$D(VInfiniteScrollIntersect, {
          "key": "end",
          "side": "end",
          "onIntersect": handleIntersect,
          "rootMargin": margin.value
        }, null), _createVNode$D("div", {
          "class": "v-infinite-scroll__side"
        }, [renderSide('end', endStatus.value)])]
      });
    });
  }
});

const {createVNode:_createVNode$C} = await importShared('vue');
const VItemGroupSymbol = Symbol.for('vuetify:v-item-group');
const makeVItemGroupProps = propsFactory({
  ...makeComponentProps(),
  ...makeGroupProps({
    selectedClass: 'v-item--selected'
  }),
  ...makeTagProps(),
  ...makeThemeProps()
}, 'VItemGroup');
const VItemGroup = genericComponent()({
  name: 'VItemGroup',
  props: makeVItemGroupProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      themeClasses
    } = provideTheme(props);
    const {
      isSelected,
      select,
      next,
      prev,
      selected
    } = useGroup(props, VItemGroupSymbol);
    return () => _createVNode$C(props.tag, {
      "class": ['v-item-group', themeClasses.value, props.class],
      "style": props.style
    }, {
      default: () => [slots.default?.({
        isSelected,
        select,
        next,
        prev,
        selected: selected.value
      })]
    });
  }
});

// Composables
const VItem = genericComponent()({
  name: 'VItem',
  props: makeGroupItemProps(),
  emits: {
    'group:selected': val => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      isSelected,
      select,
      toggle,
      selectedClass,
      value,
      disabled
    } = useGroupItem(props, VItemGroupSymbol);
    return () => slots.default?.({
      isSelected: isSelected.value,
      selectedClass: selectedClass.value,
      select,
      toggle,
      value: value.value,
      disabled: disabled.value
    });
  }
});

// Styles
const VKbd = createSimpleFunctional('v-kbd', 'kbd');

const {createVNode:_createVNode$B} = await importShared('vue');
const makeVLayoutProps = propsFactory({
  ...makeComponentProps(),
  ...makeDimensionProps(),
  ...makeLayoutProps()
}, 'VLayout');
const VLayout = genericComponent()({
  name: 'VLayout',
  props: makeVLayoutProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      layoutClasses,
      layoutStyles,
      getLayoutItem,
      items,
      layoutRef
    } = createLayout(props);
    const {
      dimensionStyles
    } = useDimension(props);
    useRender(() => _createVNode$B("div", {
      "ref": layoutRef,
      "class": [layoutClasses.value, props.class],
      "style": [dimensionStyles.value, layoutStyles.value, props.style]
    }, [slots.default?.()]));
    return {
      getLayoutItem,
      items
    };
  }
});

const {createVNode:_createVNode$A} = await importShared('vue');
const {computed: computed$q,toRef: toRef$9} = await importShared('vue');
const makeVLayoutItemProps = propsFactory({
  position: {
    type: String,
    required: true
  },
  size: {
    type: [Number, String],
    default: 300
  },
  modelValue: Boolean,
  ...makeComponentProps(),
  ...makeLayoutItemProps()
}, 'VLayoutItem');
const VLayoutItem = genericComponent()({
  name: 'VLayoutItem',
  props: makeVLayoutItemProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      layoutItemStyles
    } = useLayoutItem({
      id: props.name,
      order: computed$q(() => parseInt(props.order, 10)),
      position: toRef$9(() => props.position),
      elementSize: toRef$9(() => props.size),
      layoutSize: toRef$9(() => props.size),
      active: toRef$9(() => props.modelValue),
      absolute: toRef$9(() => props.absolute)
    });
    return () => _createVNode$A("div", {
      "class": ['v-layout-item', props.class],
      "style": [layoutItemStyles.value, props.style]
    }, [slots.default?.()]);
  }
});

const {createVNode:_createVNode$z,resolveDirective:_resolveDirective$2,withDirectives:_withDirectives$2} = await importShared('vue');
const makeVLazyProps = propsFactory({
  modelValue: Boolean,
  options: {
    type: Object,
    // For more information on types, navigate to:
    // https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API
    default: () => ({
      root: undefined,
      rootMargin: undefined,
      threshold: undefined
    })
  },
  ...makeComponentProps(),
  ...makeDimensionProps(),
  ...makeTagProps(),
  ...makeTransitionProps({
    transition: 'fade-transition'
  })
}, 'VLazy');
const VLazy = genericComponent()({
  name: 'VLazy',
  directives: {
    intersect: Intersect
  },
  props: makeVLazyProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      dimensionStyles
    } = useDimension(props);
    const isActive = useProxiedModel(props, 'modelValue');
    function onIntersect(isIntersecting) {
      if (isActive.value) return;
      isActive.value = isIntersecting;
    }
    useRender(() => _withDirectives$2(_createVNode$z(props.tag, {
      "class": ['v-lazy', props.class],
      "style": [dimensionStyles.value, props.style]
    }, {
      default: () => [isActive.value && _createVNode$z(MaybeTransition, {
        "transition": props.transition,
        "appear": true
      }, {
        default: () => [slots.default?.()]
      })]
    }), [[_resolveDirective$2("intersect"), {
      handler: onIntersect,
      options: props.options
    }, null]]));
    return {};
  }
});

const {createVNode:_createVNode$y} = await importShared('vue');
const makeVLocaleProviderProps = propsFactory({
  locale: String,
  fallbackLocale: String,
  messages: Object,
  rtl: {
    type: Boolean,
    default: undefined
  },
  ...makeComponentProps()
}, 'VLocaleProvider');
const VLocaleProvider = genericComponent()({
  name: 'VLocaleProvider',
  props: makeVLocaleProviderProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      rtlClasses
    } = provideLocale(props);
    useRender(() => _createVNode$y("div", {
      "class": ['v-locale-provider', rtlClasses.value, props.class],
      "style": props.style
    }, [slots.default?.()]));
    return {};
  }
});

const {createVNode:_createVNode$x} = await importShared('vue');
const makeVMainProps = propsFactory({
  scrollable: Boolean,
  ...makeComponentProps(),
  ...makeDimensionProps(),
  ...makeTagProps({
    tag: 'main'
  })
}, 'VMain');
const VMain = genericComponent()({
  name: 'VMain',
  props: makeVMainProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      dimensionStyles
    } = useDimension(props);
    const {
      mainStyles
    } = useLayout();
    const {
      ssrBootStyles
    } = useSsrBoot();
    useRender(() => _createVNode$x(props.tag, {
      "class": ['v-main', {
        'v-main--scrollable': props.scrollable
      }, props.class],
      "style": [mainStyles.value, ssrBootStyles.value, dimensionStyles.value, props.style]
    }, {
      default: () => [props.scrollable ? _createVNode$x("div", {
        "class": "v-main__scroller"
      }, [slots.default?.()]) : slots.default?.()]
    }));
    return {};
  }
});

// Utilities
const {computed: computed$p,onBeforeUnmount: onBeforeUnmount$3,onMounted: onMounted$4,shallowRef: shallowRef$9,watch: watch$9} = await importShared('vue');
function useSticky(_ref) {
  let {
    rootEl,
    isSticky,
    layoutItemStyles
  } = _ref;
  const isStuck = shallowRef$9(false);
  const stuckPosition = shallowRef$9(0);
  const stickyStyles = computed$p(() => {
    const side = typeof isStuck.value === 'boolean' ? 'top' : isStuck.value;
    return [isSticky.value ? {
      top: 'auto',
      bottom: 'auto',
      height: undefined
    } : undefined, isStuck.value ? {
      [side]: convertToUnit(stuckPosition.value)
    } : {
      top: layoutItemStyles.value.top
    }];
  });
  onMounted$4(() => {
    watch$9(isSticky, val => {
      if (val) {
        window.addEventListener('scroll', onScroll, {
          passive: true
        });
      } else {
        window.removeEventListener('scroll', onScroll);
      }
    }, {
      immediate: true
    });
  });
  onBeforeUnmount$3(() => {
    window.removeEventListener('scroll', onScroll);
  });
  let lastScrollTop = 0;
  function onScroll() {
    const direction = lastScrollTop > window.scrollY ? 'up' : 'down';
    const rect = rootEl.value.getBoundingClientRect();
    const layoutTop = parseFloat(layoutItemStyles.value.top ?? 0);
    const top = window.scrollY - Math.max(0, stuckPosition.value - layoutTop);
    const bottom = rect.height + Math.max(stuckPosition.value, layoutTop) - window.scrollY - window.innerHeight;
    const bodyScroll = parseFloat(getComputedStyle(rootEl.value).getPropertyValue('--v-body-scroll-y')) || 0;
    if (rect.height < window.innerHeight - layoutTop) {
      isStuck.value = 'top';
      stuckPosition.value = layoutTop;
    } else if (direction === 'up' && isStuck.value === 'bottom' || direction === 'down' && isStuck.value === 'top') {
      stuckPosition.value = window.scrollY + rect.top - bodyScroll;
      isStuck.value = true;
    } else if (direction === 'down' && bottom <= 0) {
      stuckPosition.value = 0;
      isStuck.value = 'bottom';
    } else if (direction === 'up' && top <= 0) {
      if (!bodyScroll) {
        stuckPosition.value = rect.top + top;
        isStuck.value = 'top';
      } else if (isStuck.value !== 'top') {
        stuckPosition.value = -top + bodyScroll + layoutTop;
        isStuck.value = 'top';
      }
    }
    lastScrollTop = window.scrollY;
  }
  return {
    isStuck,
    stickyStyles
  };
}

// Utilities
const HORIZON = 100; // ms
const HISTORY = 20; // number of samples to keep

/** @see https://android.googlesource.com/platform/frameworks/native/+/master/libs/input/VelocityTracker.cpp */
function kineticEnergyToVelocity(work) {
  const sqrt2 = 1.41421356237;
  return (work < 0 ? -1 : 1.0) * Math.sqrt(Math.abs(work)) * sqrt2;
}

/**
 * Returns pointer velocity in px/s
 */
function calculateImpulseVelocity(samples) {
  // The input should be in reversed time order (most recent sample at index i=0)
  if (samples.length < 2) {
    // if 0 or 1 points, velocity is zero
    return 0;
  }
  // if (samples[1].t > samples[0].t) {
  //   // Algorithm will still work, but not perfectly
  //   consoleWarn('Samples provided to calculateImpulseVelocity in the wrong order')
  // }
  if (samples.length === 2) {
    // if 2 points, basic linear calculation
    if (samples[1].t === samples[0].t) {
      // consoleWarn(`Events have identical time stamps t=${samples[0].t}, setting velocity = 0`)
      return 0;
    }
    return (samples[1].d - samples[0].d) / (samples[1].t - samples[0].t);
  }
  // Guaranteed to have at least 3 points here
  // start with the oldest sample and go forward in time
  let work = 0;
  for (let i = samples.length - 1; i > 0; i--) {
    if (samples[i].t === samples[i - 1].t) {
      // consoleWarn(`Events have identical time stamps t=${samples[i].t}, skipping sample`)
      continue;
    }
    const vprev = kineticEnergyToVelocity(work); // v[i-1]
    const vcurr = (samples[i].d - samples[i - 1].d) / (samples[i].t - samples[i - 1].t); // v[i]
    work += (vcurr - vprev) * Math.abs(vcurr);
    if (i === samples.length - 1) {
      work *= 0.5;
    }
  }
  return kineticEnergyToVelocity(work) * 1000;
}
function useVelocity() {
  const touches = {};
  function addMovement(e) {
    Array.from(e.changedTouches).forEach(touch => {
      const samples = touches[touch.identifier] ?? (touches[touch.identifier] = new CircularBuffer(HISTORY));
      samples.push([e.timeStamp, touch]);
    });
  }
  function endTouch(e) {
    Array.from(e.changedTouches).forEach(touch => {
      delete touches[touch.identifier];
    });
  }
  function getVelocity(id) {
    const samples = touches[id]?.values().reverse();
    if (!samples) {
      throw new Error(`No samples for touch id ${id}`);
    }
    const newest = samples[0];
    const x = [];
    const y = [];
    for (const val of samples) {
      if (newest[0] - val[0] > HORIZON) break;
      x.push({
        t: val[0],
        d: val[1].clientX
      });
      y.push({
        t: val[0],
        d: val[1].clientY
      });
    }
    return {
      x: calculateImpulseVelocity(x),
      y: calculateImpulseVelocity(y),
      get direction() {
        const {
          x,
          y
        } = this;
        const [absX, absY] = [Math.abs(x), Math.abs(y)];
        return absX > absY && x >= 0 ? 'right' : absX > absY && x <= 0 ? 'left' : absY > absX && y >= 0 ? 'down' : absY > absX && y <= 0 ? 'up' : oops$1();
      }
    };
  }
  return {
    addMovement,
    endTouch,
    getVelocity
  };
}
function oops$1() {
  throw new Error();
}

const {computed: computed$o,onBeforeUnmount: onBeforeUnmount$2,onMounted: onMounted$3,onScopeDispose: onScopeDispose$2,shallowRef: shallowRef$8,watchEffect: watchEffect$4} = await importShared('vue');


// Types

function useTouch(_ref) {
  let {
    el,
    isActive,
    isTemporary,
    width,
    touchless,
    position
  } = _ref;
  onMounted$3(() => {
    window.addEventListener('touchstart', onTouchstart, {
      passive: true
    });
    window.addEventListener('touchmove', onTouchmove, {
      passive: false
    });
    window.addEventListener('touchend', onTouchend, {
      passive: true
    });
  });
  onBeforeUnmount$2(() => {
    window.removeEventListener('touchstart', onTouchstart);
    window.removeEventListener('touchmove', onTouchmove);
    window.removeEventListener('touchend', onTouchend);
  });
  const isHorizontal = computed$o(() => ['left', 'right'].includes(position.value));
  const {
    addMovement,
    endTouch,
    getVelocity
  } = useVelocity();
  let maybeDragging = false;
  const isDragging = shallowRef$8(false);
  const dragProgress = shallowRef$8(0);
  const offset = shallowRef$8(0);
  let start;
  function getOffset(pos, active) {
    return (position.value === 'left' ? pos : position.value === 'right' ? document.documentElement.clientWidth - pos : position.value === 'top' ? pos : position.value === 'bottom' ? document.documentElement.clientHeight - pos : oops()) - (active ? width.value : 0);
  }
  function getProgress(pos) {
    let limit = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : true;
    const progress = position.value === 'left' ? (pos - offset.value) / width.value : position.value === 'right' ? (document.documentElement.clientWidth - pos - offset.value) / width.value : position.value === 'top' ? (pos - offset.value) / width.value : position.value === 'bottom' ? (document.documentElement.clientHeight - pos - offset.value) / width.value : oops();
    return limit ? Math.max(0, Math.min(1, progress)) : progress;
  }
  function onTouchstart(e) {
    if (touchless.value) return;
    const touchX = e.changedTouches[0].clientX;
    const touchY = e.changedTouches[0].clientY;
    const touchZone = 25;
    const inTouchZone = position.value === 'left' ? touchX < touchZone : position.value === 'right' ? touchX > document.documentElement.clientWidth - touchZone : position.value === 'top' ? touchY < touchZone : position.value === 'bottom' ? touchY > document.documentElement.clientHeight - touchZone : oops();
    const inElement = isActive.value && (position.value === 'left' ? touchX < width.value : position.value === 'right' ? touchX > document.documentElement.clientWidth - width.value : position.value === 'top' ? touchY < width.value : position.value === 'bottom' ? touchY > document.documentElement.clientHeight - width.value : oops());
    if (inTouchZone || inElement || isActive.value && isTemporary.value) {
      start = [touchX, touchY];
      offset.value = getOffset(isHorizontal.value ? touchX : touchY, isActive.value);
      dragProgress.value = getProgress(isHorizontal.value ? touchX : touchY);
      maybeDragging = offset.value > -20 && offset.value < 80;
      endTouch(e);
      addMovement(e);
    }
  }
  function onTouchmove(e) {
    const touchX = e.changedTouches[0].clientX;
    const touchY = e.changedTouches[0].clientY;
    if (maybeDragging) {
      if (!e.cancelable) {
        maybeDragging = false;
        return;
      }
      const dx = Math.abs(touchX - start[0]);
      const dy = Math.abs(touchY - start[1]);
      const thresholdMet = isHorizontal.value ? dx > dy && dx > 3 : dy > dx && dy > 3;
      if (thresholdMet) {
        isDragging.value = true;
        maybeDragging = false;
      } else if ((isHorizontal.value ? dy : dx) > 3) {
        maybeDragging = false;
      }
    }
    if (!isDragging.value) return;
    e.preventDefault();
    addMovement(e);
    const progress = getProgress(isHorizontal.value ? touchX : touchY, false);
    dragProgress.value = Math.max(0, Math.min(1, progress));
    if (progress > 1) {
      offset.value = getOffset(isHorizontal.value ? touchX : touchY, true);
    } else if (progress < 0) {
      offset.value = getOffset(isHorizontal.value ? touchX : touchY, false);
    }
  }
  function onTouchend(e) {
    maybeDragging = false;
    if (!isDragging.value) return;
    addMovement(e);
    isDragging.value = false;
    const velocity = getVelocity(e.changedTouches[0].identifier);
    const vx = Math.abs(velocity.x);
    const vy = Math.abs(velocity.y);
    const thresholdMet = isHorizontal.value ? vx > vy && vx > 400 : vy > vx && vy > 3;
    if (thresholdMet) {
      isActive.value = velocity.direction === ({
        left: 'right',
        right: 'left',
        top: 'down',
        bottom: 'up'
      }[position.value] || oops());
    } else {
      isActive.value = dragProgress.value > 0.5;
    }
  }
  const dragStyles = computed$o(() => {
    return isDragging.value ? {
      transform: position.value === 'left' ? `translateX(calc(-100% + ${dragProgress.value * width.value}px))` : position.value === 'right' ? `translateX(calc(100% - ${dragProgress.value * width.value}px))` : position.value === 'top' ? `translateY(calc(-100% + ${dragProgress.value * width.value}px))` : position.value === 'bottom' ? `translateY(calc(100% - ${dragProgress.value * width.value}px))` : oops(),
      transition: 'none'
    } : undefined;
  });
  useToggleScope(isDragging, () => {
    const transform = el.value?.style.transform ?? null;
    const transition = el.value?.style.transition ?? null;
    watchEffect$4(() => {
      el.value?.style.setProperty('transform', dragStyles.value?.transform || 'none');
      el.value?.style.setProperty('transition', dragStyles.value?.transition || null);
    });
    onScopeDispose$2(() => {
      el.value?.style.setProperty('transform', transform);
      el.value?.style.setProperty('transition', transition);
    });
  });
  return {
    isDragging,
    dragProgress,
    dragStyles
  };
}
function oops() {
  throw new Error();
}

const {Fragment:_Fragment$c,createVNode:_createVNode$w,mergeProps:_mergeProps$l} = await importShared('vue');
const {computed: computed$n,nextTick: nextTick$6,readonly,ref: ref$c,shallowRef: shallowRef$7,toRef: toRef$8,Transition,watch: watch$8} = await importShared('vue');
const locations = ['start', 'end', 'left', 'right', 'top', 'bottom'];
const makeVNavigationDrawerProps = propsFactory({
  color: String,
  disableResizeWatcher: Boolean,
  disableRouteWatcher: Boolean,
  expandOnHover: Boolean,
  floating: Boolean,
  modelValue: {
    type: Boolean,
    default: null
  },
  permanent: Boolean,
  rail: {
    type: Boolean,
    default: null
  },
  railWidth: {
    type: [Number, String],
    default: 56
  },
  scrim: {
    type: [Boolean, String],
    default: true
  },
  image: String,
  temporary: Boolean,
  persistent: Boolean,
  touchless: Boolean,
  width: {
    type: [Number, String],
    default: 256
  },
  location: {
    type: String,
    default: 'start',
    validator: value => locations.includes(value)
  },
  sticky: Boolean,
  ...makeBorderProps(),
  ...makeComponentProps(),
  ...makeDelayProps(),
  ...makeDisplayProps({
    mobile: null
  }),
  ...makeElevationProps(),
  ...makeLayoutItemProps(),
  ...makeRoundedProps(),
  ...makeTagProps({
    tag: 'nav'
  }),
  ...makeThemeProps()
}, 'VNavigationDrawer');
const VNavigationDrawer = genericComponent()({
  name: 'VNavigationDrawer',
  props: makeVNavigationDrawerProps(),
  emits: {
    'update:modelValue': val => true,
    'update:rail': val => true
  },
  setup(props, _ref) {
    let {
      attrs,
      emit,
      slots
    } = _ref;
    const {
      isRtl
    } = useRtl();
    const {
      themeClasses
    } = provideTheme(props);
    const {
      borderClasses
    } = useBorder(props);
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.color);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      displayClasses,
      mobile
    } = useDisplay(props);
    const {
      roundedClasses
    } = useRounded(props);
    const router = useRouter();
    const isActive = useProxiedModel(props, 'modelValue', null, v => !!v);
    const {
      ssrBootStyles
    } = useSsrBoot();
    const {
      scopeId
    } = useScopeId();
    const rootEl = ref$c();
    const isHovering = shallowRef$7(false);
    const {
      runOpenDelay,
      runCloseDelay
    } = useDelay(props, value => {
      isHovering.value = value;
    });
    const width = computed$n(() => {
      return props.rail && props.expandOnHover && isHovering.value ? Number(props.width) : Number(props.rail ? props.railWidth : props.width);
    });
    const location = computed$n(() => {
      return toPhysical(props.location, isRtl.value);
    });
    const isPersistent = toRef$8(() => props.persistent);
    const isTemporary = computed$n(() => !props.permanent && (mobile.value || props.temporary));
    const isSticky = computed$n(() => props.sticky && !isTemporary.value && location.value !== 'bottom');
    useToggleScope(() => props.expandOnHover && props.rail != null, () => {
      watch$8(isHovering, val => emit('update:rail', !val));
    });
    useToggleScope(() => !props.disableResizeWatcher, () => {
      watch$8(isTemporary, val => !props.permanent && nextTick$6(() => isActive.value = !val));
    });
    useToggleScope(() => !props.disableRouteWatcher && !!router, () => {
      watch$8(router.currentRoute, () => isTemporary.value && (isActive.value = false));
    });
    watch$8(() => props.permanent, val => {
      if (val) isActive.value = true;
    });
    if (props.modelValue == null && !isTemporary.value) {
      isActive.value = props.permanent || !mobile.value;
    }
    const {
      isDragging,
      dragProgress
    } = useTouch({
      el: rootEl,
      isActive,
      isTemporary,
      width,
      touchless: toRef$8(() => props.touchless),
      position: location
    });
    const layoutSize = computed$n(() => {
      const size = isTemporary.value ? 0 : props.rail && props.expandOnHover ? Number(props.railWidth) : width.value;
      return isDragging.value ? size * dragProgress.value : size;
    });
    const {
      layoutItemStyles,
      layoutItemScrimStyles
    } = useLayoutItem({
      id: props.name,
      order: computed$n(() => parseInt(props.order, 10)),
      position: location,
      layoutSize,
      elementSize: width,
      active: readonly(isActive),
      disableTransitions: toRef$8(() => isDragging.value),
      absolute: computed$n(() =>
      // eslint-disable-next-line @typescript-eslint/no-use-before-define
      props.absolute || isSticky.value && typeof isStuck.value !== 'string')
    });
    const {
      isStuck,
      stickyStyles
    } = useSticky({
      rootEl,
      isSticky,
      layoutItemStyles
    });
    const scrimColor = useBackgroundColor(() => {
      return typeof props.scrim === 'string' ? props.scrim : null;
    });
    const scrimStyles = computed$n(() => ({
      ...(isDragging.value ? {
        opacity: dragProgress.value * 0.2,
        transition: 'none'
      } : undefined),
      ...layoutItemScrimStyles.value
    }));
    provideDefaults({
      VList: {
        bgColor: 'transparent'
      }
    });
    useRender(() => {
      const hasImage = slots.image || props.image;
      return _createVNode$w(_Fragment$c, null, [_createVNode$w(props.tag, _mergeProps$l({
        "ref": rootEl,
        "onMouseenter": runOpenDelay,
        "onMouseleave": runCloseDelay,
        "class": ['v-navigation-drawer', `v-navigation-drawer--${location.value}`, {
          'v-navigation-drawer--expand-on-hover': props.expandOnHover,
          'v-navigation-drawer--floating': props.floating,
          'v-navigation-drawer--is-hovering': isHovering.value,
          'v-navigation-drawer--rail': props.rail,
          'v-navigation-drawer--temporary': isTemporary.value,
          'v-navigation-drawer--persistent': isPersistent.value,
          'v-navigation-drawer--active': isActive.value,
          'v-navigation-drawer--sticky': isSticky.value
        }, themeClasses.value, backgroundColorClasses.value, borderClasses.value, displayClasses.value, elevationClasses.value, roundedClasses.value, props.class],
        "style": [backgroundColorStyles.value, layoutItemStyles.value, ssrBootStyles.value, stickyStyles.value, props.style]
      }, scopeId, attrs), {
        default: () => [hasImage && _createVNode$w("div", {
          "key": "image",
          "class": "v-navigation-drawer__img"
        }, [!slots.image ? _createVNode$w(VImg, {
          "key": "image-img",
          "alt": "",
          "cover": true,
          "height": "inherit",
          "src": props.image
        }, null) : _createVNode$w(VDefaultsProvider, {
          "key": "image-defaults",
          "disabled": !props.image,
          "defaults": {
            VImg: {
              alt: '',
              cover: true,
              height: 'inherit',
              src: props.image
            }
          }
        }, slots.image)]), slots.prepend && _createVNode$w("div", {
          "class": "v-navigation-drawer__prepend"
        }, [slots.prepend?.()]), _createVNode$w("div", {
          "class": "v-navigation-drawer__content"
        }, [slots.default?.()]), slots.append && _createVNode$w("div", {
          "class": "v-navigation-drawer__append"
        }, [slots.append?.()])]
      }), _createVNode$w(Transition, {
        "name": "fade-transition"
      }, {
        default: () => [isTemporary.value && (isDragging.value || isActive.value) && !!props.scrim && _createVNode$w("div", _mergeProps$l({
          "class": ['v-navigation-drawer__scrim', scrimColor.backgroundColorClasses.value],
          "style": [scrimStyles.value, scrimColor.backgroundColorStyles.value],
          "onClick": () => {
            if (isPersistent.value) return;
            isActive.value = false;
          }
        }, scopeId), null)]
      })]);
    });
    return {
      isStuck
    };
  }
});

// Composables
const VNoSsr = defineComponent({
  name: 'VNoSsr',
  setup(_, _ref) {
    let {
      slots
    } = _ref;
    const show = useHydration();
    return () => show.value && slots.default?.();
  }
});

// Utilities
const {onScopeDispose: onScopeDispose$1} = await importShared('vue');

const HOLD_REPEAT = 50;
const HOLD_DELAY = 500;
function useHold(_ref) {
  let {
    toggleUpDown
  } = _ref;
  let timeout = -1;
  let interval = -1;
  onScopeDispose$1(holdStop);
  function holdStart(value) {
    holdStop();
    tick(value);
    timeout = window.setTimeout(() => {
      interval = window.setInterval(() => tick(value), HOLD_REPEAT);
    }, HOLD_DELAY);
  }
  function holdStop() {
    window.clearTimeout(timeout);
    window.clearInterval(interval);
  }
  function tick(value) {
    toggleUpDown(value === 'up');
  }
  return {
    holdStart,
    holdStop
  };
}

const {createVNode:_createVNode$v,Fragment:_Fragment$b,mergeProps:_mergeProps$k} = await importShared('vue');
const {computed: computed$m,nextTick: nextTick$5,onMounted: onMounted$2,ref: ref$b,shallowRef: shallowRef$6,toRef: toRef$7,watch: watch$7,watchEffect: watchEffect$3} = await importShared('vue');
const makeVNumberInputProps = propsFactory({
  controlVariant: {
    type: String,
    default: 'default'
  },
  inset: Boolean,
  hideInput: Boolean,
  modelValue: {
    type: Number,
    default: null
  },
  min: {
    type: Number,
    default: Number.MIN_SAFE_INTEGER
  },
  max: {
    type: Number,
    default: Number.MAX_SAFE_INTEGER
  },
  step: {
    type: Number,
    default: 1
  },
  precision: {
    type: Number,
    default: 0
  },
  ...omit(makeVTextFieldProps(), ['modelValue', 'validationValue'])
}, 'VNumberInput');
const VNumberInput = genericComponent()({
  name: 'VNumberInput',
  props: {
    ...makeVNumberInputProps()
  },
  emits: {
    'update:modelValue': val => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const vTextFieldRef = ref$b();
    const {
      holdStart,
      holdStop
    } = useHold({
      toggleUpDown
    });
    const form = useForm(props);
    const controlsDisabled = computed$m(() => form.isDisabled.value || form.isReadonly.value);
    const {
      isFocused,
      focus,
      blur
    } = useFocus(props);
    function correctPrecision(val) {
      let precision = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : props.precision;
      const fixed = precision == null ? String(val) : val.toFixed(precision);
      return isFocused.value ? Number(fixed).toString() // trim zeros
      : fixed;
    }
    const model = useProxiedModel(props, 'modelValue', null, val => val ?? null, val => val == null ? val ?? null : clamp(Number(val), props.min, props.max));
    const _inputText = shallowRef$6(null);
    watchEffect$3(() => {
      if (isFocused.value && !controlsDisabled.value) ; else if (model.value == null) {
        _inputText.value = null;
      } else if (!isNaN(model.value)) {
        _inputText.value = correctPrecision(model.value);
      }
    });
    const inputText = computed$m({
      get: () => _inputText.value,
      set(val) {
        if (val === null || val === '') {
          model.value = null;
          _inputText.value = null;
        } else if (!isNaN(Number(val)) && Number(val) <= props.max && Number(val) >= props.min) {
          model.value = Number(val);
          _inputText.value = val;
        }
      }
    });
    const canIncrease = computed$m(() => {
      if (controlsDisabled.value) return false;
      return (model.value ?? 0) + props.step <= props.max;
    });
    const canDecrease = computed$m(() => {
      if (controlsDisabled.value) return false;
      return (model.value ?? 0) - props.step >= props.min;
    });
    const controlVariant = computed$m(() => {
      return props.hideInput ? 'stacked' : props.controlVariant;
    });
    const incrementIcon = toRef$7(() => controlVariant.value === 'split' ? '$plus' : '$collapse');
    const decrementIcon = toRef$7(() => controlVariant.value === 'split' ? '$minus' : '$expand');
    const controlNodeSize = toRef$7(() => controlVariant.value === 'split' ? 'default' : 'small');
    const controlNodeDefaultHeight = toRef$7(() => controlVariant.value === 'stacked' ? 'auto' : '100%');
    const incrementSlotProps = {
      props: {
        onClick: onControlClick,
        onPointerup: onControlMouseup,
        onPointerdown: onUpControlMousedown
      }
    };
    const decrementSlotProps = {
      props: {
        onClick: onControlClick,
        onPointerup: onControlMouseup,
        onPointerdown: onDownControlMousedown
      }
    };
    watch$7(() => props.precision, () => formatInputValue());
    onMounted$2(() => {
      clampModel();
    });
    function inferPrecision(value) {
      if (value == null) return 0;
      const str = value.toString();
      const idx = str.indexOf('.');
      return ~idx ? str.length - idx : 0;
    }
    function toggleUpDown() {
      let increment = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : true;
      if (controlsDisabled.value) return;
      if (model.value == null) {
        inputText.value = correctPrecision(clamp(0, props.min, props.max));
        return;
      }
      let inferredPrecision = Math.max(inferPrecision(model.value), inferPrecision(props.step));
      if (props.precision != null) inferredPrecision = Math.max(inferredPrecision, props.precision);
      if (increment) {
        if (canIncrease.value) inputText.value = correctPrecision(model.value + props.step, inferredPrecision);
      } else {
        if (canDecrease.value) inputText.value = correctPrecision(model.value - props.step, inferredPrecision);
      }
    }
    function onBeforeinput(e) {
      if (!e.data) return;
      const existingTxt = e.target?.value;
      const selectionStart = e.target?.selectionStart;
      const selectionEnd = e.target?.selectionEnd;
      const potentialNewInputVal = existingTxt ? existingTxt.slice(0, selectionStart) + e.data + existingTxt.slice(selectionEnd) : e.data;
      // Only numbers, "-", "." are allowed
      // AND "-", "." are allowed only once
      // AND "-" is only allowed at the start
      if (!/^-?(\d+(\.\d*)?|(\.\d+)|\d*|\.)$/.test(potentialNewInputVal)) {
        e.preventDefault();
      }
      if (props.precision == null) return;

      // Ignore decimal digits above precision limit
      if (potentialNewInputVal.split('.')[1]?.length > props.precision) {
        e.preventDefault();
      }
      // Ignore decimal separator when precision = 0
      if (props.precision === 0 && potentialNewInputVal.includes('.')) {
        e.preventDefault();
      }
    }
    async function onKeydown(e) {
      if (['Enter', 'ArrowLeft', 'ArrowRight', 'Backspace', 'Delete', 'Tab'].includes(e.key) || e.ctrlKey) return;
      if (['ArrowDown', 'ArrowUp'].includes(e.key)) {
        e.preventDefault();
        clampModel();
        // _model is controlled, so need to wait until props['modelValue'] is updated
        await nextTick$5();
        if (e.key === 'ArrowDown') {
          toggleUpDown(false);
        } else {
          toggleUpDown();
        }
      }
    }
    function onControlClick(e) {
      e.stopPropagation();
    }
    function onControlMouseup(e) {
      const el = e.currentTarget;
      el?.releasePointerCapture(e.pointerId);
      e.preventDefault();
      e.stopPropagation();
      holdStop();
    }
    function onUpControlMousedown(e) {
      const el = e.currentTarget;
      el?.setPointerCapture(e.pointerId);
      e.preventDefault();
      e.stopPropagation();
      holdStart('up');
    }
    function onDownControlMousedown(e) {
      const el = e.currentTarget;
      el?.setPointerCapture(e.pointerId);
      e.preventDefault();
      e.stopPropagation();
      holdStart('down');
    }
    function clampModel() {
      if (controlsDisabled.value) return;
      if (!vTextFieldRef.value) return;
      const actualText = vTextFieldRef.value.value;
      if (actualText && !isNaN(Number(actualText))) {
        inputText.value = correctPrecision(clamp(Number(actualText), props.min, props.max));
      } else {
        inputText.value = null;
      }
    }
    function formatInputValue() {
      if (controlsDisabled.value) return;
      if (model.value === null || isNaN(model.value)) {
        inputText.value = null;
        return;
      }
      inputText.value = props.precision == null ? String(model.value) : model.value.toFixed(props.precision);
    }
    function trimDecimalZeros() {
      if (controlsDisabled.value) return;
      if (model.value === null || isNaN(model.value)) {
        inputText.value = null;
        return;
      }
      inputText.value = model.value.toString();
    }
    function onFocus() {
      focus();
      trimDecimalZeros();
    }
    function onBlur() {
      blur();
      clampModel();
    }
    useRender(() => {
      const {
        modelValue: _,
        ...textFieldProps
      } = VTextField.filterProps(props);
      function incrementControlNode() {
        return !slots.increment ? _createVNode$v(VBtn, {
          "disabled": !canIncrease.value,
          "flat": true,
          "key": "increment-btn",
          "height": controlNodeDefaultHeight.value,
          "data-testid": "increment",
          "aria-hidden": "true",
          "icon": incrementIcon.value,
          "onClick": onControlClick,
          "onPointerup": onControlMouseup,
          "onPointerdown": onUpControlMousedown,
          "size": controlNodeSize.value,
          "tabindex": "-1"
        }, null) : _createVNode$v(VDefaultsProvider, {
          "key": "increment-defaults",
          "defaults": {
            VBtn: {
              disabled: !canIncrease.value,
              flat: true,
              height: controlNodeDefaultHeight.value,
              size: controlNodeSize.value,
              icon: incrementIcon.value
            }
          }
        }, {
          default: () => [slots.increment(incrementSlotProps)]
        });
      }
      function decrementControlNode() {
        return !slots.decrement ? _createVNode$v(VBtn, {
          "disabled": !canDecrease.value,
          "flat": true,
          "key": "decrement-btn",
          "height": controlNodeDefaultHeight.value,
          "data-testid": "decrement",
          "aria-hidden": "true",
          "icon": decrementIcon.value,
          "size": controlNodeSize.value,
          "tabindex": "-1",
          "onClick": onControlClick,
          "onPointerup": onControlMouseup,
          "onPointerdown": onDownControlMousedown
        }, null) : _createVNode$v(VDefaultsProvider, {
          "key": "decrement-defaults",
          "defaults": {
            VBtn: {
              disabled: !canDecrease.value,
              flat: true,
              height: controlNodeDefaultHeight.value,
              size: controlNodeSize.value,
              icon: decrementIcon.value
            }
          }
        }, {
          default: () => [slots.decrement(decrementSlotProps)]
        });
      }
      function controlNode() {
        return _createVNode$v("div", {
          "class": "v-number-input__control"
        }, [decrementControlNode(), _createVNode$v(VDivider, {
          "vertical": controlVariant.value !== 'stacked'
        }, null), incrementControlNode()]);
      }
      function dividerNode() {
        return !props.hideInput && !props.inset ? _createVNode$v(VDivider, {
          "vertical": true
        }, null) : undefined;
      }
      const appendInnerControl = controlVariant.value === 'split' ? _createVNode$v("div", {
        "class": "v-number-input__control"
      }, [_createVNode$v(VDivider, {
        "vertical": true
      }, null), incrementControlNode()]) : props.reverse || controlVariant.value === 'hidden' ? undefined : _createVNode$v(_Fragment$b, null, [dividerNode(), controlNode()]);
      const hasAppendInner = slots['append-inner'] || appendInnerControl;
      const prependInnerControl = controlVariant.value === 'split' ? _createVNode$v("div", {
        "class": "v-number-input__control"
      }, [decrementControlNode(), _createVNode$v(VDivider, {
        "vertical": true
      }, null)]) : props.reverse && controlVariant.value !== 'hidden' ? _createVNode$v(_Fragment$b, null, [controlNode(), dividerNode()]) : undefined;
      const hasPrependInner = slots['prepend-inner'] || prependInnerControl;
      return _createVNode$v(VTextField, _mergeProps$k({
        "ref": vTextFieldRef,
        "modelValue": inputText.value,
        "onUpdate:modelValue": $event => inputText.value = $event,
        "validationValue": model.value,
        "onBeforeinput": onBeforeinput,
        "onFocus": onFocus,
        "onBlur": onBlur,
        "onKeydown": onKeydown,
        "class": ['v-number-input', {
          'v-number-input--default': controlVariant.value === 'default',
          'v-number-input--hide-input': props.hideInput,
          'v-number-input--inset': props.inset,
          'v-number-input--reverse': props.reverse,
          'v-number-input--split': controlVariant.value === 'split',
          'v-number-input--stacked': controlVariant.value === 'stacked'
        }, props.class]
      }, textFieldProps, {
        "style": props.style,
        "inputmode": "decimal"
      }), {
        ...slots,
        'append-inner': hasAppendInner ? function () {
          for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
            args[_key] = arguments[_key];
          }
          return _createVNode$v(_Fragment$b, null, [slots['append-inner']?.(...args), appendInnerControl]);
        } : undefined,
        'prepend-inner': hasPrependInner ? function () {
          for (var _len2 = arguments.length, args = new Array(_len2), _key2 = 0; _key2 < _len2; _key2++) {
            args[_key2] = arguments[_key2];
          }
          return _createVNode$v(_Fragment$b, null, [prependInnerControl, slots['prepend-inner']?.(...args)]);
        } : undefined
      });
    });
    return forwardRefs({}, vTextFieldRef);
  }
});

const {Fragment:_Fragment$a,createVNode:_createVNode$u,mergeProps:_mergeProps$j} = await importShared('vue');
const {computed: computed$l,nextTick: nextTick$4,ref: ref$a,toRef: toRef$6,watch: watch$6} = await importShared('vue');
// Types
const makeVOtpInputProps = propsFactory({
  autofocus: Boolean,
  divider: String,
  focusAll: Boolean,
  label: {
    type: String,
    default: '$vuetify.input.otp'
  },
  length: {
    type: [Number, String],
    default: 6
  },
  modelValue: {
    type: [Number, String],
    default: undefined
  },
  placeholder: String,
  type: {
    type: String,
    default: 'number'
  },
  ...makeDimensionProps(),
  ...makeFocusProps(),
  ...pick(makeVFieldProps({
    variant: 'outlined'
  }), ['baseColor', 'bgColor', 'class', 'color', 'disabled', 'error', 'loading', 'rounded', 'style', 'theme', 'variant'])
}, 'VOtpInput');
const VOtpInput = genericComponent()({
  name: 'VOtpInput',
  props: makeVOtpInputProps(),
  emits: {
    finish: val => true,
    'update:focused': val => true,
    'update:modelValue': val => true
  },
  setup(props, _ref) {
    let {
      attrs,
      emit,
      slots
    } = _ref;
    const {
      dimensionStyles
    } = useDimension(props);
    const {
      isFocused,
      focus,
      blur
    } = useFocus(props);
    const model = useProxiedModel(props, 'modelValue', '', val => val == null ? [] : String(val).split(''), val => val.join(''));
    const {
      t
    } = useLocale();
    const length = computed$l(() => Number(props.length));
    const fields = computed$l(() => Array(length.value).fill(0));
    const focusIndex = ref$a(-1);
    const contentRef = ref$a();
    const inputRef = ref$a([]);
    const current = computed$l(() => inputRef.value[focusIndex.value]);
    function onInput() {
      // The maxlength attribute doesn't work for the number type input, so the text type is used.
      // The following logic simulates the behavior of a number input.
      if (isValidNumber(current.value.value)) {
        current.value.value = '';
        return;
      }
      const array = model.value.slice();
      const value = current.value.value;
      array[focusIndex.value] = value;
      let target = null;
      if (focusIndex.value > model.value.length) {
        target = model.value.length + 1;
      } else if (focusIndex.value + 1 !== length.value) {
        target = 'next';
      }
      model.value = array;
      if (target) focusChild(contentRef.value, target);
    }
    function onKeydown(e) {
      const array = model.value.slice();
      const index = focusIndex.value;
      let target = null;
      if (!['ArrowLeft', 'ArrowRight', 'Backspace', 'Delete'].includes(e.key)) return;
      e.preventDefault();
      if (e.key === 'ArrowLeft') {
        target = 'prev';
      } else if (e.key === 'ArrowRight') {
        target = 'next';
      } else if (['Backspace', 'Delete'].includes(e.key)) {
        array[focusIndex.value] = '';
        model.value = array;
        if (focusIndex.value > 0 && e.key === 'Backspace') {
          target = 'prev';
        } else {
          requestAnimationFrame(() => {
            inputRef.value[index]?.select();
          });
        }
      }
      requestAnimationFrame(() => {
        if (target != null) {
          focusChild(contentRef.value, target);
        }
      });
    }
    function onPaste(index, e) {
      e.preventDefault();
      e.stopPropagation();
      const clipboardText = e?.clipboardData?.getData('Text').slice(0, length.value) ?? '';
      if (isValidNumber(clipboardText)) return;
      model.value = clipboardText.split('');
      inputRef.value?.[index].blur();
    }
    function reset() {
      model.value = [];
    }
    function onFocus(e, index) {
      focus();
      focusIndex.value = index;
    }
    function onBlur() {
      blur();
      focusIndex.value = -1;
    }
    function isValidNumber(value) {
      return props.type === 'number' && /[^0-9]/g.test(value);
    }
    provideDefaults({
      VField: {
        color: toRef$6(() => props.color),
        bgColor: toRef$6(() => props.color),
        baseColor: toRef$6(() => props.baseColor),
        disabled: toRef$6(() => props.disabled),
        error: toRef$6(() => props.error),
        variant: toRef$6(() => props.variant)
      }
    }, {
      scoped: true
    });
    watch$6(model, val => {
      if (val.length === length.value) emit('finish', val.join(''));
    }, {
      deep: true
    });
    watch$6(focusIndex, val => {
      if (val < 0) return;
      nextTick$4(() => {
        inputRef.value[val]?.select();
      });
    });
    useRender(() => {
      const [rootAttrs, inputAttrs] = filterInputAttrs(attrs);
      return _createVNode$u("div", _mergeProps$j({
        "class": ['v-otp-input', {
          'v-otp-input--divided': !!props.divider
        }, props.class],
        "style": [props.style]
      }, rootAttrs), [_createVNode$u("div", {
        "ref": contentRef,
        "class": "v-otp-input__content",
        "style": [dimensionStyles.value]
      }, [fields.value.map((_, i) => _createVNode$u(_Fragment$a, null, [props.divider && i !== 0 && _createVNode$u("span", {
        "class": "v-otp-input__divider"
      }, [props.divider]), _createVNode$u(VField, {
        "focused": isFocused.value && props.focusAll || focusIndex.value === i,
        "key": i
      }, {
        ...slots,
        loader: undefined,
        default: () => {
          return _createVNode$u("input", {
            "ref": val => inputRef.value[i] = val,
            "aria-label": t(props.label, i + 1),
            "autofocus": i === 0 && props.autofocus,
            "autocomplete": "one-time-code",
            "class": ['v-otp-input__field'],
            "disabled": props.disabled,
            "inputmode": props.type === 'number' ? 'numeric' : 'text',
            "min": props.type === 'number' ? 0 : undefined,
            "maxlength": i === 0 ? length.value : '1',
            "placeholder": props.placeholder,
            "type": props.type === 'number' ? 'text' : props.type,
            "value": model.value[i],
            "onInput": onInput,
            "onFocus": e => onFocus(e, i),
            "onBlur": onBlur,
            "onKeydown": onKeydown,
            "onPaste": event => onPaste(i, event)
          }, null);
        }
      })])), _createVNode$u("input", _mergeProps$j({
        "class": "v-otp-input-input",
        "type": "hidden"
      }, inputAttrs, {
        "value": model.value.join('')
      }), null), _createVNode$u(VOverlay, {
        "contained": true,
        "content-class": "v-otp-input__loader",
        "model-value": !!props.loading,
        "persistent": true
      }, {
        default: () => [slots.loader?.() ?? _createVNode$u(VProgressCircular, {
          "color": typeof props.loading === 'boolean' ? undefined : props.loading,
          "indeterminate": true,
          "size": "24",
          "width": "2"
        }, null)]
      }), slots.default?.()])]);
    });
    return {
      blur: () => {
        inputRef.value?.some(input => input.blur());
      },
      focus: () => {
        inputRef.value?.[0].focus();
      },
      reset,
      isFocused
    };
  }
});

const {createVNode:_createVNode$t} = await importShared('vue');
const {computed: computed$k,onBeforeUnmount: onBeforeUnmount$1,ref: ref$9,watch: watch$5,watchEffect: watchEffect$2} = await importShared('vue');
function floor(val) {
  return Math.floor(Math.abs(val)) * Math.sign(val);
}
const makeVParallaxProps = propsFactory({
  scale: {
    type: [Number, String],
    default: 0.5
  },
  ...makeComponentProps()
}, 'VParallax');
const VParallax = genericComponent()({
  name: 'VParallax',
  props: makeVParallaxProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      intersectionRef,
      isIntersecting
    } = useIntersectionObserver();
    const {
      resizeRef,
      contentRect
    } = useResizeObserver();
    const {
      height: displayHeight
    } = useDisplay();
    const root = ref$9();
    watchEffect$2(() => {
      intersectionRef.value = resizeRef.value = root.value?.$el;
    });
    let scrollParent;
    watch$5(isIntersecting, val => {
      if (val) {
        scrollParent = getScrollParent(intersectionRef.value);
        scrollParent = scrollParent === document.scrollingElement ? document : scrollParent;
        scrollParent.addEventListener('scroll', onScroll, {
          passive: true
        });
        onScroll();
      } else {
        scrollParent.removeEventListener('scroll', onScroll);
      }
    });
    onBeforeUnmount$1(() => {
      scrollParent?.removeEventListener('scroll', onScroll);
    });
    watch$5(displayHeight, onScroll);
    watch$5(() => contentRect.value?.height, onScroll);
    const scale = computed$k(() => {
      return 1 - clamp(Number(props.scale));
    });
    let frame = -1;
    function onScroll() {
      if (!isIntersecting.value) return;
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const el = (root.value?.$el).querySelector('.v-img__img');
        if (!el) return;
        const scrollHeight = scrollParent instanceof Document ? document.documentElement.clientHeight : scrollParent.clientHeight;
        const scrollPos = scrollParent instanceof Document ? window.scrollY : scrollParent.scrollTop;
        const top = intersectionRef.value.getBoundingClientRect().top + scrollPos;
        const height = contentRect.value.height;
        const center = top + (height - scrollHeight) / 2;
        const translate = floor((scrollPos - center) * scale.value);
        const sizeScale = Math.max(1, (scale.value * (scrollHeight - height) + height) / height);
        el.style.setProperty('transform', `translateY(${translate}px) scale(${sizeScale})`);
      });
    }
    useRender(() => _createVNode$t(VImg, {
      "class": ['v-parallax', {
        'v-parallax--active': isIntersecting.value
      }, props.class],
      "style": props.style,
      "ref": root,
      "cover": true,
      "onLoadstart": onScroll,
      "onLoad": onScroll
    }, slots));
    return {};
  }
});

const {mergeProps:_mergeProps$i,createVNode:_createVNode$s} = await importShared('vue');
const makeVRadioProps = propsFactory({
  ...makeVSelectionControlProps({
    falseIcon: '$radioOff',
    trueIcon: '$radioOn'
  })
}, 'VRadio');
const VRadio = genericComponent()({
  name: 'VRadio',
  props: makeVRadioProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    useRender(() => {
      const controlProps = VSelectionControl.filterProps(props);
      return _createVNode$s(VSelectionControl, _mergeProps$i(controlProps, {
        "class": ['v-radio', props.class],
        "style": props.style,
        "type": "radio"
      }), slots);
    });
    return {};
  }
});

const {Fragment:_Fragment$9,createVNode:_createVNode$r,mergeProps:_mergeProps$h} = await importShared('vue');
const {computed: computed$j,useId: useId$5} = await importShared('vue');
const makeVRadioGroupProps = propsFactory({
  height: {
    type: [Number, String],
    default: 'auto'
  },
  ...makeVInputProps(),
  ...omit(makeSelectionControlGroupProps(), ['multiple']),
  trueIcon: {
    type: IconValue,
    default: '$radioOn'
  },
  falseIcon: {
    type: IconValue,
    default: '$radioOff'
  },
  type: {
    type: String,
    default: 'radio'
  }
}, 'VRadioGroup');
const VRadioGroup = genericComponent()({
  name: 'VRadioGroup',
  inheritAttrs: false,
  props: makeVRadioGroupProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      attrs,
      slots
    } = _ref;
    const uid = useId$5();
    const id = computed$j(() => props.id || `radio-group-${uid}`);
    const model = useProxiedModel(props, 'modelValue');
    useRender(() => {
      const [rootAttrs, controlAttrs] = filterInputAttrs(attrs);
      const inputProps = VInput.filterProps(props);
      const controlProps = VSelectionControl.filterProps(props);
      const label = slots.label ? slots.label({
        label: props.label,
        props: {
          for: id.value
        }
      }) : props.label;
      return _createVNode$r(VInput, _mergeProps$h({
        "class": ['v-radio-group', props.class],
        "style": props.style
      }, rootAttrs, inputProps, {
        "modelValue": model.value,
        "onUpdate:modelValue": $event => model.value = $event,
        "id": id.value
      }), {
        ...slots,
        default: _ref2 => {
          let {
            id,
            messagesId,
            isDisabled,
            isReadonly
          } = _ref2;
          return _createVNode$r(_Fragment$9, null, [label && _createVNode$r(VLabel, {
            "id": id.value
          }, {
            default: () => [label]
          }), _createVNode$r(VSelectionControlGroup, _mergeProps$h(controlProps, {
            "id": id.value,
            "aria-describedby": messagesId.value,
            "defaultsTarget": "VRadio",
            "trueIcon": props.trueIcon,
            "falseIcon": props.falseIcon,
            "type": props.type,
            "disabled": isDisabled.value,
            "readonly": isReadonly.value,
            "aria-labelledby": label ? id.value : undefined,
            "multiple": false
          }, controlAttrs, {
            "modelValue": model.value,
            "onUpdate:modelValue": $event => model.value = $event
          }), slots)]);
        }
      });
    });
    return {};
  }
});

const {Fragment:_Fragment$8,createVNode:_createVNode$q,mergeProps:_mergeProps$g} = await importShared('vue');
const {computed: computed$i,ref: ref$8} = await importShared('vue');
const makeVRangeSliderProps = propsFactory({
  ...makeFocusProps(),
  ...makeVInputProps(),
  ...makeSliderProps(),
  strict: Boolean,
  modelValue: {
    type: Array,
    default: () => [0, 0]
  }
}, 'VRangeSlider');
const VRangeSlider = genericComponent()({
  name: 'VRangeSlider',
  props: makeVRangeSliderProps(),
  emits: {
    'update:focused': value => true,
    'update:modelValue': value => true,
    end: value => true,
    start: value => true
  },
  setup(props, _ref) {
    let {
      slots,
      emit
    } = _ref;
    const startThumbRef = ref$8();
    const stopThumbRef = ref$8();
    const inputRef = ref$8();
    const {
      rtlClasses
    } = useRtl();
    function getActiveThumb(e) {
      if (!startThumbRef.value || !stopThumbRef.value) return;
      const startOffset = getOffset(e, startThumbRef.value.$el, props.direction);
      const stopOffset = getOffset(e, stopThumbRef.value.$el, props.direction);
      const a = Math.abs(startOffset);
      const b = Math.abs(stopOffset);
      return a < b || a === b && startOffset < 0 ? startThumbRef.value.$el : stopThumbRef.value.$el;
    }
    const steps = useSteps(props);
    const model = useProxiedModel(props, 'modelValue', undefined, arr => {
      if (!arr?.length) return [0, 0];
      return arr.map(value => steps.roundValue(value));
    });
    const {
      activeThumbRef,
      hasLabels,
      max,
      min,
      mousePressed,
      onSliderMousedown,
      onSliderTouchstart,
      position,
      trackContainerRef,
      readonly
    } = useSlider({
      props,
      steps,
      onSliderStart: () => {
        emit('start', model.value);
      },
      onSliderEnd: _ref2 => {
        let {
          value
        } = _ref2;
        const newValue = activeThumbRef.value === startThumbRef.value?.$el ? [value, model.value[1]] : [model.value[0], value];
        if (!props.strict && newValue[0] < newValue[1]) {
          model.value = newValue;
        }
        emit('end', model.value);
      },
      onSliderMove: _ref3 => {
        let {
          value
        } = _ref3;
        const [start, stop] = model.value;
        if (!props.strict && start === stop && start !== min.value) {
          activeThumbRef.value = value > start ? stopThumbRef.value?.$el : startThumbRef.value?.$el;
          activeThumbRef.value?.focus();
        }
        if (activeThumbRef.value === startThumbRef.value?.$el) {
          model.value = [Math.min(value, stop), stop];
        } else {
          model.value = [start, Math.max(start, value)];
        }
      },
      getActiveThumb
    });
    const {
      isFocused,
      focus,
      blur
    } = useFocus(props);
    const trackStart = computed$i(() => position(model.value[0]));
    const trackStop = computed$i(() => position(model.value[1]));
    useRender(() => {
      const inputProps = VInput.filterProps(props);
      const hasPrepend = !!(props.label || slots.label || slots.prepend);
      return _createVNode$q(VInput, _mergeProps$g({
        "class": ['v-slider', 'v-range-slider', {
          'v-slider--has-labels': !!slots['tick-label'] || hasLabels.value,
          'v-slider--focused': isFocused.value,
          'v-slider--pressed': mousePressed.value,
          'v-slider--disabled': props.disabled
        }, rtlClasses.value, props.class],
        "style": props.style,
        "ref": inputRef
      }, inputProps, {
        "focused": isFocused.value
      }), {
        ...slots,
        prepend: hasPrepend ? slotProps => _createVNode$q(_Fragment$8, null, [slots.label?.(slotProps) ?? (props.label ? _createVNode$q(VLabel, {
          "class": "v-slider__label",
          "text": props.label
        }, null) : undefined), slots.prepend?.(slotProps)]) : undefined,
        default: _ref4 => {
          let {
            id,
            messagesId
          } = _ref4;
          return _createVNode$q("div", {
            "class": "v-slider__container",
            "onMousedown": !readonly.value ? onSliderMousedown : undefined,
            "onTouchstartPassive": !readonly.value ? onSliderTouchstart : undefined
          }, [_createVNode$q("input", {
            "id": `${id.value}_start`,
            "name": props.name || id.value,
            "disabled": !!props.disabled,
            "readonly": !!props.readonly,
            "tabindex": "-1",
            "value": model.value[0]
          }, null), _createVNode$q("input", {
            "id": `${id.value}_stop`,
            "name": props.name || id.value,
            "disabled": !!props.disabled,
            "readonly": !!props.readonly,
            "tabindex": "-1",
            "value": model.value[1]
          }, null), _createVNode$q(VSliderTrack, {
            "ref": trackContainerRef,
            "start": trackStart.value,
            "stop": trackStop.value
          }, {
            'tick-label': slots['tick-label']
          }), _createVNode$q(VSliderThumb, {
            "ref": startThumbRef,
            "aria-describedby": messagesId.value,
            "focused": isFocused && activeThumbRef.value === startThumbRef.value?.$el,
            "modelValue": model.value[0],
            "onUpdate:modelValue": v => model.value = [v, model.value[1]],
            "onFocus": e => {
              focus();
              activeThumbRef.value = startThumbRef.value?.$el;

              // Make sure second thumb is focused if
              // the thumbs are on top of each other
              // and they are both at minimum value
              // but only if focused from outside.
              if (max.value !== min.value && model.value[0] === model.value[1] && model.value[1] === min.value && e.relatedTarget !== stopThumbRef.value?.$el) {
                startThumbRef.value?.$el.blur();
                stopThumbRef.value?.$el.focus();
              }
            },
            "onBlur": () => {
              blur();
              activeThumbRef.value = undefined;
            },
            "min": min.value,
            "max": model.value[1],
            "position": trackStart.value,
            "ripple": props.ripple
          }, {
            'thumb-label': slots['thumb-label']
          }), _createVNode$q(VSliderThumb, {
            "ref": stopThumbRef,
            "aria-describedby": messagesId.value,
            "focused": isFocused && activeThumbRef.value === stopThumbRef.value?.$el,
            "modelValue": model.value[1],
            "onUpdate:modelValue": v => model.value = [model.value[0], v],
            "onFocus": e => {
              focus();
              activeThumbRef.value = stopThumbRef.value?.$el;

              // Make sure first thumb is focused if
              // the thumbs are on top of each other
              // and they are both at maximum value
              // but only if focused from outside.
              if (max.value !== min.value && model.value[0] === model.value[1] && model.value[0] === max.value && e.relatedTarget !== startThumbRef.value?.$el) {
                stopThumbRef.value?.$el.blur();
                startThumbRef.value?.$el.focus();
              }
            },
            "onBlur": () => {
              blur();
              activeThumbRef.value = undefined;
            },
            "min": model.value[0],
            "max": max.value,
            "position": trackStop.value,
            "ripple": props.ripple
          }, {
            'thumb-label': slots['thumb-label']
          })]);
        }
      });
    });
    return {};
  }
});

const {Fragment:_Fragment$7,createVNode:_createVNode$p,mergeProps:_mergeProps$f,createTextVNode:_createTextVNode} = await importShared('vue');
const {computed: computed$h,shallowRef: shallowRef$5,useId: useId$4} = await importShared('vue');
const makeVRatingProps = propsFactory({
  name: String,
  itemAriaLabel: {
    type: String,
    default: '$vuetify.rating.ariaLabel.item'
  },
  activeColor: String,
  color: String,
  clearable: Boolean,
  disabled: Boolean,
  emptyIcon: {
    type: IconValue,
    default: '$ratingEmpty'
  },
  fullIcon: {
    type: IconValue,
    default: '$ratingFull'
  },
  halfIncrements: Boolean,
  hover: Boolean,
  length: {
    type: [Number, String],
    default: 5
  },
  readonly: Boolean,
  modelValue: {
    type: [Number, String],
    default: 0
  },
  itemLabels: Array,
  itemLabelPosition: {
    type: String,
    default: 'top',
    validator: v => ['top', 'bottom'].includes(v)
  },
  ripple: Boolean,
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeSizeProps(),
  ...makeTagProps(),
  ...makeThemeProps()
}, 'VRating');
const VRating = genericComponent()({
  name: 'VRating',
  props: makeVRatingProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      t
    } = useLocale();
    const {
      themeClasses
    } = provideTheme(props);
    const rating = useProxiedModel(props, 'modelValue');
    const normalizedValue = computed$h(() => clamp(parseFloat(rating.value), 0, Number(props.length)));
    const range = computed$h(() => createRange(Number(props.length), 1));
    const increments = computed$h(() => range.value.flatMap(v => props.halfIncrements ? [v - 0.5, v] : [v]));
    const hoverIndex = shallowRef$5(-1);
    const itemState = computed$h(() => increments.value.map(value => {
      const isHovering = props.hover && hoverIndex.value > -1;
      const isFilled = normalizedValue.value >= value;
      const isHovered = hoverIndex.value >= value;
      const isFullIcon = isHovering ? isHovered : isFilled;
      const icon = isFullIcon ? props.fullIcon : props.emptyIcon;
      const activeColor = props.activeColor ?? props.color;
      const color = isFilled || isHovered ? activeColor : props.color;
      return {
        isFilled,
        isHovered,
        icon,
        color
      };
    }));
    const eventState = computed$h(() => [0, ...increments.value].map(value => {
      function onMouseenter() {
        hoverIndex.value = value;
      }
      function onMouseleave() {
        hoverIndex.value = -1;
      }
      function onClick() {
        if (props.disabled || props.readonly) return;
        rating.value = normalizedValue.value === value && props.clearable ? 0 : value;
      }
      return {
        onMouseenter: props.hover ? onMouseenter : undefined,
        onMouseleave: props.hover ? onMouseleave : undefined,
        onClick
      };
    }));
    const uid = useId$4();
    const name = computed$h(() => props.name ?? `v-rating-${uid}`);
    function VRatingItem(_ref2) {
      let {
        value,
        index,
        showStar = true
      } = _ref2;
      const {
        onMouseenter,
        onMouseleave,
        onClick
      } = eventState.value[index + 1];
      const id = `${name.value}-${String(value).replace('.', '-')}`;
      const btnProps = {
        color: itemState.value[index]?.color,
        density: props.density,
        disabled: props.disabled,
        icon: itemState.value[index]?.icon,
        ripple: props.ripple,
        size: props.size,
        variant: 'plain'
      };
      return _createVNode$p(_Fragment$7, null, [_createVNode$p("label", {
        "for": id,
        "class": {
          'v-rating__item--half': props.halfIncrements && value % 1 > 0,
          'v-rating__item--full': props.halfIncrements && value % 1 === 0
        },
        "onMouseenter": onMouseenter,
        "onMouseleave": onMouseleave,
        "onClick": onClick
      }, [_createVNode$p("span", {
        "class": "v-rating__hidden"
      }, [t(props.itemAriaLabel, value, props.length)]), !showStar ? undefined : slots.item ? slots.item({
        ...itemState.value[index],
        props: btnProps,
        value,
        index,
        rating: normalizedValue.value
      }) : _createVNode$p(VBtn, _mergeProps$f({
        "aria-label": t(props.itemAriaLabel, value, props.length)
      }, btnProps), null)]), _createVNode$p("input", {
        "class": "v-rating__hidden",
        "name": name.value,
        "id": id,
        "type": "radio",
        "value": value,
        "checked": normalizedValue.value === value,
        "tabindex": -1,
        "readonly": props.readonly,
        "disabled": props.disabled
      }, null)]);
    }
    function createLabel(labelProps) {
      if (slots['item-label']) return slots['item-label'](labelProps);
      if (labelProps.label) return _createVNode$p("span", null, [labelProps.label]);
      return _createVNode$p("span", null, [_createTextVNode("\xA0")]);
    }
    useRender(() => {
      const hasLabels = !!props.itemLabels?.length || slots['item-label'];
      return _createVNode$p(props.tag, {
        "class": ['v-rating', {
          'v-rating--hover': props.hover,
          'v-rating--readonly': props.readonly
        }, themeClasses.value, props.class],
        "style": props.style
      }, {
        default: () => [_createVNode$p(VRatingItem, {
          "value": 0,
          "index": -1,
          "showStar": false
        }, null), range.value.map((value, i) => _createVNode$p("div", {
          "class": "v-rating__wrapper"
        }, [hasLabels && props.itemLabelPosition === 'top' ? createLabel({
          value,
          index: i,
          label: props.itemLabels?.[i]
        }) : undefined, _createVNode$p("div", {
          "class": "v-rating__item"
        }, [props.halfIncrements ? _createVNode$p(_Fragment$7, null, [_createVNode$p(VRatingItem, {
          "value": value - 0.5,
          "index": i * 2
        }, null), _createVNode$p(VRatingItem, {
          "value": value,
          "index": i * 2 + 1
        }, null)]) : _createVNode$p(VRatingItem, {
          "value": value,
          "index": i
        }, null)]), hasLabels && props.itemLabelPosition === 'bottom' ? createLabel({
          value,
          index: i,
          label: props.itemLabels?.[i]
        }) : undefined]))]
      });
    });
    return {};
  }
});

const {createVNode:_createVNode$o,mergeProps:_mergeProps$e} = await importShared('vue');
const {computed: computed$g} = await importShared('vue');
const rootTypes = {
  actions: 'button@2',
  article: 'heading, paragraph',
  avatar: 'avatar',
  button: 'button',
  card: 'image, heading',
  'card-avatar': 'image, list-item-avatar',
  chip: 'chip',
  'date-picker': 'list-item, heading, divider, date-picker-options, date-picker-days, actions',
  'date-picker-options': 'text, avatar@2',
  'date-picker-days': 'avatar@28',
  divider: 'divider',
  heading: 'heading',
  image: 'image',
  'list-item': 'text',
  'list-item-avatar': 'avatar, text',
  'list-item-two-line': 'sentences',
  'list-item-avatar-two-line': 'avatar, sentences',
  'list-item-three-line': 'paragraph',
  'list-item-avatar-three-line': 'avatar, paragraph',
  ossein: 'ossein',
  paragraph: 'text@3',
  sentences: 'text@2',
  subtitle: 'text',
  table: 'table-heading, table-thead, table-tbody, table-tfoot',
  'table-heading': 'chip, text',
  'table-thead': 'heading@6',
  'table-tbody': 'table-row-divider@6',
  'table-row-divider': 'table-row, divider',
  'table-row': 'text@6',
  'table-tfoot': 'text@2, avatar@2',
  text: 'text'
};
function genBone(type) {
  let children = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];
  return _createVNode$o("div", {
    "class": ['v-skeleton-loader__bone', `v-skeleton-loader__${type}`]
  }, [children]);
}
function genBones(bone) {
  // e.g. 'text@3'
  const [type, length] = bone.split('@');

  // Generate a length array based upon
  // value after @ in the bone string
  return Array.from({
    length
  }).map(() => genStructure(type));
}
function genStructure(type) {
  let children = [];
  if (!type) return children;

  // TODO: figure out a better way to type this
  const bone = rootTypes[type];

  // End of recursion, do nothing
  /* eslint-disable-next-line no-empty, brace-style */
  if (type === bone) ;
  // Array of values - e.g. 'heading, paragraph, text@2'
  else if (type.includes(',')) return mapBones(type);
  // Array of values - e.g. 'paragraph@4'
  else if (type.includes('@')) return genBones(type);
  // Array of values - e.g. 'card@2'
  else if (bone.includes(',')) children = mapBones(bone);
  // Array of values - e.g. 'list-item@2'
  else if (bone.includes('@')) children = genBones(bone);
  // Single value - e.g. 'card-heading'
  else if (bone) children.push(genStructure(bone));
  return [genBone(type, children)];
}
function mapBones(bones) {
  // Remove spaces and return array of structures
  return bones.replace(/\s/g, '').split(',').map(genStructure);
}
const makeVSkeletonLoaderProps = propsFactory({
  boilerplate: Boolean,
  color: String,
  loading: Boolean,
  loadingText: {
    type: String,
    default: '$vuetify.loading'
  },
  type: {
    type: [String, Array],
    default: 'ossein'
  },
  ...makeDimensionProps(),
  ...makeElevationProps(),
  ...makeThemeProps()
}, 'VSkeletonLoader');
const VSkeletonLoader = genericComponent()({
  name: 'VSkeletonLoader',
  props: makeVSkeletonLoaderProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.color);
    const {
      dimensionStyles
    } = useDimension(props);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      themeClasses
    } = provideTheme(props);
    const {
      t
    } = useLocale();
    const items = computed$g(() => genStructure(wrapInArray(props.type).join(',')));
    useRender(() => {
      const isLoading = !slots.default || props.loading;
      const loadingProps = props.boilerplate || !isLoading ? {} : {
        ariaLive: 'polite',
        ariaLabel: t(props.loadingText),
        role: 'alert'
      };
      return _createVNode$o("div", _mergeProps$e({
        "class": ['v-skeleton-loader', {
          'v-skeleton-loader--boilerplate': props.boilerplate
        }, themeClasses.value, backgroundColorClasses.value, elevationClasses.value],
        "style": [backgroundColorStyles.value, isLoading ? dimensionStyles.value : {}]
      }, loadingProps), [isLoading ? items.value : slots.default?.()]);
    });
    return {};
  }
});

// Composables
const VSlideGroupItem = genericComponent()({
  name: 'VSlideGroupItem',
  props: makeGroupItemProps(),
  emits: {
    'group:selected': val => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const slideGroupItem = useGroupItem(props, VSlideGroupSymbol);
    return () => slots.default?.({
      isSelected: slideGroupItem.isSelected.value,
      select: slideGroupItem.select,
      toggle: slideGroupItem.toggle,
      selectedClass: slideGroupItem.selectedClass.value
    });
  }
});

const {createVNode:_createVNode$n,mergeProps:_mergeProps$d} = await importShared('vue');
const {computed: computed$f,inject: inject$2,mergeProps: mergeProps$2,nextTick: nextTick$3,onMounted: onMounted$1,onScopeDispose,ref: ref$7,shallowRef: shallowRef$4,watch: watch$4,watchEffect: watchEffect$1} = await importShared('vue');
function useCountdown(milliseconds) {
  const time = shallowRef$4(milliseconds());
  let timer = -1;
  function clear() {
    clearInterval(timer);
  }
  function reset() {
    clear();
    nextTick$3(() => time.value = milliseconds());
  }
  function start(el) {
    const style = el ? getComputedStyle(el) : {
      transitionDuration: 0.2
    };
    const interval = parseFloat(style.transitionDuration) * 1000 || 200;
    clear();
    if (time.value <= 0) return;
    const startTime = performance.now();
    timer = window.setInterval(() => {
      const elapsed = performance.now() - startTime + interval;
      time.value = Math.max(milliseconds() - elapsed, 0);
      if (time.value <= 0) clear();
    }, interval);
  }
  onScopeDispose(clear);
  return {
    clear,
    time,
    start,
    reset
  };
}
const makeVSnackbarProps = propsFactory({
  multiLine: Boolean,
  text: String,
  timer: [Boolean, String],
  timeout: {
    type: [Number, String],
    default: 5000
  },
  vertical: Boolean,
  ...makeLocationProps({
    location: 'bottom'
  }),
  ...makePositionProps(),
  ...makeRoundedProps(),
  ...makeVariantProps(),
  ...makeThemeProps(),
  ...omit(makeVOverlayProps({
    transition: 'v-snackbar-transition'
  }), ['persistent', 'noClickAnimation', 'scrim', 'scrollStrategy'])
}, 'VSnackbar');
const VSnackbar = genericComponent()({
  name: 'VSnackbar',
  props: makeVSnackbarProps(),
  emits: {
    'update:modelValue': v => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const isActive = useProxiedModel(props, 'modelValue');
    const {
      positionClasses
    } = usePosition(props);
    const {
      scopeId
    } = useScopeId();
    const {
      themeClasses
    } = provideTheme(props);
    const {
      colorClasses,
      colorStyles,
      variantClasses
    } = useVariant(props);
    const {
      roundedClasses
    } = useRounded(props);
    const countdown = useCountdown(() => Number(props.timeout));
    const overlay = ref$7();
    const timerRef = ref$7();
    const isHovering = shallowRef$4(false);
    const startY = shallowRef$4(0);
    const mainStyles = ref$7();
    const hasLayout = inject$2(VuetifyLayoutKey, undefined);
    useToggleScope(() => !!hasLayout, () => {
      const layout = useLayout();
      watchEffect$1(() => {
        mainStyles.value = layout.mainStyles.value;
      });
    });
    watch$4(isActive, startTimeout);
    watch$4(() => props.timeout, startTimeout);
    onMounted$1(() => {
      if (isActive.value) startTimeout();
    });
    let activeTimeout = -1;
    function startTimeout() {
      countdown.reset();
      window.clearTimeout(activeTimeout);
      const timeout = Number(props.timeout);
      if (!isActive.value || timeout === -1) return;
      const element = refElement(timerRef.value);
      countdown.start(element);
      activeTimeout = window.setTimeout(() => {
        isActive.value = false;
      }, timeout);
    }
    function clearTimeout() {
      countdown.reset();
      window.clearTimeout(activeTimeout);
    }
    function onPointerenter() {
      isHovering.value = true;
      clearTimeout();
    }
    function onPointerleave() {
      isHovering.value = false;
      startTimeout();
    }
    function onTouchstart(event) {
      startY.value = event.touches[0].clientY;
    }
    function onTouchend(event) {
      if (Math.abs(startY.value - event.changedTouches[0].clientY) > 50) {
        isActive.value = false;
      }
    }
    function onAfterLeave() {
      if (isHovering.value) onPointerleave();
    }
    const locationClasses = computed$f(() => {
      return props.location.split(' ').reduce((acc, loc) => {
        acc[`v-snackbar--${loc}`] = true;
        return acc;
      }, {});
    });
    useRender(() => {
      const overlayProps = VOverlay.filterProps(props);
      const hasContent = !!(slots.default || slots.text || props.text);
      return _createVNode$n(VOverlay, _mergeProps$d({
        "ref": overlay,
        "class": ['v-snackbar', {
          'v-snackbar--active': isActive.value,
          'v-snackbar--multi-line': props.multiLine && !props.vertical,
          'v-snackbar--timer': !!props.timer,
          'v-snackbar--vertical': props.vertical
        }, locationClasses.value, positionClasses.value, props.class],
        "style": [mainStyles.value, props.style]
      }, overlayProps, {
        "modelValue": isActive.value,
        "onUpdate:modelValue": $event => isActive.value = $event,
        "contentProps": mergeProps$2({
          class: ['v-snackbar__wrapper', themeClasses.value, colorClasses.value, roundedClasses.value, variantClasses.value],
          style: [colorStyles.value],
          onPointerenter,
          onPointerleave
        }, overlayProps.contentProps),
        "persistent": true,
        "noClickAnimation": true,
        "scrim": false,
        "scrollStrategy": "none",
        "_disableGlobalStack": true,
        "onTouchstartPassive": onTouchstart,
        "onTouchend": onTouchend,
        "onAfterLeave": onAfterLeave
      }, scopeId), {
        default: () => [genOverlays(false, 'v-snackbar'), props.timer && !isHovering.value && _createVNode$n("div", {
          "key": "timer",
          "class": "v-snackbar__timer"
        }, [_createVNode$n(VProgressLinear, {
          "ref": timerRef,
          "color": typeof props.timer === 'string' ? props.timer : 'info',
          "max": props.timeout,
          "model-value": countdown.time.value
        }, null)]), hasContent && _createVNode$n("div", {
          "key": "content",
          "class": "v-snackbar__content",
          "role": "status",
          "aria-live": "polite"
        }, [slots.text?.() ?? props.text, slots.default?.()]), slots.actions && _createVNode$n(VDefaultsProvider, {
          "defaults": {
            VBtn: {
              variant: 'text',
              ripple: false,
              slim: true
            }
          }
        }, {
          default: () => [_createVNode$n("div", {
            "class": "v-snackbar__actions"
          }, [slots.actions({
            isActive
          })])]
        })],
        activator: slots.activator
      });
    });
    return forwardRefs({}, overlay);
  }
});

const {Fragment:_Fragment$6,createVNode:_createVNode$m,mergeProps:_mergeProps$c} = await importShared('vue');
const {computed: computed$e,nextTick: nextTick$2,shallowRef: shallowRef$3,watch: watch$3} = await importShared('vue');
const makeVSnackbarQueueProps = propsFactory({
  // TODO: Port this to Snackbar on dev
  closable: [Boolean, String],
  closeText: {
    type: String,
    default: '$vuetify.dismiss'
  },
  modelValue: {
    type: Array,
    default: () => []
  },
  ...omit(makeVSnackbarProps(), ['modelValue'])
}, 'VSnackbarQueue');
const VSnackbarQueue = genericComponent()({
  name: 'VSnackbarQueue',
  props: makeVSnackbarQueueProps(),
  emits: {
    'update:modelValue': val => true
  },
  setup(props, _ref) {
    let {
      emit,
      slots
    } = _ref;
    const {
      t
    } = useLocale();
    const isActive = shallowRef$3(false);
    const isVisible = shallowRef$3(false);
    const current = shallowRef$3();
    watch$3(() => props.modelValue.length, (val, oldVal) => {
      if (!isVisible.value && val > oldVal) {
        showNext();
      }
    });
    watch$3(isActive, val => {
      if (val) isVisible.value = true;
    });
    function onAfterLeave() {
      if (props.modelValue.length) {
        showNext();
      } else {
        current.value = undefined;
        isVisible.value = false;
      }
    }
    function showNext() {
      const [next, ...rest] = props.modelValue;
      emit('update:modelValue', rest);
      current.value = typeof next === 'string' ? {
        text: next
      } : next;
      nextTick$2(() => {
        isActive.value = true;
      });
    }
    function onClickClose() {
      isActive.value = false;
    }
    const btnProps = computed$e(() => ({
      color: typeof props.closable === 'string' ? props.closable : undefined,
      text: t(props.closeText)
    }));
    useRender(() => {
      const hasActions = !!(props.closable || slots.actions);
      const {
        modelValue: _,
        ...snackbarProps
      } = VSnackbar.filterProps(props);
      return _createVNode$m(_Fragment$6, null, [isVisible.value && !!current.value && (slots.default ? _createVNode$m(VDefaultsProvider, {
        "defaults": {
          VSnackbar: current.value
        }
      }, {
        default: () => [slots.default({
          item: current.value
        })]
      }) : _createVNode$m(VSnackbar, _mergeProps$c(snackbarProps, current.value, {
        "modelValue": isActive.value,
        "onUpdate:modelValue": $event => isActive.value = $event,
        "onAfterLeave": onAfterLeave
      }), {
        text: slots.text ? () => slots.text?.({
          item: current.value
        }) : undefined,
        actions: hasActions ? () => _createVNode$m(_Fragment$6, null, [!slots.actions ? _createVNode$m(VBtn, _mergeProps$c(btnProps.value, {
          "onClick": onClickClose
        }), null) : _createVNode$m(VDefaultsProvider, {
          "defaults": {
            VBtn: btnProps.value
          }
        }, {
          default: () => [slots.actions({
            item: current.value,
            props: {
              onClick: onClickClose
            }
          })]
        })]) : undefined
      }))]);
    });
  }
});

// Utilities
const makeLineProps = propsFactory({
  autoDraw: Boolean,
  autoDrawDuration: [Number, String],
  autoDrawEasing: {
    type: String,
    default: 'ease'
  },
  color: String,
  gradient: {
    type: Array,
    default: () => []
  },
  gradientDirection: {
    type: String,
    validator: val => ['top', 'bottom', 'left', 'right'].includes(val),
    default: 'top'
  },
  height: {
    type: [String, Number],
    default: 75
  },
  labels: {
    type: Array,
    default: () => []
  },
  labelSize: {
    type: [Number, String],
    default: 7
  },
  lineWidth: {
    type: [String, Number],
    default: 4
  },
  id: String,
  itemValue: {
    type: String,
    default: 'value'
  },
  modelValue: {
    type: Array,
    default: () => []
  },
  min: [String, Number],
  max: [String, Number],
  padding: {
    type: [String, Number],
    default: 8
  },
  showLabels: Boolean,
  smooth: [Boolean, String, Number],
  width: {
    type: [Number, String],
    default: 300
  }
}, 'Line');

// Utilities
const {computed: computed$d,useId: useId$3,createVNode:_createVNode$l,Fragment:_Fragment$5} = await importShared('vue');
const makeVBarlineProps = propsFactory({
  autoLineWidth: Boolean,
  ...makeLineProps()
}, 'VBarline');
const VBarline = genericComponent()({
  name: 'VBarline',
  props: makeVBarlineProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const uid = useId$3();
    const id = computed$d(() => props.id || `barline-${uid}`);
    const autoDrawDuration = computed$d(() => Number(props.autoDrawDuration) || 500);
    const hasLabels = computed$d(() => {
      return Boolean(props.showLabels || props.labels.length > 0 || !!slots?.label);
    });
    const lineWidth = computed$d(() => parseFloat(props.lineWidth) || 4);
    const totalWidth = computed$d(() => Math.max(props.modelValue.length * lineWidth.value, Number(props.width)));
    const boundary = computed$d(() => {
      return {
        minX: 0,
        maxX: totalWidth.value,
        minY: 0,
        maxY: parseInt(props.height, 10)
      };
    });
    const items = computed$d(() => props.modelValue.map(item => getPropertyFromItem(item, props.itemValue, item)));
    function genBars(values, boundary) {
      const {
        minX,
        maxX,
        minY,
        maxY
      } = boundary;
      const totalValues = values.length;
      let maxValue = props.max != null ? Number(props.max) : Math.max(...values);
      let minValue = props.min != null ? Number(props.min) : Math.min(...values);
      if (minValue > 0 && props.min == null) minValue = 0;
      if (maxValue < 0 && props.max == null) maxValue = 0;
      const gridX = maxX / totalValues;
      const gridY = (maxY - minY) / (maxValue - minValue || 1);
      const horizonY = maxY - Math.abs(minValue * gridY);
      return values.map((value, index) => {
        const height = Math.abs(gridY * value);
        return {
          x: minX + index * gridX,
          y: horizonY - height + Number(value < 0) * height,
          height,
          value
        };
      });
    }
    const parsedLabels = computed$d(() => {
      const labels = [];
      const points = genBars(items.value, boundary.value);
      const len = points.length;
      for (let i = 0; labels.length < len; i++) {
        const item = points[i];
        let value = props.labels[i];
        if (!value) {
          value = typeof item === 'object' ? item.value : item;
        }
        labels.push({
          x: item.x,
          value: String(value)
        });
      }
      return labels;
    });
    const bars = computed$d(() => genBars(items.value, boundary.value));
    const offsetX = computed$d(() => (Math.abs(bars.value[0].x - bars.value[1].x) - lineWidth.value) / 2);
    const smooth = computed$d(() => typeof props.smooth === 'boolean' ? props.smooth ? 2 : 0 : Number(props.smooth));
    useRender(() => {
      const gradientData = !props.gradient.slice().length ? [''] : props.gradient.slice().reverse();
      return _createVNode$l("svg", {
        "display": "block"
      }, [_createVNode$l("defs", null, [_createVNode$l("linearGradient", {
        "id": id.value,
        "gradientUnits": "userSpaceOnUse",
        "x1": props.gradientDirection === 'left' ? '100%' : '0',
        "y1": props.gradientDirection === 'top' ? '100%' : '0',
        "x2": props.gradientDirection === 'right' ? '100%' : '0',
        "y2": props.gradientDirection === 'bottom' ? '100%' : '0'
      }, [gradientData.map((color, index) => _createVNode$l("stop", {
        "offset": index / Math.max(gradientData.length - 1, 1),
        "stop-color": color || 'currentColor'
      }, null))])]), _createVNode$l("clipPath", {
        "id": `${id.value}-clip`
      }, [bars.value.map(item => _createVNode$l("rect", {
        "x": item.x + offsetX.value,
        "y": item.y,
        "width": lineWidth.value,
        "height": item.height,
        "rx": smooth.value,
        "ry": smooth.value
      }, [props.autoDraw && _createVNode$l(_Fragment$5, null, [_createVNode$l("animate", {
        "attributeName": "y",
        "from": item.y + item.height,
        "to": item.y,
        "dur": `${autoDrawDuration.value}ms`,
        "fill": "freeze"
      }, null), _createVNode$l("animate", {
        "attributeName": "height",
        "from": "0",
        "to": item.height,
        "dur": `${autoDrawDuration.value}ms`,
        "fill": "freeze"
      }, null)])]))]), hasLabels.value && _createVNode$l("g", {
        "key": "labels",
        "style": {
          textAnchor: 'middle',
          dominantBaseline: 'mathematical',
          fill: 'currentColor'
        }
      }, [parsedLabels.value.map((item, i) => _createVNode$l("text", {
        "x": item.x + offsetX.value + lineWidth.value / 2,
        "y": parseInt(props.height, 10) - 2 + (parseInt(props.labelSize, 10) || 7 * 0.75),
        "font-size": Number(props.labelSize) || 7
      }, [slots.label?.({
        index: i,
        value: item.value
      }) ?? item.value]))]), _createVNode$l("g", {
        "clip-path": `url(#${id.value}-clip)`,
        "fill": `url(#${id.value})`
      }, [_createVNode$l("rect", {
        "x": 0,
        "y": 0,
        "width": Math.max(props.modelValue.length * lineWidth.value, Number(props.width)),
        "height": props.height
      }, null)])]);
    });
  }
});

// @ts-nocheck
/* eslint-disable */

// import { checkCollinear, getDistance, moveTo } from './math'

/**
 * From https://github.com/unsplash/react-trend/blob/master/src/helpers/DOM.helpers.js#L18
 */
function genPath(points, radius) {
  let fill = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;
  let height = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : 75;
  if (points.length === 0) return '';
  const start = points.shift();
  const end = points[points.length - 1];
  return (fill ? `M${start.x} ${height - start.x + 2} L${start.x} ${start.y}` : `M${start.x} ${start.y}`) + points.map((point, index) => {
    const next = points[index + 1];
    const prev = points[index - 1] || start;
    const isCollinear = next && checkCollinear(next, point, prev);
    if (!next || isCollinear) {
      return `L${point.x} ${point.y}`;
    }
    const threshold = Math.min(getDistance(prev, point), getDistance(next, point));
    const isTooCloseForRadius = threshold / 2 < radius;
    const radiusForPoint = isTooCloseForRadius ? threshold / 2 : radius;
    const before = moveTo(prev, point, radiusForPoint);
    const after = moveTo(next, point, radiusForPoint);
    return `L${before.x} ${before.y}S${point.x} ${point.y} ${after.x} ${after.y}`;
  }).join('') + (fill ? `L${end.x} ${height - start.x + 2} Z` : '');
}
function int(value) {
  return parseInt(value, 10);
}

/**
 * https://en.wikipedia.org/wiki/Collinearity
 * x=(x1+x2)/2
 * y=(y1+y2)/2
 */
function checkCollinear(p0, p1, p2) {
  return int(p0.x + p2.x) === int(2 * p1.x) && int(p0.y + p2.y) === int(2 * p1.y);
}
function getDistance(p1, p2) {
  return Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
}
function moveTo(to, from, radius) {
  const vector = {
    x: to.x - from.x,
    y: to.y - from.y
  };
  const length = Math.sqrt(vector.x * vector.x + vector.y * vector.y);
  const unitVector = {
    x: vector.x / length,
    y: vector.y / length
  };
  return {
    x: from.x + unitVector.x * radius,
    y: from.y + unitVector.y * radius
  };
}

// Utilities
const {computed: computed$c,nextTick: nextTick$1,ref: ref$6,useId: useId$2,watch: watch$2,createVNode:_createVNode$k} = await importShared('vue');
const makeVTrendlineProps = propsFactory({
  fill: Boolean,
  ...makeLineProps()
}, 'VTrendline');
const VTrendline = genericComponent()({
  name: 'VTrendline',
  props: makeVTrendlineProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const uid = useId$2();
    const id = computed$c(() => props.id || `trendline-${uid}`);
    const autoDrawDuration = computed$c(() => Number(props.autoDrawDuration) || (props.fill ? 500 : 2000));
    const lastLength = ref$6(0);
    const path = ref$6(null);
    function genPoints(values, boundary) {
      const {
        minX,
        maxX,
        minY,
        maxY
      } = boundary;
      const totalValues = values.length;
      const maxValue = props.max != null ? Number(props.max) : Math.max(...values);
      const minValue = props.min != null ? Number(props.min) : Math.min(...values);
      const gridX = (maxX - minX) / (totalValues - 1);
      const gridY = (maxY - minY) / (maxValue - minValue || 1);
      return values.map((value, index) => {
        return {
          x: minX + index * gridX,
          y: maxY - (value - minValue) * gridY,
          value
        };
      });
    }
    const hasLabels = computed$c(() => {
      return Boolean(props.showLabels || props.labels.length > 0 || !!slots?.label);
    });
    const lineWidth = computed$c(() => {
      return parseFloat(props.lineWidth) || 4;
    });
    const totalWidth = computed$c(() => Number(props.width));
    const boundary = computed$c(() => {
      const padding = Number(props.padding);
      return {
        minX: padding,
        maxX: totalWidth.value - padding,
        minY: padding,
        maxY: parseInt(props.height, 10) - padding
      };
    });
    const items = computed$c(() => props.modelValue.map(item => getPropertyFromItem(item, props.itemValue, item)));
    const parsedLabels = computed$c(() => {
      const labels = [];
      const points = genPoints(items.value, boundary.value);
      const len = points.length;
      for (let i = 0; labels.length < len; i++) {
        const item = points[i];
        let value = props.labels[i];
        if (!value) {
          value = typeof item === 'object' ? item.value : item;
        }
        labels.push({
          x: item.x,
          value: String(value)
        });
      }
      return labels;
    });
    watch$2(() => props.modelValue, async () => {
      await nextTick$1();
      if (!props.autoDraw || !path.value) return;
      const pathRef = path.value;
      const length = pathRef.getTotalLength();
      if (!props.fill) {
        // Initial setup to "hide" the line by using the stroke dash array
        pathRef.style.strokeDasharray = `${length}`;
        pathRef.style.strokeDashoffset = `${length}`;

        // Force reflow to ensure the transition starts from this state
        pathRef.getBoundingClientRect();

        // Animate the stroke dash offset to "draw" the line
        pathRef.style.transition = `stroke-dashoffset ${autoDrawDuration.value}ms ${props.autoDrawEasing}`;
        pathRef.style.strokeDashoffset = '0';
      } else {
        // Your existing logic for filled paths remains the same
        pathRef.style.transformOrigin = 'bottom center';
        pathRef.style.transition = 'none';
        pathRef.style.transform = `scaleY(0)`;
        pathRef.getBoundingClientRect();
        pathRef.style.transition = `transform ${autoDrawDuration.value}ms ${props.autoDrawEasing}`;
        pathRef.style.transform = `scaleY(1)`;
      }
      lastLength.value = length;
    }, {
      immediate: true
    });
    function genPath$1(fill) {
      const smoothValue = typeof props.smooth === 'boolean' ? props.smooth ? 8 : 0 : Number(props.smooth);
      return genPath(genPoints(items.value, boundary.value), smoothValue, fill, parseInt(props.height, 10));
    }
    useRender(() => {
      const gradientData = !props.gradient.slice().length ? [''] : props.gradient.slice().reverse();
      return _createVNode$k("svg", {
        "display": "block",
        "stroke-width": parseFloat(props.lineWidth) ?? 4
      }, [_createVNode$k("defs", null, [_createVNode$k("linearGradient", {
        "id": id.value,
        "gradientUnits": "userSpaceOnUse",
        "x1": props.gradientDirection === 'left' ? '100%' : '0',
        "y1": props.gradientDirection === 'top' ? '100%' : '0',
        "x2": props.gradientDirection === 'right' ? '100%' : '0',
        "y2": props.gradientDirection === 'bottom' ? '100%' : '0'
      }, [gradientData.map((color, index) => _createVNode$k("stop", {
        "offset": index / Math.max(gradientData.length - 1, 1),
        "stop-color": color || 'currentColor'
      }, null))])]), hasLabels.value && _createVNode$k("g", {
        "key": "labels",
        "style": {
          textAnchor: 'middle',
          dominantBaseline: 'mathematical',
          fill: 'currentColor'
        }
      }, [parsedLabels.value.map((item, i) => _createVNode$k("text", {
        "x": item.x + lineWidth.value / 2 + lineWidth.value / 2,
        "y": parseInt(props.height, 10) - 4 + (parseInt(props.labelSize, 10) || 7 * 0.75),
        "font-size": Number(props.labelSize) || 7
      }, [slots.label?.({
        index: i,
        value: item.value
      }) ?? item.value]))]), _createVNode$k("path", {
        "ref": path,
        "d": genPath$1(props.fill),
        "fill": props.fill ? `url(#${id.value})` : 'none',
        "stroke": props.fill ? 'none' : `url(#${id.value})`
      }, null), props.fill && _createVNode$k("path", {
        "d": genPath$1(false),
        "fill": "none",
        "stroke": props.color ?? props.gradient?.[0]
      }, null)]);
    });
  }
});

const {mergeProps:_mergeProps$b,createVNode:_createVNode$j} = await importShared('vue');
const {computed: computed$b} = await importShared('vue');
// Types

const makeVSparklineProps = propsFactory({
  type: {
    type: String,
    default: 'trend'
  },
  ...makeVBarlineProps(),
  ...makeVTrendlineProps()
}, 'VSparkline');
const VSparkline = genericComponent()({
  name: 'VSparkline',
  props: makeVSparklineProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      textColorClasses,
      textColorStyles
    } = useTextColor(() => props.color);
    const hasLabels = computed$b(() => {
      return Boolean(props.showLabels || props.labels.length > 0 || !!slots?.label);
    });
    const totalHeight = computed$b(() => {
      let height = parseInt(props.height, 10);
      if (hasLabels.value) height += parseInt(props.labelSize, 10) * 1.5;
      return height;
    });
    useRender(() => {
      const Tag = props.type === 'trend' ? VTrendline : VBarline;
      const lineProps = props.type === 'trend' ? VTrendline.filterProps(props) : VBarline.filterProps(props);
      return _createVNode$j(Tag, _mergeProps$b({
        "key": props.type,
        "class": textColorClasses.value,
        "style": textColorStyles.value,
        "viewBox": `0 0 ${props.width} ${parseInt(totalHeight.value, 10)}`
      }, lineProps), slots);
    });
  }
});

const {createVNode:_createVNode$i,mergeProps:_mergeProps$a} = await importShared('vue');
const {computed: computed$a,ref: ref$5} = await importShared('vue');
const makeVSpeedDialProps = propsFactory({
  ...makeComponentProps(),
  ...makeVMenuProps({
    offset: 8,
    minWidth: 0,
    openDelay: 0,
    closeDelay: 100,
    location: 'top center',
    transition: 'scale-transition'
  })
}, 'VSpeedDial');
const VSpeedDial = genericComponent()({
  name: 'VSpeedDial',
  props: makeVSpeedDialProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const model = useProxiedModel(props, 'modelValue');
    const menuRef = ref$5();
    const location = computed$a(() => {
      const [y, x = 'center'] = props.location?.split(' ') ?? [];
      return `${y} ${x}`;
    });
    const locationClasses = computed$a(() => ({
      [`v-speed-dial__content--${location.value.replace(' ', '-')}`]: true
    }));
    useRender(() => {
      const menuProps = VMenu.filterProps(props);
      return _createVNode$i(VMenu, _mergeProps$a(menuProps, {
        "modelValue": model.value,
        "onUpdate:modelValue": $event => model.value = $event,
        "class": props.class,
        "style": props.style,
        "contentClass": ['v-speed-dial__content', locationClasses.value, props.contentClass],
        "location": location.value,
        "ref": menuRef,
        "transition": "fade-transition"
      }), {
        ...slots,
        default: slotProps => _createVNode$i(VDefaultsProvider, {
          "defaults": {
            VBtn: {
              size: 'small'
            }
          }
        }, {
          default: () => [_createVNode$i(MaybeTransition, {
            "appear": true,
            "group": true,
            "transition": props.transition
          }, {
            default: () => [slots.default?.(slotProps)]
          })]
        })
      });
    });
    return {};
  }
});

// Types

const VStepperSymbol = Symbol.for('vuetify:v-stepper');

const {createVNode:_createVNode$h} = await importShared('vue');
const makeVStepperActionsProps = propsFactory({
  color: String,
  disabled: {
    type: [Boolean, String],
    default: false
  },
  prevText: {
    type: String,
    default: '$vuetify.stepper.prev'
  },
  nextText: {
    type: String,
    default: '$vuetify.stepper.next'
  }
}, 'VStepperActions');
const VStepperActions = genericComponent()({
  name: 'VStepperActions',
  props: makeVStepperActionsProps(),
  emits: {
    'click:prev': () => true,
    'click:next': () => true
  },
  setup(props, _ref) {
    let {
      emit,
      slots
    } = _ref;
    const {
      t
    } = useLocale();
    function onClickPrev() {
      emit('click:prev');
    }
    function onClickNext() {
      emit('click:next');
    }
    useRender(() => {
      const prevSlotProps = {
        onClick: onClickPrev
      };
      const nextSlotProps = {
        onClick: onClickNext
      };
      return _createVNode$h("div", {
        "class": "v-stepper-actions"
      }, [_createVNode$h(VDefaultsProvider, {
        "defaults": {
          VBtn: {
            disabled: ['prev', true].includes(props.disabled),
            text: t(props.prevText),
            variant: 'text'
          }
        }
      }, {
        default: () => [slots.prev?.({
          props: prevSlotProps
        }) ?? _createVNode$h(VBtn, prevSlotProps, null)]
      }), _createVNode$h(VDefaultsProvider, {
        "defaults": {
          VBtn: {
            color: props.color,
            disabled: ['next', true].includes(props.disabled),
            text: t(props.nextText),
            variant: 'tonal'
          }
        }
      }, {
        default: () => [slots.next?.({
          props: nextSlotProps
        }) ?? _createVNode$h(VBtn, nextSlotProps, null)]
      })]);
    });
    return {};
  }
});

// Utilities
const VStepperHeader = createSimpleFunctional('v-stepper-header');

const {createVNode:_createVNode$g,resolveDirective:_resolveDirective$1,withDirectives:_withDirectives$1} = await importShared('vue');
const {computed: computed$9} = await importShared('vue');
const makeStepperItemProps = propsFactory({
  color: String,
  title: String,
  subtitle: String,
  complete: Boolean,
  completeIcon: {
    type: IconValue,
    default: '$complete'
  },
  editable: Boolean,
  editIcon: {
    type: IconValue,
    default: '$edit'
  },
  error: Boolean,
  errorIcon: {
    type: IconValue,
    default: '$error'
  },
  icon: IconValue,
  ripple: {
    type: [Boolean, Object],
    default: true
  },
  rules: {
    type: Array,
    default: () => []
  }
}, 'StepperItem');
const makeVStepperItemProps = propsFactory({
  ...makeStepperItemProps(),
  ...makeGroupItemProps()
}, 'VStepperItem');
const VStepperItem = genericComponent()({
  name: 'VStepperItem',
  directives: {
    Ripple
  },
  props: makeVStepperItemProps(),
  emits: {
    'group:selected': val => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const group = useGroupItem(props, VStepperSymbol, true);
    const step = computed$9(() => group?.value.value ?? props.value);
    const isValid = computed$9(() => props.rules.every(handler => handler() === true));
    const isClickable = computed$9(() => !props.disabled && props.editable);
    const canEdit = computed$9(() => !props.disabled && props.editable);
    const hasError = computed$9(() => props.error || !isValid.value);
    const hasCompleted = computed$9(() => props.complete || props.rules.length > 0 && isValid.value);
    const icon = computed$9(() => {
      if (hasError.value) return props.errorIcon;
      if (hasCompleted.value) return props.completeIcon;
      if (group.isSelected.value && props.editable) return props.editIcon;
      return props.icon;
    });
    const slotProps = computed$9(() => ({
      canEdit: canEdit.value,
      hasError: hasError.value,
      hasCompleted: hasCompleted.value,
      title: props.title,
      subtitle: props.subtitle,
      step: step.value,
      value: props.value
    }));
    useRender(() => {
      const hasColor = (!group || group.isSelected.value || hasCompleted.value || canEdit.value) && !hasError.value && !props.disabled;
      const hasTitle = !!(props.title != null || slots.title);
      const hasSubtitle = !!(props.subtitle != null || slots.subtitle);
      function onClick() {
        group?.toggle();
      }
      return _withDirectives$1(_createVNode$g("button", {
        "class": ['v-stepper-item', {
          'v-stepper-item--complete': hasCompleted.value,
          'v-stepper-item--disabled': props.disabled,
          'v-stepper-item--error': hasError.value
        }, group?.selectedClass.value],
        "disabled": !props.editable,
        "type": "button",
        "onClick": onClick
      }, [isClickable.value && genOverlays(true, 'v-stepper-item'), _createVNode$g(VAvatar, {
        "key": "stepper-avatar",
        "class": "v-stepper-item__avatar",
        "color": hasColor ? props.color : undefined,
        "size": 24
      }, {
        default: () => [slots.icon?.(slotProps.value) ?? (icon.value ? _createVNode$g(VIcon, {
          "icon": icon.value
        }, null) : step.value)]
      }), _createVNode$g("div", {
        "class": "v-stepper-item__content"
      }, [hasTitle && _createVNode$g("div", {
        "key": "title",
        "class": "v-stepper-item__title"
      }, [slots.title?.(slotProps.value) ?? props.title]), hasSubtitle && _createVNode$g("div", {
        "key": "subtitle",
        "class": "v-stepper-item__subtitle"
      }, [slots.subtitle?.(slotProps.value) ?? props.subtitle]), slots.default?.(slotProps.value)])]), [[_resolveDirective$1("ripple"), props.ripple && props.editable, null]]);
    });
    return {};
  }
});

const {mergeProps:_mergeProps$9,createVNode:_createVNode$f} = await importShared('vue');
const {computed: computed$8,inject: inject$1} = await importShared('vue');
const makeVStepperWindowProps = propsFactory({
  ...omit(makeVWindowProps(), ['continuous', 'nextIcon', 'prevIcon', 'showArrows', 'touch', 'mandatory'])
}, 'VStepperWindow');
const VStepperWindow = genericComponent()({
  name: 'VStepperWindow',
  props: makeVStepperWindowProps(),
  emits: {
    'update:modelValue': v => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const group = inject$1(VStepperSymbol, null);
    const _model = useProxiedModel(props, 'modelValue');
    const model = computed$8({
      get() {
        // Always return modelValue if defined
        // or if not within a VStepper group
        if (_model.value != null || !group) return _model.value;

        // If inside of a VStepper, find the currently selected
        // item by id. Item value may be assigned by its index
        return group.items.value.find(item => group.selected.value.includes(item.id))?.value;
      },
      set(val) {
        _model.value = val;
      }
    });
    useRender(() => {
      const windowProps = VWindow.filterProps(props);
      return _createVNode$f(VWindow, _mergeProps$9({
        "_as": "VStepperWindow"
      }, windowProps, {
        "modelValue": model.value,
        "onUpdate:modelValue": $event => model.value = $event,
        "class": ['v-stepper-window', props.class],
        "style": props.style,
        "mandatory": false,
        "touch": false
      }), slots);
    });
    return {};
  }
});

const {mergeProps:_mergeProps$8,createVNode:_createVNode$e} = await importShared('vue');
const makeVStepperWindowItemProps = propsFactory({
  ...makeVWindowItemProps()
}, 'VStepperWindowItem');
const VStepperWindowItem = genericComponent()({
  name: 'VStepperWindowItem',
  props: makeVStepperWindowItemProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    useRender(() => {
      const windowItemProps = VWindowItem.filterProps(props);
      return _createVNode$e(VWindowItem, _mergeProps$8({
        "_as": "VStepperWindowItem"
      }, windowItemProps, {
        "class": ['v-stepper-window-item', props.class],
        "style": props.style
      }), slots);
    });
    return {};
  }
});

const {Fragment:_Fragment$4,createVNode:_createVNode$d,mergeProps:_mergeProps$7} = await importShared('vue');
const {computed: computed$7,toRefs} = await importShared('vue');
const makeStepperProps = propsFactory({
  altLabels: Boolean,
  bgColor: String,
  completeIcon: IconValue,
  editIcon: IconValue,
  editable: Boolean,
  errorIcon: IconValue,
  hideActions: Boolean,
  items: {
    type: Array,
    default: () => []
  },
  itemTitle: {
    type: String,
    default: 'title'
  },
  itemValue: {
    type: String,
    default: 'value'
  },
  nonLinear: Boolean,
  flat: Boolean,
  ...makeDisplayProps()
}, 'Stepper');
const makeVStepperProps = propsFactory({
  ...makeStepperProps(),
  ...makeGroupProps({
    mandatory: 'force',
    selectedClass: 'v-stepper-item--selected'
  }),
  ...makeVSheetProps(),
  ...pick(makeVStepperActionsProps(), ['prevText', 'nextText'])
}, 'VStepper');
const VStepper = genericComponent()({
  name: 'VStepper',
  props: makeVStepperProps(),
  emits: {
    'update:modelValue': v => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      items: _items,
      next,
      prev,
      selected
    } = useGroup(props, VStepperSymbol);
    const {
      displayClasses,
      mobile
    } = useDisplay(props);
    const {
      completeIcon,
      editIcon,
      errorIcon,
      color,
      editable,
      prevText,
      nextText
    } = toRefs(props);
    const items = computed$7(() => props.items.map((item, index) => {
      const title = getPropertyFromItem(item, props.itemTitle, item);
      const value = getPropertyFromItem(item, props.itemValue, index + 1);
      return {
        title,
        value,
        raw: item
      };
    }));
    const activeIndex = computed$7(() => {
      return _items.value.findIndex(item => selected.value.includes(item.id));
    });
    const disabled = computed$7(() => {
      if (props.disabled) return props.disabled;
      if (activeIndex.value === 0) return 'prev';
      if (activeIndex.value === _items.value.length - 1) return 'next';
      return false;
    });
    provideDefaults({
      VStepperItem: {
        editable,
        errorIcon,
        completeIcon,
        editIcon,
        prevText,
        nextText
      },
      VStepperActions: {
        color,
        disabled,
        prevText,
        nextText
      }
    });
    useRender(() => {
      const sheetProps = VSheet.filterProps(props);
      const hasHeader = !!(slots.header || props.items.length);
      const hasWindow = props.items.length > 0;
      const hasActions = !props.hideActions && !!(hasWindow || slots.actions);
      return _createVNode$d(VSheet, _mergeProps$7(sheetProps, {
        "color": props.bgColor,
        "class": ['v-stepper', {
          'v-stepper--alt-labels': props.altLabels,
          'v-stepper--flat': props.flat,
          'v-stepper--non-linear': props.nonLinear,
          'v-stepper--mobile': mobile.value
        }, displayClasses.value, props.class],
        "style": props.style
      }), {
        default: () => [hasHeader && _createVNode$d(VStepperHeader, {
          "key": "stepper-header"
        }, {
          default: () => [items.value.map((_ref2, index) => {
            let {
              raw,
              ...item
            } = _ref2;
            return _createVNode$d(_Fragment$4, null, [!!index && _createVNode$d(VDivider, null, null), _createVNode$d(VStepperItem, item, {
              default: slots[`header-item.${item.value}`] ?? slots.header,
              icon: slots.icon,
              title: slots.title,
              subtitle: slots.subtitle
            })]);
          })]
        }), hasWindow && _createVNode$d(VStepperWindow, {
          "key": "stepper-window"
        }, {
          default: () => [items.value.map(item => _createVNode$d(VStepperWindowItem, {
            "value": item.value
          }, {
            default: () => slots[`item.${item.value}`]?.(item) ?? slots.item?.(item)
          }))]
        }), slots.default?.({
          prev,
          next
        }), hasActions && (slots.actions?.({
          next,
          prev
        }) ?? _createVNode$d(VStepperActions, {
          "key": "stepper-actions",
          "onClick:prev": prev,
          "onClick:next": next
        }, slots))]
      });
    });
    return {
      prev,
      next
    };
  }
});

const {createVNode:_createVNode$c,Fragment:_Fragment$3,mergeProps:_mergeProps$6} = await importShared('vue');
const {ref: ref$4,toRef: toRef$5,useId: useId$1} = await importShared('vue');
const makeVSwitchProps = propsFactory({
  indeterminate: Boolean,
  inset: Boolean,
  flat: Boolean,
  loading: {
    type: [Boolean, String],
    default: false
  },
  ...makeVInputProps(),
  ...makeVSelectionControlProps()
}, 'VSwitch');
const VSwitch = genericComponent()({
  name: 'VSwitch',
  inheritAttrs: false,
  props: makeVSwitchProps(),
  emits: {
    'update:focused': focused => true,
    'update:modelValue': value => true,
    'update:indeterminate': value => true
  },
  setup(props, _ref) {
    let {
      attrs,
      slots
    } = _ref;
    const indeterminate = useProxiedModel(props, 'indeterminate');
    const model = useProxiedModel(props, 'modelValue');
    const {
      loaderClasses
    } = useLoader(props);
    const {
      isFocused,
      focus,
      blur
    } = useFocus(props);
    const control = ref$4();
    const isForcedColorsModeActive = IN_BROWSER && window.matchMedia('(forced-colors: active)').matches;
    const loaderColor = toRef$5(() => {
      return typeof props.loading === 'string' && props.loading !== '' ? props.loading : props.color;
    });
    const uid = useId$1();
    const id = toRef$5(() => props.id || `switch-${uid}`);
    function onChange() {
      if (indeterminate.value) {
        indeterminate.value = false;
      }
    }
    function onTrackClick(e) {
      e.stopPropagation();
      e.preventDefault();
      control.value?.input?.click();
    }
    useRender(() => {
      const [rootAttrs, controlAttrs] = filterInputAttrs(attrs);
      const inputProps = VInput.filterProps(props);
      const controlProps = VSelectionControl.filterProps(props);
      return _createVNode$c(VInput, _mergeProps$6({
        "class": ['v-switch', {
          'v-switch--flat': props.flat
        }, {
          'v-switch--inset': props.inset
        }, {
          'v-switch--indeterminate': indeterminate.value
        }, loaderClasses.value, props.class]
      }, rootAttrs, inputProps, {
        "modelValue": model.value,
        "onUpdate:modelValue": $event => model.value = $event,
        "id": id.value,
        "focused": isFocused.value,
        "style": props.style
      }), {
        ...slots,
        default: _ref2 => {
          let {
            id,
            messagesId,
            isDisabled,
            isReadonly,
            isValid
          } = _ref2;
          const slotProps = {
            model,
            isValid
          };
          return _createVNode$c(VSelectionControl, _mergeProps$6({
            "ref": control
          }, controlProps, {
            "modelValue": model.value,
            "onUpdate:modelValue": [$event => model.value = $event, onChange],
            "id": id.value,
            "aria-describedby": messagesId.value,
            "type": "checkbox",
            "aria-checked": indeterminate.value ? 'mixed' : undefined,
            "disabled": isDisabled.value,
            "readonly": isReadonly.value,
            "onFocus": focus,
            "onBlur": blur
          }, controlAttrs), {
            ...slots,
            default: _ref3 => {
              let {
                backgroundColorClasses,
                backgroundColorStyles
              } = _ref3;
              return _createVNode$c("div", {
                "class": ['v-switch__track', !isForcedColorsModeActive ? backgroundColorClasses.value : undefined],
                "style": backgroundColorStyles.value,
                "onClick": onTrackClick
              }, [slots['track-true'] && _createVNode$c("div", {
                "key": "prepend",
                "class": "v-switch__track-true"
              }, [slots['track-true'](slotProps)]), slots['track-false'] && _createVNode$c("div", {
                "key": "append",
                "class": "v-switch__track-false"
              }, [slots['track-false'](slotProps)])]);
            },
            input: _ref4 => {
              let {
                inputNode,
                icon,
                backgroundColorClasses,
                backgroundColorStyles
              } = _ref4;
              return _createVNode$c(_Fragment$3, null, [inputNode, _createVNode$c("div", {
                "class": ['v-switch__thumb', {
                  'v-switch__thumb--filled': icon || props.loading
                }, props.inset || isForcedColorsModeActive ? undefined : backgroundColorClasses.value],
                "style": props.inset ? undefined : backgroundColorStyles.value
              }, [slots.thumb ? _createVNode$c(VDefaultsProvider, {
                "defaults": {
                  VIcon: {
                    icon,
                    size: 'x-small'
                  }
                }
              }, {
                default: () => [slots.thumb({
                  ...slotProps,
                  icon
                })]
              }) : _createVNode$c(VScaleTransition, null, {
                default: () => [!props.loading ? icon && _createVNode$c(VIcon, {
                  "key": String(icon),
                  "icon": icon,
                  "size": "x-small"
                }, null) : _createVNode$c(LoaderSlot, {
                  "name": "v-switch",
                  "active": true,
                  "color": isValid.value === false ? undefined : loaderColor.value
                }, {
                  default: slotProps => slots.loader ? slots.loader(slotProps) : _createVNode$c(VProgressCircular, {
                    "active": slotProps.isActive,
                    "color": slotProps.color,
                    "indeterminate": true,
                    "size": "16",
                    "width": "2"
                  }, null)
                })]
              })])]);
            }
          });
        }
      });
    });
    return {};
  }
});

const {createVNode:_createVNode$b} = await importShared('vue');
const {computed: computed$6,shallowRef: shallowRef$2,toRef: toRef$4} = await importShared('vue');
const makeVSystemBarProps = propsFactory({
  color: String,
  height: [Number, String],
  window: Boolean,
  ...makeComponentProps(),
  ...makeElevationProps(),
  ...makeLayoutItemProps(),
  ...makeRoundedProps(),
  ...makeTagProps(),
  ...makeThemeProps()
}, 'VSystemBar');
const VSystemBar = genericComponent()({
  name: 'VSystemBar',
  props: makeVSystemBarProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      themeClasses
    } = provideTheme(props);
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.color);
    const {
      elevationClasses
    } = useElevation(props);
    const {
      roundedClasses
    } = useRounded(props);
    const {
      ssrBootStyles
    } = useSsrBoot();
    const height = computed$6(() => props.height ?? (props.window ? 32 : 24));
    const {
      layoutItemStyles
    } = useLayoutItem({
      id: props.name,
      order: computed$6(() => parseInt(props.order, 10)),
      position: shallowRef$2('top'),
      layoutSize: height,
      elementSize: height,
      active: computed$6(() => true),
      absolute: toRef$4(() => props.absolute)
    });
    useRender(() => _createVNode$b(props.tag, {
      "class": ['v-system-bar', {
        'v-system-bar--window': props.window
      }, themeClasses.value, backgroundColorClasses.value, elevationClasses.value, roundedClasses.value, props.class],
      "style": [backgroundColorStyles.value, layoutItemStyles.value, ssrBootStyles.value, props.style]
    }, slots));
    return {};
  }
});

// Types

const VTabsSymbol = Symbol.for('vuetify:v-tabs');

const {Fragment:_Fragment$2,createVNode:_createVNode$a,mergeProps:_mergeProps$5} = await importShared('vue');
const {computed: computed$5,ref: ref$3} = await importShared('vue');
const makeVTabProps = propsFactory({
  fixed: Boolean,
  sliderColor: String,
  hideSlider: Boolean,
  direction: {
    type: String,
    default: 'horizontal'
  },
  ...omit(makeVBtnProps({
    selectedClass: 'v-tab--selected',
    variant: 'text'
  }), ['active', 'block', 'flat', 'location', 'position', 'symbol'])
}, 'VTab');
const VTab = genericComponent()({
  name: 'VTab',
  props: makeVTabProps(),
  setup(props, _ref) {
    let {
      slots,
      attrs
    } = _ref;
    const {
      textColorClasses: sliderColorClasses,
      textColorStyles: sliderColorStyles
    } = useTextColor(() => props.sliderColor);
    const rootEl = ref$3();
    const sliderEl = ref$3();
    const isHorizontal = computed$5(() => props.direction === 'horizontal');
    const isSelected = computed$5(() => rootEl.value?.group?.isSelected.value ?? false);
    function updateSlider(_ref2) {
      let {
        value
      } = _ref2;
      if (value) {
        const prevEl = rootEl.value?.$el.parentElement?.querySelector('.v-tab--selected .v-tab__slider');
        const nextEl = sliderEl.value;
        if (!prevEl || !nextEl) return;
        const color = getComputedStyle(prevEl).color;
        const prevBox = prevEl.getBoundingClientRect();
        const nextBox = nextEl.getBoundingClientRect();
        const xy = isHorizontal.value ? 'x' : 'y';
        const XY = isHorizontal.value ? 'X' : 'Y';
        const rightBottom = isHorizontal.value ? 'right' : 'bottom';
        const widthHeight = isHorizontal.value ? 'width' : 'height';
        const prevPos = prevBox[xy];
        const nextPos = nextBox[xy];
        const delta = prevPos > nextPos ? prevBox[rightBottom] - nextBox[rightBottom] : prevBox[xy] - nextBox[xy];
        const origin = Math.sign(delta) > 0 ? isHorizontal.value ? 'right' : 'bottom' : Math.sign(delta) < 0 ? isHorizontal.value ? 'left' : 'top' : 'center';
        const size = Math.abs(delta) + (Math.sign(delta) < 0 ? prevBox[widthHeight] : nextBox[widthHeight]);
        const scale = size / Math.max(prevBox[widthHeight], nextBox[widthHeight]) || 0;
        const initialScale = prevBox[widthHeight] / nextBox[widthHeight] || 0;
        const sigma = 1.5;
        animate(nextEl, {
          backgroundColor: [color, 'currentcolor'],
          transform: [`translate${XY}(${delta}px) scale${XY}(${initialScale})`, `translate${XY}(${delta / sigma}px) scale${XY}(${(scale - 1) / sigma + 1})`, 'none'],
          transformOrigin: Array(3).fill(origin)
        }, {
          duration: 225,
          easing: standardEasing
        });
      }
    }
    useRender(() => {
      const btnProps = VBtn.filterProps(props);
      return _createVNode$a(VBtn, _mergeProps$5({
        "symbol": VTabsSymbol,
        "ref": rootEl,
        "class": ['v-tab', props.class],
        "style": props.style,
        "tabindex": isSelected.value ? 0 : -1,
        "role": "tab",
        "aria-selected": String(isSelected.value),
        "active": false
      }, btnProps, attrs, {
        "block": props.fixed,
        "maxWidth": props.fixed ? 300 : undefined,
        "onGroup:selected": updateSlider
      }), {
        ...slots,
        default: () => _createVNode$a(_Fragment$2, null, [slots.default?.() ?? props.text, !props.hideSlider && _createVNode$a("div", {
          "ref": sliderEl,
          "class": ['v-tab__slider', sliderColorClasses.value],
          "style": sliderColorStyles.value
        }, null)])
      });
    });
    return forwardRefs({}, rootEl);
  }
});

const {mergeProps:_mergeProps$4,createVNode:_createVNode$9} = await importShared('vue');
const {computed: computed$4,inject} = await importShared('vue');
const makeVTabsWindowProps = propsFactory({
  ...omit(makeVWindowProps(), ['continuous', 'nextIcon', 'prevIcon', 'showArrows', 'touch', 'mandatory'])
}, 'VTabsWindow');
const VTabsWindow = genericComponent()({
  name: 'VTabsWindow',
  props: makeVTabsWindowProps(),
  emits: {
    'update:modelValue': v => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const group = inject(VTabsSymbol, null);
    const _model = useProxiedModel(props, 'modelValue');
    const model = computed$4({
      get() {
        // Always return modelValue if defined
        // or if not within a VTabs group
        if (_model.value != null || !group) return _model.value;

        // If inside of a VTabs, find the currently selected
        // item by id. Item value may be assigned by its index
        return group.items.value.find(item => group.selected.value.includes(item.id))?.value;
      },
      set(val) {
        _model.value = val;
      }
    });
    useRender(() => {
      const windowProps = VWindow.filterProps(props);
      return _createVNode$9(VWindow, _mergeProps$4({
        "_as": "VTabsWindow"
      }, windowProps, {
        "modelValue": model.value,
        "onUpdate:modelValue": $event => model.value = $event,
        "class": ['v-tabs-window', props.class],
        "style": props.style,
        "mandatory": false,
        "touch": false
      }), slots);
    });
    return {};
  }
});

const {mergeProps:_mergeProps$3,createVNode:_createVNode$8} = await importShared('vue');
const makeVTabsWindowItemProps = propsFactory({
  ...makeVWindowItemProps()
}, 'VTabsWindowItem');
const VTabsWindowItem = genericComponent()({
  name: 'VTabsWindowItem',
  props: makeVTabsWindowItemProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    useRender(() => {
      const windowItemProps = VWindowItem.filterProps(props);
      return _createVNode$8(VWindowItem, _mergeProps$3({
        "_as": "VTabsWindowItem"
      }, windowItemProps, {
        "class": ['v-tabs-window-item', props.class],
        "style": props.style
      }), slots);
    });
    return {};
  }
});

const {Fragment:_Fragment$1,mergeProps:_mergeProps$2,createVNode:_createVNode$7} = await importShared('vue');
const {computed: computed$3,toRef: toRef$3} = await importShared('vue');
function parseItems(items) {
  if (!items) return [];
  return items.map(item => {
    if (!isObject(item)) return {
      text: item,
      value: item
    };
    return item;
  });
}
const makeVTabsProps = propsFactory({
  alignTabs: {
    type: String,
    default: 'start'
  },
  color: String,
  fixedTabs: Boolean,
  items: {
    type: Array,
    default: () => []
  },
  stacked: Boolean,
  bgColor: String,
  grow: Boolean,
  height: {
    type: [Number, String],
    default: undefined
  },
  hideSlider: Boolean,
  sliderColor: String,
  ...makeVSlideGroupProps({
    mandatory: 'force',
    selectedClass: 'v-tab-item--selected'
  }),
  ...makeDensityProps(),
  ...makeTagProps()
}, 'VTabs');
const VTabs = genericComponent()({
  name: 'VTabs',
  props: makeVTabsProps(),
  emits: {
    'update:modelValue': v => true
  },
  setup(props, _ref) {
    let {
      attrs,
      slots
    } = _ref;
    const model = useProxiedModel(props, 'modelValue');
    const items = computed$3(() => parseItems(props.items));
    const {
      densityClasses
    } = useDensity(props);
    const {
      backgroundColorClasses,
      backgroundColorStyles
    } = useBackgroundColor(() => props.bgColor);
    const {
      scopeId
    } = useScopeId();
    provideDefaults({
      VTab: {
        color: toRef$3(() => props.color),
        direction: toRef$3(() => props.direction),
        stacked: toRef$3(() => props.stacked),
        fixed: toRef$3(() => props.fixedTabs),
        sliderColor: toRef$3(() => props.sliderColor),
        hideSlider: toRef$3(() => props.hideSlider)
      }
    });
    useRender(() => {
      const slideGroupProps = VSlideGroup.filterProps(props);
      const hasWindow = !!(slots.window || props.items.length > 0);
      return _createVNode$7(_Fragment$1, null, [_createVNode$7(VSlideGroup, _mergeProps$2(slideGroupProps, {
        "modelValue": model.value,
        "onUpdate:modelValue": $event => model.value = $event,
        "class": ['v-tabs', `v-tabs--${props.direction}`, `v-tabs--align-tabs-${props.alignTabs}`, {
          'v-tabs--fixed-tabs': props.fixedTabs,
          'v-tabs--grow': props.grow,
          'v-tabs--stacked': props.stacked
        }, densityClasses.value, backgroundColorClasses.value, props.class],
        "style": [{
          '--v-tabs-height': convertToUnit(props.height)
        }, backgroundColorStyles.value, props.style],
        "role": "tablist",
        "symbol": VTabsSymbol
      }, scopeId, attrs), {
        default: () => [slots.default?.() ?? items.value.map(item => slots.tab?.({
          item
        }) ?? _createVNode$7(VTab, _mergeProps$2(item, {
          "key": item.text,
          "value": item.value
        }), {
          default: slots[`tab.${item.value}`] ? () => slots[`tab.${item.value}`]?.({
            item
          }) : undefined
        }))]
      }), hasWindow && _createVNode$7(VTabsWindow, _mergeProps$2({
        "modelValue": model.value,
        "onUpdate:modelValue": $event => model.value = $event,
        "key": "tabs-window"
      }, scopeId), {
        default: () => [items.value.map(item => slots.item?.({
          item
        }) ?? _createVNode$7(VTabsWindowItem, {
          "value": item.value
        }, {
          default: () => slots[`item.${item.value}`]?.({
            item
          })
        })), slots.window?.()]
      })]);
    });
    return {};
  }
});

const {Fragment:_Fragment,createVNode:_createVNode$6,resolveDirective:_resolveDirective,mergeProps:_mergeProps$1,withDirectives:_withDirectives,vModelText:_vModelText} = await importShared('vue');
const {computed: computed$2,nextTick,onBeforeUnmount,onMounted,ref: ref$2,shallowRef: shallowRef$1,watch: watch$1,watchEffect} = await importShared('vue');
const makeVTextareaProps = propsFactory({
  autoGrow: Boolean,
  autofocus: Boolean,
  counter: [Boolean, Number, String],
  counterValue: Function,
  prefix: String,
  placeholder: String,
  persistentPlaceholder: Boolean,
  persistentCounter: Boolean,
  noResize: Boolean,
  rows: {
    type: [Number, String],
    default: 5,
    validator: v => !isNaN(parseFloat(v))
  },
  maxRows: {
    type: [Number, String],
    validator: v => !isNaN(parseFloat(v))
  },
  suffix: String,
  modelModifiers: Object,
  ...makeVInputProps(),
  ...makeVFieldProps()
}, 'VTextarea');
const VTextarea = genericComponent()({
  name: 'VTextarea',
  directives: {
    Intersect
  },
  inheritAttrs: false,
  props: makeVTextareaProps(),
  emits: {
    'click:control': e => true,
    'mousedown:control': e => true,
    'update:focused': focused => true,
    'update:modelValue': val => true
  },
  setup(props, _ref) {
    let {
      attrs,
      emit,
      slots
    } = _ref;
    const model = useProxiedModel(props, 'modelValue');
    const {
      isFocused,
      focus,
      blur
    } = useFocus(props);
    const counterValue = computed$2(() => {
      return typeof props.counterValue === 'function' ? props.counterValue(model.value) : (model.value || '').toString().length;
    });
    const max = computed$2(() => {
      if (attrs.maxlength) return attrs.maxlength;
      if (!props.counter || typeof props.counter !== 'number' && typeof props.counter !== 'string') return undefined;
      return props.counter;
    });
    function onIntersect(isIntersecting, entries) {
      if (!props.autofocus || !isIntersecting) return;
      entries[0].target?.focus?.();
    }
    const vInputRef = ref$2();
    const vFieldRef = ref$2();
    const controlHeight = shallowRef$1('');
    const textareaRef = ref$2();
    const isActive = computed$2(() => props.persistentPlaceholder || isFocused.value || props.active);
    function onFocus() {
      if (textareaRef.value !== document.activeElement) {
        textareaRef.value?.focus();
      }
      if (!isFocused.value) focus();
    }
    function onControlClick(e) {
      onFocus();
      emit('click:control', e);
    }
    function onControlMousedown(e) {
      emit('mousedown:control', e);
    }
    function onClear(e) {
      e.stopPropagation();
      onFocus();
      nextTick(() => {
        model.value = '';
        callEvent(props['onClick:clear'], e);
      });
    }
    function onInput(e) {
      const el = e.target;
      model.value = el.value;
      if (props.modelModifiers?.trim) {
        const caretPosition = [el.selectionStart, el.selectionEnd];
        nextTick(() => {
          el.selectionStart = caretPosition[0];
          el.selectionEnd = caretPosition[1];
        });
      }
    }
    const sizerRef = ref$2();
    const rows = ref$2(Number(props.rows));
    const isPlainOrUnderlined = computed$2(() => ['plain', 'underlined'].includes(props.variant));
    watchEffect(() => {
      if (!props.autoGrow) rows.value = Number(props.rows);
    });
    function calculateInputHeight() {
      if (!props.autoGrow) return;
      nextTick(() => {
        if (!sizerRef.value || !vFieldRef.value) return;
        const style = getComputedStyle(sizerRef.value);
        const fieldStyle = getComputedStyle(vFieldRef.value.$el);
        const padding = parseFloat(style.getPropertyValue('--v-field-padding-top')) + parseFloat(style.getPropertyValue('--v-input-padding-top')) + parseFloat(style.getPropertyValue('--v-field-padding-bottom'));
        const height = sizerRef.value.scrollHeight;
        const lineHeight = parseFloat(style.lineHeight);
        const minHeight = Math.max(parseFloat(props.rows) * lineHeight + padding, parseFloat(fieldStyle.getPropertyValue('--v-input-control-height')));
        const maxHeight = parseFloat(props.maxRows) * lineHeight + padding || Infinity;
        const newHeight = clamp(height ?? 0, minHeight, maxHeight);
        rows.value = Math.floor((newHeight - padding) / lineHeight);
        controlHeight.value = convertToUnit(newHeight);
      });
    }
    onMounted(calculateInputHeight);
    watch$1(model, calculateInputHeight);
    watch$1(() => props.rows, calculateInputHeight);
    watch$1(() => props.maxRows, calculateInputHeight);
    watch$1(() => props.density, calculateInputHeight);
    let observer;
    watch$1(sizerRef, val => {
      if (val) {
        observer = new ResizeObserver(calculateInputHeight);
        observer.observe(sizerRef.value);
      } else {
        observer?.disconnect();
      }
    });
    onBeforeUnmount(() => {
      observer?.disconnect();
    });
    useRender(() => {
      const hasCounter = !!(slots.counter || props.counter || props.counterValue);
      const hasDetails = !!(hasCounter || slots.details);
      const [rootAttrs, inputAttrs] = filterInputAttrs(attrs);
      const {
        modelValue: _,
        ...inputProps
      } = VInput.filterProps(props);
      const fieldProps = VField.filterProps(props);
      return _createVNode$6(VInput, _mergeProps$1({
        "ref": vInputRef,
        "modelValue": model.value,
        "onUpdate:modelValue": $event => model.value = $event,
        "class": ['v-textarea v-text-field', {
          'v-textarea--prefixed': props.prefix,
          'v-textarea--suffixed': props.suffix,
          'v-text-field--prefixed': props.prefix,
          'v-text-field--suffixed': props.suffix,
          'v-textarea--auto-grow': props.autoGrow,
          'v-textarea--no-resize': props.noResize || props.autoGrow,
          'v-input--plain-underlined': isPlainOrUnderlined.value
        }, props.class],
        "style": props.style
      }, rootAttrs, inputProps, {
        "centerAffix": rows.value === 1 && !isPlainOrUnderlined.value,
        "focused": isFocused.value
      }), {
        ...slots,
        default: _ref2 => {
          let {
            id,
            isDisabled,
            isDirty,
            isReadonly,
            isValid
          } = _ref2;
          return _createVNode$6(VField, _mergeProps$1({
            "ref": vFieldRef,
            "style": {
              '--v-textarea-control-height': controlHeight.value
            },
            "onClick": onControlClick,
            "onMousedown": onControlMousedown,
            "onClick:clear": onClear,
            "onClick:prependInner": props['onClick:prependInner'],
            "onClick:appendInner": props['onClick:appendInner']
          }, fieldProps, {
            "id": id.value,
            "active": isActive.value || isDirty.value,
            "centerAffix": rows.value === 1 && !isPlainOrUnderlined.value,
            "dirty": isDirty.value || props.dirty,
            "disabled": isDisabled.value,
            "focused": isFocused.value,
            "error": isValid.value === false
          }), {
            ...slots,
            default: _ref3 => {
              let {
                props: {
                  class: fieldClass,
                  ...slotProps
                }
              } = _ref3;
              return _createVNode$6(_Fragment, null, [props.prefix && _createVNode$6("span", {
                "class": "v-text-field__prefix"
              }, [props.prefix]), _withDirectives(_createVNode$6("textarea", _mergeProps$1({
                "ref": textareaRef,
                "class": fieldClass,
                "value": model.value,
                "onInput": onInput,
                "autofocus": props.autofocus,
                "readonly": isReadonly.value,
                "disabled": isDisabled.value,
                "placeholder": props.placeholder,
                "rows": props.rows,
                "name": props.name,
                "onFocus": onFocus,
                "onBlur": blur
              }, slotProps, inputAttrs), null), [[_resolveDirective("intersect"), {
                handler: onIntersect
              }, null, {
                once: true
              }]]), props.autoGrow && _withDirectives(_createVNode$6("textarea", {
                "class": [fieldClass, 'v-textarea__sizer'],
                "id": `${slotProps.id}-sizer`,
                "onUpdate:modelValue": $event => model.value = $event,
                "ref": sizerRef,
                "readonly": true,
                "aria-hidden": "true"
              }, null), [[_vModelText, model.value]]), props.suffix && _createVNode$6("span", {
                "class": "v-text-field__suffix"
              }, [props.suffix])]);
            }
          });
        },
        details: hasDetails ? slotProps => _createVNode$6(_Fragment, null, [slots.details?.(slotProps), hasCounter && _createVNode$6(_Fragment, null, [_createVNode$6("span", null, null), _createVNode$6(VCounter, {
          "active": props.persistentCounter || isFocused.value,
          "value": counterValue.value,
          "max": max.value,
          "disabled": props.disabled
        }, slots.counter)])]) : undefined
      });
    });
    return forwardRefs({}, vInputRef, vFieldRef, textareaRef);
  }
});

const {createVNode:_createVNode$5} = await importShared('vue');
const makeVThemeProviderProps = propsFactory({
  withBackground: Boolean,
  ...makeComponentProps(),
  ...makeThemeProps(),
  ...makeTagProps()
}, 'VThemeProvider');
const VThemeProvider = genericComponent()({
  name: 'VThemeProvider',
  props: makeVThemeProviderProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      themeClasses
    } = provideTheme(props);
    return () => {
      if (!props.withBackground) return slots.default?.();
      return _createVNode$5(props.tag, {
        "class": ['v-theme-provider', themeClasses.value, props.class],
        "style": props.style
      }, {
        default: () => [slots.default?.()]
      });
    };
  }
});

const {createVNode:_createVNode$4} = await importShared('vue');
const makeVTimelineDividerProps = propsFactory({
  dotColor: String,
  fillDot: Boolean,
  hideDot: Boolean,
  icon: IconValue,
  iconColor: String,
  lineColor: String,
  ...makeComponentProps(),
  ...makeRoundedProps(),
  ...makeSizeProps(),
  ...makeElevationProps()
}, 'VTimelineDivider');
const VTimelineDivider = genericComponent()({
  name: 'VTimelineDivider',
  props: makeVTimelineDividerProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      sizeClasses,
      sizeStyles
    } = useSize(props, 'v-timeline-divider__dot');
    const {
      backgroundColorStyles,
      backgroundColorClasses
    } = useBackgroundColor(() => props.dotColor);
    const {
      roundedClasses
    } = useRounded(props, 'v-timeline-divider__dot');
    const {
      elevationClasses
    } = useElevation(props);
    const {
      backgroundColorClasses: lineColorClasses,
      backgroundColorStyles: lineColorStyles
    } = useBackgroundColor(() => props.lineColor);
    useRender(() => _createVNode$4("div", {
      "class": ['v-timeline-divider', {
        'v-timeline-divider--fill-dot': props.fillDot
      }, props.class],
      "style": props.style
    }, [_createVNode$4("div", {
      "class": ['v-timeline-divider__before', lineColorClasses.value],
      "style": lineColorStyles.value
    }, null), !props.hideDot && _createVNode$4("div", {
      "key": "dot",
      "class": ['v-timeline-divider__dot', elevationClasses.value, roundedClasses.value, sizeClasses.value],
      "style": sizeStyles.value
    }, [_createVNode$4("div", {
      "class": ['v-timeline-divider__inner-dot', backgroundColorClasses.value, roundedClasses.value],
      "style": backgroundColorStyles.value
    }, [!slots.default ? _createVNode$4(VIcon, {
      "key": "icon",
      "color": props.iconColor,
      "icon": props.icon,
      "size": props.size
    }, null) : _createVNode$4(VDefaultsProvider, {
      "key": "icon-defaults",
      "disabled": !props.icon,
      "defaults": {
        VIcon: {
          color: props.iconColor,
          icon: props.icon,
          size: props.size
        }
      }
    }, slots.default)])]), _createVNode$4("div", {
      "class": ['v-timeline-divider__after', lineColorClasses.value],
      "style": lineColorStyles.value
    }, null)]));
    return {};
  }
});

const {createVNode:_createVNode$3} = await importShared('vue');
const {ref: ref$1,shallowRef,watch} = await importShared('vue');
// Types
const makeVTimelineItemProps = propsFactory({
  density: String,
  dotColor: String,
  fillDot: Boolean,
  hideDot: Boolean,
  hideOpposite: {
    type: Boolean,
    default: undefined
  },
  icon: IconValue,
  iconColor: String,
  lineInset: [Number, String],
  side: {
    type: String,
    validator: v => v == null || ['start', 'end'].includes(v)
  },
  ...makeComponentProps(),
  ...makeDimensionProps(),
  ...makeElevationProps(),
  ...makeRoundedProps(),
  ...makeSizeProps(),
  ...makeTagProps()
}, 'VTimelineItem');
const VTimelineItem = genericComponent()({
  name: 'VTimelineItem',
  props: makeVTimelineItemProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      dimensionStyles
    } = useDimension(props);
    const dotSize = shallowRef(0);
    const dotRef = ref$1();
    watch(dotRef, newValue => {
      if (!newValue) return;
      dotSize.value = newValue.$el.querySelector('.v-timeline-divider__dot')?.getBoundingClientRect().width ?? 0;
    }, {
      flush: 'post'
    });
    useRender(() => _createVNode$3("div", {
      "class": ['v-timeline-item', {
        'v-timeline-item--fill-dot': props.fillDot,
        'v-timeline-item--side-start': props.side === 'start',
        'v-timeline-item--side-end': props.side === 'end'
      }, props.class],
      "style": [{
        '--v-timeline-dot-size': convertToUnit(dotSize.value),
        '--v-timeline-line-inset': props.lineInset ? `calc(var(--v-timeline-dot-size) / 2 + ${convertToUnit(props.lineInset)})` : convertToUnit(0)
      }, props.style]
    }, [_createVNode$3("div", {
      "class": "v-timeline-item__body",
      "style": dimensionStyles.value
    }, [slots.default?.()]), _createVNode$3(VTimelineDivider, {
      "ref": dotRef,
      "hideDot": props.hideDot,
      "icon": props.icon,
      "iconColor": props.iconColor,
      "size": props.size,
      "elevation": props.elevation,
      "dotColor": props.dotColor,
      "fillDot": props.fillDot,
      "rounded": props.rounded
    }, {
      default: slots.icon
    }), props.density !== 'compact' && _createVNode$3("div", {
      "class": "v-timeline-item__opposite"
    }, [!props.hideOpposite && slots.opposite?.()])]));
    return {};
  }
});

const {createVNode:_createVNode$2} = await importShared('vue');
const {computed: computed$1,toRef: toRef$2} = await importShared('vue');
const makeVTimelineProps = propsFactory({
  align: {
    type: String,
    default: 'center',
    validator: v => ['center', 'start'].includes(v)
  },
  direction: {
    type: String,
    default: 'vertical',
    validator: v => ['vertical', 'horizontal'].includes(v)
  },
  justify: {
    type: String,
    default: 'auto',
    validator: v => ['auto', 'center'].includes(v)
  },
  side: {
    type: String,
    validator: v => v == null || ['start', 'end'].includes(v)
  },
  lineThickness: {
    type: [String, Number],
    default: 2
  },
  lineColor: String,
  truncateLine: {
    type: String,
    validator: v => ['start', 'end', 'both'].includes(v)
  },
  ...pick(makeVTimelineItemProps({
    lineInset: 0
  }), ['dotColor', 'fillDot', 'hideOpposite', 'iconColor', 'lineInset', 'size']),
  ...makeComponentProps(),
  ...makeDensityProps(),
  ...makeTagProps(),
  ...makeThemeProps()
}, 'VTimeline');
const VTimeline = genericComponent()({
  name: 'VTimeline',
  props: makeVTimelineProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const {
      themeClasses
    } = provideTheme(props);
    const {
      densityClasses
    } = useDensity(props);
    const {
      rtlClasses
    } = useRtl();
    provideDefaults({
      VTimelineDivider: {
        lineColor: toRef$2(() => props.lineColor)
      },
      VTimelineItem: {
        density: toRef$2(() => props.density),
        dotColor: toRef$2(() => props.dotColor),
        fillDot: toRef$2(() => props.fillDot),
        hideOpposite: toRef$2(() => props.hideOpposite),
        iconColor: toRef$2(() => props.iconColor),
        lineColor: toRef$2(() => props.lineColor),
        lineInset: toRef$2(() => props.lineInset),
        size: toRef$2(() => props.size)
      }
    });
    const sideClasses = computed$1(() => {
      const side = props.side ? props.side : props.density !== 'default' ? 'end' : null;
      return side && `v-timeline--side-${side}`;
    });
    const truncateClasses = computed$1(() => {
      const classes = ['v-timeline--truncate-line-start', 'v-timeline--truncate-line-end'];
      switch (props.truncateLine) {
        case 'both':
          return classes;
        case 'start':
          return classes[0];
        case 'end':
          return classes[1];
        default:
          return null;
      }
    });
    useRender(() => _createVNode$2(props.tag, {
      "class": ['v-timeline', `v-timeline--${props.direction}`, `v-timeline--align-${props.align}`, `v-timeline--justify-${props.justify}`, truncateClasses.value, {
        'v-timeline--inset-line': !!props.lineInset
      }, themeClasses.value, densityClasses.value, sideClasses.value, rtlClasses.value, props.class],
      "style": [{
        '--v-timeline-line-thickness': convertToUnit(props.lineThickness)
      }, props.style]
    }, slots));
    return {};
  }
});

const {createVNode:_createVNode$1} = await importShared('vue');
const {toRef: toRef$1} = await importShared('vue');
const makeVToolbarItemsProps = propsFactory({
  ...makeComponentProps(),
  ...makeVariantProps({
    variant: 'text'
  })
}, 'VToolbarItems');
const VToolbarItems = genericComponent()({
  name: 'VToolbarItems',
  props: makeVToolbarItemsProps(),
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    provideDefaults({
      VBtn: {
        color: toRef$1(() => props.color),
        height: 'inherit',
        variant: toRef$1(() => props.variant)
      }
    });
    useRender(() => _createVNode$1("div", {
      "class": ['v-toolbar-items', props.class],
      "style": props.style
    }, [slots.default?.()]));
    return {};
  }
});

const {mergeProps:_mergeProps,createVNode:_createVNode} = await importShared('vue');
const {computed,mergeProps: mergeProps$1,ref,toRef,useId} = await importShared('vue');
const makeVTooltipProps = propsFactory({
  id: String,
  interactive: Boolean,
  text: String,
  ...omit(makeVOverlayProps({
    closeOnBack: false,
    location: 'end',
    locationStrategy: 'connected',
    eager: true,
    minWidth: 0,
    offset: 10,
    openOnClick: false,
    openOnHover: true,
    origin: 'auto',
    scrim: false,
    scrollStrategy: 'reposition',
    transition: null
  }), ['absolute', 'persistent'])
}, 'VTooltip');
const VTooltip = genericComponent()({
  name: 'VTooltip',
  props: makeVTooltipProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const isActive = useProxiedModel(props, 'modelValue');
    const {
      scopeId
    } = useScopeId();
    const uid = useId();
    const id = toRef(() => props.id || `v-tooltip-${uid}`);
    const overlay = ref();
    const location = computed(() => {
      return props.location.split(' ').length > 1 ? props.location : props.location + ' center';
    });
    const origin = computed(() => {
      return props.origin === 'auto' || props.origin === 'overlap' || props.origin.split(' ').length > 1 || props.location.split(' ').length > 1 ? props.origin : props.origin + ' center';
    });
    const transition = toRef(() => {
      if (props.transition != null) return props.transition;
      return isActive.value ? 'scale-transition' : 'fade-transition';
    });
    const activatorProps = computed(() => mergeProps$1({
      'aria-describedby': id.value
    }, props.activatorProps));
    useRender(() => {
      const overlayProps = VOverlay.filterProps(props);
      return _createVNode(VOverlay, _mergeProps({
        "ref": overlay,
        "class": ['v-tooltip', {
          'v-tooltip--interactive': props.interactive
        }, props.class],
        "style": props.style,
        "id": id.value
      }, overlayProps, {
        "modelValue": isActive.value,
        "onUpdate:modelValue": $event => isActive.value = $event,
        "transition": transition.value,
        "absolute": true,
        "location": location.value,
        "origin": origin.value,
        "persistent": true,
        "role": "tooltip",
        "activatorProps": activatorProps.value,
        "_disableGlobalStack": true
      }, scopeId), {
        activator: slots.activator,
        default: function () {
          for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
            args[_key] = arguments[_key];
          }
          return slots.default?.(...args) ?? props.text;
        }
      });
    });
    return forwardRefs({}, overlay);
  }
});

// Composables
const VValidation = genericComponent()({
  name: 'VValidation',
  props: makeValidationProps(),
  emits: {
    'update:modelValue': value => true
  },
  setup(props, _ref) {
    let {
      slots
    } = _ref;
    const validation = useValidation(props, 'validation');
    return () => slots.default?.(validation);
  }
});

const components = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  VAlert,
  VAlertTitle,
  VApp,
  VAppBar,
  VAppBarNavIcon,
  VAppBarTitle,
  VAutocomplete,
  VAvatar,
  VBadge,
  VBanner,
  VBannerActions,
  VBannerText,
  VBottomNavigation,
  VBottomSheet,
  VBreadcrumbs,
  VBreadcrumbsDivider,
  VBreadcrumbsItem,
  VBtn,
  VBtnGroup,
  VBtnToggle,
  VCard,
  VCardActions,
  VCardItem,
  VCardSubtitle,
  VCardText,
  VCardTitle,
  VCarousel,
  VCarouselItem,
  VCheckbox,
  VCheckboxBtn,
  VChip,
  VChipGroup,
  VClassIcon,
  VCode,
  VCol,
  VColorPicker,
  VCombobox,
  VComponentIcon,
  VConfirmEdit,
  VContainer,
  VCounter,
  VDataIterator,
  VDataTable,
  VDataTableFooter,
  VDataTableHeaders,
  VDataTableRow,
  VDataTableRows,
  VDataTableServer,
  VDataTableVirtual,
  VDatePicker,
  VDatePickerControls,
  VDatePickerHeader,
  VDatePickerMonth,
  VDatePickerMonths,
  VDatePickerYears,
  VDefaultsProvider,
  VDialog,
  VDialogBottomTransition,
  VDialogTopTransition,
  VDialogTransition,
  VDivider,
  VEmptyState,
  VExpandTransition,
  VExpandXTransition,
  VExpansionPanel,
  VExpansionPanelText,
  VExpansionPanelTitle,
  VExpansionPanels,
  VFab,
  VFabTransition,
  VFadeTransition,
  VField,
  VFieldLabel,
  VFileInput,
  VFooter,
  VForm,
  VHover,
  VIcon,
  VImg,
  VInfiniteScroll,
  VInput,
  VItem,
  VItemGroup,
  VKbd,
  VLabel,
  VLayout,
  VLayoutItem,
  VLazy,
  VLigatureIcon,
  VList,
  VListGroup,
  VListImg,
  VListItem,
  VListItemAction,
  VListItemMedia,
  VListItemSubtitle,
  VListItemTitle,
  VListSubheader,
  VLocaleProvider,
  VMain,
  VMenu,
  VMessages,
  VNavigationDrawer,
  VNoSsr,
  VNumberInput,
  VOtpInput,
  VOverlay,
  VPagination,
  VParallax,
  VProgressCircular,
  VProgressLinear,
  VRadio,
  VRadioGroup,
  VRangeSlider,
  VRating,
  VResponsive,
  VRow,
  VScaleTransition,
  VScrollXReverseTransition,
  VScrollXTransition,
  VScrollYReverseTransition,
  VScrollYTransition,
  VSelect,
  VSelectionControl,
  VSelectionControlGroup,
  VSheet,
  VSkeletonLoader,
  VSlideGroup,
  VSlideGroupItem,
  VSlideXReverseTransition,
  VSlideXTransition,
  VSlideYReverseTransition,
  VSlideYTransition,
  VSlider,
  VSnackbar,
  VSnackbarQueue,
  VSpacer,
  VSparkline,
  VSpeedDial,
  VStepper,
  VStepperActions,
  VStepperHeader,
  VStepperItem,
  VStepperWindow,
  VStepperWindowItem,
  VSvgIcon,
  VSwitch,
  VSystemBar,
  VTab,
  VTable,
  VTabs,
  VTabsWindow,
  VTabsWindowItem,
  VTextField,
  VTextarea,
  VThemeProvider,
  VTimeline,
  VTimelineItem,
  VToolbar,
  VToolbarItems,
  VToolbarTitle,
  VTooltip,
  VValidation,
  VVirtualScroll,
  VWindow,
  VWindowItem
}, Symbol.toStringTag, { value: 'Module' }));

// Types

function mounted$2(el, binding) {
  const modifiers = binding.modifiers || {};
  const value = binding.value;
  const {
    once,
    immediate,
    ...modifierKeys
  } = modifiers;
  const defaultValue = !Object.keys(modifierKeys).length;
  const {
    handler,
    options
  } = typeof value === 'object' ? value : {
    handler: value,
    options: {
      attributes: modifierKeys?.attr ?? defaultValue,
      characterData: modifierKeys?.char ?? defaultValue,
      childList: modifierKeys?.child ?? defaultValue,
      subtree: modifierKeys?.sub ?? defaultValue
    }
  };
  const observer = new MutationObserver(function () {
    let mutations = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];
    let observer = arguments.length > 1 ? arguments[1] : undefined;
    handler?.(mutations, observer);
    if (once) unmounted$2(el, binding);
  });
  if (immediate) handler?.([], observer);
  el._mutate = Object(el._mutate);
  el._mutate[binding.instance.$.uid] = {
    observer
  };
  observer.observe(el, options);
}
function unmounted$2(el, binding) {
  if (!el._mutate?.[binding.instance.$.uid]) return;
  el._mutate[binding.instance.$.uid].observer.disconnect();
  delete el._mutate[binding.instance.$.uid];
}
const Mutate = {
  mounted: mounted$2,
  unmounted: unmounted$2
};

// Types

function mounted$1(el, binding) {
  const handler = binding.value;
  const options = {
    passive: !binding.modifiers?.active
  };
  window.addEventListener('resize', handler, options);
  el._onResize = Object(el._onResize);
  el._onResize[binding.instance.$.uid] = {
    handler,
    options
  };
  if (!binding.modifiers?.quiet) {
    handler();
  }
}
function unmounted$1(el, binding) {
  if (!el._onResize?.[binding.instance.$.uid]) return;
  const {
    handler,
    options
  } = el._onResize[binding.instance.$.uid];
  window.removeEventListener('resize', handler, options);
  delete el._onResize[binding.instance.$.uid];
}
const Resize = {
  mounted: mounted$1,
  unmounted: unmounted$1
};

// Types

function mounted(el, binding) {
  const {
    self = false
  } = binding.modifiers ?? {};
  const value = binding.value;
  const options = typeof value === 'object' && value.options || {
    passive: true
  };
  const handler = typeof value === 'function' || 'handleEvent' in value ? value : value.handler;
  const target = self ? el : binding.arg ? document.querySelector(binding.arg) : window;
  if (!target) return;
  target.addEventListener('scroll', handler, options);
  el._onScroll = Object(el._onScroll);
  el._onScroll[binding.instance.$.uid] = {
    handler,
    options,
    // Don't reference self
    target: self ? undefined : target
  };
}
function unmounted(el, binding) {
  if (!el._onScroll?.[binding.instance.$.uid]) return;
  const {
    handler,
    options,
    target = el
  } = el._onScroll[binding.instance.$.uid];
  target.removeEventListener('scroll', handler, options);
  delete el._onScroll[binding.instance.$.uid];
}
function updated(el, binding) {
  if (binding.value === binding.oldValue) return;
  unmounted(el, binding);
  mounted(el, binding);
}
const Scroll = {
  mounted,
  unmounted,
  updated
};

// Utilities
const {h,mergeProps,render,resolveComponent} = await importShared('vue');
function useDirectiveComponent(component, props) {
  const concreteComponent = typeof component === 'string' ? resolveComponent(component) : component;
  const hook = mountComponent(concreteComponent, props);
  return {
    mounted: hook,
    updated: hook,
    unmounted(el) {
      render(null, el);
    }
  };
}
function mountComponent(component, props) {
  return function (el, binding, vnode) {
    const _props = typeof props === 'function' ? props(binding) : props;
    const text = binding.value?.text ?? binding.value ?? _props?.text;
    const value = isObject(binding.value) ? binding.value : {};

    // Get the children from the props or directive value, or the element's children
    const children = () => text ?? el.textContent;

    // If vnode.ctx is the same as the instance, then we're bound to a plain element
    // and need to find the nearest parent component instance to inherit provides from
    const provides = (vnode.ctx === binding.instance.$ ? findComponentParent(vnode, binding.instance.$)?.provides : vnode.ctx?.provides) ?? binding.instance.$.provides;
    const node = h(component, mergeProps(_props, value), children);
    node.appContext = Object.assign(Object.create(null), binding.instance.$.appContext, {
      provides
    });
    render(node, el);
  };
}
function findComponentParent(vnode, root) {
  // Walk the tree from root until we find the child vnode
  const stack = new Set();
  const walk = children => {
    for (const child of children) {
      if (!child) continue;
      if (child === vnode || child.el && vnode.el && child.el === vnode.el) {
        return true;
      }
      stack.add(child);
      let result;
      if (child.suspense) {
        result = walk([child.ssContent]);
      } else if (Array.isArray(child.children)) {
        result = walk(child.children);
      } else if (child.component?.vnode) {
        result = walk([child.component?.subTree]);
      }
      if (result) {
        return result;
      }
      stack.delete(child);
    }
    return false;
  };
  if (!walk([root.subTree])) {
    consoleError('Could not find original vnode, component will not inherit provides');
    return root;
  }

  // Return the first component parent
  const result = Array.from(stack).reverse();
  for (const child of result) {
    if (child.component) {
      return child.component;
    }
  }
  return root;
}

// Components
const Tooltip = useDirectiveComponent(VTooltip, binding => {
  return {
    activator: 'parent',
    location: binding.arg?.replace('-', ' '),
    text: typeof binding.value === 'boolean' ? undefined : binding.value
  };
});

const directives = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  ClickOutside,
  Intersect,
  Mutate,
  Resize,
  Ripple,
  Scroll,
  Tooltip,
  Touch
}, Symbol.toStringTag, { value: 'Module' }));

const {createApp} = await importShared('vue');
const {createVuetify} = await importShared('vuetify');


// 创建Vuetify实例
const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'dark'
  }
});

// 创建应用
const app = createApp(App);

// 使用插件
app.use(vuetify);

// 挂载应用
app.mount('#app');
