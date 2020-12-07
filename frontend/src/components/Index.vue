<template>
  <!--<div>-->
  <!--<router-link :to="{path: '/login'}">to login</router-link>-->
  <!--<router-link :to="{path: '/info'}">to info</router-link>-->
  <!--</div>-->
  <div id="index">
    <div class="background"></div>
    <div id="info" @dblclick="changeModel">
      <div class="user" @click="login">
        <img v-bind:src="'../static/icons/' + (icon? icon: 'default.png')" class="icon">
        <p style="width: 100px; font-size: 15px; font-weight: bold">{{username? username:'尚未登录'}}</p>
      </div>
      <div class="create" @click="showModal">发布</div>
    </div>

    <Scroll :on-reach-bottom="handleReachBottom" id="scroll" height="600" v-if="details">

      <Card v-for="(item, index) in (modelSelect === 'time'? taskListTime: taskListPrice)" :key="index" padding="14"
            style="margin: 10px 0">
        <div class="card" @click="getDetails(item)">
          <div class="time">
            <img src="../assets/img/clock.png" class="clock"></img>
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
            <img src="../assets/img/money.png" class="money"></img>
            <p>{{item.price}}</p>
          </div>
        </div>
      </Card>
    </Scroll>
    <Task :user="initUser" :details="currentTask" :apply="apply" v-else></Task>
    <Modal
      v-model="modal"
      title="发布任务"
      footer-hide>
      <div class="union-input">
        <img src="../assets/img/flag.png"/>
        <p>任务标题</p>
        <Input v-model="taskInfo.title" style="width: 80%"/>
      </div>
      <div class="union-input">
        <img src="../assets/img/money.png"/>
        <p>任务价格</p>
        <!--<Input v-model="taskInfo.price" style="width: 80px" type="text"-->
        <!--:rules="[-->
        <!--{ required: true, message: '最小分不能为空',},-->
        <!--{ message: '最小分只能是数字', trigger:'change', pattern:/^(([1-9]\d{0,3})|0)(\.\d{0,2})?$/,}-->
        <!--]"/>-->
        <Input type="text" v-model="taskInfo.price"
               @keyup.native="taskInfo.price=taskInfo.price.replace(/^\D*(\d*(?:\.\d{0,1})?).*$/g, '$1')"
               style="width: 80px" icon="logo-usd"/>
      </div>
      <div class="union-input">
        <img src="../assets/img/text.png"/>
        <p>任务内容</p>
        <Input v-model="taskInfo.disc" style="width: 80%" :autosize="{minRows: 3, maxRows: 6}" type="textarea"/>
      </div>
      <div class="union-input">
        <img src="../assets/img/phone.png"/>
        <p>联系方式</p>
        <Input v-model="taskInfo.contact" style="width: 80%" :autosize="{minRows: 2, maxRows: 4}" type="textarea"/>
      </div>
      <div style="text-align: center">
        <Button type="info" size="large" style="width: 100px" ghost @click="createTask">
          <span v-if="!load">填好了</span>
          <span v-else>Loading...</span>
        </Button>
      </div>
    </Modal>
  </div>
</template>

