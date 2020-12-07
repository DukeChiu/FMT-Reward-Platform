<template>
  <div class="info">
    {{msg}}
    <div @click="redirect">{{auto}}</div>
  </div>
</template>

<script>
  import axios from 'axios';
  import Common from '../Common';
  export default {
    name: "Verify",
    mounted: function () {
      let code = this.$route.query.code.toString();
      console.log(code);
      let that = this;
      axios({
        url: this.host + 'verifyEmail',
        method: 'POST',
        params: {code: code}
      }).then(res => {
        if (res.data.code === 1 || res.data.code === -1){
          that.success(res.data.msg.errmsg);
          // that.$router.replace('/login');
          that.msg = res.data.msg.errmsg + '\n' + '点击下方进行登录';
          that.auto = '登录'
        }
        else {
          that.error(res.data.msg.errmsg);
          // that.$router.replace('/login')
          that.msg = res.data.msg.errmsg + '\n' + '点击下方进行注册或刷新重试';
          that.auto = '注册'
        }
      }).catch(err => {
          that.error('网络错误');
      })
    },
    data() {
      return {
        // code: '',
        host: Common.BASEHOST,
        msg: '',
        auto: ''
      }
    },
    methods: {
      error: function (msg) {
        this.$Message.error(msg);
      },
      success: function (msg) {
        this.$Message.success(msg);
      },
      redirect: function () {
        this.$router.replace('/login');
      }
    }
  }
</script>

<style scoped>
  .info{
    display: flex;
    align-items: center;
    flex-direction: column;
  }
</style>
