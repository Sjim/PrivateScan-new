import Vue from 'vue'
import Router from 'vue-router'
import PrivacyScan from '@/components/PrivacyScan'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'HelloWorld',
      component: PrivacyScan
    }
  ]
})
