import { importShared } from './__federation_fn_import-054b33c3.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_f579374d_lang = '';

const {defineComponent,ref,reactive,toRefs,computed,watch,onMounted} = await importShared('vue');


const _sfc_main = defineComponent({
  name: 'Config',
  
  props: {
    api: {
      type: [Object, Function],
      required: true
    },
    initialConfig: {
      type: Object,
      default: () => ({})
    }
  },
  
  emits: ['switch', 'close', 'save'],
  
  setup(props, { emit }) {
    // 状态
    const state = reactive({
      error: null,
      successMessage: null,
      saving: false,
      isFormValid: true,
      initialConfigLoaded: false,
      editableConfig: {
        enable: false,
        notify: true,
        cron: '0 4 * * *',
        only_when_no_download: true,
        monitor_paths: [],
        empty_dir_cleanup: true,
        small_dir_cleanup: false,
        small_dir_max_size: 10,
        size_reduction_cleanup: false,
        size_reduction_threshold: 80,
        scan_interval: 24,
        exclude_dirs: []
      },
      originalConfig: null,
      
      // 路径选择器相关
      showPathSelector: false,
      showExcludePathSelector: false,
      currentPath: '',
      currentPathIndex: -1, // 当前编辑的路径索引
      currentExcludePathIndex: -1, // 当前编辑的排除目录索引
      pathItems: [],
      pathSelectorLoading: false,
      pathSelectorError: null,
      
      // 下载器状态相关
      downloaders: [],
      downloadersLoading: false
    });
    
    // 初始化配置
    const initConfig = () => {
      if (props.initialConfig) {
        // 深拷贝配置对象防止引用问题
        state.editableConfig = JSON.parse(JSON.stringify(props.initialConfig));
        state.originalConfig = JSON.parse(JSON.stringify(props.initialConfig));
        
        // 确保exclude_dirs是数组
        if (!Array.isArray(state.editableConfig.exclude_dirs)) {
          state.editableConfig.exclude_dirs = [];
        }
        
        // 确保monitor_paths是数组
        if (!Array.isArray(state.editableConfig.monitor_paths)) {
          state.editableConfig.monitor_paths = [];
        }
        
        state.initialConfigLoaded = true;
        
        // 如果启用了仅在无下载任务时执行，获取下载器状态
        if (state.editableConfig.only_when_no_download) {
          loadDownloaderStatus();
        }
      }
    };
    
    // 加载配置
    const loadConfig = async () => {
      try {
        state.error = null;
        const response = await props.api.get('plugin/TrashClean/config');
        if (response) {
          // 深拷贝配置对象以防引用问题
          state.editableConfig = JSON.parse(JSON.stringify(response));
          state.originalConfig = JSON.parse(JSON.stringify(response));
          
          // 确保exclude_dirs是数组
          if (!Array.isArray(state.editableConfig.exclude_dirs)) {
            state.editableConfig.exclude_dirs = [];
          }
          
          // 确保monitor_paths是数组
          if (!Array.isArray(state.editableConfig.monitor_paths)) {
            state.editableConfig.monitor_paths = [];
          }
          
          state.initialConfigLoaded = true;
          
          // 如果启用了仅在无下载任务时执行，获取下载器状态
          if (state.editableConfig.only_when_no_download) {
            loadDownloaderStatus();
          }
        }
      } catch (error) {
        state.error = `加载配置失败: ${error.message || error}`;
        console.error('加载配置失败:', error);
      }
    };
    
    // 保存配置
    const saveConfig = async () => {
      try {
        state.error = null;
        state.successMessage = null;
        state.saving = true;
        
        // 确保配置对象中包含所有必要的字段
        const configToSave = {
          enable: state.editableConfig.enable,
          notify: state.editableConfig.notify,
          cron: state.editableConfig.cron,
          only_when_no_download: state.editableConfig.only_when_no_download,
          monitor_paths: state.editableConfig.monitor_paths.filter(path => path && path.trim()),
          empty_dir_cleanup: state.editableConfig.empty_dir_cleanup,
          small_dir_cleanup: state.editableConfig.small_dir_cleanup,
          small_dir_max_size: parseInt(state.editableConfig.small_dir_max_size) || 10,
          size_reduction_cleanup: state.editableConfig.size_reduction_cleanup,
          size_reduction_threshold: parseInt(state.editableConfig.size_reduction_threshold) || 80,
          scan_interval: parseInt(state.editableConfig.scan_interval) || 24,
          exclude_dirs: state.editableConfig.exclude_dirs || []
        };
        
        // 验证必填字段
        if (configToSave.small_dir_cleanup && (!configToSave.small_dir_max_size || configToSave.small_dir_max_size <= 0)) {
          state.error = "小体积目录最大值必须大于0";
          state.saving = false;
          return;
        }
        
        if (configToSave.size_reduction_cleanup && (!configToSave.size_reduction_threshold || configToSave.size_reduction_threshold <= 0)) {
          state.error = "体积减少阈值必须大于0";
          state.saving = false;
          return;
        }
        
        // 向父组件发送保存事件
        emit('save', configToSave);
        
        const response = await props.api.post('plugin/TrashClean/config', configToSave);
        
        if (response && response.status === 'success') {
          state.successMessage = '配置保存成功';
          // 更新原始配置
          state.originalConfig = JSON.parse(JSON.stringify(configToSave));
          state.editableConfig = JSON.parse(JSON.stringify(configToSave));
          
          // 如果启用了仅在无下载任务时执行，获取下载器状态
          if (state.editableConfig.only_when_no_download) {
            loadDownloaderStatus();
          }
          
          // 3秒后清除成功消息
          setTimeout(() => {
            state.successMessage = null;
          }, 3000);
        } else {
          state.error = response?.message || '配置保存失败';
        }
      } catch (error) {
        state.error = `配置保存失败: ${error.message || error}`;
        console.error('配置保存失败:', error);
      } finally {
        state.saving = false;
      }
    };
    
    // 重置配置
    const resetConfig = () => {
      if (state.originalConfig) {
        state.editableConfig = JSON.parse(JSON.stringify(state.originalConfig));
      }
    };
    
    // 移除排除目录
    const removeExcludeDir = (index) => {
      state.editableConfig.exclude_dirs.splice(index, 1);
    };
    
    // 添加空的监控路径
    const addEmptyPath = () => {
      state.editableConfig.monitor_paths.push('');
    };
    
    // 添加监控路径
    const addPath = (path) => {
      if (path && !state.editableConfig.monitor_paths.includes(path)) {
        state.editableConfig.monitor_paths.push(path);
      }
    };
    
    // 移除监控路径
    const removePath = (index) => {
      state.editableConfig.monitor_paths.splice(index, 1);
    };
    
    // 设置监控路径
    const setPath = (index, path) => {
      if (index >= 0 && index < state.editableConfig.monitor_paths.length) {
        state.editableConfig.monitor_paths[index] = path;
      }
    };
    
    // 加载下载器状态
    const loadDownloaderStatus = async () => {
      try {
        state.downloadersLoading = true;
        // 获取所有下载器及其活动状态
        const response = await props.api.get('plugin/TrashClean/downloaders');
        if (response && Array.isArray(response)) {
          state.downloaders = response;
        } else {
          state.downloaders = [];
        }
      } catch (error) {
        console.error('加载下载器状态失败:', error);
        state.downloaders = [];
      } finally {
        state.downloadersLoading = false;
      }
    };
    
    // 路径选择器相关
    const browseDirectory = async (path = null) => {
      try {
        state.pathSelectorLoading = true;
        state.pathSelectorError = null;
        
        // 使用MoviePilot的文件管理API
        const response = await props.api.post('storage/list', {
          path: path || '/',
          type: 'share', // 使用默认的share类型
          flag: 'ROOT'
        });
        
        if (response && Array.isArray(response)) {
          state.currentPath = path || '/';
          state.pathItems = response.map(item => ({
            name: item.name,
            path: item.path,
            type: item.type === 'dir' ? 'dir' : 'file'
          }));
          
          // 添加上级目录（如果不是根目录）
          if (path && path !== '/') {
            const parentPath = path.split('/').slice(0, -1).join('/') || '/';
            state.pathItems.unshift({
              name: '..',
              path: parentPath,
              type: 'parent'
            });
          }
        } else {
          state.pathSelectorError = '浏览目录失败：无效响应';
          state.pathItems = [];
        }
      } catch (error) {
        state.pathSelectorError = `浏览目录失败: ${error.message || error}`;
        state.pathItems = [];
        console.error('浏览目录失败:', error);
      } finally {
        state.pathSelectorLoading = false;
      }
    };
    
    // 导航到指定目录
    const navigateTo = (item) => {
      if (item && (item.type === 'dir' || item.type === 'drive' || item.type === 'parent')) {
        browseDirectory(item.path);
      }
    };
    
    // 选择当前目录作为监控路径
    const selectCurrentPath = () => {
      if (state.currentPath) {
        if (state.currentPathIndex >= 0) {
          // 更新现有路径
          setPath(state.currentPathIndex, state.currentPath);
        } else {
          // 添加新路径
          addPath(state.currentPath);
        }
        state.showPathSelector = false;
        state.currentPathIndex = -1;
      }
    };
    
    // 选择当前目录作为排除目录
    const selectExcludePath = () => {
      if (state.currentPath) {
        // 添加到排除目录
        if (!state.editableConfig.exclude_dirs) {
          state.editableConfig.exclude_dirs = [];
        }
        
        if (state.currentExcludePathIndex >= 0) {
          // 更新现有的排除目录
          state.editableConfig.exclude_dirs[state.currentExcludePathIndex] = state.currentPath;
        } else if (!state.editableConfig.exclude_dirs.includes(state.currentPath)) {
          // 添加新的排除目录
          state.editableConfig.exclude_dirs.push(state.currentPath);
        }
        
        state.currentExcludePathIndex = -1;
        state.showExcludePathSelector = false;
      }
    };
    
    // 添加空的排除目录
    const addEmptyExcludeDir = () => {
      if (!state.editableConfig.exclude_dirs) {
        state.editableConfig.exclude_dirs = [];
      }
      state.editableConfig.exclude_dirs.push('');
    };
    
    // 监听路径选择器的显示状态
    watch(() => state.showPathSelector, (newVal) => {
      if (newVal) {
        // 显示路径选择器时，加载目录列表
        browseDirectory();
      }
    });
    
    // 监听排除目录路径选择器的显示状态
    watch(() => state.showExcludePathSelector, (newVal) => {
      if (newVal) {
        // 显示排除目录路径选择器时，加载目录列表
        browseDirectory();
      }
    });
    
    // 监听只在无下载任务时执行开关
    watch(() => state.editableConfig.only_when_no_download, (newVal) => {
      if (newVal) {
        loadDownloaderStatus();
      }
    });
    
    // 组件创建时，初始化配置
    onMounted(() => {
      initConfig();
      
      // 如果没有初始配置，尝试加载
      if (!Object.keys(props.initialConfig || {}).length) {
        loadConfig();
      }
    });
    
    return {
      ...toRefs(state),
      saveConfig,
      resetConfig,
      removeExcludeDir,
      addEmptyPath,
      addPath,
      removePath,
      setPath,
      loadDownloaderStatus,
      browseDirectory,
      navigateTo,
      selectCurrentPath,
      selectExcludePath,
      addEmptyExcludeDir,
      emit
    };
  }
});

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,withCtx:_withCtx,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,withModifiers:_withModifiers} = await importShared('vue');


