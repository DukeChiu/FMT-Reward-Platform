<template>
  <div>
    <Card id="card">
      <!--<div class="canal">-->
      <Icon type="ios-close" class="canal" size="30" @click="$parent.details = true"></Icon>
      <!--</div>-->
      <div slot="title" class="title">
        <!--<Breadcrumb separator="|" slot="title" class="title">-->
        <!--<BreadcrumbItem>-->
        <div class="user">
          <img :src="'../../static/icons/'+user.user.icon" class="icon">
          <div class="time">
            <p>{{user.user.username}}</p>
            <Time :time="new Date(details.time.substring(0, details.time.length-4)).getTime()" type="datetime"
                  style="font-size: 5px; color: darkgray"/>
          </div>
        </div>
        <!--</BreadcrumbItem>-->
        <!--<BreadcrumbItem>-->
        <div class="title-price">
          <p style="font-size: 18px; font-weight: bold;">{{details.title}}</p>
          <div class="price">
            <img src="../../assets/img/money.png" height="16">
            <p>{{details.price}}</p>
          </div>
        </div>
        <!--</BreadcrumbItem>-->
        <!--</Breadcrumb>-->
      </div>
      <div id="disc">
        <p style="font-weight: bold">详情：</p>
        {{details.disc}}
      </div>
      <div v-if="user.contact" class="contact">
        <img src="../../assets/img/phone.png" style="width: 20px">
        {{user.contact}}
      </div>
      <!--<div style="width: 400px">-->
      <div v-if="apply" class="apply-div">
        <ul class="apply">
          <li v-for="item in apply" @click="agree(item)" :style="{background: item.is_on? 'rgb(222, 234, 247)': ''}">
            <img :src="'../../../static/icons/' + item.user.icon" class="apply-icon" >
            <div style="padding-left: 15px">
              <p>{{item.user.username}}</p>
              <p style="font-size: 10px"><img src="../../assets/img/tinkle.png" style="height: 10px">&emsp;{{item.user.rate}}
              </p>
            </div>
            <p class="choice" v-if="!item.is_on">{{msg}}</p>
            <p v-else style="margin: auto"><img src="../../assets/img/ok.png" height="15"/></p>
          </li>
        </ul>
      </div>

      <!--</div>-->
      <div class="button">
        <Button @click="choose" :disabled="buttonUnused">{{buttonName}}</Button>
      </div>
    </Card>
    <Modal
      v-model="modal"
      title="评价"
      footer-hide>
      <!--<div v-if="haveRated">-->
      <div style="display: flex; flex-direction: column; align-items: center">
        <Rate allow-half :value.sync="valuetinkle" :disabled="haveRated? true:false" @on-change="changeRate"></Rate>
        <Button style="width: 60px" type="primary" ghost @click="toRate" v-if="!haveRated">提交</Button>
      </div>
      <!--{{valuetinkle}}-->
    </Modal>
  </div>
</template>

