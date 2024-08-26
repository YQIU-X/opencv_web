import Vue from 'vue'
import Router from 'vue-router'
import MainLayout from '@/components/MainLayout.vue'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'MainLayout',
      component: MainLayout
    }
  ]
})