const _hoisted_1 = { class: "plugin-config" };
const _hoisted_2 = { class: "setting-item d-flex align-center py-2" };
const _hoisted_3 = { class: "setting-content flex-grow-1" };
const _hoisted_4 = { class: "d-flex justify-space-between align-center" };
const _hoisted_5 = { class: "setting-item d-flex align-center py-2" };
const _hoisted_6 = { class: "setting-content flex-grow-1" };
const _hoisted_7 = { class: "d-flex justify-space-between align-center" };
const _hoisted_8 = { class: "setting-item d-flex align-center py-2" };
const _hoisted_9 = { class: "setting-content flex-grow-1" };
const _hoisted_10 = { class: "d-flex justify-space-between align-center" };
const _hoisted_11 = { class: "mb-2" };
const _hoisted_12 = { class: "mt-3" };
const _hoisted_13 = { class: "ml-2 mt-1 pa-2 rounded bg-blue-lighten-5" };
const _hoisted_14 = { class: "d-flex align-center" };
const _hoisted_15 = { class: "d-flex align-center" };
const _hoisted_16 = { class: "d-flex align-items-center" };
const _hoisted_17 = { class: "d-flex justify-end mt-2" };
const _hoisted_18 = { class: "setting-item d-flex align-center py-2" };
const _hoisted_19 = { class: "setting-content flex-grow-1" };
const _hoisted_20 = { class: "d-flex justify-space-between align-center" };
const _hoisted_21 = { class: "setting-item d-flex align-center py-2" };
const _hoisted_22 = { class: "setting-content flex-grow-1" };
const _hoisted_23 = { class: "d-flex justify-space-between align-center" };
const _hoisted_24 = {
  key: 0,
  class: "ml-6 mt-1"
};
const _hoisted_25 = { class: "setting-item d-flex align-center py-2" };
const _hoisted_26 = { class: "setting-content flex-grow-1" };
const _hoisted_27 = { class: "d-flex justify-space-between align-center" };
const _hoisted_28 = {
  key: 0,
  class: "ml-6 mt-1"
};
const _hoisted_29 = { class: "mt-2 pa-2 rounded bg-error-lighten-5" };
const _hoisted_30 = { class: "d-flex" };
const _hoisted_31 = { class: "d-flex" };
const _hoisted_32 = { class: "text-caption" };
const _hoisted_33 = { class: "d-flex flex-wrap ml-1" };
const _hoisted_34 = { class: "mr-3 mb-1" };
const _hoisted_35 = { class: "mr-3 mb-1" };
const _hoisted_36 = { class: "mb-1" };
const _hoisted_37 = { class: "d-flex align-center" };
const _hoisted_38 = { class: "d-flex align-items-center" };
const _hoisted_39 = { class: "d-flex justify-end mt-2" };
const _hoisted_40 = {
  key: 0,
  class: "d-flex justify-center my-3"
};
const _hoisted_41 = { key: 1 };
const _hoisted_42 = {
  key: 0,
  class: "d-flex justify-center my-3"
};
const _hoisted_43 = { key: 1 };

