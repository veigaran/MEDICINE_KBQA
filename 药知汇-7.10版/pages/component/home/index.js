var app = getApp();

Component({
  
  /* 开启全局样式设置 */
  options: {
    addGlobalClass: true,
  },

  /* 组件的属性列表 */
  properties: {
    name: {
      type: String,
      value: 'cost'
    }
  },

  /* 组件的初始数据 */
  data: {

  },

  /* 组件声明周期函数 */
  lifetimes: {
    attached: function (options) {
        console.log('sss')
    },
    moved: function () {

    },
    detached: function () {

    },

  },

  /* 组件的方法列表 */
  methods: {
    //执行点击事件
    formSubmit: function (e) {

      //声明当天执行的
      var that = this;

      //获取表单所有name=keyword的值
      var formData = e.detail.value.keyword;

      //显示搜索中的提示
      wx.showLoading({
        title: '搜索中',
        icon: 'loading'
      })

      //向搜索后端服务器发起请求
      wx.request({

        //URL
        url: 'https://www.veiagra.top/wechat',

        //发送的数据
        data: { formData: JSON.stringify(formData) },

        //请求方式
        method: "POST",
        dataType: "json",

        //请求的数据时JSON格式
        header: {
          'content-type': 'application/json',
        },

        //请求成功
        success: function (res) {

          //控制台打印（开发调试用）
          console.log(res.data)

          //把所有结果存进一个名为re的数组
          that.setData({
            re: res.data,
          })

          wx.showToast({
            title: '已提交',
            icon: 'success',
            duration: 2000
          })

          //搜索成功后，隐藏搜索中的提示
          wx.hideLoading();
        }
      })
    },

    
  }

})