<script>
  import axios from 'axios';
  import Common from "./Common";
  import Task from './task/Task';

  axios.defaults.withCredentials = true;

  export default {
    name: "Index",
    data: function () {
      return {
        icon: 'default.png',
        username: '',
        rate: '',
        userInfo: null,
        taskListTime: [],
        taskListPrice: [],
        host: Common.BASEHOST,
        page: 1000000000,
        info: [],
        details: true,
        currentTask: null,
        apply: null,
        initUser: null,
        modal: false,
        modelSelect: 'time',
        price: 1000000000,
        taskInfo: {
          title: '',
          price: '',
          disc: '',
          contact: ''
        },
        load: false,
        priceId: 0
      }
    },
    components: {
      Task
    }
    ,
    mounted: function () {
      let cookie = this.$cookie.get('auth');
      if (cookie) {
        let that = this;
        axios({
          url: that.host + 'getInfo',
          method: 'POST',
        }).then(res => {
          that.$Message.destroy();
          if (res.data.code === 1) {
            let user = res.data.msg.info.user;
            that.userInfo = user;
            that.icon = user.icon;
            that.username = user.username;
            that.rate = user.rate;
          } else if (res.data.code === -2) {
            that.error('异地登录设备，请重新登录');
          } else if (res.data.code === 0) {
            that.error(res.data.msg.errmsg);
            that.$cookie.delete('auth');
          }
        }).catch(err => {
          that.error('网络或服务器错误');
          console.log(err)
        })
      }
      // this.taskList = this.getAll();
      this.getAll(true);
      // console.log(this.userInfo)
    },
    methods: {
      getAll: async function (b) {
        let that = this;
        let resp = await axios.post(that.host + 'getAll', {
          page: that.modelSelect === 'time' ? that.page : that.price,
          model: that.modelSelect
        }).then(function (res) {
          if (res.data.code === 1) {
            // console.log(res.data.msg.info);
            that.info = res.data.msg.info;
            let length = that.info.length;
            that.count = length;
            if (length > 0) {
              if (that.modelSelect === 'time')
                that.page = that.info[length - 1].id;
              else {
                that.price = that.info[length - 1].price;
                that.priceId = that.info[length - 1].id
                that.modelSelect = that.priceId
              }
              console.log(that.page);
            }
            // console.log(that.page);
            if (b) {
              if (that.modelSelect === 'time')
                that.taskListTime = that.info;
              else
                that.taskListPrice = that.info;
            }
          } else {
            that.$Message.error(res.data.msg.errmsg);
            that.info = [];
          }
        }).catch(function (err) {
          console.log(err);
          that.$Message.error('网络或服务器出错！');
          that.info = []
        });
      },
      handleReachBottom: function () {
        this.getAll(false);
        let that = this;
        return new Promise(resolve => {
          setTimeout(() => {
            for (let i = 0; i < that.info.length; ++i) {
              if (that.modelSelect === 'time')
                that.taskListTime.push(that.info[i]);
              else
                that.taskListPrice.push(that.info[i])
            }
            resolve();
          }, 2000);
        });
      },
      login: function () {
        if (this.username)
          this.$router.push({
            path: '/info',
            params: {userInfo: this.userInfo}
          });
        else
          this.$router.push({
            path: '/login',
            query: {
              path: '/'
            }
          })
      },
      error: function (msg) {
        this.$Message.error(msg);
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
      },
      showModal: function () {
        let cookie = this.$cookie.get('auth');
        let that = this;
        if (cookie && this.userInfo) {
          axios({
            url: this.host + 'auth',
            method: 'POST',
          }).then(res => {
            if (res.data.code === 1) {
              that.modal = true;
            } else {
              this.$Notice.error({
                title: res.data.msg.errmsg,
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
      },
      createTask: function () {
          this.load = true;
          if (this.taskInfo.title === '' || this.taskInfo.price === '' || this.taskInfo.disc === '' || this.taskInfo.contact === '') {
            this.$Notice.error('选项不能为空');
            this.load = false;
          }
          else{
            let that = this;
            axios({
              url: that.host + 'createTask',
              method: 'POST',
              params: that.taskInfo
            }).then(res => {
              if(res.data.code === 1){
                that.$Message.success('发布成功');
                that.load = false;
                that.modal = false;
              }
              else {
                that.$Message.error(res.data.msg.errmsg);
                that.load = false;
              }
            }).catch(err => {
              console.log(err);
              that.$Message.error('网络或服务器错误');
              that.load = false;
            })
          }
      },
      changeModel:function () {
        this.price = 1000000000;
        this.priceId = 0;
        this.page = 1000000000;
        this.modelSelect = this.modelSelect === 'time'? this.priceId: 'time';
        this.getAll(true);
      }
    }
  }
</script>

<style scoped>
  #info {
    height: 80px;
    width: 100%;
    background-color: white;
    position: fixed;
    top: 0;
  }

  #scroll {
    margin-top: 100px;
    width: 55%;
  }

  #index {
    /*background-color: darkgray;*/
    height: 100%;
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    -webkit-align-content: center;
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

  .background {
    width: 100%;
    height: 100%;
    background: url("../assets/img/login_bg.jpg") center;
    background-size: 100% 100%;
    filter: blur(15px);
    position: absolute;
    z-index: -1;
    overflow: hidden;
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

  .user {
    margin: 10px 0 0 100px;
    display: flex;
    flex-direction: row;
    align-items: flex-end;
    width: 200px;
  }

  .icon {
    height: 60px;
    width: auto;
    /*margin-top: 10px;*/
  }

  .create {
    position: absolute;
    width: 80px;
    height: 60px;
    color: white;
    background-color: rgb(127, 174, 225);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 120%;
    top: 30px;
    right: 100px;
    border-radius: 5px;
    z-index: 10;
  }

  .union-input {
    display: flex;
    /*justify-content: flex-start;*/
    align-items: center;
    margin: 20px 0;
  }

  .union-input > img {
    width: 13px;
    height: auto;
  }

  .union-input > p, Input, img {
    margin-right: 10px;
  }

  @media screen and (max-device-width: 919px) {

    .create {
      width: 80px;
      height: 60px;
      right: 50px;
    }

    .user {
      margin: 10px 0 0 50px;
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

    #scroll {
      margin-top: 180px;
      width: 90%;
    }
  }
</style>
