import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import Map from '../views/Map.vue'
import Report from '../views/Report.vue'
import Upload from '../views/Upload.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/about', component: About },
  { path: '/map', component: Map },
  { path: '/report', component: Report },  
  { path: '/uploads', component: Upload }  
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router