<script>
  import axios from 'axios';
  import Common from '../Common';

  axios.defaults.withCredentials = true;
  export default {
    name: "Task",
    data() {
      return {
        buttonName: '',
        host: Common.BASEHOST,
        buttonUnused: false,
        msg: '选我',
        modal: false,
        valuetinkle: 2.5,
        haveRated: true,
      }
    },
    props: {
      user: Object,
      details: Object,
      apply: Array
    },
    mounted: function () {
      // console.log
      // console.log(this.viewDetails)
      this.msg = '选我';
      if (this.user.apply === 0)
        this.buttonName = '删除任务';
      else if (this.user.apply === 1)
        this.buttonName = '申请';
      else if (this.user.apply === -1)
        this.buttonName = '取消申请';
      else if (this.user.apply === 999) {
        this.buttonName = '任务已被派发';
        this.buttonUnused = true;
      }
      if (this.apply && this.apply[0].is_on)
        this.msg = '不可选中';
      else
        this.msg = '选我';
      // console.log(this.apply)
    },
    methods: {
      choose: function () {
        let that = this;
        if (this.buttonName === '删除任务') {
          axios({
            url: that.host + 'delTask',
            method: 'POST',
            params: {id: that.details.id}
          }).then(res => {
            if (res.data.code === 1) {
              that.$parent.details = true;
              if (that.$parent.modelSelect === 'time')
                for (var i = 0; i < that.$parent.taskListTime.length; ++i) {
                  if (that.$parent.taskListTime[i].id === that.details.id) {
                    that.$parent.taskListTime.splice(i, 1);
                    break;
                  }
                }
              else
                for (var i = 0; i < that.$parent.taskListPrice.length; ++i) {
                  if (that.$parent.taskListPrice[i].id === that.details.id) {
                    that.$parent.taskListPrice.splice(i, 1);
                    break;
                  }
                }
              that.$Message.success('删除成功')
            } else if (res.data.code === -1) {
              that.$router.push({
                path: '/login',
                query: {path: '/'}
              });
              that.$Message.error(res.data.msg.errmsg);
            } else
              that.$Message.error(res.data.msg.errmsg);
          }).catch(err => {
            that.$Message.error('网络或服务器出错');
            console.log(err)
          })
        } else if (this.buttonName === '申请') {
          axios({
            url: that.host + 'apply',
            method: 'POST',
            params: {task: this.details.id}
          }).then(res => {
            if (res.data.code === 1) {
              that.$Message.success('申请成功');
              that.buttonName = '取消申请';
              that.user.apply = -1;
            } else if (res.data.code === -1) {
              that.$router.push({
                path: '/login',
                query: {path: '/'}
              });
              that.$Message.error(res.data.msg.errmsg);
            } else
              that.$Message.error(res.data.msg.errmsg);
          }).catch(err => {
            that.$Message.error('网络或服务器出错');
            console.log(err)
          });
        } else if (this.buttonName === '取消申请') {
          if (this.user.contact) {
            this.$Message.warning('请联系任务发起人更换新的执行人')
          }
          axios({
            url: that.host + 'delApply',
            method: 'POST',
            params: {task: this.details.id}
          }).then(res => {
            if (res.data.code === 1) {
              that.$Message.success('取消成功');
              that.buttonName = '申请';
              that.user.apply = 1;
            } else if (res.data.code === -1) {
              that.$router.push({
                path: '/login',
                query: {path: '/'}
              });
              that.$Message.error(res.data.msg.errmsg);
            } else
              that.$Message.error(res.data.msg.errmsg);
          }).catch(err => {
            that.$Message.error('网络或服务器出错');
            console.log(err)
          });
        }
      },
      agree: function (item) {
        if (item.is_on)
          this.rateUser(item);
        else{
          let flag = 1;
          let that = this;
          for (var i = 0; i < this.apply.length; ++i) {
            if (that.apply[i].is_on) {
              flag = 0;
              break;
            }
          }
          if (flag === 1) {
            axios({
              url: that.host + 'agree',
              method: 'POST',
              params: {task: that.details.id, apply_user: item.user.id}
            }).then(res => {
              if (res.data.code === 1) {
                for (var i = 0; i < that.apply.length; ++i) {
                  if (that.apply[i].user.id === item.user.id) {
                    that.apply[i].is_on = true;
                    break;
                  }
                }
                that.msg = '不可选中';
                that.$Message.success('成功');
              } else
                that.$Meaage.error(res.data.msg.errmsg)
            }).catch(err => {
              that.$Message.error('网络或服务器错误');
            })
          }
        }
      },
      rateUser: function (item) {
        // console.log(item);
        // console.log(item);
        if(item.is_on){
          // console.log(1);
          this.modal = true;
          if(item.rate === -1){
            console.log(1);
            this.valuetinkle = 2.5;
            this.haveRated = false;
          }
          else{
            this.haveRated = true;
            this.valuetinkle = item.rate;
          }
        }
      },
      toRate: function () {
        let that = this;
        console.log(that.valuetinkle);
        axios({
          url: that.host + 'rate',
          method: 'POST',
          params: {task: that.details.id, rate: that.valuetinkle}
        }).then(res => {
          if (res.data.code === 1)
          {
            that.$Message.success('评价成功');
            that.modal = false;
            for(var i=0; i<that.apply.length; ++i){
              if(that.apply[i].is_on)
              {
                that.apply[i].rate = that.valuetinkle;
                break;
              }
            }
          }
          else
            that.$Message.error(res.data.msg.errmsg);
        }).catch(err=> {
          console.log(err)
          that.$Message.error('网络或服务器错误');
        })
      },
      changeRate: function (item) {
       this.valuetinkle = item;
      }
    }
  }
</script>

<style scoped>
  /*.taskDetails{*/
  /*width: 55%;*/
  /*border-radius: 8px;*/
  /*background-color: white;*/
  /*}*/
  #card {
    width: 600px;
    height: 400px;
    /*display: flex;*/
    /*flex-direction: column;*/
    /*align-items: center;*/
  }

  .title {
    display: flex;
    height: 60px;
    flex-direction: row;
  }

  .icon {
    height: 60px;
    width: auto;
  }

  .user {
    height: 60px;
    display: flex;
    align-items: flex-end;
    width: 150px;
    /*margin-bottom: 50px;*/
    border-right: solid 1px #c0c0c0;
  }

  .time {
    /*float: bottom;*/
  }

  .canal {
    position: absolute;
    top: 8px;
    right: 8px;
    /*width: 30px;*/
  }

  .canal:hover {
    -webkit-transform: scale(1.3);
  }

  .title-price {
    display: flex;
    width: 300px;
    height: 60px;
    align-items: center;
    margin-left: 30px;
  }

  .price {
    display: flex;
  }

  .contact {
    text-align: center;
    margin-top: 30px;
  }

  .button {
    /*margin: 0 auto;*/
    /*justify-content: center;*/
    text-align: center;
    position: absolute;
    bottom: 30px;
    width: 100%;
    left: 0;
  }

  .apply {
    display: inline;
    text-align: center;
    /*margin-top: 50px;*/
    max-height: 120px;
    /*overflow-y: auto;*/
  }

  li {
    /*width: 180px;*/
    width: 45%;
    margin: 5px 2.5%;
    height: 50px;
    /*height: 50px;*/
    float: left;
    /*margin: 0 10px;*/
    /*background-color: pink;*/
    list-style: none;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    border-radius: 5px;
  }

  #disc {
    flex: none;
  }

  .apply-icon {
    height: 40px;
    width: auto;
    margin-left: 30px;
  }

  li:hover {
    /*content: '选我';*/
    background-color: rgb(222, 234, 247);
  }

  .choice {
    margin: auto;
    display: none;
  }

  li:hover .choice {
    display: block;
  }

  .apply-div {
    height: 120px;
    overflow-y: scroll;
  }

  @media screen and (max-device-width: 919px) {
    #card {
      width: 80%;
      /*height: 60%;*/
      margin-left: 10%;
    }
  }
</style>
