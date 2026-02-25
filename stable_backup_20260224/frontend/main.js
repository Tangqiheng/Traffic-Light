import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router/index.js'
import store from './store/index.js'

// 创建Vue应用实例
const app = createApp(App)

app.use(store)
app.use(router)
app.use(ElementPlus)

// 挂载应用到DOM
app.mount('#app')
