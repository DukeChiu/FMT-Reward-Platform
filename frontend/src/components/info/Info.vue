<template>
  <div id="info">
    <!--{{'info: '}}{{msg}}-->
    <!--<Button ghost type="info" @click="logout">退出</Button>-->
    <div class="background"></div>
    <div id="user-info">
      <div class="user">
        <Poptip trigger="hover" word-wrap :content="'邮箱:' + userInfo.email+'\n ID:' + userInfo.id + '\n'">
          <img v-bind:src="'../static/icons/' + (userInfo.icon? userInfo.icon: 'default.png')" class="icon">
        </Poptip>
        <p style="width: 100px; font-size: 15px; font-weight: bold">{{userInfo.username? userInfo.username:'尚未登录'}}</p>
        <p><img src="../../assets/img/tinkle.png" style="height: 10px">{{userInfo? userInfo.rate: ''}}</p>
      </div>
      <!--<div class="create" @click="showModal">发布</div>-->
      <Button type="info" ghost class="log-out" size="small" @click="logout">退出</Button>
    </div>
    <div id="nav">
      <div :class="{border: isOn}" @click="change(0)">
        <img src="../../assets/img/my_issue.png"/>
      </div>
      <div :class="{border: !isOn}" @click="change(1)">
        <img src="../../assets/img/my_apply.png"/>
      </div>
    </div>
    <div id="swiper-info" v-if="details">
      <Card v-for="(item, index) in (modelSelect === 'time'? taskListTime: taskListPrice)" :key="index" padding="14"
            style="margin: 10px 0">
        <div class="card" @click="getDetails(item)">
          <div class="time">
            <img src="../../assets/img/clock.png" class="clock"></img>
            <Time :time="new Date(item.time.substring(0, item.time.length-4)).getTime()"
                  :type="new Date().getTime() - new Date(item.time.substring(0, item.time.length-4)).getTime() > 86400* 2* 1000 ? 'datetime':'relative'"
                  style="padding-top: 3px "/>
          </div>
          <div class="task">
            <p style="font-size: 18px; font-weight: bold">
              {{item.title}}
            </p><br>
            <p class="disc">
              {{item.disc}}
            </p>
          </div>
          <div class="price">
            <img src="../../assets/img/money.png" class="money"></img>
            <p>{{item.price}}</p>
          </div>
        </div>
      </Card>
    </div>
    <Task :user="initUser" :details="currentTask" :apply="apply" v-else></Task>
  </div>
</template>

<script>
  import Common from '../Common';
  import axios from 'axios';
  import 'swiper/dist/css/swiper.min.css';
  // import Swiper from 'swiper';
  import Task from '../task/Task'
  axios.defaults.withCredentials = true;
  export default {
    name: "Info",
    data() {
      return {
        msg: '',
        host: Common.BASEHOST,
        userInfo: null,
        isOn: true,
        details: true,
        currentTask: null,
        apply: null,
        initUser: null,
        modal: false,
        modelSelect: 'time',
        taskListTime: [],
        taskListPrice: [],
        // initUser: null
      }
    },components: {
      Task
    },
    mounted: function () {
      let cookie = this.$cookie.get('auth');
      if (!cookie) {
        this.$router.replace({
          path: '/login'
        })
      } else {
        this.loading();
        // msg.onclose;
        let that = this;
        axios({
          url: that.host + 'getInfo',
          method: 'POST',
        }).then(res => {
          that.$Message.destroy();
          if (res.data.code === 1) {
            that.userInfo = res.data.msg.info.user;
            axios({
              url: that.host + 'getSelf',
              method: 'POST'
            }).then(resSelf => {
              if (resSelf.data.code === 1) {
                that.taskListTime = resSelf.data.msg.info.task;
                that.taskListPrice = resSelf.data.msg.info.apply;
              }
              else
                that.$Meaasge.error(resSelf.data.msg.errmsg);
            }).catch( errSelf => {
              that.$Meaasge.error('网络或服务器出错')
            })
          } else if (res.data.code === -2)
            that.error('异地登录设备，请重新登录');
          else if (res.data.code === 0) {
            that.error(res.data.msg.errmsg);
          } else
            that.$router.replace({path: '/login'});
        }).catch(error => {
          that.error('网络或服务器错误')
        })
      }
      // this.swiper = new Swiper("#swiper-info", {
      //   autoplay: 3000,
      //   speed: 1000,
      //   allowTouchMove: true
      // });
    },
    methods: {
      loading: function () {
        const msg = this.$Message.loading({
          content: 'Loading...',
          duration: 20
        });
        // setTimeout(msg, 3000);
        // return msg;
      },
      error: function (msg) {
        this.$Message.error(msg);
      },
      logout: function () {
        let that = this;
        let cookie = this.$cookie.get('auth');
        if (cookie) {
          axios({
            url: that.host + 'logout',
            method: 'POST',
          }).then(res => {
            that.$Message.success('下线成功！');
            that.$cookie.delete('auth');
            that.$router.replace({path: '/login'});
          }).catch(error => {
            that.error('网络或服务器错误')
          })
        }
      },
      change: function (index) {
        // console.log(this.swiper);
        // this.swiper.slideTo(index);
        // this.thisIndex = (++this.thisIndex) % 2;
        this.isOn = parseInt(index) === 0 ? true : false;
        this.modelSelect = this.modelSelect === 'price'? 'time': 'price';
      },
      getDetails: function (task) {
        let cookie = this.$cookie.get('auth');
        let that = this;
        if (cookie && this.userInfo) {
          axios({
            url: this.host + 'getTaskDetails',
            method: 'POST',
            params: {task: task.id}
          }).then(res => {
            console.log();
            if (res.data.code === 1) {
              this.currentTask = task;
              let info = res.data.msg.info;
              that.initUser = info;
              if (info.apply === 0) {
                axios({
                  url: that.host + 'getApplyDetails',
                  method: 'POST',
                  params: {task: task.id}
                }).then(resApply => {
                  if (resApply.data.code === 1) {
                    that.apply = resApply.data.msg.info.length >= 1 ? resApply.data.msg.info : null;
                    console.log(that.apply)
                  } else {
                    that.apply = null;
                    that.error(resApply.data.msg.errmsg);
                  }
                })
              } else {
                console.log(1);
                that.apply = null;
              }
              this.details = false;
            } else if (res.data.code === -1) {
              this.$Notice.error({
                title: '登录失效',
                desc: '',
                duration: 2
              });
              this.$router.push({
                path: '/login',
                query: {
                  path: '/'
                }
              })
            } else {
              this.error(res.data.msg.errmsg);
            }
          }).catch(err => {
            that.error('网络错误或服务器异常');
          })
        } else {
          this.$cookie.delete('auth');
          this.$Notice.error({
            title: '请先登录',
            desc: '',
            duration: 2
          });
          this.$router.push({
            path: '/login',
            query: {
              path: '/'
            }
          })
        }
      }
    },
  }
