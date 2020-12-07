import Vue from 'vue'
import Router from 'vue-router'
// import HelloWorld from '@/components/HelloWorld'
import Index from '@/components/Index'
import Login from '@/components/login/Login'
import Info from '@/components/info/Info'
import iView from 'iview';
import 'iview/dist/styles/iview.css';
import VueCookie from 'vue-cookie'
import Common from '@/components/Common'
import axios from 'axios'
import Verify from '@/components/login/Verify'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
// import './global'
Vue.use(Router);
Vue.use(iView);
Vue.use(VueCookie);
Vue.use(ElementUI);
// Vue.use(axios);
const allrouter = new Router({
  routes: [
    {
      path: '/',
      name: 'index',
      component: Index
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
    },
    {
      path: '/info',
      name: 'info',
      component: Info,
      meta: {
        required: true
      }
    },
    {
      path: '/verify',
      name: 'verify',
      component: Verify
    }

  ]
});
allrouter.beforeEach(function (to, from, next) {
  // console.log(VueCookie.get('jsonverify'));
  if (to.meta.required) {
    let cookie = VueCookie.get('auth');
    console.log(cookie);
    if (cookie) {
      // let that = this;
      axios({
        url: Common.BASEHOST + 'auth',
        method: 'POST',
        // params: that.userInfo
      }).then(res => {
        if (res.data.code === 1 || res.data.code === -2) {
          if (res.data.code === -2) {
            iView.Notice.error({
              title: '账号在异地登录',
              desc: '',
              duration: 2
            });
            next({
              path: '/login'
            });
          } else
            next();
        }
        // that.success('成功', res.data.msg.errmsg);
        else
          next({
            path: '/login'
          })
      })
    } else
      next({
        path: '/login'
      })
  }
  else
    next();
  // console.log(from.name)
});
export default allrouter;
