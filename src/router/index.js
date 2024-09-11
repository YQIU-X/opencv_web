import Vue from 'vue'
import Router from 'vue-router'
import MainLayout from '@/components/MainLayout.vue'
import ImgGeoTransf from '@/components/ImgGeoTransf.vue' // 引入新的页面组件

Vue.use(Router)

export default new Router({
  mode: 'history', // 确保使用 history 模式，防止使用哈希 URL
  routes: [
    {
      path: '/',
      name: 'MainLayout',
      component: MainLayout
    },
    {
      path: '/img-geo-transf', // 定义新页面的路由
      name: 'ImgGeoTransf',
      component: ImgGeoTransf // 新页面组件
    }
  ]
})
