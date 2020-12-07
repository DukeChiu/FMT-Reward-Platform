<template>
  <div id="main">
    <div class="background"></div>
    <div class="swiper-container" id="swiper-login">
      <div class="swiper-wrapper">
        <div class="swiper-slide" id="slide1">
          <div class="login">
            <p class="title">Login with your account!</p>
            <br>
            <!--<Input suffix="ios-person" v-model="userInfo.email" placeholder="Email" type="email" style="width: 200px; "></Input>-->
            <AutoComplete
              v-model="userInfo.email"
              @on-search="emailSearch"
              placeholder="Email"
              icon="ios-person"
              style="width:200px">
              <!--<Icon type="ios-person" />-->
              <Option v-for="item in dataEmail" :value="item" :key="item">{{ item }}</Option>
            </AutoComplete>
            <br>
            <Input suffix="ios-keypad" v-model="userInfo.pwd" placeholder="Password" type="password"
                   style="width: 200px" maxlength="16" minlength="8"></Input>
            <br>
            <div class="layout">
              <Input placeholder="Code" v-model="userInfo.code" type="text" style="width: 95px; margin-right: 10px;"
                     maxlength="4" minlength="4"></Input>

              <img :src="urlCode" @click="reNew" class="code"/>
            </div>
            <br>
            <Button type="info" ghost @click="logIn" :loading="buttons.inLoad" style="width: 200px">
              <span v-if="!buttons.inLoad">Log in</span>
              <span v-else>Loading...</span>
            </Button>
            <br>
            <br>
            <p @click="toTheother" class="change"><a style="text-decoration-line: underline">without an account to sign
              up?</a></p>
          </div>
        </div>
        <div class="swiper-slide" id="slide2">
          <div class="login" v-if="registerStatus">
            <p class="title">Sign up with your email!</p>
            <br>
            <!--<Input suffix="ios-person" v-model="userInfo.email" placeholder="Email" type="email" style="width: 200px; "></Input>-->
            <AutoComplete
              v-model="registerInfo.email"
              @on-search="emailSearch"
              placeholder="Email"
              icon="ios-person"
              style="width:200px">
              <!--<Icon type="ios-person" />-->
              <Option v-for="item in dataEmail" :value="item" :key="item">{{ item }}</Option>
            </AutoComplete>
            <br>
            <Input suffix="ios-keypad" v-model="registerInfo.pwd" placeholder="Password(8-16位字符)" type="password"
                   style="width: 200px" maxlength="16" minlength="8" @on-change="pwdVerify"></Input>
            <Progress :percent="percent" :status="status" hide-info="true" :stroke-width="2" style="width: 200px"/>
            <!--<br>-->
            <Input :icon="suffixR" v-model="registerInfo.pwdRepeat" placeholder="Password Repeat(8-16位字符)"
                   type="password"
                   style="width: 200px" maxlength="16" minlength="8" @on-change="rPwdVerify"></Input>
            <br>
            <Input suffix="ios-contact" v-model="registerInfo.username" placeholder="Username(支持2-15个字符)" type="text"
                   style="width: 200px" maxlength="15" minlength="2"></Input>
            <br>
            <!--<div class="layout">-->
            <!--<Input placeholder="Code" v-model="registerInfo.code" type="text" style="width: 95px; margin-right: 10px;"-->
            <!--maxlength="4" minlength="4"></Input>-->

            <!--<img :src="urlCode" @click="reNew" class="code"/>-->
            <!--</div>-->
            <!--<br>-->
            <Button type="info" ghost @click="register" :loading="buttons.reg" style="width: 200px">
              <span v-if="!buttons.reg">Sign up</span>
              <span v-else>Loading...</span>
            </Button>
            <br>
            <!--<br>-->
            <p @click="toTheother" class="change"><a style="text-decoration-line: underline">own an account to
              login?</a>
            </p>
          </div>
          <div class="login" v-else>
            注册成功，请前往邮箱进行验证！
            <p @click="toTheother" class="change"><a style="text-decoration-line: underline">own an account to
              login?</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import Common from "../Common";
  import {hex_md5} from "./md5";
  import Swiper from 'swiper';
  import 'swiper/dist/css/swiper.min.css';
  import axios from 'axios';

  axios.defaults.withCredentials = true;
  export default {
    name: "Login",
    data() {
      return {
        userInfo: {
          email: '',
          pwd: '',
          code: ''
        },
        registerInfo: {
          email: '',
          pwd: '',
          pwdRepeat: '',
          username: ''
        },
        thisIndex: 1,
        mySwiper: null,
        dataEmail: [],
        host: Common.BASEHOST,
        urlCode: '#',
        buttons: {
          inLoad: false,
          reg: false
        },
        percent: 0,
        statusAll: ['', 'wrong', 'normal', 'success'],
        status: 'wrong',
        suffixR: '',
        registerStatus: true,
        fromPath: ''
      }
    },
    mounted: function () {
      if (this.$route.query.path) {
        this.fromPath = this.$route.query.path;
        console.log(this.fromPath)
      } else
        this.fromPath = '';
      this.reNew();
      this.$nextTick(function () {
        setInterval(this.reNew, 90000);
      });
      this.mySwiper = new Swiper("#swiper-login", {
        allowTouchMove: false,
        // loop:true,
        // effect : 'flip',
        // flipEffect: {
        //   slideShadows : true,
        //   limitRotation : true,
        // },
        effect: "cube",
        cubeEffect: {
          slideShadows: false,
          shadow: false,
          shadowOffset: 100,
          shadowScale: 0.6
        }
      });
      let cookie = this.$cookie.get('auth');
      if (cookie) {
        let that = this;
        axios({
          url: that.host + 'auth',
          method: 'POST',
          // params: that.userInfo
        }).then(res => {
          if (res.data.code === 1) {
            if (that.fromPath !== '')
              this.$router.replace({
                path: that.fromPath
              });
            else
              this.$router.replace({
                path: '/info'
              });
          }
        })
      }
    },
    methods: {
      reNew: function () {
        this.urlCode = this.host + 'vcode?timestamp=' + String(Date.parse(new Date()));
        console.log(this.urlCode);
      },
      error(title, nodesc) {
        this.$Notice.error({
          title: title,
          desc: nodesc ? nodesc : ''
        });
      },
      success(title, nodesc) {
        this.$Notice.success({
          title: title,
          desc: nodesc ? nodesc : '',
          duration: 1
        });
      },
      logIn: function () {
        this.buttons.inLoad = true;
        // console.log(this.userInfo);
        // console.log(this.$cookie.get('jsonverify'));
        let code = true;
        let re = /^[\u4E00-\u9FA5\uF900-\uFA2D]*$/;
        if (this.userInfo.email && re.test(this.userInfo.email)) {
          this.error('邮箱异常', '邮箱中包含非法字符！');
          code = false;
          this.buttons.inLoad = true;
        } else if (!this.userInfo.email) {
          this.error('邮箱异常', '邮箱为空！');
          code = false;
          this.buttons.inLoad = true;
        }
        if (!this.userInfo.pwd || this.userInfo.pwd.length < 8) {
          this.error('密码异常', '密码为空或者少于8位！');
          code = false;
          this.buttons.inLoad = true;
        }
        if (!this.userInfo.code || this.userInfo.code.length !== 4) {
          this.error('验证码异常', '验证码为空或少于4位！');
          this.reNew();
          this.buttons.inLoad = true;
        } else if (code) {
          let md5 = hex_md5(this.userInfo.code);
          console.log(md5);
          console.log(this.$cookie);
          if (md5 === this.$cookie.get('jsonverify')) {
            let that = this;
            axios({
              url: that.host + 'login',
              method: 'POST',
              params: that.userInfo
            }).then(res => {
              if (res.data.code !== 1) {
                that.error('错误', res.data.msg.errmsg);
                that.reNew();
              } else {
                that.success('成功', res.data.msg.errmsg);
                if (that.fromPath !== '')
                  this.$router.replace({
                    path: that.fromPath
                  });
                else
                  this.$router.replace({
                    path: '/info'
                  });
              }
              that.buttons.inLoad = false;
            }).catch(error => {
              that.error('登录错误', '网络或服务器出错！');
              that.buttons.inLoad = false;
            })
            // this.success('验证成功', '正在登录！');
          } else {
            this.error('验证码异常', '验证码错误，请重新填写验证码！');
            this.buttons.inLoad = false;
            this.reNew();
          }
        }
      },
      emailSearch(value) {
        this.dataEmail = !value || value.indexOf('@') >= 0 ? [] : [
          value + '@qq.com',
          value + '@sina.com',
          value + '@s.upc.edu.cn',
          value + '@163.com',
          value + '@outlook.com',
          value + '@gmail.com',
          value + '@yahoo.com',
        ];
      },
      toTheother: function () {
        this.mySwiper.slideTo(this.thisIndex, 500, false);
        this.thisIndex = (++this.thisIndex) % 2;
      },
      register: function () {
        this.buttons.reg = true;
        // console.log(this.userInfo);
        // console.log(this.$cookie.get('jsonverify'));
        let code = true;
        let re = /^[\u4E00-\u9FA5\uF900-\uFA2D]*$/;
        if (this.registerInfo.email && re.test(this.registerInfo.email)) {
          this.error('邮箱异常', '邮箱中包含非法字符！');
          code = false;
        } else if (!this.registerInfo.email) {
          this.error('邮箱异常', '邮箱为空！');
          code = false;
        }
        if (!this.registerInfo.pwd || this.registerInfo.pwd.length < 8) {
          this.error('密码异常', '密码为空或者少于8位！');
          code = false;
        }
        if (this.registerInfo.pwd !== this.registerInfo.pwdRepeat) {
          this.error('密码错误', '两次输入密码不一致！');
          code = false;
        }
        if (!this.registerInfo.username) {
          this.error('用户名异常', '用户名不能为空！');
          code = false;
        }
        if (this.registerInfo.username.length < 2) {
          this.error('用户名异常', '用户名不能少于2位！')
          code = false;
        }
        if (code) {

          let that = this;
          axios({
            url: that.host + 'register',
            method: 'POST',
            params: that.registerInfo
          }).then(res => {
            if (res.data.code !== 1) {
              that.error('错误', res.data.msg.errmsg);
              // that.reNew();
            } else {
              // that.success('成功', res.data.msg.errmsg);
              // this.$router.replace({
              //   path: '/info'
              // })
              that.registerStatus = false;
            }
          }).then(function () {
            that.buttons.reg = false;
          }).catch(error => {
            that.error('登录错误', '网络或服务器出错！');
            that.buttons.reg = false;
          })
          // this.success('验证成功', '正在登录！');
        }

      },
      changePercent: function (per) {
        this.percent = per * 33.333333;
        this.status = this.statusAll[per];
        // console.log(per);
      },
      pwdVerify: function () {
        // this.status = 'wrong';
        let level = 0;
        if (/[0-9]+/.test(this.registerInfo.pwd))
          level++;
        if (/[a-z]+/.test(this.registerInfo.pwd))
          level++;
        if (/[A-Z]+/.test(this.registerInfo.pwd))
          level++;
        if (/[`~!@#$^&*()=|{}'":;,\[\].<>]+/.test(this.registerInfo.pwd))
          level++;
        if (!this.registerInfo.pwd)
          level = 0;
        if (level > 3)
          level = 3;
        if (this.registerInfo.pwd.length < 8)
          level = 0;
        // console.log(level);
        this.changePercent(level);
      },
      rPwdVerify: function () {
        if (this.registerInfo.pwd !== this.registerInfo.pwdRepeat)
          this.suffixR = 'ios-close-circle-outline';
        else
          this.suffixR = 'ios-checkmark-circle-outline';
      }
    }
  }
</script>

<style scoped>
  #main {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .background {
    width: 100%;
    height: 100%;
    background: url("../../assets/img/login_bg.jpg") center;
    background-size: 100% 100%;
    filter: blur(15px);
    position: absolute;
  }

  .login {
    /*height: 30px;*/
    background-color: rgba(255, 255, 255, 0.5);
    filter: blur(0);
    width: 400px;
    height: 400px;
    border-radius: 10px;
    text-align: center;
    display: flex;
    align-items: center;
    flex-direction: column;
  }

  .title {
    padding-top: 50px;
    font-size: 20px;
    color: gray;
  }

  .code {
    width: 95px;
    height: 32px;
    margin-left: 10px;
  }

  .layout {
    display: flex;
    width: 200px;
    /*text-align: center;*/
  }

  .swiper-container {
    width: 400px;
    height: auto;
  }

  .change {
    height: 30px;
    display: flex;
    align-items: center;
  }
</style>
