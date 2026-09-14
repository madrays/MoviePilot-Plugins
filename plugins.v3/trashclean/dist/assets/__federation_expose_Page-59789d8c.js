import { importShared } from './__federation_fn_import-054b33c3.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Page_vue_vue_type_style_index_0_lang = '';

const {defineComponent,ref,reactive,toRefs,computed,onMounted,onUnmounted} = await importShared('vue');


const _sfc_main = defineComponent({
  name: 'Page',
  
  props: {
    api: {
      type: [Object, Function],
      required: true
    }
  },
  
  emits: ['switch', 'close'],
  
  setup(props, { emit }) {
    // 状态
    const state = reactive({
      error: null,
      loading: true,
      refreshing: false,
      initialDataLoaded: false,
      actionMessage: null,
      actionMessageType: 'info',
      actionLoading: false,
      statusData: {
        enabled: false,
        cron: '',
        next_run_time: '',
        monitor_paths: [],
        exclude_dirs: [],
        only_when_no_download: false,
        dir_history_count: 0,
        cleanup_rules: {
          empty_dir: false,
          small_dir: {
            enabled: false,
            max_size: 10
          },
          size_reduction: {
            enabled: false,
            threshold: 80
          }
        }
      },
      pathStats: [],
      showCleanResultDialog: false,
      cleanResult: null,
      downloaders: [],
      loadingDownloaders: false,
      cleanHistory: [],
      loadingHistory: false,
      showHistoryDialog: false,
      lastStatsUpdate: '',
      updatingStats: false,
      showUpdateStatsDialog: false,
      updateStatsProgress: 0,
      updateStatsMessage: '',
      cleanProgress: {
        running: false,
        total_dirs: 0,
        processed_dirs: 0,
        current_dir: "",
        removed_dirs: [],
        start_time: null,
        status: "idle",
        message: "",
        percent: 0
      },
      showCleanProgressDialog: false,
      progressPollTimer: null
    });
    
    // 计算属性：有效的路径统计
    const validPathStats = computed(() => {
      return state.pathStats.filter(path => path.exists && path.status === 'valid');
    });
    
    // 计算属性：清理规则
    const cleanupRules = computed(() => {
      return state.statusData.cleanup_rules || {
        empty_dir: false,
        small_dir: {
          enabled: false,
          max_size: 10
        },
        size_reduction: {
          enabled: false,
          threshold: 80
        }
      };
    });
    
    // 计算属性：下载器是否有活动任务
    const downloadersHaveActiveTasks = computed(() => {
      return state.downloaders.some(downloader => downloader.hasActiveTasks);
    });
    
    // 加载状态数据
    const loadStatusData = async () => {
      try {
        state.error = null;
        state.loading = true;
        
        const response = await props.api.get('plugin/TrashClean/status');
        if (response) {
          state.statusData = response;
          state.initialDataLoaded = true;
        }
      } catch (error) {
        state.error = `加载状态数据失败: ${error.message || error}`;
        console.error('加载状态数据失败:', error);
      } finally {
        state.loading = false;
      }
    };
    
    // 加载路径统计数据
    const loadPathStats = async () => {
      try {
        const response = await props.api.get('plugin/TrashClean/stats');
        if (response) {
          state.pathStats = response;
        }
      } catch (error) {
        state.error = `加载路径统计数据失败: ${error.message || error}`;
        console.error('加载路径统计数据失败:', error);
      }
    };
    
    // 加载下载器状态
    const loadDownloaderStatus = async () => {
      try {
        state.loadingDownloaders = true;
        
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
        state.loadingDownloaders = false;
      }
    };
    
    // 加载清理历史记录
    const loadCleanHistory = async () => {
      try {
        state.loadingHistory = true;
        const response = await props.api.get('plugin/TrashClean/history');
        if (response) {
          state.cleanHistory = response;
        } else {
          state.cleanHistory = [];
        }
      } catch (error) {
        console.error('加载清理历史记录失败:', error);
        state.cleanHistory = [];
      } finally {
        state.loadingHistory = false;
      }
    };
    
    // 加载最新清理结果
    const loadLatestCleanResult = async () => {
      try {
        const response = await props.api.get('plugin/TrashClean/latest_clean_result');
        if (response) {
          state.cleanResult = response;
          console.log('已加载最新清理结果:', response);
        }
      } catch (error) {
        console.error('加载最新清理结果失败:', error);
      }
    };
    
    // 刷新所有数据
    const refreshData = async () => {
      try {
        state.refreshing = true;
        state.error = null;
        state.actionMessage = null;
        
        await loadStatusData();
        await loadPathStats();
        
        // 获取统计缓存信息
        try {
          const statsCache = await props.api.get('plugin/TrashClean/stats_cache');
          if (statsCache && statsCache.last_update) {
            state.lastStatsUpdate = statsCache.last_update;
          }
        } catch (error) {
          console.error('获取统计缓存失败:', error);
        }
        
        // 如果启用了只在无下载任务时执行，则加载下载器状态
        if (state.statusData.only_when_no_download) {
          await loadDownloaderStatus();
        }
        
        // 如果有历史记录，加载历史数据
        if (state.statusData.dir_history_count > 0) {
          await loadCleanHistory();
        }
        
        // 加载最新清理结果
        await loadLatestCleanResult();
        
        state.actionMessage = '数据刷新成功';
        state.actionMessageType = 'success';
        
        // 3秒后清除成功消息
        setTimeout(() => {
          state.actionMessage = null;
        }, 3000);
      } catch (error) {
        state.error = `刷新数据失败: ${error.message || error}`;
        console.error('刷新数据失败:', error);
      } finally {
        state.refreshing = false;
      }
    };
    
    // 手动更新统计数据
    const updateStats = async () => {
      try {
        state.updatingStats = true;
        state.error = null;
        state.showUpdateStatsDialog = true; // 显示更新对话框
        state.updateStatsProgress = 0; // 初始进度
        state.updateStatsMessage = "准备开始更新统计数据...";
        
        // 显示加载消息
        state.actionMessage = "正在更新目录统计数据，这可能需要一些时间...";
        state.actionMessageType = "info";
        
        // 启动进度轮询
        const progressTimer = setInterval(async () => {
          try {
            const statsCache = await props.api.get('plugin/TrashClean/stats_cache');
            if (statsCache) {
              state.updateStatsProgress = statsCache.progress || 0;
              state.updateStatsMessage = statsCache.message || "更新中...";
              
              // 如果更新完成，停止轮询
              if (statsCache.status === "success" && statsCache.progress >= 100) {
                clearInterval(progressTimer);
              }
            }
          } catch (err) {
            console.error('获取统计缓存进度失败:', err);
          }
        }, 500);
        
        // 执行更新操作
        const response = await props.api.post('plugin/TrashClean/update_stats');
        
        // 停止进度轮询
        clearInterval(progressTimer);
        
        // 获取最终结果
        const finalStats = await props.api.get('plugin/TrashClean/stats_cache');
        if (finalStats) {
          state.updateStatsProgress = finalStats.progress || 100;
          state.updateStatsMessage = finalStats.message || "更新完成";
          state.lastStatsUpdate = finalStats.last_update || "";
        }
        
        // 重新加载统计数据
        await loadPathStats();
        
        // 更新完成，但不自动关闭对话框，让用户手动关闭
        state.updatingStats = false;
        
        state.actionMessage = "目录统计数据更新成功";
        state.actionMessageType = "success";
        
        // 3秒后清除成功消息
        setTimeout(() => {
          if (state.actionMessage === "目录统计数据更新成功") {
            state.actionMessage = null;
          }
        }, 3000);
      } catch (error) {
        state.error = `更新目录统计数据失败: ${error.message || error}`;
        console.error('更新目录统计数据失败:', error);
        state.updatingStats = false;
      }
    };
    
    // 获取清理进度
    const getCleanProgress = async () => {
      try {
        const response = await props.api.get('plugin/TrashClean/clean_progress');
        if (response) {
          state.cleanProgress = response;
          
          // 如果清理任务正在运行并且进度对话框未显示，则显示它
          if (response.running && !state.showCleanProgressDialog) {
            state.showCleanProgressDialog = true;
          }
          
          // 如果清理任务已完成但对话框仍显示，则5秒后自动关闭
          if (!response.running && response.status !== "idle" && state.showCleanProgressDialog) {
            setTimeout(() => {
              if (!state.cleanProgress.running) {
                state.showCleanProgressDialog = false;
              }
            }, 5000);
          }
        }
      } catch (error) {
        console.error('获取清理进度失败:', error);
      }
    };
    
    // 启动清理进度轮询
    const startProgressPolling = () => {
      if (state.progressPollTimer) {
        clearInterval(state.progressPollTimer);
      }
      
      // 每秒轮询一次进度
      state.progressPollTimer = setInterval(async () => {
        await getCleanProgress();
        
        // 如果清理任务已经完成且不是初始状态，则停止轮询
        if (!state.cleanProgress.running && state.cleanProgress.status !== "idle") {
          stopProgressPolling();
        }
      }, 1000);
    };
    
    // 停止清理进度轮询
    const stopProgressPolling = () => {
      if (state.progressPollTimer) {
        clearInterval(state.progressPollTimer);
        state.progressPollTimer = null;
      }
    };
    
    // 触发手动清理
    const triggerClean = async () => {
      try {
        state.actionLoading = true;
        state.error = null;
        state.actionMessage = null;
        
        // 开始进度轮询
        startProgressPolling();
        
        // 显示进度对话框
        state.showCleanProgressDialog = true;
        
        const response = await props.api.post('plugin/TrashClean/clean');
        
        if (response) {
          state.cleanResult = response;
          
          // 继续轮询一段时间以显示最终结果
          setTimeout(() => {
            getCleanProgress();
          }, 1000);
          
          // 刷新数据
          await refreshData();
        }
      } catch (error) {
        state.error = `手动清理失败: ${error.message || error}`;
        console.error('手动清理失败:', error);
        
        // 停止进度轮询
        stopProgressPolling();
      } finally {
        state.actionLoading = false;
      }
    };
    
    // 格式化文件大小
    const formatSize = (bytes) => {
      if (bytes === 0) return '0 B';
      
      const units = ['B', 'KB', 'MB', 'GB', 'TB'];
      const i = Math.floor(Math.log(bytes) / Math.log(1024));
      
      return (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + units[i];
    };
    
    // 获取清理类型对应的颜色
    const getCleanTypeColor = (type) => {
      switch (type) {
        case 'empty':
          return 'success';
        case 'small':
          return 'warning';
        case 'size_reduction':
          return 'error';
        default:
          return 'grey';
      }
    };
    
    // 获取清理类型对应的文本
    const getCleanTypeText = (type) => {
      switch (type) {
        case 'empty':
          return '空目录';
        case 'small':
          return '小体积';
        case 'size_reduction':
          return '体积减少';
        default:
          return '未知';
      }
    };
    
    // 格式化日期时间
    const formatDate = (date) => {
      if (!date) return '';
      
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      
      return `${year}-${month}-${day} ${hours}:${minutes}`;
    };
    
    // 获取清理类型对应的图标
    const getCleanTypeIcon = (type) => {
      switch (type) {
        case 'empty':
          return 'mdi-folder-remove';
        case 'small':
          return 'mdi-weight';
        case 'size_reduction':
          return 'mdi-chart-line-variant';
        default:
          return 'mdi-folder';
      }
    };
    
    // 添加格式化速度函数
    const formatSpeed = (bytesPerSecond) => {
      if (bytesPerSecond < 0 || bytesPerSecond === undefined) return "未知";
      const units = ['B/s', 'KB/s', 'MB/s', 'GB/s'];
      let speed = bytesPerSecond;
      let unitIndex = 0;
      
      while (speed >= 1024 && unitIndex < units.length - 1) {
        speed /= 1024;
        unitIndex++;
      }
      
      return speed.toFixed(2) + ' ' + units[unitIndex];
    };
    
    // 添加格式化时间函数
    const formatETA = (seconds) => {
      if (seconds < 0 || seconds === undefined || seconds >= 8640000) return "未知";
      
      if (seconds < 60) {
        return `${seconds}秒`;
      } else if (seconds < 3600) {
        return `${Math.floor(seconds / 60)}分钟`;
      } else if (seconds < 86400) {
        return `${Math.floor(seconds / 3600)}小时${Math.floor((seconds % 3600) / 60)}分钟`;
      } else {
        return `${Math.floor(seconds / 86400)}天${Math.floor((seconds % 86400) / 3600)}小时`;
      }
    };
    
    // 获取历史记录颜色
    const getHistoryColor = (index) => {
      const colors = ['success', 'warning', 'error'];
      return colors[index % colors.length];
    };
    
    // 计算属性：进度状态颜色
    const getProgressStatusColor = computed(() => {
      switch (state.cleanProgress.status) {
        case 'success':
          return 'success';
        case 'error':
          return 'error';
        case 'running':
          return 'primary';
        default:
          return 'grey';
      }
    });
    
    // 计算属性：进度状态文本
    const getProgressStatusText = computed(() => {
      switch (state.cleanProgress.status) {
        case 'success':
          return '清理任务完成';
        case 'error':
          return '清理任务失败';
        case 'running':
          return '清理任务进行中...';
        default:
          return '准备开始清理';
      }
    });
    
    // 计算属性：进度状态图标
    const getProgressStatusIcon = computed(() => {
      switch (state.cleanProgress.status) {
        case 'success':
          return 'mdi-check-circle';
        case 'error':
          return 'mdi-alert-circle';
        case 'running':
          return 'mdi-progress-clock';
        default:
          return 'mdi-broom';
      }
    });
    
    // 计算属性：进度状态类
    const getProgressStatusClass = computed(() => {
      switch (state.cleanProgress.status) {
        case 'success':
          return 'bg-success-lighten-5';
        case 'error':
          return 'bg-error-lighten-5';
        case 'running':
          return 'bg-primary-lighten-5';
        default:
          return 'bg-grey-lighten-5';
      }
    });
    
    // 计算属性：进度信息背景类
    const getProgressInfoBgClass = computed(() => {
      switch (state.cleanProgress.status) {
        case 'success':
          return 'bg-success-lighten-5';
        case 'error':
          return 'bg-error-lighten-5';
        case 'running':
          return 'bg-primary-lighten-5';
        default:
          return 'bg-grey-lighten-5';
      }
    });
    
    // 组件挂载时加载数据
    onMounted(() => {
      refreshData();
      
      // 加载最新清理结果
      loadLatestCleanResult();
      
      // 检查是否有正在进行的清理任务
      getCleanProgress().then(() => {
        if (state.cleanProgress.running) {
          state.showCleanProgressDialog = true;
          startProgressPolling();
        }
      });
    });
    
    // 组件卸载时清理
    onUnmounted(() => {
      stopProgressPolling();
    });
    
    return {
      ...toRefs(state),
      validPathStats,
      cleanupRules,
      downloadersHaveActiveTasks,
      refreshData,
      triggerClean,
      formatSize,
      getCleanTypeColor,
      getCleanTypeText,
      formatDate,
      getCleanTypeIcon,
      formatSpeed,
      formatETA,
      getHistoryColor,
      updateStats,
      getProgressStatusColor,
      getProgressStatusText,
      getProgressStatusIcon,
      getProgressStatusClass,
      getProgressInfoBgClass,
      emit
    };
  }
});

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,withCtx:_withCtx,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,createElementBlock:_createElementBlock,renderList:_renderList,Fragment:_Fragment,normalizeClass:_normalizeClass} = await importShared('vue');


