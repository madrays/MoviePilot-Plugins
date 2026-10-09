<template>
  <v-card-text class="pa-0">
    <v-tabs v-model="panSubTab" color="primary" class="sub-category-tabs" slider-color="primary">
      <v-tab value="tab-pan-transfer" class="sub-tab">
        <v-icon size="small" start>mdi-transfer</v-icon>网盘整理
      </v-tab>
    </v-tabs>
    <v-divider></v-divider>
    <v-window v-model="panSubTab" :touch="false" class="tab-window">
      <v-window-item value="tab-pan-transfer">
        <v-card-text>
          <v-row>
            <v-col cols="12" md="4">
              <v-switch v-model="config.pan_transfer_enabled" label="启用" color="info"></v-switch>
            </v-col>
          </v-row>

          <!-- 待整理和未识别目录 -->
          <v-card variant="outlined" class="mt-4">
            <v-card-title class="text-subtitle-1">
              <v-icon start>mdi-folder-move</v-icon>
              待整理和未识别目录
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12">
                  <div class="d-flex flex-column">
                    <div v-for="(path, index) in panTransferPaths" :key="`pan-${index}`"
                      class="mb-2 d-flex align-center">
                      <v-text-field v-model="path.path" label="网盘待整理目录" density="compact"
                        append-icon="mdi-folder-network"
                        @click:append="openDirSelector(index, 'remote', 'panTransfer')"
                        class="flex-grow-1"></v-text-field>
                      <v-btn icon size="small" color="primary" class="ml-2" @click="manualTransfer(index)"
                        :disabled="!path.path" title="手动整理此目录">
                        <v-icon>mdi-play</v-icon>
                      </v-btn>
                      <v-btn icon size="small" color="error" class="ml-2"
                        @click="removePanTransferPath(index)">
                        <v-icon>mdi-delete</v-icon>
                      </v-btn>
                    </div>
                    <v-btn size="small" prepend-icon="mdi-plus" variant="outlined"
                      class="mt-2 align-self-start" @click="addPanTransferPath">
                      添加路径
                    </v-btn>
                  </div>
                </v-col>
              </v-row>

              <v-row class="mt-4">
                <v-col cols="12">
                  <v-text-field v-model="config.pan_transfer_unrecognized_path" label="网盘整理未识别目录"
                    density="compact" append-icon="mdi-folder-network"
                    @click:append="openDirSelector('unrecognized', 'remote', 'panTransferUnrecognized')"></v-text-field>
                  <v-alert type="info" variant="tonal" density="compact" class="mt-3"
                    icon="mdi-information">
                    <div class="text-caption">提示：此目录用于存放整理过程中未能识别的媒体文件。</div>
                  </v-alert>
                  <v-alert type="warning" variant="tonal" density="compact" class="mt-3" icon="mdi-alert">
                    <div class="text-caption">注意：未识别目录不能设置在任何媒体库目录或待整理目录的内部。</div>
                  </v-alert>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- 分享转存目录 -->
          <v-card variant="outlined" class="mt-4">
            <v-card-title class="text-subtitle-1">
              <v-icon start>mdi-share-variant</v-icon>
              分享转存目录
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12">
                  <div class="d-flex flex-column">
                    <div v-for="(path, index) in shareReceivePaths" :key="`share-${index}`"
                      class="mb-2 d-flex align-center">
                      <v-text-field v-model="path.path" label="分享转存目录" density="compact"
                        append-icon="mdi-folder-network"
                        @click:append="openDirSelector(index, 'remote', 'shareReceive')"
                        class="flex-grow-1"></v-text-field>
                      <v-btn icon size="small" color="error" class="ml-2"
                        @click="removeShareReceivePath(index)">
                        <v-icon>mdi-delete</v-icon>
                      </v-btn>
                    </div>
                    <v-btn size="small" prepend-icon="mdi-plus" variant="outlined"
                      class="mt-2 align-self-start" @click="addShareReceivePath">
                      添加路径
                    </v-btn>
                  </div>
                </v-col>
              </v-row>
              <v-alert type="info" variant="tonal" density="compact" class="mt-3" icon="mdi-information">
                <div class="text-caption">提示：此目录用于存放通过分享链接转存的资源。</div>
              </v-alert>
            </v-card-text>
          </v-card>

          <!-- 离线下载目录 -->
          <v-card variant="outlined" class="mt-4">
            <v-card-title class="text-subtitle-1">
              <v-icon start>mdi-download</v-icon>
              离线下载目录
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12">
                  <div class="d-flex flex-column">
                    <div v-for="(path, index) in offlineDownloadPaths" :key="`offline-${index}`"
                      class="mb-2 d-flex align-center">
                      <v-text-field v-model="path.path" label="离线下载目录" density="compact"
                        append-icon="mdi-folder-network"
                        @click:append="openDirSelector(index, 'remote', 'offlineDownload')"
                        class="flex-grow-1"></v-text-field>
                      <v-btn icon size="small" color="error" class="ml-2"
                        @click="removeOfflineDownloadPath(index)">
                        <v-icon>mdi-delete</v-icon>
                      </v-btn>
                    </div>
                    <v-btn size="small" prepend-icon="mdi-plus" variant="outlined"
                      class="mt-2 align-self-start" @click="addOfflineDownloadPath">
                      添加路径
                    </v-btn>
                  </div>
                </v-col>
              </v-row>
              <v-alert type="info" variant="tonal" density="compact" class="mt-3" icon="mdi-information">
                <div class="text-caption">提示：此目录用于存放通过离线下载功能下载的资源。</div>
              </v-alert>
            </v-card-text>
          </v-card>

          <v-divider class="my-4"></v-divider>

          <v-alert type="info" variant="tonal" density="compact" class="mt-3" icon="mdi-information">
            <div class="text-body-2 mb-1"><strong>配置说明：</strong></div>
            <div class="text-caption">
              <div class="mb-1">使用本功能需要先进入 设定-目录 进行配置：</div>
              <div class="mb-1">1. 添加目录配置卡，按需配置媒体类型和媒体类别，资源存储选择115网盘，资源目录输入网盘待整理文件夹</div>
              <div class="mb-1">2. 自动整理模式选择手动整理，媒体库存储依旧选择115网盘，并配置好媒体库路径，整理方式选择移动，按需配置分类、重命名、通知</div>
              <div>3. 配置完成目录设置后只需要在上方 网盘待整理目录 填入 网盘待整理文件夹 即可</div>
            </div>
          </v-alert>

          <v-alert type="warning" variant="tonal" density="compact" class="mt-3" icon="mdi-alert">
            <div class="text-caption">注意：配置目录时不能选择刮削元数据，否则可能导致风控！</div>
          </v-alert>

          <v-alert type="warning" variant="tonal" density="compact" class="mt-3" icon="mdi-alert">
            <div class="text-body-2 mb-1"><strong>注意事项：</strong></div>
            <div class="text-caption">
              <div>• 115 分享转存和离线下载可配合网盘整理自动入库</div>
            </div>
          </v-alert>

          <v-alert type="warning" variant="tonal" density="compact" class="mt-3" icon="mdi-alert">
            <div class="text-caption">注意：115生活事件监控默认会忽略网盘整理触发的移动事件，所以推荐使用MP整理事件监控生成STRM</div>
          </v-alert>

          <v-row class="mt-4">
            <v-col cols="12">
              <v-btn color="info" variant="outlined" prepend-icon="mdi-bug-check"
                @click="checkLifeEventStatus">
                故障检查
              </v-btn>
              <div class="text-caption text-grey mt-2">
                检查115生活事件进程状态，测试数据拉取功能，并提供详细的调试信息
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-window-item>
    </v-window>
  </v-card-text>
</template>

<script setup>
import { ref, inject } from 'vue';

const panSubTab = ref('tab-pan-transfer');

const config = inject('config');
const panTransferPaths = inject('panTransferPaths');
const shareReceivePaths = inject('shareReceivePaths');
const offlineDownloadPaths = inject('offlineDownloadPaths');
const directoryUploadPaths = inject('directoryUploadPaths');
const fuseStrmTakeoverRules = inject('fuseStrmTakeoverRules');
const addPath = inject('addPath');
const removePath = inject('removePath');
const addPanTransferPath = inject('addPanTransferPath');
const removePanTransferPath = inject('removePanTransferPath');
const addShareReceivePath = inject('addShareReceivePath');
const removeShareReceivePath = inject('removeShareReceivePath');
const addOfflineDownloadPath = inject('addOfflineDownloadPath');
const removeOfflineDownloadPath = inject('removeOfflineDownloadPath');
const openDirSelector = inject('openDirSelector');
const manualTransfer = inject('manualTransfer');
const checkLifeEventStatus = inject('checkLifeEventStatus');
const openConfigGeneratorDialog = inject('openConfigGeneratorDialog');
</script>