function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");
  const _component_VCronField = _resolveComponent("VCronField");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_form = _resolveComponent("v-form");
  const _component_v_divider = _resolveComponent("v-divider");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_card_actions = _resolveComponent("v-card-actions");
  const _component_v_progress_circular = _resolveComponent("v-progress-circular");
  const _component_v_list_item_title = _resolveComponent("v-list-item-title");
  const _component_v_list_item = _resolveComponent("v-list-item");
  const _component_v_list = _resolveComponent("v-list");
  const _component_v_dialog = _resolveComponent("v-dialog");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_v_card, {
      flat: "",
      class: "rounded border"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card_title, { class: "text-subtitle-1 d-flex align-center px-3 py-2 bg-primary-lighten-5" }, {
          default: _withCtx(() => [
            _createVNode(_component_v_icon, {
              icon: "mdi-cog",
              class: "mr-2",
              color: "primary",
              size: "small"
            }),
            _cache[21] || (_cache[21] = _createElementVNode("span", null, "垃圾文件清理配置", -1))
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
          default: _withCtx(() => [
            (_ctx.error)
              ? (_openBlock(), _createBlock(_component_v_alert, {
                  key: 0,
                  type: "error",
                  density: "compact",
                  class: "mb-2 text-caption",
                  variant: "tonal",
                  closable: ""
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(_ctx.error), 1)
                  ]),
                  _: 1
                }))
              : _createCommentVNode("", true),
            (_ctx.successMessage)
              ? (_openBlock(), _createBlock(_component_v_alert, {
                  key: 1,
                  type: "success",
                  density: "compact",
                  class: "mb-2 text-caption",
                  variant: "tonal",
                  closable: ""
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(_ctx.successMessage), 1)
                  ]),
                  _: 1
                }))
              : _createCommentVNode("", true),
            _createVNode(_component_v_form, {
              ref: "form",
              modelValue: _ctx.isFormValid,
              "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((_ctx.isFormValid) = $event)),
              onSubmit: _withModifiers(_ctx.saveConfig, ["prevent"])
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card, {
                  flat: "",
                  class: "rounded mb-3 border config-card"
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_title, { class: "text-caption d-flex align-center px-3 py-2 bg-primary-lighten-5" }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_icon, {
                          icon: "mdi-tune",
                          class: "mr-2",
                          color: "primary",
                          size: "small"
                        }),
                        _cache[22] || (_cache[22] = _createElementVNode("span", null, "基本设置", -1))
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_row, null, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_col, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_2, [
                                  _createVNode(_component_v_icon, {
                                    icon: "mdi-power",
                                    size: "small",
                                    color: _ctx.editableConfig.enable ? 'success' : 'grey',
                                    class: "mr-3"
                                  }, null, 8, ["color"]),
                                  _createElementVNode("div", _hoisted_3, [
                                    _createElementVNode("div", _hoisted_4, [
                                      _cache[23] || (_cache[23] = _createElementVNode("div", null, [
                                        _createElementVNode("div", { class: "text-subtitle-2" }, "启用插件"),
                                        _createElementVNode("div", { class: "text-caption text-grey" }, "是否启用垃圾文件自动清理功能")
                                      ], -1)),
                                      _createVNode(_component_v_switch, {
                                        modelValue: _ctx.editableConfig.enable,
                                        "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((_ctx.editableConfig.enable) = $event)),
                                        color: "primary",
                                        inset: "",
                                        disabled: _ctx.saving,
                                        density: "compact",
                                        "hide-details": "",
                                        class: "small-switch"
                                      }, null, 8, ["modelValue", "disabled"])
                                    ])
                                  ])
                                ])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_v_col, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_5, [
                                  _createVNode(_component_v_icon, {
                                    icon: "mdi-bell",
                                    size: "small",
                                    color: _ctx.editableConfig.notify ? 'info' : 'grey',
                                    class: "mr-3"
                                  }, null, 8, ["color"]),
                                  _createElementVNode("div", _hoisted_6, [
                                    _createElementVNode("div", _hoisted_7, [
                                      _cache[24] || (_cache[24] = _createElementVNode("div", null, [
                                        _createElementVNode("div", { class: "text-subtitle-2" }, "启用通知"),
                                        _createElementVNode("div", { class: "text-caption text-grey" }, "清理完成后发送站内消息通知")
                                      ], -1)),
                                      _createVNode(_component_v_switch, {
                                        modelValue: _ctx.editableConfig.notify,
                                        "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((_ctx.editableConfig.notify) = $event)),
                                        color: "info",
                                        inset: "",
                                        disabled: _ctx.saving,
                                        density: "compact",
                                        "hide-details": "",
                                        class: "small-switch"
                                      }, null, 8, ["modelValue", "disabled"])
                                    ])
                                  ])
                                ])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_v_row, null, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_col, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_8, [
                                  _createVNode(_component_v_icon, {
                                    icon: "mdi-download",
                                    size: "small",
                                    color: _ctx.editableConfig.only_when_no_download ? 'warning' : 'grey',
                                    class: "mr-3"
                                  }, null, 8, ["color"]),
                                  _createElementVNode("div", _hoisted_9, [
                                    _createElementVNode("div", _hoisted_10, [
                                      _cache[25] || (_cache[25] = _createElementVNode("div", null, [
                                        _createElementVNode("div", { class: "text-subtitle-2" }, "仅在无下载任务时执行"),
                                        _createElementVNode("div", { class: "text-caption text-grey" }, "避免在下载器繁忙时清理文件")
                                      ], -1)),
                                      _createVNode(_component_v_switch, {
                                        modelValue: _ctx.editableConfig.only_when_no_download,
                                        "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((_ctx.editableConfig.only_when_no_download) = $event)),
                                        color: "warning",
                                        inset: "",
                                        disabled: _ctx.saving,
                                        density: "compact",
                                        "hide-details": "",
                                        class: "small-switch"
                                      }, null, 8, ["modelValue", "disabled"])
                                    ])
                                  ])
                                ])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_card, {
                  flat: "",
                  class: "rounded mb-3 border config-card"
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_title, { class: "text-caption d-flex align-center px-3 py-2 bg-primary-lighten-5" }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_icon, {
                          icon: "mdi-clock-time-five",
                          class: "mr-2",
                          color: "primary",
                          size: "small"
                        }),
                        _cache[26] || (_cache[26] = _createElementVNode("span", null, "定时任务设置", -1))
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                      default: _withCtx(() => [
                        _createElementVNode("div", _hoisted_11, [
                          _createVNode(_component_VCronField, {
                            modelValue: _ctx.editableConfig.cron,
                            "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((_ctx.editableConfig.cron) = $event)),
                            label: "CRON表达式",
                            hint: "设置垃圾文件清理的执行周期，如：0 4 * * * (每天凌晨4点)",
                            "persistent-hint": "",
                            density: "compact"
                          }, null, 8, ["modelValue"])
                        ]),
                        _createElementVNode("div", _hoisted_12, [
                          _createVNode(_component_v_text_field, {
                            modelValue: _ctx.editableConfig.scan_interval,
                            "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((_ctx.editableConfig.scan_interval) = $event)),
                            modelModifiers: { number: true },
                            label: "监控扫描间隔(小时)",
                            type: "number",
                            variant: "outlined",
                            min: 1,
                            max: 168,
                            rules: [v => v === null || v === '' || (Number.isInteger(Number(v)) && Number(v) >= 1 && Number(v) <= 168) || '必须是1-168之间的整数'],
                            hint: "目录大小监控的间隔时间，用于判断体积减少阈值",
                            "persistent-hint": "",
                            disabled: _ctx.saving,
                            density: "compact"
                          }, null, 8, ["modelValue", "rules", "disabled"]),
                          _createElementVNode("div", _hoisted_13, [
                            _createElementVNode("div", _hoisted_14, [
                              _createVNode(_component_v_icon, {
                                icon: "mdi-information-outline",
                                size: "small",
                                color: "info",
                                class: "mr-2"
                              }),
                              _cache[27] || (_cache[27] = _createElementVNode("span", { class: "text-caption" }, " 扫描间隔是系统记录目录大小变化的时间周期，对\"体积减少目录\"功能至关重要。系统会在每次清理时更新目录大小记录，当下次清理时发现目录大小减少超过阈值，就会判定为可清理目录。建议设置为与清理任务执行时间相同或更长。 ", -1))
                            ])
                          ])
                        ])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_card, {
                  flat: "",
                  class: "rounded mb-3 border config-card"
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_title, { class: "text-caption d-flex align-center justify-space-between px-3 py-2 bg-primary-lighten-5" }, {
                      default: _withCtx(() => [
                        _createElementVNode("div", _hoisted_15, [
                          _createVNode(_component_v_icon, {
                            icon: "mdi-folder-search",
                            class: "mr-2",
                            color: "primary",
                            size: "small"
                          }),
                          _cache[28] || (_cache[28] = _createElementVNode("span", null, "监控路径设置", -1))
                        ]),
                        _createVNode(_component_v_btn, {
                          size: "x-small",
                          color: "primary",
                          variant: "text",
                          "prepend-icon": "mdi-folder-plus",
                          onClick: _cache[5] || (_cache[5] = $event => (_ctx.showPathSelector = true)),
                          disabled: _ctx.saving
                        }, {
                          default: _withCtx(() => _cache[29] || (_cache[29] = [
                            _createTextVNode(" 添加路径 ")
                          ])),
                          _: 1
                        }, 8, ["disabled"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                      default: _withCtx(() => [
                        (!_ctx.editableConfig.monitor_paths.length)
                          ? (_openBlock(), _createBlock(_component_v_alert, {
                              key: 0,
                              density: "compact",
                              type: "warning",
                              variant: "tonal",
                              class: "text-caption"
                            }, {
                              default: _withCtx(() => _cache[30] || (_cache[30] = [
                                _createTextVNode(" 未设置任何监控路径，请点击\"添加路径\"按钮添加需要清理的目录 ")
                              ])),
                              _: 1
                            }))
                          : _createCommentVNode("", true),
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(_ctx.editableConfig.monitor_paths, (path, index) => {
                          return (_openBlock(), _createElementBlock("div", {
                            key: index,
                            class: "mb-2"
                          }, [
                            _createElementVNode("div", _hoisted_16, [
                              _createVNode(_component_v_text_field, {
                                modelValue: _ctx.editableConfig.monitor_paths[index],
                                "onUpdate:modelValue": $event => ((_ctx.editableConfig.monitor_paths[index]) = $event),
                                label: "监控路径",
                                hint: "文件夹路径",
                                "persistent-hint": "",
                                density: "compact",
                                variant: "outlined",
                                class: "flex-grow-1"
                              }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                              _createVNode(_component_v_btn, {
                                size: "x-small",
                                color: "error",
                                variant: "text",
                                icon: "",
                                onClick: $event => (_ctx.removePath(index)),
                                disabled: _ctx.saving,
                                class: "ml-2"
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_v_icon, {
                                    icon: "mdi-delete",
                                    size: "small"
                                  })
                                ]),
                                _: 2
                              }, 1032, ["onClick", "disabled"]),
                              _createVNode(_component_v_btn, {
                                size: "x-small",
                                color: "primary",
                                variant: "text",
                                icon: "",
                                onClick: $event => {_ctx.showPathSelector = true; _ctx.currentPathIndex = index;},
                                disabled: _ctx.saving,
                                class: "ml-2"
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_v_icon, {
                                    icon: "mdi-folder-search",
                                    size: "small"
                                  })
                                ]),
                                _: 2
                              }, 1032, ["onClick", "disabled"])
                            ])
                          ]))
                        }), 128)),
                        _createElementVNode("div", _hoisted_17, [
                          _createVNode(_component_v_btn, {
                            size: "small",
                            color: "primary",
                            variant: "text",
                            "prepend-icon": "mdi-folder-plus",
                            onClick: _ctx.addEmptyPath,
                            disabled: _ctx.saving
                          }, {
                            default: _withCtx(() => _cache[31] || (_cache[31] = [
                              _createTextVNode(" 添加路径 ")
                            ])),
                            _: 1
                          }, 8, ["onClick", "disabled"])
                        ])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_card, {
                  flat: "",
                  class: "rounded mb-3 border config-card"
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_title, { class: "text-caption d-flex align-center px-3 py-2 bg-primary-lighten-5" }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_icon, {
                          icon: "mdi-filter-settings",
                          class: "mr-2",
                          color: "primary",
                          size: "small"
                        }),
                        _cache[32] || (_cache[32] = _createElementVNode("span", null, "清理规则", -1))
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_row, null, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_col, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_18, [
                                  _createVNode(_component_v_icon, {
                                    icon: "mdi-folder-remove",
                                    size: "small",
                                    color: _ctx.editableConfig.empty_dir_cleanup ? 'success' : 'grey',
                                    class: "mr-3"
                                  }, null, 8, ["color"]),
                                  _createElementVNode("div", _hoisted_19, [
                                    _createElementVNode("div", _hoisted_20, [
                                      _cache[33] || (_cache[33] = _createElementVNode("div", null, [
                                        _createElementVNode("div", { class: "text-subtitle-2" }, "清理空目录"),
                                        _createElementVNode("div", { class: "text-caption text-grey" }, "自动删除不包含任何文件的空文件夹")
                                      ], -1)),
                                      _createVNode(_component_v_switch, {
                                        modelValue: _ctx.editableConfig.empty_dir_cleanup,
                                        "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((_ctx.editableConfig.empty_dir_cleanup) = $event)),
                                        color: "success",
                                        inset: "",
                                        disabled: _ctx.saving,
                                        density: "compact",
                                        "hide-details": "",
                                        class: "small-switch"
                                      }, null, 8, ["modelValue", "disabled"])
                                    ])
                                  ])
                                ])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_v_col, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_21, [
                                  _createVNode(_component_v_icon, {
                                    icon: "mdi-weight",
                                    size: "small",
                                    color: _ctx.editableConfig.small_dir_cleanup ? 'warning' : 'grey',
                                    class: "mr-3"
                                  }, null, 8, ["color"]),
                                  _createElementVNode("div", _hoisted_22, [
                                    _createElementVNode("div", _hoisted_23, [
                                      _cache[34] || (_cache[34] = _createElementVNode("div", null, [
                                        _createElementVNode("div", { class: "text-subtitle-2" }, "清理小体积目录"),
                                        _createElementVNode("div", { class: "text-caption text-grey" }, "清理小于指定体积的目录")
                                      ], -1)),
                                      _createVNode(_component_v_switch, {
                                        modelValue: _ctx.editableConfig.small_dir_cleanup,
                                        "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((_ctx.editableConfig.small_dir_cleanup) = $event)),
                                        color: "warning",
                                        inset: "",
                                        disabled: _ctx.saving,
                                        density: "compact",
                                        "hide-details": "",
                                        class: "small-switch"
                                      }, null, 8, ["modelValue", "disabled"])
                                    ])
                                  ])
                                ]),
                                (_ctx.editableConfig.small_dir_cleanup)
                                  ? (_openBlock(), _createElementBlock("div", _hoisted_24, [
                                      _createVNode(_component_v_text_field, {
                                        modelValue: _ctx.editableConfig.small_dir_max_size,
                                        "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((_ctx.editableConfig.small_dir_max_size) = $event)),
                                        modelModifiers: { number: true },
                                        label: "小体积目录最大值(MB)",
                                        type: "number",
                                        variant: "outlined",
                                        min: 1,
                                        max: 1000,
                                        rules: [v => v === null || v === '' || (Number.isInteger(Number(v)) && Number(v) >= 1 && Number(v) <= 1000) || '必须是1-1000之间的整数'],
                                        disabled: _ctx.saving,
                                        density: "compact"
                                      }, null, 8, ["modelValue", "rules", "disabled"])
                                    ]))
                                  : _createCommentVNode("", true)
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_v_col, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_25, [
                                  _createVNode(_component_v_icon, {
                                    icon: "mdi-chart-line-variant",
                                    size: "small",
                                    color: _ctx.editableConfig.size_reduction_cleanup ? 'error' : 'grey',
                                    class: "mr-3"
                                  }, null, 8, ["color"]),
                                  _createElementVNode("div", _hoisted_26, [
                                    _createElementVNode("div", _hoisted_27, [
                                      _cache[35] || (_cache[35] = _createElementVNode("div", null, [
                                        _createElementVNode("div", { class: "text-subtitle-2" }, "清理体积减少目录"),
                                        _createElementVNode("div", { class: "text-caption text-grey" }, "清理体积减少超过阈值的目录")
                                      ], -1)),
                                      _createVNode(_component_v_switch, {
                                        modelValue: _ctx.editableConfig.size_reduction_cleanup,
                                        "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((_ctx.editableConfig.size_reduction_cleanup) = $event)),
                                        color: "error",
                                        inset: "",
                                        disabled: _ctx.saving,
                                        density: "compact",
                                        "hide-details": "",
                                        class: "small-switch"
                                      }, null, 8, ["modelValue", "disabled"])
                                    ])
                                  ])
                                ]),
                                (_ctx.editableConfig.size_reduction_cleanup)
                                  ? (_openBlock(), _createElementBlock("div", _hoisted_28, [
                                      _createVNode(_component_v_text_field, {
                                        modelValue: _ctx.editableConfig.size_reduction_threshold,
                                        "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((_ctx.editableConfig.size_reduction_threshold) = $event)),
                                        modelModifiers: { number: true },
                                        label: "体积减少阈值(%)",
                                        type: "number",
                                        variant: "outlined",
                                        min: 10,
                                        max: 99,
                                        rules: [v => v === null || v === '' || (Number.isInteger(Number(v)) && Number(v) >= 10 && Number(v) <= 99) || '必须是10-99之间的整数'],
                                        disabled: _ctx.saving,
                                        density: "compact"
                                      }, null, 8, ["modelValue", "rules", "disabled"]),
                                      _createElementVNode("div", _hoisted_29, [
                                        _createElementVNode("div", _hoisted_30, [
                                          _createVNode(_component_v_icon, {
                                            icon: "mdi-alert-circle-outline",
                                            size: "small",
                                            color: "error",
                                            class: "mr-2 mt-1"
                                          }),
                                          _cache[36] || (_cache[36] = _createElementVNode("div", { class: "text-caption" }, [
                                            _createElementVNode("strong", null, "功能说明："),
                                            _createTextVNode("系统会记录目录大小变化，当目录大小减少超过设定阈值时判定为可清理。例如：原始目录10GB，解压后删除压缩包，减少到1GB(减少90%)，即可被清理。适用于下载后处理的临时目录。"),
                                            _createElementVNode("span", { class: "text-error" }, "此功能需配合\"扫描间隔\"使用！")
                                          ], -1))
                                        ])
                                      ])
                                    ]))
                                  : _createCommentVNode("", true)
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_card, {
                  flat: "",
                  class: "rounded mb-3 border config-card"
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                      default: _withCtx(() => [
                        _createElementVNode("div", _hoisted_31, [
                          _createVNode(_component_v_icon, {
                            icon: "mdi-information",
                            color: "info",
                            class: "mr-2",
                            size: "small"
                          }),
                          _createElementVNode("div", _hoisted_32, [
                            _cache[40] || (_cache[40] = _createElementVNode("p", { class: "mb-1" }, [
                              _createElementVNode("strong", null, "垃圾文件清理插件"),
                              _createTextVNode("可定期清理下载目录中不需要的文件，支持三种清理模式：")
                            ], -1)),
                            _createElementVNode("div", _hoisted_33, [
                              _createElementVNode("div", _hoisted_34, [
                                _createVNode(_component_v_icon, {
                                  icon: "mdi-folder-remove",
                                  size: "x-small",
                                  color: "success",
                                  class: "mr-1"
                                }),
                                _cache[37] || (_cache[37] = _createElementVNode("strong", null, "空目录清理", -1))
                              ]),
                              _createElementVNode("div", _hoisted_35, [
                                _createVNode(_component_v_icon, {
                                  icon: "mdi-weight",
                                  size: "x-small",
                                  color: "warning",
                                  class: "mr-1"
                                }),
                                _cache[38] || (_cache[38] = _createElementVNode("strong", null, "小体积目录清理", -1))
                              ]),
                              _createElementVNode("div", _hoisted_36, [
                                _createVNode(_component_v_icon, {
                                  icon: "mdi-chart-line-variant",
                                  size: "x-small",
                                  color: "error",
                                  class: "mr-1"
                                }),
                                _cache[39] || (_cache[39] = _createElementVNode("strong", null, "体积减少目录清理", -1))
                              ])
                            ]),
                            _cache[41] || (_cache[41] = _createElementVNode("div", { class: "mt-1 text-grey-darken-1" }, "配置完成后，插件将按CRON设定定时执行。可设置仅在下载器空闲时执行，避免影响正常下载。", -1))
                          ])
                        ])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_card, {
                  flat: "",
                  class: "rounded mb-3 border config-card"
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_title, { class: "text-caption d-flex align-center justify-space-between px-3 py-2 bg-primary-lighten-5" }, {
                      default: _withCtx(() => [
                        _createElementVNode("div", _hoisted_37, [
                          _createVNode(_component_v_icon, {
                            icon: "mdi-folder-remove",
                            class: "mr-2",
                            color: "primary",
                            size: "small"
                          }),
                          _cache[42] || (_cache[42] = _createElementVNode("span", null, "排除目录设置", -1))
                        ]),
                        _createVNode(_component_v_btn, {
                          size: "x-small",
                          color: "primary",
                          variant: "text",
                          "prepend-icon": "mdi-folder-plus",
                          onClick: _cache[11] || (_cache[11] = $event => (_ctx.showExcludePathSelector = true)),
                          disabled: _ctx.saving
                        }, {
                          default: _withCtx(() => _cache[43] || (_cache[43] = [
                            _createTextVNode(" 添加排除目录 ")
                          ])),
                          _: 1
                        }, 8, ["disabled"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                      default: _withCtx(() => [
                        (!_ctx.editableConfig.exclude_dirs.length)
                          ? (_openBlock(), _createBlock(_component_v_alert, {
                              key: 0,
                              density: "compact",
                              type: "info",
                              variant: "tonal",
                              class: "text-caption"
                            }, {
                              default: _withCtx(() => _cache[44] || (_cache[44] = [
                                _createTextVNode(" 未设置任何排除目录，可点击\"添加排除目录\"按钮添加需要排除的目录 ")
                              ])),
                              _: 1
                            }))
                          : _createCommentVNode("", true),
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(_ctx.editableConfig.exclude_dirs, (path, index) => {
                          return (_openBlock(), _createElementBlock("div", {
                            key: index,
                            class: "mb-2"
                          }, [
                            _createElementVNode("div", _hoisted_38, [
                              _createVNode(_component_v_text_field, {
                                modelValue: _ctx.editableConfig.exclude_dirs[index],
                                "onUpdate:modelValue": $event => ((_ctx.editableConfig.exclude_dirs[index]) = $event),
                                label: "排除目录",
                                hint: "不会被清理的文件夹路径",
                                "persistent-hint": "",
                                density: "compact",
                                variant: "outlined",
                                class: "flex-grow-1"
                              }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                              _createVNode(_component_v_btn, {
                                size: "x-small",
                                color: "error",
                                variant: "text",
                                icon: "",
                                onClick: $event => (_ctx.removeExcludeDir(index)),
                                disabled: _ctx.saving,
                                class: "ml-2"
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_v_icon, {
                                    icon: "mdi-delete",
                                    size: "small"
                                  })
                                ]),
                                _: 2
                              }, 1032, ["onClick", "disabled"]),
                              _createVNode(_component_v_btn, {
                                size: "x-small",
                                color: "primary",
                                variant: "text",
                                icon: "",
                                onClick: $event => {_ctx.showExcludePathSelector = true; _ctx.currentExcludePathIndex = index;},
                                disabled: _ctx.saving,
                                class: "ml-2"
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_v_icon, {
                                    icon: "mdi-folder-search",
                                    size: "small"
                                  })
                                ]),
                                _: 2
                              }, 1032, ["onClick", "disabled"])
                            ])
                          ]))
                        }), 128)),
                        _createElementVNode("div", _hoisted_39, [
                          _createVNode(_component_v_btn, {
                            size: "small",
                            color: "primary",
                            variant: "text",
                            "prepend-icon": "mdi-folder-plus",
                            onClick: _ctx.addEmptyExcludeDir,
                            disabled: _ctx.saving
                          }, {
                            default: _withCtx(() => _cache[45] || (_cache[45] = [
                              _createTextVNode(" 添加排除目录 ")
                            ])),
                            _: 1
                          }, 8, ["onClick", "disabled"])
                        ])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }, 8, ["modelValue", "onSubmit"])
          ]),
          _: 1
        }),
        _createVNode(_component_v_divider),
        _createVNode(_component_v_card_actions, { class: "px-2 py-1" }, {
          default: _withCtx(() => [
            _createVNode(_component_v_btn, {
              color: "info",
              onClick: _cache[13] || (_cache[13] = $event => (_ctx.emit('switch'))),
              "prepend-icon": "mdi-view-dashboard",
              disabled: _ctx.saving,
              variant: "text",
              size: "small"
            }, {
              default: _withCtx(() => _cache[46] || (_cache[46] = [
                _createTextVNode("状态页")
              ])),
              _: 1
            }, 8, ["disabled"]),
            _createVNode(_component_v_spacer),
            _createVNode(_component_v_btn, {
              color: "secondary",
              variant: "text",
              onClick: _ctx.resetConfig,
              disabled: !_ctx.initialConfigLoaded || _ctx.saving,
              "prepend-icon": "mdi-restore",
              size: "small"
            }, {
              default: _withCtx(() => _cache[47] || (_cache[47] = [
                _createTextVNode("重置")
              ])),
              _: 1
            }, 8, ["onClick", "disabled"]),
            _createVNode(_component_v_btn, {
              color: "primary",
              disabled: !_ctx.isFormValid || _ctx.saving,
              onClick: _ctx.saveConfig,
              loading: _ctx.saving,
              "prepend-icon": "mdi-content-save",
              variant: "text",
              size: "small"
            }, {
              default: _withCtx(() => _cache[48] || (_cache[48] = [
                _createTextVNode("保存配置")
              ])),
              _: 1
            }, 8, ["disabled", "onClick", "loading"]),
            _createVNode(_component_v_btn, {
              color: "grey",
              onClick: _cache[14] || (_cache[14] = $event => (_ctx.emit('close'))),
              "prepend-icon": "mdi-close",
              disabled: _ctx.saving,
              variant: "text",
              size: "small"
            }, {
              default: _withCtx(() => _cache[49] || (_cache[49] = [
                _createTextVNode("关闭")
              ])),
              _: 1
            }, 8, ["disabled"])
          ]),
          _: 1
        })
      ]),
      _: 1
    }),
    _createVNode(_component_v_dialog, {
      modelValue: _ctx.showPathSelector,
      "onUpdate:modelValue": _cache[17] || (_cache[17] = $event => ((_ctx.showPathSelector) = $event)),
      "max-width": "800"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, { class: "text-subtitle-1 d-flex align-center px-3 py-2 bg-primary-lighten-5" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-folder-search",
                  class: "mr-2",
                  color: "primary"
                }),
                _cache[50] || (_cache[50] = _createElementVNode("span", null, "选择监控路径", -1))
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
              default: _withCtx(() => [
                (_ctx.pathSelectorLoading)
                  ? (_openBlock(), _createElementBlock("div", _hoisted_40, [
                      _createVNode(_component_v_progress_circular, {
                        indeterminate: "",
                        color: "primary"
                      })
                    ]))
                  : (_openBlock(), _createElementBlock("div", _hoisted_41, [
                      _createVNode(_component_v_text_field, {
                        modelValue: _ctx.currentPath,
                        "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((_ctx.currentPath) = $event)),
                        label: "当前路径",
                        variant: "outlined",
                        readonly: "",
                        density: "compact",
                        class: "mb-2"
                      }, null, 8, ["modelValue"]),
                      _createVNode(_component_v_list, {
                        class: "border rounded",
                        "max-height": "300px",
                        "overflow-y": "auto"
                      }, {
                        default: _withCtx(() => [
                          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(_ctx.pathItems, (item, index) => {
                            return (_openBlock(), _createBlock(_component_v_list_item, {
                              key: index,
                              onClick: $event => (_ctx.navigateTo(item)),
                              disabled: item.type !== 'parent' && item.type !== 'dir' && item.type !== 'drive',
                              class: "py-1"
                            }, {
                              prepend: _withCtx(() => [
                                _createVNode(_component_v_icon, {
                                  icon: item.type === 'parent' ? 'mdi-arrow-up' : (item.type === 'dir' ? 'mdi-folder' : (item.type === 'drive' ? 'mdi-harddisk' : 'mdi-file')),
                                  size: "small",
                                  class: "mr-2",
                                  color: item.type === 'parent' ? 'grey' : (item.type === 'dir' || item.type === 'drive' ? 'amber-darken-2' : 'blue')
                                }, null, 8, ["icon", "color"])
                              ]),
                              default: _withCtx(() => [
                                _createVNode(_component_v_list_item_title, { class: "text-body-2" }, {
                                  default: _withCtx(() => [
                                    _createTextVNode(_toDisplayString(item.name), 1)
                                  ]),
                                  _: 2
                                }, 1024)
                              ]),
                              _: 2
                            }, 1032, ["onClick", "disabled"]))
                          }), 128)),
                          (!_ctx.pathItems.length)
                            ? (_openBlock(), _createBlock(_component_v_list_item, {
                                key: 0,
                                class: "py-2 text-center"
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_v_list_item_title, { class: "text-body-2 text-grey" }, {
                                    default: _withCtx(() => _cache[51] || (_cache[51] = [
                                      _createTextVNode("该目录为空或访问受限")
                                    ])),
                                    _: 1
                                  })
                                ]),
                                _: 1
                              }))
                            : _createCommentVNode("", true)
                        ]),
                        _: 1
                      })
                    ])),
                (_ctx.pathSelectorError)
                  ? (_openBlock(), _createBlock(_component_v_alert, {
                      key: 2,
                      type: "error",
                      density: "compact",
                      class: "mt-2 text-caption",
                      variant: "tonal"
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode(_toDisplayString(_ctx.pathSelectorError), 1)
                      ]),
                      _: 1
                    }))
                  : _createCommentVNode("", true)
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, { class: "px-3 py-2" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  color: "primary",
                  onClick: _ctx.selectCurrentPath,
                  disabled: !_ctx.currentPath || _ctx.pathSelectorLoading,
                  variant: "text",
                  size: "small"
                }, {
                  default: _withCtx(() => _cache[52] || (_cache[52] = [
                    _createTextVNode(" 选择当前目录 ")
                  ])),
                  _: 1
                }, 8, ["onClick", "disabled"]),
                _createVNode(_component_v_btn, {
                  color: "grey",
                  onClick: _cache[16] || (_cache[16] = $event => (_ctx.showPathSelector = false)),
                  variant: "text",
                  size: "small"
                }, {
                  default: _withCtx(() => _cache[53] || (_cache[53] = [
                    _createTextVNode(" 取消 ")
                  ])),
                  _: 1
                })
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
      modelValue: _ctx.showExcludePathSelector,
      "onUpdate:modelValue": _cache[20] || (_cache[20] = $event => ((_ctx.showExcludePathSelector) = $event)),
      "max-width": "800"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, { class: "text-subtitle-1 d-flex align-center px-3 py-2 bg-primary-lighten-5" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-folder-search",
                  class: "mr-2",
                  color: "primary"
                }),
                _cache[54] || (_cache[54] = _createElementVNode("span", null, "选择排除目录", -1))
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
              default: _withCtx(() => [
                (_ctx.pathSelectorLoading)
                  ? (_openBlock(), _createElementBlock("div", _hoisted_42, [
                      _createVNode(_component_v_progress_circular, {
                        indeterminate: "",
                        color: "primary"
                      })
                    ]))
                  : (_openBlock(), _createElementBlock("div", _hoisted_43, [
                      _createVNode(_component_v_text_field, {
                        modelValue: _ctx.currentPath,
                        "onUpdate:modelValue": _cache[18] || (_cache[18] = $event => ((_ctx.currentPath) = $event)),
                        label: "当前路径",
                        variant: "outlined",
                        readonly: "",
                        density: "compact",
                        class: "mb-2"
                      }, null, 8, ["modelValue"]),
                      _createVNode(_component_v_list, {
                        class: "border rounded",
                        "max-height": "300px",
                        "overflow-y": "auto"
                      }, {
                        default: _withCtx(() => [
                          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(_ctx.pathItems, (item, index) => {
                            return (_openBlock(), _createBlock(_component_v_list_item, {
                              key: index,
                              onClick: $event => (_ctx.navigateTo(item)),
                              disabled: item.type !== 'parent' && item.type !== 'dir' && item.type !== 'drive',
                              class: "py-1"
                            }, {
                              prepend: _withCtx(() => [
                                _createVNode(_component_v_icon, {
                                  icon: item.type === 'parent' ? 'mdi-arrow-up' : (item.type === 'dir' ? 'mdi-folder' : (item.type === 'drive' ? 'mdi-harddisk' : 'mdi-file')),
                                  size: "small",
                                  class: "mr-2",
                                  color: item.type === 'parent' ? 'grey' : (item.type === 'dir' || item.type === 'drive' ? 'amber-darken-2' : 'blue')
                                }, null, 8, ["icon", "color"])
                              ]),
                              default: _withCtx(() => [
                                _createVNode(_component_v_list_item_title, { class: "text-body-2" }, {
                                  default: _withCtx(() => [
                                    _createTextVNode(_toDisplayString(item.name), 1)
                                  ]),
                                  _: 2
                                }, 1024)
                              ]),
                              _: 2
                            }, 1032, ["onClick", "disabled"]))
                          }), 128)),
                          (!_ctx.pathItems.length)
                            ? (_openBlock(), _createBlock(_component_v_list_item, {
                                key: 0,
                                class: "py-2 text-center"
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_v_list_item_title, { class: "text-body-2 text-grey" }, {
                                    default: _withCtx(() => _cache[55] || (_cache[55] = [
                                      _createTextVNode("该目录为空或访问受限")
                                    ])),
                                    _: 1
                                  })
                                ]),
                                _: 1
                              }))
                            : _createCommentVNode("", true)
                        ]),
                        _: 1
                      })
                    ])),
                (_ctx.pathSelectorError)
                  ? (_openBlock(), _createBlock(_component_v_alert, {
                      key: 2,
                      type: "error",
                      density: "compact",
                      class: "mt-2 text-caption",
                      variant: "tonal"
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode(_toDisplayString(_ctx.pathSelectorError), 1)
                      ]),
                      _: 1
                    }))
                  : _createCommentVNode("", true)
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, { class: "px-3 py-2" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  color: "primary",
                  onClick: _ctx.selectExcludePath,
                  disabled: !_ctx.currentPath || _ctx.pathSelectorLoading,
                  variant: "text",
                  size: "small"
                }, {
                  default: _withCtx(() => _cache[56] || (_cache[56] = [
                    _createTextVNode(" 选择当前目录 ")
                  ])),
                  _: 1
                }, 8, ["onClick", "disabled"]),
                _createVNode(_component_v_btn, {
                  color: "grey",
                  onClick: _cache[19] || (_cache[19] = $event => (_ctx.showExcludePathSelector = false)),
                  variant: "text",
                  size: "small"
                }, {
                  default: _withCtx(() => _cache[57] || (_cache[57] = [
                    _createTextVNode(" 取消 ")
                  ])),
                  _: 1
                })
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
const Config = /*#__PURE__*/_export_sfc(_sfc_main, [['render',_sfc_render],['__scopeId',"data-v-f579374d"]]);

export { Config as default };
