import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-pcqpp-6-.js';

const {resolveComponent:_resolveComponent,createVNode:_createVNode,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,withCtx:_withCtx,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,createElementVNode:_createElementVNode,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass} = await importShared('vue');


const _hoisted_1 = { class: "dashboard-widget" };
const _hoisted_2 = {
  key: 0,
  class: "text-center py-2"
};
const _hoisted_3 = {
  key: 1,
  class: "text-error text-caption d-flex align-center"
};
const _hoisted_4 = { key: 2 };
const _hoisted_5 = {
  key: 3,
  class: "text-caption text-disabled text-center py-3"
};
const _hoisted_6 = { class: "text-caption text-disabled" };

const {ref,reactive,onMounted,onUnmounted,computed} = await importShared('vue');



const _sfc_main = {
  __name: 'Dashboard',
  props: {
  api: { 
    type: Object,  // 修正类型为Object
    required: true,
  },
  config: { // Widget display config (title, border etc.)
    type: Object,
    default: () => ({ attrs: {} }),
  },
  allowRefresh: {
    type: Boolean,
    default: false,
  },
  refreshInterval: {
    type: Number,
    default: 0, // 0 means no auto-refresh
  },
},
  setup(__props) {

const props = __props;

const loading = ref(false);
const error = ref(null);
const initialDataLoaded = ref(false);
const summaryData = reactive({ 
    enabled: null,
    rows: 300,
    last_cleaned_lines: null, 
    last_run_time: null,
    next_run_time: null,
    cleaning_history: [], 
});
const lastRefreshedTimestamp = ref(null);

let refreshTimer = null;

const getPluginId = () => {
  return "LogsClean";  // 使用固定的插件ID
};

async function fetchSummary() {
  loading.value = true;
  error.value = null;
  
  try {
    // 获取插件ID
    const pluginId = getPluginId();
    
    // 使用props.api对象调用API
    const data = await props.api.get(`plugin/${pluginId}/status`);
    
    if (data) {
      // 更新数据
      summaryData.enabled = data.enabled;
      summaryData.rows = data.rows;
      summaryData.next_run_time = data.next_run_time;
      summaryData.cleaning_history = data.cleaning_history || [];
      
      // 从历史记录中提取最近的清理数据
      if (summaryData.cleaning_history.length > 0) {
        const lastRecord = summaryData.cleaning_history[0];
        summaryData.last_cleaned_lines = lastRecord.total_lines_cleaned;
        summaryData.last_run_time = lastRecord.timestamp;
      } else {
        summaryData.last_cleaned_lines = null;
        summaryData.last_run_time = null;
      }
      
      initialDataLoaded.value = true;
      lastRefreshedTimestamp.value = Date.now();
    } else {
      throw new Error('仪表盘数据响应无效');
    }
  } catch (err) {
    console.error('获取仪表盘数据失败:', err);
    error.value = err.message || '获取仪表盘数据失败';
  } finally {
    loading.value = false;
  }
}

const lastRefreshedTimeDisplay = computed(() => {
  if (!lastRefreshedTimestamp.value) return '';
  return `上次更新: ${new Date(lastRefreshedTimestamp.value).toLocaleTimeString()}`;
});

const getLastCleanedLinesText = () => {
    if (summaryData.last_cleaned_lines === null || summaryData.last_cleaned_lines === undefined) {
      return '无数据';
    }
    return `${summaryData.last_cleaned_lines} 行`;
};

const getLastRunTimeText = () => {
    return summaryData.last_run_time || '无数据';
};

onMounted(() => {
  fetchSummary();
  
  // 设置自动刷新
  if (props.allowRefresh && props.refreshInterval > 0) {
    refreshTimer = setInterval(fetchSummary, props.refreshInterval * 1000);
  }
});

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
});

