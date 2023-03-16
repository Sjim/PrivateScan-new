// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.

import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index'
import ElementUI from 'element-plus';
import 'element-plus/dist/index.css'
const app = createApp(App)
app.use(ElementUI)
app.use(router)

app.mount('#app')


/* eslint-disable no-new */