const _hoisted_1 = { class: "plugin-page" };
const _hoisted_2 = {
  key: 3,
  class: "my-1"
};
const _hoisted_3 = {
  class: "text-caption px-2 py-1 rounded",
  style: {"background-color":"rgba(0,0,0,0.05)"}
};
const _hoisted_4 = { class: "text-caption" };
const _hoisted_5 = {
  key: 0,
  class: "text-center text-grey py-3"
};
const _hoisted_6 = {
  key: 0,
  class: "text-center text-grey py-3"
};
const _hoisted_7 = { class: "d-flex align-center" };
const _hoisted_8 = {
  key: 0,
  class: "d-flex justify-center py-4"
};
const _hoisted_9 = {
  key: 1,
  class: "text-center text-grey py-3"
};
const _hoisted_10 = { key: 2 };
const _hoisted_11 = { class: "downloader-grid pa-2" };
const _hoisted_12 = { class: "d-flex align-center px-3 py-2" };
const _hoisted_13 = { class: "font-weight-medium" };
const _hoisted_14 = { class: "text-caption" };
const _hoisted_15 = { class: "d-flex align-center" };
const _hoisted_16 = { class: "tasks-container" };
const _hoisted_17 = { class: "d-flex align-center mb-1" };
const _hoisted_18 = ["title"];
const _hoisted_19 = { class: "task-info d-flex align-center justify-space-between mt-1" };
const _hoisted_20 = { class: "text-caption progress-value ml-2" };
const _hoisted_21 = { class: "task-details d-flex flex-wrap justify-space-between mt-2" };
const _hoisted_22 = { class: "info-chip" };
const _hoisted_23 = { class: "info-chip" };
const _hoisted_24 = { class: "info-chip" };
const _hoisted_25 = {
  key: 0,
  class: "text-caption mr-2"
};
const _hoisted_26 = {
  key: 0,
  class: "text-caption mr-2"
};
const _hoisted_27 = { class: "d-flex align-center" };
const _hoisted_28 = { class: "d-flex align-center" };
const _hoisted_29 = {
  class: "text-truncate",
  style: {"max-width":"300px"}
};
const _hoisted_30 = { class: "text-center" };
const _hoisted_31 = { class: "text-center" };
const _hoisted_32 = { class: "text-center" };
const _hoisted_33 = { key: 0 };
const _hoisted_34 = { class: "d-flex align-center px-2 py-1" };
const _hoisted_35 = { class: "text-caption" };
const _hoisted_36 = { class: "my-2 px-3" };
const _hoisted_37 = { class: "text-subtitle-2 font-weight-medium d-flex justify-space-between align-center" };
const _hoisted_38 = { class: "d-flex align-center" };
const _hoisted_39 = {
  key: 0,
  class: "text-caption mr-2"
};
const _hoisted_40 = {
  key: 1,
  class: "text-caption mr-2"
};
const _hoisted_41 = {
  key: 1,
  class: "text-center py-3"
};
const _hoisted_42 = {
  key: 0,
  class: "text-center text-grey py-1"
};
const _hoisted_43 = { class: "d-flex justify-space-between align-center mb-1" };
const _hoisted_44 = { class: "text-caption text-grey-darken-2" };
const _hoisted_45 = { class: "text-caption" };
const _hoisted_46 = { class: "text-caption d-flex align-center" };
const _hoisted_47 = { class: "text-grey" };
const _hoisted_48 = { key: 0 };
const _hoisted_49 = { key: 0 };
const _hoisted_50 = {
  key: 1,
  class: "text-center py-2"
};
const _hoisted_51 = { class: "d-flex justify-space-between align-center mb-1" };
const _hoisted_52 = { class: "text-caption font-weight-medium" };
const _hoisted_53 = { class: "text-body-2" };
const _hoisted_54 = { class: "d-flex flex-wrap text-caption mt-1" };
const _hoisted_55 = {
  key: 1,
  class: "d-flex align-center justify-center py-4"
};
const _hoisted_56 = { class: "text-center mb-3" };
const _hoisted_57 = { class: "text-subtitle-2" };
const _hoisted_58 = {
  key: 0,
  class: "text-caption text-center mt-3 text-grey"
};
const _hoisted_59 = { class: "progress-content" };
const _hoisted_60 = { class: "mb-3" };
const _hoisted_61 = { class: "d-flex justify-space-between align-center mb-1" };
const _hoisted_62 = { class: "text-subtitle-2" };
const _hoisted_63 = { class: "d-flex flex-wrap" };
const _hoisted_64 = { class: "progress-stat-item" };
const _hoisted_65 = { class: "progress-stat-item" };
const _hoisted_66 = { class: "progress-stat-item" };
const _hoisted_67 = { class: "progress-stat-item" };
const _hoisted_68 = {
  key: 0,
  class: "mt-2"
};
const _hoisted_69 = { class: "text-caption" };
const _hoisted_70 = {
  key: 0,
  class: "mt-3"
};
const _hoisted_71 = { class: "removed-dirs-container bg-grey-lighten-5 rounded pa-1" };
const _hoisted_72 = { class: "d-flex align-center" };
const _hoisted_73 = { class: "text-caption text-truncate" };
const _hoisted_74 = {
  key: 0,
  class: "text-center pa-2"
};
const _hoisted_75 = { class: "text-caption" };

