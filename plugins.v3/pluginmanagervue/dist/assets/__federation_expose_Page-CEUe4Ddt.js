import { importShared } from './__federation_fn_import-JrT3xvdd.js';

const _export_sfc = (sfc, props) => {
  const target = sfc.__vccOpts || sfc;
  for (const [key, val] of props) {
    target[key] = val;
  }
  return target;
};

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,mergeProps:_mergeProps,withCtx:_withCtx,toDisplayString:_toDisplayString,renderList:_renderList,Fragment:_Fragment,openBlock:_openBlock,createElementBlock:_createElementBlock,withModifiers:_withModifiers,createBlock:_createBlock,createCommentVNode:_createCommentVNode,normalizeClass:_normalizeClass} = await importShared('vue');


const _hoisted_1 = { class: "plugin-manager" };
const _hoisted_2 = { class: "control-panel" };
const _hoisted_3 = { class: "panel-left" };
const _hoisted_4 = { class: "search-container" };
const _hoisted_5 = { class: "panel-right" };
const _hoisted_6 = { class: "quick-reload-header" };
const _hoisted_7 = { class: "quick-reload-list" };
const _hoisted_8 = ["onClick"];
const _hoisted_9 = { class: "quick-reload-name" };
const _hoisted_10 = { class: "quick-reload-actions" };
const _hoisted_11 = { class: "status-grid" };
const _hoisted_12 = { class: "status-indicator" };
const _hoisted_13 = { class: "status-data" };
const _hoisted_14 = { class: "status-value" };
const _hoisted_15 = { class: "status-label" };
const _hoisted_16 = {
  key: 1,
  class: "loading-panel"
};
const _hoisted_17 = { class: "loading-content" };
const _hoisted_18 = {
  key: 2,
  class: "error-panel"
};
const _hoisted_19 = { class: "error-message" };
const _hoisted_20 = {
  key: 3,
  class: "empty-panel"
};
const _hoisted_21 = { class: "empty-title" };
const _hoisted_22 = { class: "empty-subtitle" };
const _hoisted_23 = {
  key: 4,
  class: "plugin-matrix"
};
const _hoisted_24 = { class: "module-header" };
const _hoisted_25 = { class: "module-avatar" };
const _hoisted_26 = { class: "module-info" };
const _hoisted_27 = { class: "module-name" };
const _hoisted_28 = { class: "module-meta" };
const _hoisted_29 = { class: "module-status" };
const _hoisted_30 = { class: "module-tags" };
const _hoisted_31 = { class: "module-controls" };
const _hoisted_32 = {
  key: 0,
  class: "module-overlay"
};
const _hoisted_33 = { class: "overlay-text" };
const _hoisted_34 = { class: "target-info" };
const _hoisted_35 = { class: "target-name" };
const _hoisted_36 = { class: "target-meta" };
const _hoisted_37 = { class: "repo-info" };
const _hoisted_38 = { class: "info-section" };
const _hoisted_39 = { class: "info-label" };
const _hoisted_40 = ["title"];
const _hoisted_41 = { class: "info-section" };
const _hoisted_42 = { class: "info-label" };
const _hoisted_43 = { class: "info-value" };
const _hoisted_44 = { class: "info-section" };
const _hoisted_45 = { class: "info-label" };
const _hoisted_46 = { class: "info-value" };
const _hoisted_47 = { class: "info-section" };
const _hoisted_48 = { class: "info-label" };
const _hoisted_49 = { class: "info-value" };
const _hoisted_50 = { class: "dialog-title" };
const _hoisted_51 = { class: "target-info" };
const _hoisted_52 = { class: "target-name" };
const _hoisted_53 = { class: "target-meta" };
const _hoisted_54 = { class: "option-list" };
const _hoisted_55 = { class: "option-header" };

const {ref,computed,onMounted} = await importShared('vue');

  
  // Props
  const pluginId = "PluginManagerVue";
  
  // 计算属性
  