</script>

<style scoped>
  #user-info {
    height: 80px;
    width: 100%;
    background-color: white;
    position: fixed;
    top: 0;
  }

  #info {
    /*background-color: darkgray;*/
    height: 100%;
    overflow: hidden;
    display: flex;
    /*justify-content: center;*/
    align-items: center;
    /*-webkit-align-content: center;*/
    flex-direction: column;
  }

  .user {
    margin: 10px 0 0 100px;
    display: flex;
    flex-direction: row;
    align-items: flex-end;
    width: 250px;
  }

  .icon {
    height: 60px;
    width: auto;
    /*margin-top: 10px;*/
  }

  .background {
    width: 100%;
    height: 100%;
    background: url("../../assets/img/login_bg.jpg") center;
    background-size: 100% 100%;
    filter: blur(15px);
    position: absolute;
    z-index: -1;
    overflow: hidden;
  }

  .log-out {
    position: absolute;
    top: 50px;
    right: 10px;
    z-index: 10;
  }

  #nav {
    display: flex;
    height: 60px;
    margin-top: 100px;
    justify-content: center;
    align-items: center;
    width: 100%;
  }

  #nav > div {
    height: 50px;
    /*width: auto;*/
    margin: 0 20px;
  }

  #nav > div:hover {
    border-bottom: solid 2px rgb(127, 174, 225);
  }

  #nav > div > img {
    height: 40px;
    width: auto;
  }

  .border {
    border-bottom: solid 2px rgb(127, 174, 225);
  }

  #swiper-info {
    width: 55%;
    /*z-index: 10;*/
    height: auto;
  }

  .swiper-slide {
    height: 550px;
    /*background: white;*/
  }
  .card {
    display: flex;
    flex-direction: row;
    width: 100%;
    /*background: url("../assets/img/login_bg.jpg") center;*/
    /*background-size: 100% 100%;*/
    /*filter: blur(15px);*/
    /*background-color: rgba(255, 255, 255, 0.5);*/
    /*filter: blur(0);*/
  }
  .clock {
    height: auto;
    width: 30px;
  }

  .time {
    display: flex;
    flex-direction: column;
    width: 120px;
    align-items: center;
    color: rgb(127, 174, 225);
    font-size: 7px;
    justify-content: center;
  }

  .disc {
    width: 500px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    font-size: 12px;
    color: rgb(151, 151, 151);
  }

  .price {
    margin-left: auto;
    margin-right: 40px;
    /*display: block;*/
    display: flex;
    flex-direction: row;
    width: 80px;
    align-items: center;
  }

  .money {
    width: 18px;
    height: auto;
    padding-right: 5px;
  }
  @media screen and (max-device-width: 919px) {
    .user {
      margin: 10px 0 0 20px;
    }
    #nav > div > img {
      height: 20px;
      width: auto;
    }
    #swiper-info{
      width: 90%;
    }
    .clock {
      width: 20px;
    }

    .disc {
      width: 160px;
    }

    .price {
      margin-left: 20px;
    }
  }
</style>
