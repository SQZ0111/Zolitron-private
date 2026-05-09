// main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router/router'
import 'vuetify/styles'
import vuetify from './plugins/vuetifiyCustom'

const app = createApp(App)
app.use(router)
app.use(vuetify)
app.mount('#app')