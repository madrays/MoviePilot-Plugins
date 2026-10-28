import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import federation from '@originjs/vite-plugin-federation'

export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: 'gladossign',
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
      format: 'esm',
    }),
  ],
  build: {
    target: 'esnext',
    minify: 'terser',
    cssCodeSplit: true,
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        // vuetify / vue 一律交给宿主共享，禁止单独成 chunk
        manualChunks: (id) => {
          if (id.includes('node_modules')) {
            if (id.includes('vuetify') || id.includes('@mdi')) return undefined
            if (id.includes('/vue/') || id.includes('vue-router') || id.includes('pinia')) return undefined
            return 'vendor'
          }
        },
      },
    },
  },
  css: {
    postcss: {
      plugins: [
        {
          postcssPlugin: 'internal:charset-removal',
          AtRule: {
            charset: (atRule) => {
              if (atRule.name === 'charset') atRule.remove()
            },
          },
        },
      ],
    },
  },
  server: {
    port: 5002,
    cors: true,
    origin: 'http://localhost:5002',
  },
})
