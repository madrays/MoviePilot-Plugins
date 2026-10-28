import { createApp } from 'vue'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import 'vuetify/styles'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import App from './App.vue'

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi },
  },
  theme: {
    defaultTheme: 'gladosDark',
    themes: {
      gladosDark: {
        dark: true,
        colors: {
          primary: '#4ea1ff',
          secondary: '#8ea0b5',
          success: '#3ecf8e',
          warning: '#ffb545',
          error: '#ff6b6b',
          info: '#4ea1ff',
          background: '#121212',
          surface: '#1b1f24',
        },
      },
    },
  },
})

createApp(App).use(vuetify).mount('#app')
