import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import federation from '@originjs/vite-plugin-federation'

export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: 'p115lite',
      filename: 'remoteEntry.js',
      exposes: {
        './Page': './src/components/Page.vue',
        './Config': './src/components/Config.vue',
        './Dashboard': './src/components/Dashboard.vue',
      },
      shared: {
        vue: {
          requiredVersion: false,
          generate: false,
        },
        vuetify: {
          requiredVersion: false,
          generate: false,
          singleton: true,
        },
        'vuetify/styles': {
          requiredVersion: false,
          generate: false,
          singleton: true,
        },
      },
      format: 'esm'
    })
  ],
  build: {
    target: 'esnext',   // 必须设置为esnext以支持顶层await
    minify: 'terser',      // 开发阶段建议关闭混淆
    cssCodeSplit: true, // 改为true以便能分离样式文件
    chunkSizeWarningLimit: 1000, // 提高警告阈值到 1000KB
    rollupOptions: {
      output: {
        // 手动分割代码块，将大型依赖库分离。
        // 注意：vuetify / vue 已由 federation shared(generate:false) 交由宿主提供，
        // 若在此再拆成独立 chunk，会被 expose 组件 import，导致远程 vuetify 运行时
        // 与主程序冲突（官方强制要求联邦插件不得打包 vuetify）。因此必须显式排除。
        manualChunks: (id) => {
          if (id.includes('node_modules')) {
            // vuetify 与 vue 一律排除，交由宿主共享，禁止单独成 chunk
            if (id.includes('vuetify') || id.includes('@mdi')) {
              return undefined;
            }
            if (id.includes('/vue/') || id.includes('vue-router') || id.includes('pinia')) {
              return undefined;
            }
            // ECharts 单独打包（通常很大）
            if (id.includes('echarts') || id.includes('vue-echarts')) {
              return 'echarts';
            }
            // 其他大型库
            if (id.includes('cron') || id.includes('cronstrue')) {
              return 'cron-vendor';
            }
            // 其他 node_modules 依赖
            return 'vendor';
          }
        },
      },
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: '/* 覆盖vuetify样式 */',
      }
    },
    postcss: {
      plugins: [
        {
          postcssPlugin: 'internal:charset-removal',
          AtRule: {
            charset: (atRule) => {
              if (atRule.name === 'charset') {
                atRule.remove();
              }
            }
          }
        },
        // 只在非开发环境下启用 vuetify 样式过滤
        ...(process.env.NODE_ENV !== 'development' ? [{
          postcssPlugin: 'vuetify-filter',
          Root(root) {
            // 过滤掉所有vuetify相关的CSS
            root.walkRules(rule => {
              if (rule.selector && (
                rule.selector.includes('.v-') ||
                rule.selector.includes('.mdi-'))) {
                rule.remove();
              }
            });
          }
        }] : [])
      ]
    }
  },
  server: {
    port: 5001,   // 使用不同于主应用的端口
    cors: true,   // 启用CORS
    origin: 'http://localhost:5001'
  },
})