function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_skeleton_loader = _resolveComponent("v-skeleton-loader");
  const _component_v_list_item_title = _resolveComponent("v-list-item-title");
  const _component_v_chip = _resolveComponent("v-chip");
  const _component_v_list_item = _resolveComponent("v-list-item");
  const _component_v_divider = _resolveComponent("v-divider");
  const _component_v_list = _resolveComponent("v-list");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card_actions = _resolveComponent("v-card-actions");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_progress_circular = _resolveComponent("v-progress-circular");
  const _component_v_avatar = _resolveComponent("v-avatar");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_expansion_panel_title = _resolveComponent("v-expansion-panel-title");
  const _component_v_progress_linear = _resolveComponent("v-progress-linear");
  const _component_v_expansion_panel_text = _resolveComponent("v-expansion-panel-text");
  const _component_v_expansion_panel = _resolveComponent("v-expansion-panel");
  const _component_v_expansion_panels = _resolveComponent("v-expansion-panels");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_table = _resolveComponent("v-table");
  const _component_v_timeline_item = _resolveComponent("v-timeline-item");
  const _component_v_timeline = _resolveComponent("v-timeline");
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
              icon: "mdi-broom",
              class: "mr-2",
              color: "primary",
              size: "small"
            }),
            _cache[15] || (_cache[15] = _createElementVNode("span", null, "垃圾文件清理", -1))
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
            (_ctx.actionMessage)
              ? (_openBlock(), _createBlock(_component_v_alert, {
                  key: 1,
                  type: _ctx.actionMessageType,
                  density: "compact",
                  class: "mb-2 text-caption",
                  variant: "tonal",
                  closable: ""
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(_ctx.actionMessage), 1)
                  ]),
                  _: 1
                }, 8, ["type"]))
              : _createCommentVNode("", true),
            (_ctx.loading && !_ctx.initialDataLoaded)
              ? (_openBlock(), _createBlock(_component_v_skeleton_loader, {
                  key: 2,
                  type: "article, actions"
                }))
              : _createCommentVNode("", true),
            (_ctx.initialDataLoaded)
              ? (_openBlock(), _createElementBlock("div", _hoisted_2, [
                  _createVNode(_component_v_row, null, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_col, {
                        cols: "12",
                        md: "6"
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
                                    icon: "mdi-information",
                                    class: "mr-2",
                                    color: "primary",
                                    size: "small"
                                  }),
                                  _cache[16] || (_cache[16] = _createElementVNode("span", null, "当前状态", -1))
                                ]),
                                _: 1
                              }),
                              _createVNode(_component_v_card_text, { class: "pa-0" }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_v_list, { class: "bg-transparent pa-0" }, {
                                    default: _withCtx(() => [
                                      _createVNode(_component_v_list_item, { class: "px-3 py-1" }, {
                                        prepend: _withCtx(() => [
                                          _createVNode(_component_v_icon, {
                                            color: _ctx.statusData.enabled ? 'success' : 'grey',
                                            icon: "mdi-power",
                                            size: "small"
                                          }, null, 8, ["color"])
                                        ]),
                                        append: _withCtx(() => [
                                          _createVNode(_component_v_chip, {
                                            color: _ctx.statusData.enabled ? 'success' : 'grey',
                                            size: "x-small",
                                            variant: "tonal"
                                          }, {
                                            default: _withCtx(() => [
                                              _createTextVNode(_toDisplayString(_ctx.statusData.enabled ? '已启用' : '已禁用'), 1)
                                            ]),
                                            _: 1
                                          }, 8, ["color"])
                                        ]),
                                        default: _withCtx(() => [
                                          _createVNode(_component_v_list_item_title, { class: "text-caption" }, {
                                            default: _withCtx(() => _cache[17] || (_cache[17] = [
                                              _createTextVNode("插件状态")
                                            ])),
                                            _: 1
                                          })
                                        ]),
                                        _: 1
                                      }),
                                      _createVNode(_component_v_divider, { class: "my-1" }),
                                      _createVNode(_component_v_list_item, { class: "px-3 py-1" }, {
                                        prepend: _withCtx(() => [
                                          _createVNode(_component_v_icon, {
                                            icon: "mdi-code-braces",
                                            color: "primary",
                                            size: "small"
                                          })
                                        ]),
                                        append: _withCtx(() => [
                                          _createElementVNode("code", _hoisted_3, _toDisplayString(_ctx.statusData.cron || '未设置'), 1)
                                        ]),
                                        default: _withCtx(() => [
                                          _createVNode(_component_v_list_item_title, { class: "text-caption" }, {
                                            default: _withCtx(() => _cache[18] || (_cache[18] = [
                                              _createTextVNode("CRON表达式")
                                            ])),
                                            _: 1
                                          })
                                        ]),
                                        _: 1
                                      }),
                                      _createVNode(_component_v_divider, { class: "my-1" }),
                                      _createVNode(_component_v_list_item, { class: "px-3 py-1" }, {
                                        prepend: _withCtx(() => [
                                          _createVNode(_component_v_icon, {
                                            icon: "mdi-clock-time-five",
                                            color: "amber-darken-2",
                                            size: "small"
                                          })
                                        ]),
                                        append: _withCtx(() => [
                                          _createElementVNode("span", _hoisted_4, _toDisplayString(_ctx.statusData.next_run_time || '未知'), 1)
                                        ]),
                                        default: _withCtx(() => [
                                          _createVNode(_component_v_list_item_title, { class: "text-caption" }, {
                                            default: _withCtx(() => _cache[19] || (_cache[19] = [
                                              _createTextVNode("下次运行")
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
                              }),
                              _createVNode(_component_v_divider),
                              _createVNode(_component_v_card_actions, { class: "px-3 py-2" })
                            ]),
                            _: 1
                          })
                        ]),
                        _: 1
                      }),
                      _createVNode(_component_v_col, {
                        cols: "12",
                        md: "6"
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
                                    icon: "mdi-folder-search",
                                    class: "mr-2",
                                    color: "primary",
                                    size: "small"
                                  }),
                                  _cache[20] || (_cache[20] = _createElementVNode("span", null, "监控路径", -1)),
                                  _createVNode(_component_v_chip, {
                                    class: "ml-1",
                                    size: "x-small",
                                    color: "info",
                                    variant: "flat"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(_ctx.pathStats.length || 0) + " 个路径", 1)
                                    ]),
                                    _: 1
                                  })
                                ]),
                                _: 1
                              }),
                              _createVNode(_component_v_card_text, { class: "pa-0" }, {
                                default: _withCtx(() => [
                                  (!_ctx.pathStats.length)
                                    ? (_openBlock(), _createElementBlock("div", _hoisted_5, [
                                        _createVNode(_component_v_icon, {
                                          icon: "mdi-folder-off",
                                          size: "small",
                                          class: "mb-1"
                                        }),
                                        _cache[21] || (_cache[21] = _createElementVNode("div", { class: "text-caption" }, "未设置任何监控路径", -1))
                                      ]))
                                    : (_openBlock(), _createBlock(_component_v_list, {
                                        key: 1,
                                        class: "pa-0 bg-transparent",
                                        density: "compact"
                                      }, {
                                        default: _withCtx(() => [
                                          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(_ctx.pathStats, (path, index) => {
                                            return (_openBlock(), _createBlock(_component_v_list_item, {
                                              key: index,
                                              class: "px-3 py-1"
                                            }, {
                                              prepend: _withCtx(() => [
                                                _createVNode(_component_v_icon, {
                                                  icon: path.exists ? 'mdi-folder' : 'mdi-folder-off',
                                                  color: path.exists ? 'amber-darken-2' : 'grey',
                                                  size: "small",
                                                  class: "mr-2"
                                                }, null, 8, ["icon", "color"])
                                              ]),
                                              append: _withCtx(() => [
                                                _createVNode(_component_v_chip, {
                                                  size: "x-small",
                                                  color: path.exists ? (path.status === 'valid' ? 'success' : 'error') : 'grey',
                                                  variant: "flat"
                                                }, {
                                                  default: _withCtx(() => [
                                                    _createTextVNode(_toDisplayString(path.exists ? (path.status === 'valid' ? '可用' : '错误') : '不存在'), 1)
                                                  ]),
                                                  _: 2
                                                }, 1032, ["color"])
                                              ]),
                                              default: _withCtx(() => [
                                                _createVNode(_component_v_list_item_title, { class: "text-caption" }, {
                                                  default: _withCtx(() => [
                                                    _createTextVNode(_toDisplayString(path.path), 1)
                                                  ]),
                                                  _: 2
                                                }, 1024)
                                              ]),
                                              _: 2
                                            }, 1024))
                                          }), 128))
                                        ]),
                                        _: 1
                                      }))
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
                                    icon: "mdi-folder-remove",
                                    class: "mr-2",
                                    color: "primary",
                                    size: "small"
                                  }),
                                  _cache[22] || (_cache[22] = _createElementVNode("span", null, "排除目录", -1)),
                                  _createVNode(_component_v_chip, {
                                    class: "ml-1",
                                    size: "x-small",
                                    color: "info",
                                    variant: "flat"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(_ctx.statusData.exclude_dirs?.length || 0) + " 个目录", 1)
                                    ]),
                                    _: 1
                                  })
                                ]),
                                _: 1
                              }),
                              _createVNode(_component_v_card_text, { class: "pa-0" }, {
                                default: _withCtx(() => [
                                  (!_ctx.statusData.exclude_dirs?.length)
                                    ? (_openBlock(), _createElementBlock("div", _hoisted_6, [
                                        _createVNode(_component_v_icon, {
                                          icon: "mdi-folder-off",
                                          size: "small",
                                          class: "mb-1"
                                        }),
                                        _cache[23] || (_cache[23] = _createElementVNode("div", { class: "text-caption" }, "未设置任何排除目录", -1))
                                      ]))
                                    : (_openBlock(), _createBlock(_component_v_list, {
                                        key: 1,
                                        class: "pa-0 bg-transparent",
                                        density: "compact"
                                      }, {
                                        default: _withCtx(() => [
                                          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(_ctx.statusData.exclude_dirs, (path, index) => {
                                            return (_openBlock(), _createBlock(_component_v_list_item, {
                                              key: index,
                                              class: "px-3 py-1"
                                            }, {
                                              prepend: _withCtx(() => [
                                                _createVNode(_component_v_icon, {
                                                  icon: "mdi-folder-remove",
                                                  color: "error",
                                                  size: "small",
                                                  class: "mr-2"
                                                })
                                              ]),
                                              default: _withCtx(() => [
                                                _createVNode(_component_v_list_item_title, { class: "text-caption" }, {
                                                  default: _withCtx(() => [
                                                    _createTextVNode(_toDisplayString(path), 1)
                                                  ]),
                                                  _: 2
                                                }, 1024)
                                              ]),
                                              _: 2
                                            }, 1024))
                                          }), 128))
                                        ]),
                                        _: 1
                                      }))
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
                  (_ctx.statusData.only_when_no_download)
                    ? (_openBlock(), _createBlock(_component_v_card, {
                        key: 0,
                        flat: "",
                        class: "rounded mb-3 border config-card"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_card_title, { class: "text-caption d-flex align-center justify-space-between px-3 py-2 bg-primary-lighten-5" }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_7, [
                                _createVNode(_component_v_icon, {
                                  icon: "mdi-download-network",
                                  class: "mr-2",
                                  color: "primary",
                                  size: "small"
                                }),
                                _cache[24] || (_cache[24] = _createElementVNode("span", null, "下载器监控状态", -1))
                              ]),
                              _createVNode(_component_v_chip, {
                                size: "x-small",
                                color: _ctx.downloadersHaveActiveTasks ? 'warning' : 'success',
                                variant: "flat"
                              }, {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(_ctx.downloadersHaveActiveTasks ? '有活动任务' : '无活动任务'), 1)
                                ]),
                                _: 1
                              }, 8, ["color"])
                            ]),
                            _: 1
                          }),
                          _createVNode(_component_v_card_text, { class: "pa-0" }, {
                            default: _withCtx(() => [
                              (_ctx.loadingDownloaders)
                                ? (_openBlock(), _createElementBlock("div", _hoisted_8, [
                                    _createVNode(_component_v_progress_circular, {
                                      indeterminate: "",
                                      color: "primary",
                                      size: "24"
                                    })
                                  ]))
                                : (!_ctx.downloaders.length)
                                  ? (_openBlock(), _createElementBlock("div", _hoisted_9, [
                                      _createVNode(_component_v_icon, {
                                        icon: "mdi-download-off",
                                        size: "small",
                                        class: "mb-1"
                                      }),
                                      _cache[25] || (_cache[25] = _createElementVNode("div", { class: "text-caption" }, "未找到可用的下载器", -1))
                                    ]))
                                  : (_openBlock(), _createElementBlock("div", _hoisted_10, [
                                      _createElementVNode("div", _hoisted_11, [
                                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(_ctx.downloaders, (downloader, index) => {
                                          return (_openBlock(), _createBlock(_component_v_card, {
                                            key: index,
                                            color: downloader.hasActiveTasks ? 'warning-lighten-5' : 'success-lighten-5',
                                            class: "downloader-card",
                                            flat: "",
                                            rounded: "",
                                            elevation: "0"
                                          }, {
                                            default: _withCtx(() => [
                                              _createElementVNode("div", _hoisted_12, [
                                                _createVNode(_component_v_avatar, {
                                                  size: "40",
                                                  color: downloader.hasActiveTasks ? 'warning-lighten-4' : 'success-lighten-4',
                                                  class: "mr-3"
                                                }, {
                                                  default: _withCtx(() => [
                                                    _createVNode(_component_v_icon, {
                                                      icon: downloader.hasActiveTasks ? 'mdi-download' : 'mdi-check-circle',
                                                      color: downloader.hasActiveTasks ? 'warning-darken-1' : 'success-darken-1'
                                                    }, null, 8, ["icon", "color"])
                                                  ]),
                                                  _: 2
                                                }, 1032, ["color"]),
                                                _createElementVNode("div", null, [
                                                  _createElementVNode("div", _hoisted_13, _toDisplayString(downloader.name), 1),
                                                  _createElementVNode("div", _hoisted_14, _toDisplayString(downloader.hasActiveTasks ? `${downloader.count || '0'} 个活动任务` : '空闲'), 1)
                                                ]),
                                                _createVNode(_component_v_spacer),
                                                _createVNode(_component_v_chip, {
                                                  size: "small",
                                                  color: downloader.hasActiveTasks ? 'warning' : 'success',
                                                  variant: "tonal",
                                                  class: "ml-2"
                                                }, {
                                                  default: _withCtx(() => [
                                                    _createTextVNode(_toDisplayString(downloader.hasActiveTasks ? '运行中' : '可清理'), 1)
                                                  ]),
                                                  _: 2
                                                }, 1032, ["color"])
                                              ]),
                                              (downloader.hasActiveTasks && downloader.activeTasks && downloader.activeTasks.length > 0)
                                                ? (_openBlock(), _createElementBlock(_Fragment, { key: 0 }, [
                                                    _createVNode(_component_v_divider),
                                                    _createVNode(_component_v_expansion_panels, {
                                                      variant: "accordion",
                                                      class: "mt-1"
                                                    }, {
                                                      default: _withCtx(() => [
                                                        _createVNode(_component_v_expansion_panel, null, {
                                                          default: _withCtx(() => [
                                                            _createVNode(_component_v_expansion_panel_title, {
                                                              class: "py-1 px-3",
                                                              density: "compact"
                                                            }, {
                                                              default: _withCtx(() => [
                                                                _createElementVNode("div", _hoisted_15, [
                                                                  _createVNode(_component_v_icon, {
                                                                    icon: "mdi-download-network",
                                                                    size: "small",
                                                                    class: "mr-1"
                                                                  }),
                                                                  _createElementVNode("span", null, "活动任务 (" + _toDisplayString(downloader.count) + ")", 1)
                                                                ])
                                                              ]),
                                                              _: 2
                                                            }, 1024),
                                                            _createVNode(_component_v_expansion_panel_text, { class: "py-1 px-0" }, {
                                                              default: _withCtx(() => [
                                                                _createElementVNode("div", _hoisted_16, [
                                                                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(downloader.activeTasks, (task, taskIndex) => {
                                                                    return (_openBlock(), _createElementBlock("div", {
                                                                      key: taskIndex,
                                                                      class: "task-item py-2 px-3"
                                                                    }, [
                                                                      _createElementVNode("div", _hoisted_17, [
                                                                        _createVNode(_component_v_icon, {
                                                                          icon: "mdi-download",
                                                                          size: "small",
                                                                          class: "mr-2",
                                                                          color: "warning"
                                                                        }),
                                                                        _createElementVNode("div", {
                                                                          class: "text-subtitle-2 text-truncate",
                                                                          title: task.name
                                                                        }, _toDisplayString(task.name), 9, _hoisted_18)
                                                                      ]),
                                                                      _createElementVNode("div", _hoisted_19, [
                                                                        _createVNode(_component_v_progress_linear, {
                                                                          modelValue: task.progress,
                                                                          "onUpdate:modelValue": $event => ((task.progress) = $event),
                                                                          color: "warning",
                                                                          height: "6",
                                                                          class: "rounded-lg flex-grow-1"
                                                                        }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                                                                        _createElementVNode("span", _hoisted_20, _toDisplayString(task.progress.toFixed(1)) + "%", 1)
                                                                      ]),
                                                                      _createElementVNode("div", _hoisted_21, [
                                                                        _createElementVNode("span", _hoisted_22, [
                                                                          _createVNode(_component_v_icon, {
                                                                            icon: "mdi-speedometer",
                                                                            size: "x-small",
                                                                            class: "mr-1"
                                                                          }),
                                                                          _createTextVNode(" " + _toDisplayString(_ctx.formatSpeed(task.dlspeed)), 1)
                                                                        ]),
                                                                        _createElementVNode("span", _hoisted_23, [
                                                                          _createVNode(_component_v_icon, {
                                                                            icon: "mdi-clock-outline",
                                                                            size: "x-small",
                                                                            class: "mr-1"
                                                                          }),
                                                                          _createTextVNode(" " + _toDisplayString(_ctx.formatETA(task.eta)), 1)
                                                                        ]),
                                                                        _createElementVNode("span", _hoisted_24, [
                                                                          _createVNode(_component_v_icon, {
                                                                            icon: "mdi-harddisk",
                                                                            size: "x-small",
                                                                            class: "mr-1"
                                                                          }),
                                                                          _createTextVNode(" " + _toDisplayString(_ctx.formatSize(task.size)), 1)
                                                                        ])
                                                                      ])
                                                                    ]))
                                                                  }), 128))
                                                                ])
                                                              ]),
                                                              _: 2
                                                            }, 1024)
                                                          ]),
                                                          _: 2
                                                        }, 1024)
                                                      ]),
                                                      _: 2
                                                    }, 1024)
                                                  ], 64))
                                                : _createCommentVNode("", true)
                                            ]),
                                            _: 2
                                          }, 1032, ["color"]))
                                        }), 128))
                                      ])
                                    ]))
                            ]),
                            _: 1
                          })
                        ]),
                        _: 1
                      }))
                    : _createCommentVNode("", true),
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
                          _cache[26] || (_cache[26] = _createElementVNode("span", null, "清理规则", -1))
                        ]),
                        _: 1
                      }),
                      _createVNode(_component_v_card_text, { class: "pa-0" }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_list, { class: "bg-transparent pa-0" }, {
                            default: _withCtx(() => [
                              _createVNode(_component_v_list_item, { class: "px-3 py-1" }, {
                                prepend: _withCtx(() => [
                                  _createVNode(_component_v_icon, {
                                    color: _ctx.cleanupRules.empty_dir ? 'success' : 'grey',
                                    icon: "mdi-folder-remove",
                                    size: "small"
                                  }, null, 8, ["color"])
                                ]),
                                append: _withCtx(() => [
                                  _createVNode(_component_v_chip, {
                                    color: _ctx.cleanupRules.empty_dir ? 'success' : 'grey',
                                    size: "x-small",
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(_ctx.cleanupRules.empty_dir ? '已启用' : '已禁用'), 1)
                                    ]),
                                    _: 1
                                  }, 8, ["color"])
                                ]),
                                default: _withCtx(() => [
                                  _createVNode(_component_v_list_item_title, { class: "text-caption" }, {
                                    default: _withCtx(() => _cache[27] || (_cache[27] = [
                                      _createTextVNode("清理空目录")
                                    ])),
                                    _: 1
                                  })
                                ]),
                                _: 1
                              }),
                              _createVNode(_component_v_divider, { class: "my-1" }),
                              _createVNode(_component_v_list_item, { class: "px-3 py-1" }, {
                                prepend: _withCtx(() => [
                                  _createVNode(_component_v_icon, {
                                    color: _ctx.cleanupRules.small_dir.enabled ? 'warning' : 'grey',
                                    icon: "mdi-weight",
                                    size: "small"
                                  }, null, 8, ["color"])
                                ]),
                                append: _withCtx(() => [
                                  (_ctx.cleanupRules.small_dir.enabled)
                                    ? (_openBlock(), _createElementBlock("span", _hoisted_25, " 最大体积 " + _toDisplayString(_ctx.cleanupRules.small_dir.max_size) + "MB ", 1))
                                    : _createCommentVNode("", true),
                                  _createVNode(_component_v_chip, {
                                    color: _ctx.cleanupRules.small_dir.enabled ? 'warning' : 'grey',
                                    size: "x-small",
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(_ctx.cleanupRules.small_dir.enabled ? '已启用' : '已禁用'), 1)
                                    ]),
                                    _: 1
                                  }, 8, ["color"])
                                ]),
                                default: _withCtx(() => [
                                  _createVNode(_component_v_list_item_title, { class: "text-caption" }, {
                                    default: _withCtx(() => _cache[28] || (_cache[28] = [
                                      _createTextVNode("清理小体积目录")
                                    ])),
                                    _: 1
                                  })
                                ]),
                                _: 1
                              }),
                              _createVNode(_component_v_divider, { class: "my-1" }),
                              _createVNode(_component_v_list_item, { class: "px-3 py-1" }, {
                                prepend: _withCtx(() => [
                                  _createVNode(_component_v_icon, {
                                    color: _ctx.cleanupRules.size_reduction.enabled ? 'error' : 'grey',
                                    icon: "mdi-chart-line-variant",
                                    size: "small"
                                  }, null, 8, ["color"])
                                ]),
                                append: _withCtx(() => [
                                  (_ctx.cleanupRules.size_reduction.enabled)
                                    ? (_openBlock(), _createElementBlock("span", _hoisted_26, " 减少阈值 " + _toDisplayString(_ctx.cleanupRules.size_reduction.threshold) + "% ", 1))
                                    : _createCommentVNode("", true),
                                  _createVNode(_component_v_chip, {
                                    color: _ctx.cleanupRules.size_reduction.enabled ? 'error' : 'grey',
                                    size: "x-small",
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(_ctx.cleanupRules.size_reduction.enabled ? '已启用' : '已禁用'), 1)
                                    ]),
                                    _: 1
                                  }, 8, ["color"])
                                ]),
                                default: _withCtx(() => [
                                  _createVNode(_component_v_list_item_title, { class: "text-caption" }, {
                                    default: _withCtx(() => _cache[29] || (_cache[29] = [
                                      _createTextVNode("清理体积减少目录")
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
                      })
                    ]),
                    _: 1
                  }),
                  (_ctx.pathStats.length)
                    ? (_openBlock(), _createBlock(_component_v_card, {
                        key: 1,
                        flat: "",
                        class: "rounded mb-3 border config-card"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_card_title, { class: "text-caption d-flex align-center justify-space-between px-3 py-2 bg-primary-lighten-5" }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_27, [
                                _createVNode(_component_v_icon, {
                                  icon: "mdi-chart-bar",
                                  class: "mr-2",
                                  color: "primary",
                                  size: "small"
                                }),
                                _cache[30] || (_cache[30] = _createElementVNode("span", null, "目录统计", -1)),
                                (_ctx.lastStatsUpdate)
                                  ? (_openBlock(), _createBlock(_component_v_chip, {
                                      key: 0,
                                      size: "x-small",
                                      color: "info",
                                      variant: "flat",
                                      class: "ml-1"
                                    }, {
                                      default: _withCtx(() => [
                                        _createTextVNode(_toDisplayString(_ctx.lastStatsUpdate), 1)
                                      ]),
                                      _: 1
                                    }))
                                  : _createCommentVNode("", true)
                              ]),
                              _createVNode(_component_v_btn, {
                                size: "small",
                                color: "primary",
                                variant: "tonal",
                                loading: _ctx.updatingStats,
                                disabled: _ctx.updatingStats,
                                onClick: _ctx.updateStats,
                                class: "stats-update-btn"
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_v_icon, {
                                    icon: "mdi-refresh",
                                    size: "small",
                                    class: "mr-1"
                                  }),
                                  _cache[31] || (_cache[31] = _createElementVNode("span", null, "更新统计", -1))
                                ]),
                                _: 1
                              }, 8, ["loading", "disabled", "onClick"])
                            ]),
                            _: 1
                          }),
                          _createVNode(_component_v_card_text, { class: "pa-0" }, {
                            default: _withCtx(() => [
                              _createVNode(_component_v_table, {
                                density: "compact",
                                class: "text-body-2"
                              }, {
                                default: _withCtx(() => [
                                  _cache[32] || (_cache[32] = _createElementVNode("thead", null, [
                                    _createElementVNode("tr", null, [
                                      _createElementVNode("th", { class: "text-body-2 font-weight-bold" }, "路径"),
                                      _createElementVNode("th", { class: "text-body-2 font-weight-bold text-center" }, "总大小"),
                                      _createElementVNode("th", { class: "text-body-2 font-weight-bold text-center" }, "文件数"),
                                      _createElementVNode("th", { class: "text-body-2 font-weight-bold text-center" }, "子目录数")
                                    ])
                                  ], -1)),
                                  _createElementVNode("tbody", null, [
                                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(_ctx.validPathStats, (path, index) => {
                                      return (_openBlock(), _createElementBlock("tr", { key: index }, [
                                        _createElementVNode("td", null, [
                                          _createElementVNode("div", _hoisted_28, [
                                            _createVNode(_component_v_icon, {
                                              icon: "mdi-folder",
                                              size: "small",
                                              color: "amber-darken-2",
                                              class: "mr-2"
                                            }),
                                            _createElementVNode("span", _hoisted_29, _toDisplayString(path.path), 1)
                                          ])
                                        ]),
                                        _createElementVNode("td", _hoisted_30, _toDisplayString(_ctx.formatSize(path.total_size_bytes)), 1),
                                        _createElementVNode("td", _hoisted_31, _toDisplayString(path.file_count), 1),
                                        _createElementVNode("td", _hoisted_32, _toDisplayString(path.dir_count), 1)
                                      ]))
                                    }), 128))
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
                  (_ctx.cleanResult)
                    ? (_openBlock(), _createBlock(_component_v_card, {
                        key: 2,
                        flat: "",
                        class: "rounded mb-3 border config-card"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_card_title, { class: "text-caption d-flex align-center px-3 py-2 bg-primary-lighten-5" }, {
                            default: _withCtx(() => [
                              _createVNode(_component_v_icon, {
                                icon: "mdi-history",
                                class: "mr-2",
                                color: "primary",
                                size: "small"
                              }),
                              _cache[33] || (_cache[33] = _createElementVNode("span", null, "最近清理记录", -1)),
                              _createVNode(_component_v_chip, {
                                size: "x-small",
                                color: "success",
                                variant: "flat",
                                class: "ml-2"
                              }, {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(_ctx.formatDate(new Date())), 1)
                                ]),
                                _: 1
                              })
                            ]),
                            _: 1
                          }),
                          _createVNode(_component_v_card_text, { class: "pa-0" }, {
                            default: _withCtx(() => [
                              _createVNode(_component_v_alert, {
                                type: _ctx.cleanResult.status === 'success' ? 'success' : 'error',
                                variant: "tonal",
                                density: "compact",
                                class: "ma-2"
                              }, {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(_ctx.cleanResult.status === 'success' ? 
                  `清理成功，共删除 ${_ctx.cleanResult.removed_dirs.length} 个目录，释放 ${_ctx.cleanResult.total_freed_space.toFixed(2)}MB 空间` : 
                  _ctx.cleanResult.message || '清理失败'), 1)
                                ]),
                                _: 1
                              }, 8, ["type"]),
                              (_ctx.cleanResult.status === 'success' && _ctx.cleanResult.removed_dirs.length)
                                ? (_openBlock(), _createElementBlock("div", _hoisted_33, [
                                    _createVNode(_component_v_card, {
                                      flat: "",
                                      class: "ma-2 px-2 py-1 bg-grey-lighten-5"
                                    }, {
                                      default: _withCtx(() => [
                                        _createElementVNode("div", _hoisted_34, [
                                          _createVNode(_component_v_icon, {
                                            icon: "mdi-information-outline",
                                            size: "small",
                                            color: "info",
                                            class: "mr-2"
                                          }),
                                          _createElementVNode("span", _hoisted_35, "按类型统计：空目录(" + _toDisplayString(_ctx.cleanResult.removed_empty_dirs_count) + ")、小体积目录(" + _toDisplayString(_ctx.cleanResult.removed_small_dirs_count) + ")、体积减少目录(" + _toDisplayString(_ctx.cleanResult.removed_size_reduction_dirs_count) + ")", 1)
                                        ])
                                      ]),
                                      _: 1
                                    }),
                                    _createElementVNode("div", _hoisted_36, [
                                      _createElementVNode("div", _hoisted_37, [
                                        _cache[35] || (_cache[35] = _createElementVNode("span", null, "已删除的目录：", -1)),
                                        (_ctx.cleanResult.removed_dirs.length > 3)
                                          ? (_openBlock(), _createBlock(_component_v_btn, {
                                              key: 0,
                                              size: "x-small",
                                              color: "primary",
                                              variant: "text",
                                              onClick: _cache[0] || (_cache[0] = $event => (_ctx.showCleanResultDialog = true))
                                            }, {
                                              default: _withCtx(() => _cache[34] || (_cache[34] = [
                                                _createTextVNode(" 查看全部 ")
                                              ])),
                                              _: 1
                                            }))
                                          : _createCommentVNode("", true)
                                      ])
                                    ]),
                                    _createVNode(_component_v_list, {
                                      density: "compact",
                                      class: "pa-0"
                                    }, {
                                      default: _withCtx(() => [
                                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(_ctx.cleanResult.removed_dirs.slice(0, 3), (dir, index) => {
                                          return (_openBlock(), _createBlock(_component_v_list_item, {
                                            key: index,
                                            class: "clean-history-item"
                                          }, {
                                            prepend: _withCtx(() => [
                                              _createVNode(_component_v_avatar, {
                                                color: _ctx.getCleanTypeColor(dir.type) + '-lighten-4',
                                                size: "28",
                                                class: "mr-2"
                                              }, {
                                                default: _withCtx(() => [
                                                  _createVNode(_component_v_icon, {
                                                    icon: _ctx.getCleanTypeIcon(dir.type),
                                                    size: "small",
                                                    color: _ctx.getCleanTypeColor(dir.type)
                                                  }, null, 8, ["icon", "color"])
                                                ]),
                                                _: 2
                                              }, 1032, ["color"])
                                            ]),
                                            append: _withCtx(() => [
                                              _createElementVNode("div", _hoisted_38, [
                                                (dir.type === 'small')
                                                  ? (_openBlock(), _createElementBlock("span", _hoisted_39, _toDisplayString(dir.size.toFixed(2)) + "MB", 1))
                                                  : _createCommentVNode("", true),
                                                (dir.type === 'size_reduction')
                                                  ? (_openBlock(), _createElementBlock("span", _hoisted_40, "减少" + _toDisplayString(dir.reduction_percent.toFixed(0)) + "%", 1))
                                                  : _createCommentVNode("", true),
                                                _createVNode(_component_v_chip, {
                                                  size: "x-small",
                                                  color: _ctx.getCleanTypeColor(dir.type),
                                                  variant: "flat",
                                                  class: "clean-type-chip"
                                                }, {
                                                  default: _withCtx(() => [
                                                    _createTextVNode(_toDisplayString(_ctx.getCleanTypeText(dir.type)), 1)
                                                  ]),
                                                  _: 2
                                                }, 1032, ["color"])
                                              ])
                                            ]),
                                            default: _withCtx(() => [
                                              _createVNode(_component_v_list_item_title, { class: "text-body-2 clean-dir-path" }, {
                                                default: _withCtx(() => [
                                                  _createTextVNode(_toDisplayString(dir.path), 1)
                                                ]),
                                                _: 2
                                              }, 1024)
                                            ]),
                                            _: 2
                                          }, 1024))
                                        }), 128)),
                                        (_ctx.cleanResult.removed_dirs.length > 3)
                                          ? (_openBlock(), _createBlock(_component_v_list_item, {
                                              key: 0,
                                              class: "text-center py-1"
                                            }, {
                                              default: _withCtx(() => [
                                                _createVNode(_component_v_btn, {
                                                  size: "small",
                                                  color: "primary",
                                                  variant: "text",
                                                  onClick: _cache[1] || (_cache[1] = $event => (_ctx.showCleanResultDialog = true)),
                                                  class: "mx-auto"
                                                }, {
                                                  default: _withCtx(() => [
                                                    _createVNode(_component_v_icon, {
                                                      size: "small",
                                                      class: "mr-1"
                                                    }, {
                                                      default: _withCtx(() => _cache[36] || (_cache[36] = [
                                                        _createTextVNode("mdi-dots-horizontal")
                                                      ])),
                                                      _: 1
                                                    }),
                                                    _createTextVNode(" 查看全部 " + _toDisplayString(_ctx.cleanResult.removed_dirs.length) + " 个目录 ", 1)
                                                  ]),
                                                  _: 1
                                                })
                                              ]),
                                              _: 1
                                            }))
                                          : _createCommentVNode("", true)
                                      ]),
                                      _: 1
                                    })
                                  ]))
                                : (_ctx.cleanResult.status === 'success' && _ctx.cleanResult.removed_dirs.length === 0)
                                  ? (_openBlock(), _createElementBlock("div", _hoisted_41, [
                                      _createVNode(_component_v_icon, {
                                        icon: "mdi-information-outline",
                                        size: "large",
                                        color: "info",
                                        class: "mb-2"
                                      }),
                                      _cache[37] || (_cache[37] = _createElementVNode("div", null, "没有符合清理条件的目录", -1))
                                    ]))
                                  : _createCommentVNode("", true)
                            ]),
                            _: 1
                          })
                        ]),
                        _: 1
                      }))
                    : _createCommentVNode("", true),
                  _createVNode(_component_v_card, {
                    flat: "",
                    class: "rounded mb-3 border config-card"
                  }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_card_title, { class: "text-caption d-flex align-center px-3 py-2 bg-primary-lighten-5" }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_icon, {
                            icon: "mdi-history",
                            class: "mr-2",
                            color: "primary",
                            size: "small"
                          }),
                          _cache[38] || (_cache[38] = _createElementVNode("span", null, "清理历史", -1))
                        ]),
                        _: 1
                      }),
                      _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                        default: _withCtx(() => [
                          (!_ctx.cleanHistory.length)
                            ? (_openBlock(), _createElementBlock("div", _hoisted_42, [
                                _createVNode(_component_v_icon, {
                                  icon: "mdi-information-outline",
                                  size: "small",
                                  class: "mb-1"
                                }),
                                _cache[39] || (_cache[39] = _createElementVNode("div", { class: "text-caption" }, "暂无清理历史记录", -1))
                              ]))
                            : (_openBlock(), _createBlock(_component_v_timeline, {
                                key: 1,
                                density: "compact",
                                align: "start",
                                "truncate-line": "both",
                                class: "mt-0"
                              }, {
                                default: _withCtx(() => [
                                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(_ctx.cleanHistory.slice(0, 3), (item, index) => {
                                    return (_openBlock(), _createBlock(_component_v_timeline_item, {
                                      key: index,
                                      "dot-color": _ctx.getHistoryColor(index),
                                      size: "x-small"
                                    }, {
                                      icon: _withCtx(() => [
                                        _createVNode(_component_v_icon, { size: "x-small" }, {
                                          default: _withCtx(() => _cache[40] || (_cache[40] = [
                                            _createTextVNode("mdi-broom")
                                          ])),
                                          _: 1
                                        })
                                      ]),
                                      default: _withCtx(() => [
                                        _createElementVNode("div", _hoisted_43, [
                                          _createElementVNode("span", _hoisted_44, _toDisplayString(_ctx.formatDate(new Date(item.last_update))), 1),
                                          _createVNode(_component_v_chip, {
                                            size: "x-small",
                                            color: _ctx.getHistoryColor(index),
                                            variant: "flat"
                                          }, {
                                            default: _withCtx(() => [
                                              _createTextVNode(" #" + _toDisplayString(index + 1), 1)
                                            ]),
                                            _: 2
                                          }, 1032, ["color"])
                                        ]),
                                        _createElementVNode("div", _hoisted_45, [
                                          _cache[41] || (_cache[41] = _createTextVNode(" 清理 ")),
                                          _createElementVNode("strong", null, _toDisplayString(item.removed_dirs.length), 1),
                                          _createTextVNode(" 个目录 (释放 " + _toDisplayString(item.total_freed_space.toFixed(2)) + "MB) ", 1)
                                        ])
                                      ]),
                                      _: 2
                                    }, 1032, ["dot-color"]))
                                  }), 128)),
                                  (_ctx.cleanHistory.length > 3)
                                    ? (_openBlock(), _createBlock(_component_v_timeline_item, {
                                        key: 0,
                                        "dot-color": "primary",
                                        size: "x-small"
                                      }, {
                                        icon: _withCtx(() => [
                                          _createVNode(_component_v_icon, { size: "x-small" }, {
                                            default: _withCtx(() => _cache[42] || (_cache[42] = [
                                              _createTextVNode("mdi-dots-horizontal")
                                            ])),
                                            _: 1
                                          })
                                        ]),
                                        default: _withCtx(() => [
                                          _createElementVNode("div", _hoisted_46, [
                                            _createElementVNode("span", _hoisted_47, "还有 " + _toDisplayString(_ctx.cleanHistory.length - 3) + " 条历史记录", 1),
                                            _createVNode(_component_v_btn, {
                                              variant: "text",
                                              density: "comfortable",
                                              size: "x-small",
                                              color: "primary",
                                              class: "ml-2",
                                              onClick: _cache[2] || (_cache[2] = $event => (_ctx.showHistoryDialog = true))
                                            }, {
                                              default: _withCtx(() => _cache[43] || (_cache[43] = [
                                                _createTextVNode(" 查看更多 ")
                                              ])),
                                              _: 1
                                            })
                                          ])
                                        ]),
                                        _: 1
                                      }))
                                    : _createCommentVNode("", true)
                                ]),
                                _: 1
                              }))
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
                      _createVNode(_component_v_card_text, { class: "d-flex align-center px-3 py-2" }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_icon, {
                            icon: "mdi-information",
                            color: "info",
                            class: "mr-2",
                            size: "small"
                          }),
                          _cache[44] || (_cache[44] = _createElementVNode("span", { class: "text-caption" }, " 点击\"配置\"按钮可设置清理策略和监控目录。点击\"立即清理\"按钮可立即执行清理任务。 ", -1))
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  })
                ]))
              : _createCommentVNode("", true)
          ]),
          _: 1
        }),
        _createVNode(_component_v_divider),
        _createVNode(_component_v_card_actions, { class: "px-2 py-1" }, {
          default: _withCtx(() => [
            _createVNode(_component_v_btn, {
              color: "info",
              onClick: _ctx.refreshData,
              "prepend-icon": "mdi-refresh",
              disabled: _ctx.refreshing,
              loading: _ctx.refreshing,
              variant: "text",
              size: "small"
            }, {
              default: _withCtx(() => _cache[45] || (_cache[45] = [
                _createTextVNode("刷新数据")
              ])),
              _: 1
            }, 8, ["onClick", "disabled", "loading"]),
            _createVNode(_component_v_spacer),
            _createVNode(_component_v_btn, {
              color: "success",
              onClick: _ctx.triggerClean,
              loading: _ctx.actionLoading,
              disabled: _ctx.actionLoading || _ctx.cleanProgress.running,
              "prepend-icon": "mdi-broom",
              variant: "text",
              size: "small"
            }, {
              default: _withCtx(() => _cache[46] || (_cache[46] = [
                _createTextVNode(" 立即清理 ")
              ])),
              _: 1
            }, 8, ["onClick", "loading", "disabled"]),
            _createVNode(_component_v_btn, {
              color: "primary",
              onClick: _cache[3] || (_cache[3] = $event => (_ctx.emit('switch'))),
              "prepend-icon": "mdi-cog",
              variant: "text",
              size: "small"
            }, {
              default: _withCtx(() => _cache[47] || (_cache[47] = [
                _createTextVNode("配置")
              ])),
              _: 1
            }),
            _createVNode(_component_v_btn, {
              color: "grey",
              onClick: _cache[4] || (_cache[4] = $event => (_ctx.emit('close'))),
              "prepend-icon": "mdi-close",
              variant: "text",
              size: "small"
            }, {
              default: _withCtx(() => _cache[48] || (_cache[48] = [
                _createTextVNode("关闭")
              ])),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }),
    _createVNode(_component_v_dialog, {
      modelValue: _ctx.showCleanResultDialog,
      "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((_ctx.showCleanResultDialog) = $event)),
      "max-width": "600"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, { class: "text-subtitle-1 d-flex align-center px-3 py-2 bg-primary-lighten-5" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-broom",
                  class: "mr-2",
                  color: "primary"
                }),
                _cache[49] || (_cache[49] = _createElementVNode("span", null, "清理结果", -1))
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
              default: _withCtx(() => [
                (_ctx.cleanResult)
                  ? (_openBlock(), _createElementBlock("div", _hoisted_48, [
                      _createVNode(_component_v_alert, {
                        type: _ctx.cleanResult.status === 'success' ? 'success' : 'error',
                        variant: "tonal",
                        density: "compact",
                        class: "mb-3"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(_ctx.cleanResult.status === 'success' ? 
                `清理成功，共删除 ${_ctx.cleanResult.removed_dirs.length} 个目录，释放 ${_ctx.cleanResult.total_freed_space.toFixed(2)}MB 空间` : 
                _ctx.cleanResult.message || '清理失败'), 1)
                        ]),
                        _: 1
                      }, 8, ["type"]),
                      (_ctx.cleanResult.status === 'success' && _ctx.cleanResult.removed_dirs.length)
                        ? (_openBlock(), _createElementBlock("div", _hoisted_49, [
                            _cache[50] || (_cache[50] = _createElementVNode("div", { class: "text-subtitle-2 mb-2" }, "已删除的目录：", -1)),
                            _createVNode(_component_v_list, {
                              density: "compact",
                              class: "bg-grey-lighten-5 rounded"
                            }, {
                              default: _withCtx(() => [
                                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(_ctx.cleanResult.removed_dirs, (dir, index) => {
                                  return (_openBlock(), _createBlock(_component_v_list_item, {
                                    key: index,
                                    class: "py-1"
                                  }, {
                                    prepend: _withCtx(() => [
                                      _createVNode(_component_v_icon, {
                                        icon: "mdi-folder-remove",
                                        size: "small",
                                        color: _ctx.getCleanTypeColor(dir.type),
                                        class: "mr-2"
                                      }, null, 8, ["color"])
                                    ]),
                                    append: _withCtx(() => [
                                      _createVNode(_component_v_chip, {
                                        size: "x-small",
                                        color: _ctx.getCleanTypeColor(dir.type),
                                        variant: "flat"
                                      }, {
                                        default: _withCtx(() => [
                                          _createTextVNode(_toDisplayString(_ctx.getCleanTypeText(dir.type)) + " " + _toDisplayString(dir.type === 'size_reduction' ? `(${dir.reduction_percent.toFixed(0)}%)` : 
                         dir.type === 'small' ? `(${dir.size.toFixed(2)}MB)` : ''), 1)
                                        ]),
                                        _: 2
                                      }, 1032, ["color"])
                                    ]),
                                    default: _withCtx(() => [
                                      _createVNode(_component_v_list_item_title, { class: "text-caption" }, {
                                        default: _withCtx(() => [
                                          _createTextVNode(_toDisplayString(dir.path), 1)
                                        ]),
                                        _: 2
                                      }, 1024)
                                    ]),
                                    _: 2
                                  }, 1024))
                                }), 128))
                              ]),
                              _: 1
                            })
                          ]))
                        : _createCommentVNode("", true),
                      (_ctx.cleanResult.status === 'success' && _ctx.cleanResult.removed_dirs.length === 0)
                        ? (_openBlock(), _createElementBlock("div", _hoisted_50, [
                            _createVNode(_component_v_icon, {
                              icon: "mdi-information-outline",
                              size: "large",
                              color: "info",
                              class: "mb-2"
                            }),
                            _cache[51] || (_cache[51] = _createElementVNode("div", null, "没有符合清理条件的目录", -1))
                          ]))
                        : _createCommentVNode("", true)
                    ]))
                  : _createCommentVNode("", true)
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, { class: "px-3 py-2" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  color: "primary",
                  variant: "text",
                  onClick: _cache[5] || (_cache[5] = $event => (_ctx.showCleanResultDialog = false))
                }, {
                  default: _withCtx(() => _cache[52] || (_cache[52] = [
                    _createTextVNode("关闭")
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
      modelValue: _ctx.showHistoryDialog,
      "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((_ctx.showHistoryDialog) = $event)),
      "max-width": "600px"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, { class: "text-subtitle-1 d-flex align-center px-4 py-3 bg-primary-lighten-5" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-history",
                  class: "mr-2",
                  color: "primary"
                }),
                _cache[53] || (_cache[53] = _createElementVNode("span", null, "清理历史记录", -1))
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_text, { class: "pa-4" }, {
              default: _withCtx(() => [
                (_ctx.cleanHistory.length)
                  ? (_openBlock(), _createBlock(_component_v_timeline, {
                      key: 0,
                      density: "compact",
                      align: "start"
                    }, {
                      default: _withCtx(() => [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(_ctx.cleanHistory, (item, index) => {
                          return (_openBlock(), _createBlock(_component_v_timeline_item, {
                            key: index,
                            "dot-color": _ctx.getHistoryColor(index),
                            size: "small"
                          }, {
                            icon: _withCtx(() => [
                              _createVNode(_component_v_icon, { size: "x-small" }, {
                                default: _withCtx(() => _cache[54] || (_cache[54] = [
                                  _createTextVNode("mdi-broom")
                                ])),
                                _: 1
                              })
                            ]),
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_51, [
                                _createElementVNode("span", _hoisted_52, _toDisplayString(_ctx.formatDate(new Date(item.last_update))), 1),
                                _createVNode(_component_v_chip, {
                                  size: "x-small",
                                  color: _ctx.getHistoryColor(index),
                                  variant: "flat"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode(" #" + _toDisplayString(index + 1), 1)
                                  ]),
                                  _: 2
                                }, 1032, ["color"])
                              ]),
                              _createElementVNode("div", _hoisted_53, [
                                _cache[55] || (_cache[55] = _createTextVNode(" 清理 ")),
                                _createElementVNode("strong", null, _toDisplayString(item.removed_dirs.length), 1),
                                _createTextVNode(" 个目录 (释放 " + _toDisplayString(item.total_freed_space.toFixed(2)) + "MB 空间) ", 1)
                              ]),
                              _createElementVNode("div", _hoisted_54, [
                                _createVNode(_component_v_chip, {
                                  size: "x-small",
                                  color: "success",
                                  variant: "flat",
                                  class: "mr-1 mb-1"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode(" 空目录: " + _toDisplayString(item.removed_empty_dirs_count), 1)
                                  ]),
                                  _: 2
                                }, 1024),
                                _createVNode(_component_v_chip, {
                                  size: "x-small",
                                  color: "warning",
                                  variant: "flat",
                                  class: "mr-1 mb-1"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode(" 小体积目录: " + _toDisplayString(item.removed_small_dirs_count), 1)
                                  ]),
                                  _: 2
                                }, 1024),
                                _createVNode(_component_v_chip, {
                                  size: "x-small",
                                  color: "error",
                                  variant: "flat",
                                  class: "mb-1"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode(" 体积减少目录: " + _toDisplayString(item.removed_size_reduction_dirs_count), 1)
                                  ]),
                                  _: 2
                                }, 1024)
                              ])
                            ]),
                            _: 2
                          }, 1032, ["dot-color"]))
                        }), 128))
                      ]),
                      _: 1
                    }))
                  : (_openBlock(), _createElementBlock("div", _hoisted_55, [
                      _createVNode(_component_v_icon, {
                        icon: "mdi-information-outline",
                        color: "grey",
                        class: "mr-2"
                      }),
                      _cache[56] || (_cache[56] = _createElementVNode("span", { class: "text-grey" }, "暂无清理历史记录", -1))
                    ]))
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, { class: "px-4 py-3" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  variant: "text",
                  color: "primary",
                  onClick: _cache[7] || (_cache[7] = $event => (_ctx.showHistoryDialog = false))
                }, {
                  default: _withCtx(() => _cache[57] || (_cache[57] = [
                    _createTextVNode("关闭")
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
      modelValue: _ctx.showUpdateStatsDialog,
      "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((_ctx.showUpdateStatsDialog) = $event)),
      persistent: "",
      "max-width": "400px"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, {
              class: _normalizeClass(["text-subtitle-1 d-flex align-center px-4 py-3", _ctx.updatingStats ? 'bg-primary-lighten-5' : 'bg-success-lighten-5'])
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: _ctx.updatingStats ? 'mdi-refresh' : 'mdi-check-circle',
                  class: "mr-2",
                  color: _ctx.updatingStats ? 'primary' : 'success'
                }, null, 8, ["icon", "color"]),
                _createElementVNode("span", null, _toDisplayString(_ctx.updatingStats ? '正在更新目录统计' : '更新完成'), 1)
              ]),
              _: 1
            }, 8, ["class"]),
            _createVNode(_component_v_card_text, { class: "pa-4" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_56, [
                  _createElementVNode("span", _hoisted_57, _toDisplayString(_ctx.updateStatsMessage || (_ctx.updatingStats ? '正在更新目录统计数据，请稍候...' : '目录统计数据更新完成！')), 1),
                  _createElementVNode("div", {
                    class: _normalizeClass(["text-h4 font-weight-bold mt-2", _ctx.updatingStats ? 'primary--text' : 'success--text'])
                  }, _toDisplayString(_ctx.updateStatsProgress) + "% ", 3)
                ]),
                _createVNode(_component_v_progress_linear, {
                  modelValue: _ctx.updateStatsProgress,
                  "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((_ctx.updateStatsProgress) = $event)),
                  color: _ctx.updatingStats ? 'primary' : 'success',
                  height: "10",
                  rounded: "",
                  striped: ""
                }, null, 8, ["modelValue", "color"]),
                (_ctx.updatingStats)
                  ? (_openBlock(), _createElementBlock("div", _hoisted_58, [
                      _createVNode(_component_v_icon, {
                        icon: "mdi-information-outline",
                        size: "x-small",
                        class: "mr-1"
                      }),
                      _cache[58] || (_cache[58] = _createTextVNode(" 该过程可能需要较长时间，您可以关闭此窗口，统计将在后台继续进行 "))
                    ]))
                  : _createCommentVNode("", true)
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, { class: "px-4 py-3" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  color: _ctx.updatingStats ? 'primary' : 'success',
                  variant: "text",
                  onClick: _cache[10] || (_cache[10] = $event => (_ctx.showUpdateStatsDialog = false)),
                  disabled: _ctx.updatingStats && _ctx.updateStatsProgress < 5
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(_ctx.updatingStats ? '关闭窗口（后台继续）' : '关闭'), 1)
                  ]),
                  _: 1
                }, 8, ["color", "disabled"])
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
      modelValue: _ctx.showCleanProgressDialog,
      "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((_ctx.showCleanProgressDialog) = $event)),
      persistent: "",
      "max-width": "600px"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, {
              class: _normalizeClass(["text-subtitle-1 d-flex align-center px-4 py-3", _ctx.getProgressStatusClass])
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: _ctx.getProgressStatusIcon,
                  class: "mr-2",
                  color: _ctx.getProgressStatusColor
                }, null, 8, ["icon", "color"]),
                _createElementVNode("span", null, _toDisplayString(_ctx.getProgressStatusText), 1)
              ]),
              _: 1
            }, 8, ["class"]),
            _createVNode(_component_v_card_text, { class: "pa-4" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_59, [
                  _createElementVNode("div", _hoisted_60, [
                    _createElementVNode("div", _hoisted_61, [
                      _createElementVNode("span", _hoisted_62, _toDisplayString(_ctx.cleanProgress.message), 1),
                      _createElementVNode("span", {
                        class: _normalizeClass(["text-h6 font-weight-bold", _ctx.getProgressStatusColor + '--text'])
                      }, _toDisplayString(_ctx.cleanProgress.percent.toFixed(0)) + "% ", 3)
                    ]),
                    _createVNode(_component_v_progress_linear, {
                      modelValue: _ctx.cleanProgress.percent,
                      "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((_ctx.cleanProgress.percent) = $event)),
                      color: _ctx.getProgressStatusColor,
                      height: "12",
                      rounded: "",
                      striped: ""
                    }, null, 8, ["modelValue", "color"])
                  ]),
                  _createElementVNode("div", {
                    class: _normalizeClass(["progress-details pa-3 rounded-lg", _ctx.getProgressInfoBgClass])
                  }, [
                    _createElementVNode("div", _hoisted_63, [
                      _createElementVNode("div", _hoisted_64, [
                        _createVNode(_component_v_icon, {
                          icon: "mdi-clock-time-five",
                          size: "small",
                          class: "mr-1"
                        }),
                        _createElementVNode("span", null, "开始时间: " + _toDisplayString(_ctx.formatDate(new Date(_ctx.cleanProgress.start_time || Date.now()))), 1)
                      ]),
                      _createElementVNode("div", _hoisted_65, [
                        _createVNode(_component_v_icon, {
                          icon: "mdi-folder-multiple",
                          size: "small",
                          class: "mr-1"
                        }),
                        _createElementVNode("span", null, "总目录数: " + _toDisplayString(_ctx.cleanProgress.total_dirs), 1)
                      ]),
                      _createElementVNode("div", _hoisted_66, [
                        _createVNode(_component_v_icon, {
                          icon: "mdi-folder-check",
                          size: "small",
                          class: "mr-1"
                        }),
                        _createElementVNode("span", null, "已处理: " + _toDisplayString(_ctx.cleanProgress.processed_dirs), 1)
                      ]),
                      _createElementVNode("div", _hoisted_67, [
                        _createVNode(_component_v_icon, {
                          icon: "mdi-delete",
                          size: "small",
                          class: "mr-1"
                        }),
                        _createElementVNode("span", null, "已清理: " + _toDisplayString(_ctx.cleanProgress.removed_dirs.length), 1)
                      ])
                    ]),
                    (_ctx.cleanProgress.current_dir)
                      ? (_openBlock(), _createElementBlock("div", _hoisted_68, [
                          _createVNode(_component_v_icon, {
                            icon: "mdi-folder-open",
                            size: "small",
                            class: "mr-1"
                          }),
                          _createElementVNode("span", _hoisted_69, "当前处理: " + _toDisplayString(_ctx.cleanProgress.current_dir), 1)
                        ]))
                      : _createCommentVNode("", true)
                  ], 2),
                  (_ctx.cleanProgress.removed_dirs.length > 0)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_70, [
                        _cache[59] || (_cache[59] = _createElementVNode("div", { class: "text-subtitle-2 mb-2" }, "已删除的目录:", -1)),
                        _createElementVNode("div", _hoisted_71, [
                          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(_ctx.cleanProgress.removed_dirs.slice(0, 5), (dir, index) => {
                            return (_openBlock(), _createElementBlock("div", {
                              key: index,
                              class: "removed-dir-item pa-2"
                            }, [
                              _createElementVNode("div", _hoisted_72, [
                                _createVNode(_component_v_icon, {
                                  icon: _ctx.getCleanTypeIcon(dir.type),
                                  color: _ctx.getCleanTypeColor(dir.type),
                                  size: "small",
                                  class: "mr-2"
                                }, null, 8, ["icon", "color"]),
                                _createElementVNode("span", _hoisted_73, _toDisplayString(dir.path), 1)
                              ])
                            ]))
                          }), 128)),
                          (_ctx.cleanProgress.removed_dirs.length > 5)
                            ? (_openBlock(), _createElementBlock("div", _hoisted_74, [
                                _createElementVNode("span", _hoisted_75, "... 还有 " + _toDisplayString(_ctx.cleanProgress.removed_dirs.length - 5) + " 个目录已删除", 1)
                              ]))
                            : _createCommentVNode("", true)
                        ])
                      ]))
                    : _createCommentVNode("", true)
                ])
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, { class: "pa-4" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  color: "primary",
                  variant: "text",
                  onClick: _cache[13] || (_cache[13] = $event => (_ctx.showCleanProgressDialog = false)),
                  disabled: _ctx.cleanProgress.running
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(_ctx.cleanProgress.running ? '清理中...' : '关闭'), 1)
                  ]),
                  _: 1
                }, 8, ["disabled"])
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
const Page = /*#__PURE__*/_export_sfc(_sfc_main, [['render',_sfc_render]]);

export { Page as default };
