## 微信小程序flask后端

#### 一、wxml页面

```html
<!-- 标题 -->
<view class="title">医药小助手</view>
 
<!-- 搜索框view -->
<view class="search_con">
 
<!-- 表单 -->
  <form bindsubmit="formSubmit">
  <!-- 记得设置name值，这样JS才能接收name=keyword的值 -->
    <input type="text" name="keyword" class="search_input" placeholder='请输入你的问题？'/>
    <button formType="submit" class="search_btn">搜索</button>    
  </form>
</view>
 
<!-- 搜索结果展示 -->
<view  class="search_result">
<view class="resname"> {{re}}</view>


<!-- 当提交空白表单的时候 -->
  <view class="empty">{{item.empty}}</view>
  <!-- 当有搜索结果的时候 -->
  <view class="resname">{{item.resname}}</view>
  <!-- 当查询不到结果的时候 -->
  <view class="noresult">{{item.noresult}}</view>
</view>

```

![image-20200303214148880](C:\Users\ph\AppData\Roaming\Typora\typora-user-images\image-20200303214148880.png)

#### 二、js函数

```javascript
const app = getApp()
Page({
  data: {},

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
      url: 'http://www.veiagra.top/wechat',

      //发送的数据
      data: {formData:JSON.stringify(formData)},

      //请求方式
      method: "POST",
      dataType:"json",

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
})
```

#### 三、css样式

```css
/* 搜索样式 */
.title{
  text-align: center;
  font-size: 20px;
  font-weight: bold;
}
 
 
.search_con{
  width: 80%;
  margin:20px auto;
}
 
.search_con .search_input{
  border: 1px solid rgb(214, 211, 211);
  height: 45px;
  border-radius: 100px;
  font-size: 17px;
  padding-left: 15px;/*此处要用padding-left才可以把光标往右移动15像素，不可以用text-indent*/
  color: #333;
}
 
.search_con .search_btn{
  margin-top: 15px;
  width: 100%;
  height: 45px;
  background: #56b273;
  color: #fff;
  border-radius: 100px;
}
 
.search_result{
  width: 80%;
  margin:10px auto;
}
 
 
.search_result .empty{
  text-align: center;
  color: #f00;
  font-size: 15px;
}
 
.search_result .noresult{
  text-align: center;
  color: #666;
  font-size: 15px;
}
 
.search_result .resname{
  text-align: left;
  color: #333;
  font-size: 15px;

}
```

#### 四、flask后台

```python
from flask import Flask, request, render_template, json
import kbqa

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('search.html')


@app.route('/wstmsearch', methods=['GET', 'POST'])
def wstm_search():
    answer = str
    if request.method == 'POST':
        # 取出待搜索keyword
        keyword = request.form['keyword']
        handler = kbqa.KBQA()
        # question = input("用户：")
        question = keyword
        answer = handler.qa_main(question)
        print('ok')
        # print("AI机器人：", answer)
        # print("*" * 50)

        return render_template('result.html', search_result=answer, keyword=question)
    return render_template('search.html')


@app.route('/wechat', methods=['POST'])
def wechat():
    answer = 'none'
    if request.method == 'POST':
        # print(1)
        # data = request.get_data()
        # print(data,type(data))
        data = request.get_json()
        print(data, type(data))
        question = data['formData']
        # print(2)
        print(question)
        # print(3)
        handler = kbqa.KBQA()
        answer = handler.qa_main(question)
        print("小程序")
        print(answer)
    return json.dumps(answer)


if __name__ == '__main__':
    app.run(debug=True)
```

![小程序测试](F:\A文档\python学习\Competition\Medication\小程序测试.gif)