return (_ctx, _cache) => {
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_card_subtitle = _resolveComponent("v-card-subtitle");
  const _component_v_card_item = _resolveComponent("v-card-item");
  const _component_v_progress_circular = _resolveComponent("v-progress-circular");
  const _component_v_list_item_title = _resolveComponent("v-list-item-title");
  const _component_v_list_item = _resolveComponent("v-list-item");
  const _component_v_divider = _resolveComponent("v-divider");
  const _component_v_list = _resolveComponent("v-list");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_card_actions = _resolveComponent("v-card-actions");
  const _component_v_card = _resolveComponent("v-card");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_v_card, {
      flat: !props.config?.attrs?.border,
      loading: loading.value,
      class: "fill-height d-flex flex-column"
    }, {
      default: _withCtx(() => [
        (props.config?.attrs?.title || props.config?.attrs?.subtitle)
          ? (_openBlock(), _createBlock(_component_v_card_item, { key: 0 }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card_title, { class: "d-flex align-center" }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_icon, {
                      icon: "mdi-broom",
                      class: "mr-2",
                      color: "primary"
                    }),
                    _createTextVNode(" " + _toDisplayString(props.config?.attrs?.title || '日志清理概览'), 1)
                  ]),
                  _: 1
                }),
                (props.config?.attrs?.subtitle)
                  ? (_openBlock(), _createBlock(_component_v_card_subtitle, { key: 0 }, {
                      default: _withCtx(() => [
                        _createTextVNode(_toDisplayString(props.config.attrs.subtitle), 1)
                      ]),
                      _: 1
                    }))
                  : _createCommentVNode("", true)
              ]),
              _: 1
            }))
          : _createCommentVNode("", true),
        _createVNode(_component_v_card_text, { class: "flex-grow-1 pa-3" }, {
          default: _withCtx(() => [
            (loading.value && !initialDataLoaded.value)
              ? (_openBlock(), _createElementBlock("div", _hoisted_2, [
                  _createVNode(_component_v_progress_circular, {
                    indeterminate: "",
                    color: "primary",
                    size: "small"
                  }),
                  _cache[0] || (_cache[0] = _createElementVNode("div", { class: "text-caption mt-2" }, "加载中...", -1))
                ]))
              : (error.value)
                ? (_openBlock(), _createElementBlock("div", _hoisted_3, [
                    _createVNode(_component_v_icon, {
                      size: "small",
                      color: "error",
                      class: "mr-2"
                    }, {
                      default: _withCtx(() => _cache[1] || (_cache[1] = [
                        _createTextVNode("mdi-alert-circle-outline")
                      ])),
                      _: 1
                    }),
                    _createTextVNode(" " + _toDisplayString(error.value || '数据加载失败'), 1)
                  ]))
                : (initialDataLoaded.value && summaryData)
                  ? (_openBlock(), _createElementBlock("div", _hoisted_4, [
                      _createVNode(_component_v_list, {
                        density: "compact",
                        class: "py-0",
                        nav: ""
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_list_item, { class: "px-2" }, {
                            prepend: _withCtx(() => [
                              _createVNode(_component_v_icon, {
                                size: "small",
                                color: summaryData.enabled ? 'success' : 'grey',
                                class: "mr-2"
                              }, {
                                default: _withCtx(() => _cache[2] || (_cache[2] = [
                                  _createTextVNode(" mdi-power ")
                                ])),
                                _: 1
                              }, 8, ["color"])
                            ]),
                            default: _withCtx(() => [
                              _createVNode(_component_v_list_item_title, { class: "text-caption" }, {
                                default: _withCtx(() => [
                                  _cache[3] || (_cache[3] = _createTextVNode(" 插件状态: ")),
                                  _createElementVNode("span", {
                                    class: _normalizeClass(summaryData.enabled ? 'text-success' : 'text-grey')
                                  }, _toDisplayString(summaryData.enabled ? '已启用' : '已禁用'), 3)
                                ]),
                                _: 1
                              })
                            ]),
                            _: 1
                          }),
                          _createVNode(_component_v_divider, { class: "my-1" }),
                          _createVNode(_component_v_list_item, { class: "px-2" }, {
                            prepend: _withCtx(() => [
                              _createVNode(_component_v_icon, {
                                size: "small",
                                color: "primary",
                                class: "mr-2"
                              }, {
                                default: _withCtx(() => _cache[4] || (_cache[4] = [
                                  _createTextVNode("mdi-calendar-clock")
                                ])),
                                _: 1
                              })
                            ]),
                            default: _withCtx(() => [
                              _createVNode(_component_v_list_item_title, { class: "text-caption" }, {
                                default: _withCtx(() => [
                                  _createTextVNode(" 上次清理: " + _toDisplayString(getLastRunTimeText()), 1)
                                ]),
                                _: 1
                              })
                            ]),
                            _: 1
                          }),
                          _createVNode(_component_v_list_item, { class: "px-2" }, {
                            prepend: _withCtx(() => [
                              _createVNode(_component_v_icon, {
                                size: "small",
                                color: "info",
                                class: "mr-2"
                              }, {
                                default: _withCtx(() => _cache[5] || (_cache[5] = [
                                  _createTextVNode("mdi-counter")
                                ])),
                                _: 1
                              })
                            ]),
                            default: _withCtx(() => [
                              _createVNode(_component_v_list_item_title, { class: "text-caption" }, {
                                default: _withCtx(() => [
                                  _createTextVNode(" 最近清理: " + _toDisplayString(getLastCleanedLinesText()), 1)
                                ]),
                                _: 1
                              })
                            ]),
                            _: 1
                          }),
                          (summaryData.enabled)
                            ? (_openBlock(), _createBlock(_component_v_list_item, {
                                key: 0,
                                class: "px-2"
                              }, {
                                prepend: _withCtx(() => [
                                  _createVNode(_component_v_icon, {
                                    size: "small",
                                    color: "amber-darken-2",
                                    class: "mr-2"
                                  }, {
                                    default: _withCtx(() => _cache[6] || (_cache[6] = [
                                      _createTextVNode("mdi-timer-outline")
                                    ])),
                                    _: 1
                                  })
                                ]),
                                default: _withCtx(() => [
                                  _createVNode(_component_v_list_item_title, { class: "text-caption" }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(" 下次运行: " + _toDisplayString(summaryData.next_run_time || '未知'), 1)
                                    ]),
                                    _: 1
                                  })
                                ]),
                                _: 1
                              }))
                            : _createCommentVNode("", true),
                          _createVNode(_component_v_list_item, { class: "px-2" }, {
                            prepend: _withCtx(() => [
                              _createVNode(_component_v_icon, {
                                size: "small",
                                color: "deep-purple",
                                class: "mr-2"
                              }, {
                                default: _withCtx(() => _cache[7] || (_cache[7] = [
                                  _createTextVNode("mdi-cog-outline")
                                ])),
                                _: 1
                              })
                            ]),
                            default: _withCtx(() => [
                              _createVNode(_component_v_list_item_title, { class: "text-caption" }, {
                                default: _withCtx(() => [
                                  _createTextVNode(" 保留行数: " + _toDisplayString(summaryData.rows || 300) + " 行 ", 1)
                                ]),
                                _: 1
                              })
                            ]),
                            _: 1
                          })
                        ]),
                        _: 1
                      })
                    ]))
                  : (_openBlock(), _createElementBlock("div", _hoisted_5, [
                      _createVNode(_component_v_icon, {
                        icon: "mdi-information-outline",
                        class: "mb-2"
                      }),
                      _cache[8] || (_cache[8] = _createElementVNode("div", null, "暂无数据，请检查插件配置", -1))
                    ]))
          ]),
          _: 1
        }),
        (props.allowRefresh)
          ? (_openBlock(), _createBlock(_component_v_divider, { key: 1 }))
          : _createCommentVNode("", true),
        (props.allowRefresh)
          ? (_openBlock(), _createBlock(_component_v_card_actions, {
              key: 2,
              class: "px-3 py-1"
            }, {
              default: _withCtx(() => [
                _createElementVNode("span", _hoisted_6, _toDisplayString(lastRefreshedTimeDisplay.value), 1),
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  icon: "",
                  variant: "text",
                  size: "small",
                  onClick: fetchSummary,
                  loading: loading.value
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_icon, { size: "small" }, {
                      default: _withCtx(() => _cache[9] || (_cache[9] = [
                        _createTextVNode("mdi-refresh")
                      ])),
                      _: 1
                    })
                  ]),
                  _: 1
                }, 8, ["loading"])
              ]),
              _: 1
            }))
          : _createCommentVNode("", true)
      ]),
      _: 1
    }, 8, ["flat", "loading"])
  ]))
}
}

};
const DashboardComponent = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-6a0ff1b0"]]);

export { DashboardComponent as default };
