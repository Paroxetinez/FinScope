import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { clerkPlugin } from 'vue-clerk'
import { message } from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import { Chart } from '@antv/g2';
const app = createApp(App)

// 全局挂载 message
app.config.globalProperties.$message = message

// Clerk 配置
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!PUBLISHABLE_KEY) {
  throw new Error('Missing Publishable Key')
}

app.use(clerkPlugin, {
  publishableKey: PUBLISHABLE_KEY,
  appearance: {
    layout: {
      socialButtonsPlacement: 'bottom',
      socialButtonsVariant: 'iconButton',
    },
    variables: {
      colorPrimary: '#1677ff'
    },
    elements: {
      formButtonPrimary: 'bg-primary hover:bg-primary-dark',
      card: 'w-full'
    }
  }
})

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(router)
app.use(pinia)


const chart = new Chart({
  container: 'c1',
  width: 600,
  height: 300
});

app.mount('#app')