const _sfc_main = {
  __name: 'Page',
  props: {
    api: {
      type: [Object, Function],
      required: true,
    }
  },
  emits: ['close'],
  setup(__props, { emit: __emit }) {

  const props = __props;
  
  // Emits
  const emit = __emit;
  
  // 响应式数据
  const loading = ref(false);
  const error = ref(null);
  const dataLoaded = ref(false);
  const searchQuery = ref('');
  const globalMessage = ref(null);
  const globalMessageType = ref('info');
  const actionDialog = ref(false);
  const reinstallDialog = ref(false);
  const selectedPlugin = ref(null);
  const onlinePluginInfo = ref(null);
const clearConfig = ref(false);
const clearData = ref(false);
const forceClean = ref(false);
const actionLoading = ref(false);
const showFullRepoUrl = ref(false);
  
  // 快速重载相关
const quickReloadLoading = ref(false);
const lastReloadPlugins = ref([]);
const selectedQuickReloadIds = ref(new Set());

// 插件数据
const plugins = ref([]);
const reloadingPlugins = ref(new Set());
const reinstallingPlugins = ref(new Set());
  
  // 插件ID
  const filteredPlugins = computed(() => {
    if (!searchQuery.value) {
      return plugins.value;
    }
    
    const query = searchQuery.value.toLowerCase();
    return plugins.value.filter(plugin => 
      plugin.name.toLowerCase().includes(query) ||
      plugin.id.toLowerCase().includes(query) ||
      plugin.author.toLowerCase().includes(query) ||
      plugin.desc.toLowerCase().includes(query)
    );
  });
  
  const statusStats = computed(() => [
  {
    icon: 'mdi-package-variant',
    value: plugins.value.length,
    label: '总数'
  },
  {
    icon: 'mdi-check-circle',
    value: plugins.value.filter(p => p.installed).length,
    label: '已装'
  },
  {
    icon: 'mdi-play-circle',
    value: plugins.value.filter(p => p.running).length,
    label: '运行'
  },
  {
    icon: 'mdi-cloud',
    value: plugins.value.filter(p => p.type !== 'local').length,
    label: '在线'
  },
  {
    icon: 'mdi-folder',
    value: plugins.value.filter(p => p.type === 'local').length,
    label: '本地'
  }
]);

const allOptionsSelected = computed(() => {
  if (selectedPlugin.value?.installed) {
    // 已安装插件：配置 + 数据
    return clearConfig.value && clearData.value;
  } else {
    // 未安装插件：配置 + 数据 + 强制清理
    return clearConfig.value && clearData.value && forceClean.value;
  }
});

const allQuickReloadSelected = computed(() => {
  const availablePlugins = lastReloadPlugins.value.slice(0, 6);
  return availablePlugins.length > 0 && availablePlugins.every(plugin => selectedQuickReloadIds.value.has(plugin.id));
});
  
  // 方法
  function getStatusColor(plugin) {
  if (plugin.running) return 'success';
  if (plugin.installed) return 'primary';
  return 'grey';
}

function getStatusText(plugin) {
  if (plugin.running) return '运行中';
  if (plugin.installed) return '已安装';
  return '未安装';
}

function getStatusClass(plugin) {
  if (plugin.running) return 'dot-active';
  if (plugin.installed) return 'dot-ready';
  return 'dot-offline';
}
  
  function handleImageError(event) {
    if (event?.target?.src) {
      console.warn('插件图标加载失败:', event.target.src);
    }
  }
  
  function showMessage(message, type = 'info') {
    globalMessage.value = message;
    globalMessageType.value = type;
    
    setTimeout(() => {
      clearMessage();
    }, 5000);
  }
  
  function clearMessage() {
    globalMessage.value = null;
  }
  
  async function fetchPlugins() {
    loading.value = true;
    error.value = null;
  
    try {
      const response = await props.api.get(`plugin/${pluginId}/plugins`);
      
      if (response?.success) {
        plugins.value = response.data || [];
        dataLoaded.value = true;
      } else {
        throw new Error(response?.message || '获取插件列表失败');
      }
    } catch (err) {
      console.error('获取插件列表失败:', err);
      error.value = err.message || '获取插件列表失败';
    } finally {
      loading.value = false;
    }
  }
  
  async function refreshPlugins() {
    await fetchPlugins();
    await fetchLastReload();
  }
  
  async function reloadPlugin(plugin) {
  if (reloadingPlugins.value.has(plugin.id)) {
    return;
  }

  reloadingPlugins.value.add(plugin.id);

  try {
    const response = await props.api.post(`plugin/${pluginId}/reload`, {
      plugin_id: plugin.id
    });

    if (response?.success) {
      showMessage(`${plugin.name} 重载成功`, 'success');
      
      // 延迟刷新数据
      setTimeout(() => {
        refreshPlugins();
      }, 1000);
    } else {
      throw new Error(response?.message || '重载失败');
    }
  } catch (err) {
    console.error('重载插件失败:', err);
    showMessage(`${plugin.name} 重载失败: ${err.message}`, 'error');
  } finally {
    reloadingPlugins.value.delete(plugin.id);
  }
}


  
  async function reloadAllRecent() {
    if (lastReloadPlugins.value.length === 0) return;
    
    quickReloadLoading.value = true;
    let successCount = 0;
    let failCount = 0;
    
    for (const plugin of lastReloadPlugins.value) {
      try {
        const response = await props.api.post(`plugin/${pluginId}/reload`, {
          plugin_id: plugin.id
        });
        
        if (response?.success) {
          successCount++;
        } else {
          failCount++;
        }
      } catch (err) {
        console.error(`重载插件 ${plugin.id} 失败:`, err);
        failCount++;
      }
    }
    
    quickReloadLoading.value = false;
    
    if (failCount === 0) {
      showMessage(`成功重载 ${successCount} 个插件`, 'success');
    } else {
      showMessage(`重载完成：成功 ${successCount} 个，失败 ${failCount} 个`, 'warning');
    }
    
    setTimeout(() => {
      refreshPlugins();
    }, 1000);
  }
  
  function showActionDialog(plugin) {
  selectedPlugin.value = plugin;
  clearConfig.value = false;
  clearData.value = false;
  forceClean.value = false;
  actionDialog.value = true;
}

async function showReinstallDialog(plugin) {
  selectedPlugin.value = plugin;
  onlinePluginInfo.value = null;
  showFullRepoUrl.value = false; // 重置为显示简洁名称
  reinstallDialog.value = true;
  
  // 获取在线插件信息
  await fetchOnlinePluginInfo(plugin.id);
}

async function fetchOnlinePluginInfo(targetPluginId) {
  try {
    // 调用插件管理器的API获取在线插件信息
    const response = await props.api.get(`plugin/PluginManagerVue/online_info/${targetPluginId}`);
    
    if (response?.success && response.data) {
      onlinePluginInfo.value = response.data;
      console.log('找到在线插件信息:', response.data);
    } else {
      console.log('未找到在线插件:', targetPluginId, response?.message);
    }
  } catch (err) {
    console.error('获取在线插件信息失败:', err);
  }
}

function getRepoDisplayName(repoUrl) {
  if (!repoUrl) return '未知仓库';
  if (repoUrl === 'local') return '本地插件';
  
  // 如果显示完整URL，直接返回
  if (showFullRepoUrl.value) {
    return repoUrl;
  }
  
  // 默认显示用户名的仓库
  try {
    if (repoUrl.includes('github.com')) {
      const match = repoUrl.match(/github\.com\/([^\/]+)\/([^\/]+)/);
      if (match) {
        return `${match[1]}的仓库`;
      }
    }
    
    if (repoUrl.includes('raw.githubusercontent.com')) {
      const match = repoUrl.match(/raw\.githubusercontent\.com\/([^\/]+)\/([^\/]+)/);
      if (match) {
        return `${match[1]}的仓库`;
      }
    }
    
    // 其他情况返回域名
    const url = new URL(repoUrl);
    return url.hostname;
  } catch (e) {
    return repoUrl;
  }
}

function toggleRepoUrlDisplay() {
  showFullRepoUrl.value = !showFullRepoUrl.value;
}

function getPluginIconPath(iconPath) {
  if (!iconPath) return '';
  
  // 如果是网络图片则使用代理
  if (iconPath.startsWith('http')) {
    return `/api/v1/system/img/1?imgurl=${encodeURIComponent(iconPath)}`;
  }
  
  // 本地图片使用相对路径
  return `./plugin_icon/${iconPath}`;
}

function getUpdateStatusColor() {
  if (!onlinePluginInfo.value) return 'grey';
  
  const currentVersion = selectedPlugin.value?.version;
  const latestVersion = onlinePluginInfo.value?.plugin_version;
  
  if (!currentVersion || !latestVersion) return 'grey';
  
  // 简单的版本比较
  if (currentVersion !== latestVersion) {
    return 'success';
  }
  return 'grey';
}

function getUpdateStatusText() {
  if (!onlinePluginInfo.value) return '检查中...';
  
  const currentVersion = selectedPlugin.value?.version;
  const latestVersion = onlinePluginInfo.value?.plugin_version;
  
  if (!currentVersion || !latestVersion) return '版本未知';
  
  if (currentVersion !== latestVersion) {
    return '有新版本';
  }
  return '已是最新';
}

async function confirmReinstall() {
  if (!selectedPlugin.value) return;
  
  actionLoading.value = true;
  
  try {
    const response = await props.api.post(`plugin/${pluginId}/reinstall`, {
      plugin_id: selectedPlugin.value.id
    });

    if (response?.success) {
      showMessage(`${selectedPlugin.value.name} 重装成功`, 'success');
      
      // 延迟刷新数据
      setTimeout(() => {
        refreshPlugins();
      }, 1500);
    } else {
      throw new Error(response?.message || '重装失败');
    }
  } catch (err) {
    console.error('重装插件失败:', err);
    showMessage(`${selectedPlugin.value.name} 重装失败: ${err.message}`, 'error');
  } finally {
    actionLoading.value = false;
    reinstallDialog.value = false;
    selectedPlugin.value = null;
  }
}

function toggleAllOptions() {
  if (allOptionsSelected.value) {
    // 取消全选
    clearConfig.value = false;
    clearData.value = false;
    forceClean.value = false;
  } else {
    // 全选
    clearConfig.value = true;
    clearData.value = true;
    if (!selectedPlugin.value?.installed) {
      forceClean.value = true;
    }
  }
}

function toggleAllQuickReload() {
  const availablePlugins = lastReloadPlugins.value.slice(0, 6);
  if (allQuickReloadSelected.value) {
    // 取消全选
    selectedQuickReloadIds.value.clear();
  } else {
    // 全选
    selectedQuickReloadIds.value = new Set(availablePlugins.map(p => p.id));
  }
  // 触发响应式更新
  selectedQuickReloadIds.value = new Set(selectedQuickReloadIds.value);
}

function toggleQuickReloadSelection(pluginId) {
  if (selectedQuickReloadIds.value.has(pluginId)) {
    selectedQuickReloadIds.value.delete(pluginId);
  } else {
    selectedQuickReloadIds.value.add(pluginId);
  }
  // 触发响应式更新
  selectedQuickReloadIds.value = new Set(selectedQuickReloadIds.value);
}

async function reloadSelectedPlugins() {
  if (selectedQuickReloadIds.value.size === 0) return;
  
  quickReloadLoading.value = true;
  const selectedIds = Array.from(selectedQuickReloadIds.value);
  let successCount = 0;
  let failCount = 0;
  
  for (const targetPluginId of selectedIds) {
    try {
      const response = await props.api.post(`plugin/${pluginId}/reload`, {
        plugin_id: targetPluginId
      });
      
      if (response?.success) {
        successCount++;
      } else {
        failCount++;
        console.error(`重载插件 ${targetPluginId} 失败:`, response?.message || '未知错误');
      }
    } catch (err) {
      console.error(`重载插件 ${targetPluginId} 失败:`, err);
      failCount++;
    }
  }
  
  quickReloadLoading.value = false;
  
  if (failCount === 0) {
    showMessage(`成功重载 ${successCount} 个插件`, 'success');
  } else {
    showMessage(`重载完成：成功 ${successCount} 个，失败 ${failCount} 个`, 'warning');
  }
  
  // 清空选择
  selectedQuickReloadIds.value.clear();
  selectedQuickReloadIds.value = new Set();
  
  // 延迟刷新数据
  setTimeout(() => {
    refreshPlugins();
  }, 1000);
}
  
  async function confirmAction() {
    if (!selectedPlugin.value) return;
    
    actionLoading.value = true;
    
    try {
      const response = await props.api.post(`plugin/${pluginId}/uninstall`, {
        plugin_id: selectedPlugin.value.id,
        clear_config: clearConfig.value,
        clear_data: clearData.value,
        force_clean: forceClean.value
      });
  
      if (response?.success) {
        const action = selectedPlugin.value.installed ? '卸载' : '清理';
        showMessage(`${selectedPlugin.value.name} ${action}成功`, 'success');
        
        // 立即刷新数据
        setTimeout(() => {
          refreshPlugins();
        }, 1000);
      } else {
        throw new Error(response?.message || '操作失败');
      }
    } catch (err) {
      console.error('操作失败:', err);
      showMessage(`操作失败: ${err.message}`, 'error');
    } finally {
      actionLoading.value = false;
      actionDialog.value = false;
      selectedPlugin.value = null;
    }
  }
  
  async function fetchLastReload() {
    try {
      const response = await props.api.get(`plugin/${pluginId}/last_reload`);
      if (response?.success) {
        lastReloadPlugins.value = response.data || [];
      }
    } catch (err) {
      console.error('获取上次重载插件失败:', err);
    }
  }
  
  // 组件挂载
  onMounted(() => {
    fetchPlugins();
    fetchLastReload();
  });
  
return (_ctx, _cache) => {
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_badge = _resolveComponent("v-badge");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_checkbox = _resolveComponent("v-checkbox");
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_img = _resolveComponent("v-img");
  const _component_v_avatar = _resolveComponent("v-avatar");
  const _component_v_divider = _resolveComponent("v-divider");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_menu = _resolveComponent("v-menu");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_progress_circular = _resolveComponent("v-progress-circular");
  const _component_v_chip = _resolveComponent("v-chip");
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_card_actions = _resolveComponent("v-card-actions");
  const _component_v_dialog = _resolveComponent("v-dialog");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _createElementVNode("div", _hoisted_3, [
        _createElementVNode("div", _hoisted_4, [
          _createVNode(_component_v_text_field, {
            modelValue: searchQuery.value,
            "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((searchQuery).value = $event)),
            "prepend-inner-icon": "mdi-magnify",
            placeholder: "搜索插件...",
            variant: "outlined",
            density: "compact",
            "hide-details": "",
            clearable: "",
            class: "search-field"
          }, null, 8, ["modelValue"])
        ])
      ]),
      _createElementVNode("div", _hoisted_5, [
        (lastReloadPlugins.value.length > 0)
          ? (_openBlock(), _createBlock(_component_v_menu, {
              key: 0,
              "offset-y": ""
            }, {
              activator: _withCtx(({ props }) => [
                _createVNode(_component_v_btn, _mergeProps(props, {
                  variant: "outlined",
                  size: "small",
                  class: "control-btn quick-reload-btn",
                  "prepend-icon": "mdi-lightning-bolt"
                }), {
                  default: _withCtx(() => [
                    _cache[10] || (_cache[10] = _createTextVNode(" 快速重载 ")),
                    _createVNode(_component_v_badge, {
                      content: lastReloadPlugins.value.length,
                      color: "warning",
                      inline: ""
                    }, null, 8, ["content"])
                  ]),
                  _: 2,
                  __: [10]
                }, 1040)
              ]),
              default: _withCtx(() => [
                _createVNode(_component_v_card, {
                  class: "quick-reload-menu",
                  elevation: "8"
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_text, { class: "pa-2" }, {
                      default: _withCtx(() => [
                        _createElementVNode("div", _hoisted_6, [
                          _cache[11] || (_cache[11] = _createElementVNode("span", { class: "text-caption" }, "最近重载的插件", -1)),
                          _createVNode(_component_v_btn, {
                            size: "x-small",
                            variant: "text",
                            onClick: toggleAllQuickReload,
                            class: "select-all-btn"
                          }, {
                            default: _withCtx(() => [
                              _createTextVNode(_toDisplayString(allQuickReloadSelected.value ? '取消全选' : '全选'), 1)
                            ]),
                            _: 1
                          })
                        ]),
                        _createElementVNode("div", _hoisted_7, [
                          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(lastReloadPlugins.value.slice(0, 6), (plugin) => {
                            return (_openBlock(), _createElementBlock("div", {
                              key: plugin.id,
                              class: _normalizeClass(["quick-reload-item-wrapper", { 'selected': selectedQuickReloadIds.value.has(plugin.id) }]),
                              onClick: $event => (toggleQuickReloadSelection(plugin.id))
                            }, [
                              _createVNode(_component_v_checkbox, {
                                "model-value": selectedQuickReloadIds.value.has(plugin.id),
                                onClick: _cache[1] || (_cache[1] = _withModifiers(() => {}, ["stop"])),
                                onChange: $event => (toggleQuickReloadSelection(plugin.id)),
                                "hide-details": "",
                                density: "compact",
                                class: "quick-reload-checkbox"
                              }, null, 8, ["model-value", "onChange"]),
                              _createVNode(_component_v_avatar, {
                                size: "16",
                                class: "mr-2"
                              }, {
                                default: _withCtx(() => [
                                  (plugin.icon)
                                    ? (_openBlock(), _createBlock(_component_v_img, {
                                        key: 0,
                                        src: getPluginIconPath(plugin.icon)
                                      }, {
                                        placeholder: _withCtx(() => [
                                          _createVNode(_component_v_icon, { size: "12" }, {
                                            default: _withCtx(() => _cache[12] || (_cache[12] = [
                                              _createTextVNode("mdi-puzzle")
                                            ])),
                                            _: 1,
                                            __: [12]
                                          })
                                        ]),
                                        _: 2
                                      }, 1032, ["src"]))
                                    : (_openBlock(), _createBlock(_component_v_icon, {
                                        key: 1,
                                        size: "12"
                                      }, {
                                        default: _withCtx(() => _cache[13] || (_cache[13] = [
                                          _createTextVNode("mdi-puzzle")
                                        ])),
                                        _: 1,
                                        __: [13]
                                      }))
                                ]),
                                _: 2
                              }, 1024),
                              _createElementVNode("span", _hoisted_9, _toDisplayString(plugin.name), 1)
                            ], 10, _hoisted_8))
                          }), 128))
                        ]),
                        _createVNode(_component_v_divider, { class: "my-2" }),
                        _createElementVNode("div", _hoisted_10, [
                          _createVNode(_component_v_btn, {
                            size: "small",
                            variant: "outlined",
                            onClick: reloadSelectedPlugins,
                            loading: quickReloadLoading.value,
                            disabled: selectedQuickReloadIds.value.size === 0,
                            "prepend-icon": "mdi-reload",
                            class: "mr-2"
                          }, {
                            default: _withCtx(() => [
                              _createTextVNode(" 重载选中 (" + _toDisplayString(selectedQuickReloadIds.value.size) + ") ", 1)
                            ]),
                            _: 1
                          }, 8, ["loading", "disabled"]),
                          _createVNode(_component_v_btn, {
                            size: "small",
                            variant: "tonal",
                            onClick: reloadAllRecent,
                            loading: quickReloadLoading.value,
                            "prepend-icon": "mdi-reload-alert"
                          }, {
                            default: _withCtx(() => _cache[14] || (_cache[14] = [
                              _createTextVNode(" 全部重载 ")
                            ])),
                            _: 1,
                            __: [14]
                          }, 8, ["loading"])
                        ])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }))
          : _createCommentVNode("", true),
        _createVNode(_component_v_btn, {
          variant: "outlined",
          size: "small",
          onClick: refreshPlugins,
          loading: loading.value,
          class: "control-btn",
          "prepend-icon": "mdi-refresh"
        }, {
          default: _withCtx(() => _cache[15] || (_cache[15] = [
            _createTextVNode(" 刷新 ")
          ])),
          _: 1,
          __: [15]
        }, 8, ["loading"]),
        _createVNode(_component_v_btn, {
          icon: "mdi-close",
          variant: "text",
          size: "small",
          onClick: _cache[2] || (_cache[2] = $event => (emit('close'))),
          class: "control-btn close-btn"
        })
      ])
    ]),
    _createElementVNode("div", _hoisted_11, [
      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(statusStats.value, (stat, index) => {
        return (_openBlock(), _createElementBlock("div", {
          class: "status-card",
          key: index
        }, [
          _createElementVNode("div", _hoisted_12, [
            _createVNode(_component_v_icon, {
              icon: stat.icon,
              size: "18"
            }, null, 8, ["icon"])
          ]),
          _createElementVNode("div", _hoisted_13, [
            _createElementVNode("div", _hoisted_14, _toDisplayString(stat.value), 1),
            _createElementVNode("div", _hoisted_15, _toDisplayString(stat.label), 1)
          ]),
          _cache[16] || (_cache[16] = _createElementVNode("div", { class: "status-glow" }, null, -1))
        ]))
      }), 128))
    ]),
    (globalMessage.value)
      ? (_openBlock(), _createBlock(_component_v_alert, {
          key: 0,
          type: globalMessageType.value,
          variant: "tonal",
          closable: "",
          "onClick:close": clearMessage,
          class: "mb-3 alert-panel"
        }, {
          default: _withCtx(() => [
            _createTextVNode(_toDisplayString(globalMessage.value), 1)
          ]),
          _: 1
        }, 8, ["type"]))
      : _createCommentVNode("", true),
    (loading.value && !dataLoaded.value)
      ? (_openBlock(), _createElementBlock("div", _hoisted_16, [
          _createElementVNode("div", _hoisted_17, [
            _createVNode(_component_v_progress_circular, {
              indeterminate: "",
              size: "32",
              width: "3"
            }),
            _cache[17] || (_cache[17] = _createElementVNode("div", { class: "loading-text" }, "系统扫描中...", -1))
          ])
        ]))
      : (error.value)
        ? (_openBlock(), _createElementBlock("div", _hoisted_18, [
            _createVNode(_component_v_icon, {
              size: "48",
              class: "mb-3"
            }, {
              default: _withCtx(() => _cache[18] || (_cache[18] = [
                _createTextVNode("mdi-alert-octagon")
              ])),
              _: 1,
              __: [18]
            }),
            _cache[20] || (_cache[20] = _createElementVNode("div", { class: "error-title" }, "系统故障", -1)),
            _createElementVNode("div", _hoisted_19, _toDisplayString(error.value), 1),
            _createVNode(_component_v_btn, {
              onClick: refreshPlugins,
              variant: "outlined",
              class: "mt-3"
            }, {
              default: _withCtx(() => _cache[19] || (_cache[19] = [
                _createTextVNode(" 重新连接 ")
              ])),
              _: 1,
              __: [19]
            })
          ]))
        : (filteredPlugins.value.length === 0)
          ? (_openBlock(), _createElementBlock("div", _hoisted_20, [
              _createVNode(_component_v_icon, {
                size: "64",
                class: "mb-3"
              }, {
                default: _withCtx(() => _cache[21] || (_cache[21] = [
                  _createTextVNode("mdi-package-variant-closed")
                ])),
                _: 1,
                __: [21]
              }),
              _createElementVNode("div", _hoisted_21, _toDisplayString(searchQuery.value ? '未发现目标' : '插件库为空'), 1),
              _createElementVNode("div", _hoisted_22, _toDisplayString(searchQuery.value ? '调整搜索参数' : '等待插件部署'), 1)
            ]))
          : (_openBlock(), _createElementBlock("div", _hoisted_23, [
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(filteredPlugins.value, (plugin) => {
                return (_openBlock(), _createElementBlock("div", {
                  key: plugin.id,
                  class: _normalizeClass(["plugin-module", {
            'module-active': plugin.running,
            'module-installed': plugin.installed,
            'module-local': plugin.type === 'local'
          }])
                }, [
                  _createElementVNode("div", _hoisted_24, [
                    _createElementVNode("div", _hoisted_25, [
                      _createVNode(_component_v_avatar, {
                        size: "32",
                        class: "plugin-avatar"
                      }, {
                        default: _withCtx(() => [
                          (plugin.icon)
                            ? (_openBlock(), _createBlock(_component_v_img, {
                                key: 0,
                                src: getPluginIconPath(plugin.icon),
                                onError: handleImageError
                              }, {
                                placeholder: _withCtx(() => [
                                  _createVNode(_component_v_icon, { size: "18" }, {
                                    default: _withCtx(() => _cache[22] || (_cache[22] = [
                                      _createTextVNode("mdi-puzzle")
                                    ])),
                                    _: 1,
                                    __: [22]
                                  })
                                ]),
                                _: 2
                              }, 1032, ["src"]))
                            : (_openBlock(), _createBlock(_component_v_icon, {
                                key: 1,
                                size: "18"
                              }, {
                                default: _withCtx(() => _cache[23] || (_cache[23] = [
                                  _createTextVNode("mdi-puzzle")
                                ])),
                                _: 1,
                                __: [23]
                              }))
                        ]),
                        _: 2
                      }, 1024),
                      _createElementVNode("div", {
                        class: _normalizeClass(["status-dot", getStatusClass(plugin)])
                      }, null, 2)
                    ]),
                    _createElementVNode("div", _hoisted_26, [
                      _createElementVNode("div", _hoisted_27, _toDisplayString(plugin.name), 1),
                      _createElementVNode("div", _hoisted_28, "v" + _toDisplayString(plugin.version) + " • " + _toDisplayString(plugin.author), 1)
                    ]),
                    _createElementVNode("div", _hoisted_29, [
                      _createVNode(_component_v_chip, {
                        size: "x-small",
                        color: getStatusColor(plugin),
                        variant: "flat",
                        class: "status-chip"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(getStatusText(plugin)), 1)
                        ]),
                        _: 2
                      }, 1032, ["color"])
                    ])
                  ]),
                  _createElementVNode("div", _hoisted_30, [
                    _createVNode(_component_v_chip, {
                      size: "x-small",
                      color: plugin.type === 'local' ? 'primary' : 'info',
                      variant: "outlined",
                      class: "type-chip"
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode(_toDisplayString(plugin.type === 'local' ? '本地' : '在线'), 1)
                      ]),
                      _: 2
                    }, 1032, ["color"]),
                    (plugin.has_update)
                      ? (_openBlock(), _createBlock(_component_v_chip, {
                          key: 0,
                          size: "x-small",
                          color: "error",
                          variant: "flat",
                          class: "update-chip"
                        }, {
                          default: _withCtx(() => _cache[24] || (_cache[24] = [
                            _createTextVNode(" 有更新 ")
                          ])),
                          _: 1,
                          __: [24]
                        }))
                      : _createCommentVNode("", true)
                  ]),
                  _createElementVNode("div", _hoisted_31, [
                    (plugin.installed)
                      ? (_openBlock(), _createBlock(_component_v_btn, {
                          key: 0,
                          size: "small",
                          variant: "outlined",
                          onClick: $event => (reloadPlugin(plugin)),
                          loading: reloadingPlugins.value.has(plugin.id),
                          class: "control-action reload-action",
                          "prepend-icon": "mdi-reload"
                        }, {
                          default: _withCtx(() => _cache[25] || (_cache[25] = [
                            _createTextVNode(" 重载 ")
                          ])),
                          _: 2,
                          __: [25]
                        }, 1032, ["onClick", "loading"]))
                      : _createCommentVNode("", true),
                    (plugin.installed && plugin.type !== 'local')
                      ? (_openBlock(), _createBlock(_component_v_btn, {
                          key: 1,
                          size: "small",
                          variant: "outlined",
                          onClick: $event => (showReinstallDialog(plugin)),
                          loading: reinstallingPlugins.value.has(plugin.id),
                          class: "control-action reinstall-action",
                          "prepend-icon": "mdi-download"
                        }, {
                          default: _withCtx(() => _cache[26] || (_cache[26] = [
                            _createTextVNode(" 重装 ")
                          ])),
                          _: 2,
                          __: [26]
                        }, 1032, ["onClick", "loading"]))
                      : _createCommentVNode("", true),
                    _createVNode(_component_v_btn, {
                      size: "small",
                      color: "error",
                      variant: "text",
                      onClick: $event => (showActionDialog(plugin)),
                      class: "control-action danger-action",
                      "prepend-icon": plugin.installed ? 'mdi-delete' : 'mdi-folder-remove'
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode(_toDisplayString(plugin.installed ? '卸载' : '清理'), 1)
                      ]),
                      _: 2
                    }, 1032, ["onClick", "prepend-icon"])
                  ]),
                  (reloadingPlugins.value.has(plugin.id) || reinstallingPlugins.value.has(plugin.id))
                    ? (_openBlock(), _createElementBlock("div", _hoisted_32, [
                        _createVNode(_component_v_progress_circular, {
                          indeterminate: "",
                          size: "20",
                          width: "2"
                        }),
                        _createElementVNode("div", _hoisted_33, _toDisplayString(reloadingPlugins.value.has(plugin.id) ? '重载中...' : '重装中...'), 1)
                      ]))
                    : _createCommentVNode("", true)
                ], 2))
              }), 128))
            ])),
    _createVNode(_component_v_dialog, {
      modelValue: reinstallDialog.value,
      "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((reinstallDialog).value = $event)),
      "max-width": "500"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, { class: "dialog-card" }, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, { class: "dialog-header" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  color: "purple",
                  size: "24",
                  class: "mr-2"
                }, {
                  default: _withCtx(() => _cache[27] || (_cache[27] = [
                    _createTextVNode("mdi-download-circle")
                  ])),
                  _: 1,
                  __: [27]
                }),
                _cache[28] || (_cache[28] = _createElementVNode("span", { class: "dialog-title" }, "重装插件", -1))
              ]),
              _: 1,
              __: [28]
            }),
            _createVNode(_component_v_card_text, { class: "dialog-content" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_34, [
                  _createElementVNode("div", _hoisted_35, _toDisplayString(selectedPlugin.value?.name), 1),
                  _createElementVNode("div", _hoisted_36, " 当前版本: " + _toDisplayString(selectedPlugin.value?.version) + " | 作者: " + _toDisplayString(selectedPlugin.value?.author), 1)
                ]),
                _createVNode(_component_v_alert, {
                  type: "info",
                  variant: "tonal",
                  class: "mb-3 info-alert"
                }, {
                  default: _withCtx(() => _cache[29] || (_cache[29] = [
                    _createTextVNode(" 重装将从仓库重新下载最新版本的插件，并保留现有配置 ")
                  ])),
                  _: 1,
                  __: [29]
                }),
                _createElementVNode("div", _hoisted_37, [
                  _createElementVNode("div", _hoisted_38, [
                    _createElementVNode("div", _hoisted_39, [
                      _createVNode(_component_v_icon, {
                        size: "16",
                        class: "mr-1"
                      }, {
                        default: _withCtx(() => _cache[30] || (_cache[30] = [
                          _createTextVNode("mdi-source-repository")
                        ])),
                        _: 1,
                        __: [30]
                      }),
                      _cache[31] || (_cache[31] = _createTextVNode(" 插件仓库 "))
                    ]),
                    _createElementVNode("div", {
                      class: "info-value repo-clickable",
                      onClick: toggleRepoUrlDisplay,
                      title: showFullRepoUrl.value ? '点击显示简洁名称' : '点击显示完整URL'
                    }, [
                      _createTextVNode(_toDisplayString(getRepoDisplayName(onlinePluginInfo.value?.repo_url || selectedPlugin.value?.repo_url)) + " ", 1),
                      _createVNode(_component_v_icon, {
                        size: "12",
                        class: "ml-1"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(showFullRepoUrl.value ? 'mdi-eye-off' : 'mdi-eye'), 1)
                        ]),
                        _: 1
                      })
                    ], 8, _hoisted_40)
                  ]),
                  _createElementVNode("div", _hoisted_41, [
                    _createElementVNode("div", _hoisted_42, [
                      _createVNode(_component_v_icon, {
                        size: "16",
                        class: "mr-1"
                      }, {
                        default: _withCtx(() => _cache[32] || (_cache[32] = [
                          _createTextVNode("mdi-tag")
                        ])),
                        _: 1,
                        __: [32]
                      }),
                      _cache[33] || (_cache[33] = _createTextVNode(" 当前版本 "))
                    ]),
                    _createElementVNode("div", _hoisted_43, "v" + _toDisplayString(selectedPlugin.value?.version), 1)
                  ]),
                  _createElementVNode("div", _hoisted_44, [
                    _createElementVNode("div", _hoisted_45, [
                      _createVNode(_component_v_icon, {
                        size: "16",
                        class: "mr-1"
                      }, {
                        default: _withCtx(() => _cache[34] || (_cache[34] = [
                          _createTextVNode("mdi-cloud-download")
                        ])),
                        _: 1,
                        __: [34]
                      }),
                      _cache[35] || (_cache[35] = _createTextVNode(" 最新版本 "))
                    ]),
                    _createElementVNode("div", _hoisted_46, _toDisplayString(onlinePluginInfo.value?.plugin_version ? `v${onlinePluginInfo.value.plugin_version}` : '获取中...'), 1)
                  ]),
                  _createElementVNode("div", _hoisted_47, [
                    _createElementVNode("div", _hoisted_48, [
                      _createVNode(_component_v_icon, {
                        size: "16",
                        class: "mr-1"
                      }, {
                        default: _withCtx(() => _cache[36] || (_cache[36] = [
                          _createTextVNode("mdi-update")
                        ])),
                        _: 1,
                        __: [36]
                      }),
                      _cache[37] || (_cache[37] = _createTextVNode(" 更新状态 "))
                    ]),
                    _createElementVNode("div", _hoisted_49, [
                      _createVNode(_component_v_chip, {
                        size: "small",
                        color: getUpdateStatusColor(),
                        variant: "flat"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(getUpdateStatusText()), 1)
                        ]),
                        _: 1
                      }, 8, ["color"])
                    ])
                  ])
                ])
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, { class: "dialog-actions" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_btn, {
                  onClick: _cache[3] || (_cache[3] = $event => (reinstallDialog.value = false)),
                  variant: "text"
                }, {
                  default: _withCtx(() => _cache[38] || (_cache[38] = [
                    _createTextVNode("取消")
                  ])),
                  _: 1,
                  __: [38]
                }),
                _createVNode(_component_v_btn, {
                  color: "purple",
                  onClick: confirmReinstall,
                  loading: actionLoading.value,
                  variant: "outlined"
                }, {
                  default: _withCtx(() => _cache[39] || (_cache[39] = [
                    _createTextVNode(" 确认重装 ")
                  ])),
                  _: 1,
                  __: [39]
                }, 8, ["loading"])
              ]),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }, 8, ["modelValue"]),
    _createVNode(_component_v_dialog, {
      modelValue: actionDialog.value,
      "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((actionDialog).value = $event)),
      "max-width": "400"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, { class: "dialog-card" }, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, { class: "dialog-header" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  color: selectedPlugin.value?.installed ? 'error' : 'warning',
                  size: "24",
                  class: "mr-2"
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(selectedPlugin.value?.installed ? 'mdi-delete-alert' : 'mdi-folder-remove'), 1)
                  ]),
                  _: 1
                }, 8, ["color"]),
                _createElementVNode("span", _hoisted_50, _toDisplayString(selectedPlugin.value?.installed ? '卸载模块' : '清理文件'), 1)
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_text, { class: "dialog-content" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_51, [
                  _createElementVNode("div", _hoisted_52, _toDisplayString(selectedPlugin.value?.name), 1),
                  _createElementVNode("div", _hoisted_53, " 版本: " + _toDisplayString(selectedPlugin.value?.version) + " | 作者: " + _toDisplayString(selectedPlugin.value?.author), 1)
                ]),
                _createVNode(_component_v_alert, {
                  type: selectedPlugin.value?.installed ? 'warning' : 'error',
                  variant: "tonal",
                  class: "mb-3 warning-alert"
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(selectedPlugin.value?.installed 
                ? '此操作将卸载插件并可选择清理相关数据' 
                : '此操作将强制删除插件文件夹，无法恢复'), 1)
                  ]),
                  _: 1
                }, 8, ["type"]),
                _createElementVNode("div", _hoisted_54, [
                  _createElementVNode("div", _hoisted_55, [
                    _cache[40] || (_cache[40] = _createElementVNode("span", { class: "option-title" }, "清理选项", -1)),
                    _createVNode(_component_v_btn, {
                      size: "x-small",
                      variant: "text",
                      onClick: toggleAllOptions,
                      class: "select-all-btn"
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode(_toDisplayString(allOptionsSelected.value ? '取消全选' : '全选'), 1)
                      ]),
                      _: 1
                    })
                  ]),
                  _createVNode(_component_v_checkbox, {
                    modelValue: clearConfig.value,
                    "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((clearConfig).value = $event)),
                    label: "清除插件配置",
                    density: "compact",
                    "hide-details": "",
                    class: "option-item"
                  }, null, 8, ["modelValue"]),
                  _createVNode(_component_v_checkbox, {
                    modelValue: clearData.value,
                    "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((clearData).value = $event)),
                    label: "清除插件数据",
                    density: "compact",
                    "hide-details": "",
                    class: "option-item"
                  }, null, 8, ["modelValue"]),
                  (!selectedPlugin.value?.installed)
                    ? (_openBlock(), _createBlock(_component_v_checkbox, {
                        key: 0,
                        modelValue: forceClean.value,
                        "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((forceClean).value = $event)),
                        label: "强制清理文件（危险操作）",
                        density: "compact",
                        "hide-details": "",
                        class: "option-item"
                      }, null, 8, ["modelValue"]))
                    : _createCommentVNode("", true)
                ])
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, { class: "dialog-actions" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_btn, {
                  onClick: _cache[8] || (_cache[8] = $event => (actionDialog.value = false)),
                  variant: "text"
                }, {
                  default: _withCtx(() => _cache[41] || (_cache[41] = [
                    _createTextVNode("取消")
                  ])),
                  _: 1,
                  __: [41]
                }),
                _createVNode(_component_v_btn, {
                  color: selectedPlugin.value?.installed ? 'error' : 'warning',
                  onClick: confirmAction,
                  loading: actionLoading.value,
                  variant: "outlined"
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(" 确认" + _toDisplayString(selectedPlugin.value?.installed ? '卸载' : '清理'), 1)
                  ]),
                  _: 1
                }, 8, ["color", "loading"])
              ]),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }, 8, ["modelValue"])
  ]))
}
}

};
const PageComponent = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-108575a4"]]);

export { _export_sfc as _, PageComponent as default };
