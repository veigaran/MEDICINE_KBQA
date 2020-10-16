# 项目说明

## 一、后端介绍

### 1.1项目整体结构图

![image-20201016191608117](https://gitee.com/veigara/images/raw/master/img/image-20201016191608117.png)

### 1.2数据构建模块

#### 1.2.1数据来源

数据来源是老师直接给我们的，并不是自己写爬虫搞的（。・＿・。）ﾉ获取方式就不过多介绍了；

源文件是一个xlsx文件，包括常见药物的名称、用法、禁忌等等字段，这些也是后续检索的主要字段信息

#### 1.2.2数据清洗

因原始文件内包括很多无用信息，需人工处理一下，也比较简单，python写个小脚本就搞定了；

#### 1.2.3数据库构建（知识图谱）

因本项目是一个简易的KBQA项目，数据库存储没有选择常见的关系数据库，而是选择图数据库Neo4j。关于此数据库的具体使用说明可以去看看相关帖子，说明的比较详细了，这里说一下它的一些特殊地方。此数据库可以很好的进行可视化展示，更关键的是可以实现不同实体之间的联系，实体间的属性，对于后续检索十分方便。

数据库导入方式，方式很多，可以使用其官方的sql语句导入，个人使用的是python的py2neo库进行导入，具体代码见相应文件

至此，数据库部分已经完成

### 1.3问题解析模块

这个是项目的重点，也是项目的关键。主要包括“用户意图识别”和“实体识别”两个模块，这两个又牵扯出很多模型的训练问题，可以说搞定了这个部分基本完成70%了。

#### 1.3.1意图识别

关于此部分的原理可以去找找论文，现在已经有很多种实现方式了，本项目采取的是一种比较简单的、功能单一的意图识别。

简单的说，这个部分就是要完成用户输入问句，程序可以判断问句的意图是什么，比如，用户输入“感冒吃什么药”，计算机应识别出意图为“疾病的适用药物”。

因实现的功能较少，故本项目采取训练分类模型（SVM）来完成常见的意图识别，首先手工构建问句集（手工编写几个模版，然后python写脚本进行关键词替换）作为训练的语料，然后基于sklearn库训练SVM分类器，最后准确率可达99%，效果还可以

具体代码见对应文件

#### 1.3.2实体识别

NER常规NLP项目了，实现方式很多，代码现在也很多了，本次项目是参考这个，说明很详细，基于pytorch写的，最后模型识别效果也很好，这里不做赘述

https://github.com/DengYangyong/medical_entity_recognize

### 1.4其它

除了上述两个重要模块外，还需要实现彼此的调用，这里主要是以下几个文件

```
Entity_Extractor.py 	//实体识别
FindSim.py	//相似度查询
Search_Answer.py  // 答案检索，也即数据库检索
Predict.py  //NER模型调用
kbqa.py  //接口
```

当然，为了项目的完善，增加实用性，还增加了一些其它功能，如相似度检索，基于模版匹配等等，这里不做介绍，详见代码部分

至此，后端部分介绍完毕，到这里已经实现本地的kbqa功能

## 二、Flask

实现了后端后，为了将项目部署到服务器，还需要相应的Web框架，python端的话常见的就是Django和Flask，本次选用的是轻量级的Flask，因其只作为后端接口，实现很简单，代码如下

```python
@app.route('/')
def hello_world():
    return render_template('search.html')

//网页版 （其实可以不需要，主要为了测试用）
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
        print("AI机器人：", answer)
        print("*" * 50)

        return render_template('result.html', search_result=answer, keyword=question)
    return render_template('search.html')

//供小程序调用接口
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
```

## 三、服务器部署

**之前没有接触过服务器部署，也都是一步一步摸索的，大多数是参考这个博客https://blog.csdn.net/qq_40423339/article/details/86606308**

下面这个是我个人服务器部署的记录，可以参考一下，说实话当时搞这个还花了不少时间，建议上手之前，先去学学`linux`相关的知识；

简单的说购买了服务器后，你只需要安装相应的环境以及容器，比如我这里的`nginx、gunicorn`，还有安装相应的`python`、第三方包等等，可以理解为在一台全新的`linux`电脑上配置项目环境，遇到bug就去Google、百度搜一搜，基本都可以解决的。实现解决不了去找懂得人问问~

#### 1.1服务器选择

服务器选择了阿里云服务器，具体为Ubuntu16.04 64位系统，内存2GB，硬盘40GB，1M固定宽带；因费用过高，使用了学生优惠下购买了3个月云服务器，总计28.5元。

#### 1.2服务器设置

##### 1.2.1设置远程链接密码

![image-20200303171401569](https://gitee.com/veigara/images/raw/master/img/image-20200303171401569.png)

如图，点击重置密码，之后保存，方便在本地进行远程调试；

为快速进行调试，使用工具为**WinSCP+Xshell6**进行控制台操作以及文件传输；

##### 1.2.2添加安全组规则

该步骤是为了添加相应的端口，否则无法访问

![image-20200303171654096](C:\Users\ph\AppData\Roaming\Typora\typora-user-images\image-20200303171654096.png)

![image-20200303171710781](https://gitee.com/veigara/images/raw/master/img/image-20200303171710781.png)

以上均为本次项目需开放的端口，其中80端口、8080端口、443端口、7474端口很重要

若需添加其他端口规则，则进行配置即可，如下图

![image-20200303171849566](https://gitee.com/veigara/images/raw/master/img/image-20200303171849566.png)

#### 1.3服务器相关软件安装

系统为ubuntu，主要使用apt工具，方便进行软件下载及更新。

本次项目架构为**Flask+Nginx+Gunicorn**，同时数据库为neo4j图数据库，则主要安装软件工具即这几个。

##### 1.3.1配置虚拟环境

在~/目录下创建文件夹，取名任意，如 /envs

**安装 **

```
pip install virtualenv
pip install virtualenvwrapper
```

**配置.bashrc**

打开.bashrc文件

```
vim ~/.bashrc
```

添加以下代码

```
export WORKON_HOME=$HOME/.envs
export PROJECT_HOME=$HOME/workspace
source /usr/local/bin/virtualenvwrapper.sh
```

添加vim用法

> 1.进入编辑器后按 字母“i”即可进入编辑状态（此时左下角会出现  “插入”）
>
> 2.退出的时候分为4种情况：保存退出、正常退出、不保存退出以及强制退出
>
> 2.1：保存退出：按“Esc”键后 此时的“插入”会消失，然后按Shift+zz 就可以保存修改内容并退出
>
> 2.2：不保存退出：当修改修改了一部分内容后发现修改错了，此时就会进行不保存退出；按“Esc”键后，再输入“：”之后在输入命令时直接输入“q!” 
>
> 2.3：强制退出：  按“Esc”键后，再输入“：”之后在输入命令时直接输入“!”
>
> 2.4：正常退出：按“Esc”键后，再输入“：”之后在输入命令时直接输入“q”

使.bashrc生效

```
source ~/.bashrc
```

**创建虚拟环境**

```
mkvirtualenv py_flask  //后面名字任意
```

**进入虚拟环境**

```
workon py_flask
```

发现命令行前出现（py_flask）即说明成功，如下图所示

![image-20200303205546749](https://gitee.com/veigara/images/raw/master/img/image-20200303205546749.png)

##### virtualenvwrapper 命令

- 创建虚拟环境：`mkvirtualenv new_env`
- 使用虚拟环境：`workon new_env`
- 退出虚拟环境：`deactivate`
- 删除虚拟环境: `rmvirtualenv new_env`
- 查看所有虚拟环境：`lsvirtualenv`

##### 1.3.2安装Nginx

安装过程中使用apt工具无法安装，故采用**离线安装方式**；

在官网下载linux对应的版本，通过winscp上传到服务器，解压缩进行安装。此外安装nginx前需要安装**gcc -c++、pcre、zlib、openssl**等工具，安装方式采用离线安装

安装方式（以nginx为例）

```
cd /usr/local/software  //cd到安装路径
$ wget http://nginx.org/download/nginx-1.8.0.tar.gz  //此步骤不需要，因已上传安装包
$ tar -zxvf nginx-1.16.1.tar.gz  //解压缩
$ cd nginx-1.16.1 
// 将Nginx安装在/usr/local/software上
$ ./configure --prefix=/usr/local/src/nginx
$ make && make install
```

**在线安装**

```
# 安装命令
sudo apt-get install nginx 
#开启Nginx
/etc/init.d/nginx start #启动
/etc/init.d/nginx stop  #停止
# 更改conf配置文件
nginx -t
usr/local/webserver/nginx/sbin/nginx -s reload            # 重新载入配置文件
/usr/local/webserver/nginx/sbin/nginx -s reopen            # 重启 Nginx
/usr/local/webserver/nginx/sbin/nginx -s stop              # 停止 Nginx
```

**配置Nginx**

```
vim /etc/nginx/sites-available/default
```

此步骤可以使用winscp打开对应目录下的default文件，进行修改并保存

具体修改如下

```
# 如果是多台服务器的话，则在此配置，并修改 location 节点下面的 proxy_pass 
upstream flask {
        server 127.0.0.1:5000;
        server 127.0.0.1:5001;
}
server {
        # 监听80端口
        listen 80 default_server;
        listen [::]:80 default_server;

        root /var/www/html;

        index index.html index.htm index.nginx-debian.html;

        server_name _;

        location / {
                # 请求转发到gunicorn服务器
                proxy_pass http://127.0.0.1:5000;
                # 请求转发到多个gunicorn服务器
                # proxy_pass http://flask;
                # 设置请求头，并将头信息传递给服务器端 
                proxy_set_header Host $host;
                # 设置请求头，传递原始请求ip给 gunicorn 服务器
                proxy_set_header X-Real-IP $remote_addr;
        }
}
```

测试nginx是否正常启动

```
/etc/init.d/nginx start
```

打开浏览器，输入你的服务器ip地址，若出现welcome to nginx 或502 Bad Gateway即表示正常

##### 1.3.3安装Gunicorn

直接使用pip工具

```
pip install gunicorn
```

安装完成后的启动flask项目

**短暂运行**

```
gunicorn -w 2 -b 127.0.0.1:5000 app:app
```

**后台运行**

```
gunicorn -w 2 -b 127.0.0.1:5000 app:app -D
```

**项目结束运行**，**若出现异常，则需要检查当前进程，并强制结束**

```
ps -aux |grep gunicorn   //查看当前gunicorn的进程
```

```
kill -9 对应最小的进程号 如 kill -9 3514
```

##### 1.3.4安装neo4j数据库

安装前需要安装JDK，同样使用离线安装方式；

安装后启动与停止等

> 1.cd 到neo4j安装目录下的bin文件夹   /usr/local/neo4j-community-3.5.14/bin
>
> 2.输入 ./neo4j console 
>
> ./neo4j stop
> 另外neo4j还有其他命令，执行方式相同：
>
> neo4j { console | start | stop | restart | status }
> 如果，./neo4j stop
>
> 如果不能停止neo4j，
> 用kill -s 9 强制杀掉进程。

**远程访问地址**

 http://116.62.180.245:7474/browser/ 

user：neo4j	

passcode：123456

本地代码已调试好，需要解决两个问题，一是本地图数据库转移，二是在flask项目生成的虚拟环境中安装所有需要的包

#### 2.1图数据库迁移

因本地已生成图数据库文件，再次在云端生成将浪费很多时间，故可以将本地的数据库导出后在上传到服务器。

**注：数据库迁移必须关闭数据库**

##### 2.1.1关闭本地数据库

```
/usr/share/neo4j/bin
neo4j stop
```

##### 2.1.2数据导出

```
./neo4j-admin  dump --database=graph.db --to=/home/graph.db.dump  //to后面的为导出路径，可自由更改
```

##### 2.1.3数据导入

首先通过winscp将刚才生成的.dump文件上传到服务器，之后执行以下命令

```
neo4j-admin load --from=/home/robot/Neoj_data/graph.db.dump --database=graph.db --force  //同理 from=后为路径，需根据实际更改
```

之后重启数据库即可

#### 2.2 flask项目环境

因尝试过将本地flask项目的所需包导出为txt文件，之后统一安装，但是具体操作过程中生成了很多没用的包，文件很大，故采取手动安装方式，因为本次项目所需python包较少

安装方式

```
pip install py2neo  //以py2neo包举例，其他类似，依次安装即可
```

测试flask项目

1、将flask项目上传

2、进入虚拟环境 ，如我的 flask_test

```
workon flask_test
cd flask_test
gunicorn -w 2 -b 127.0.0.1:5000 app:app
```

3、浏览器输入ip地址进行检验

## 四、小程序搭建

### 4.1 js函数调用

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

因为核心就这一个后台API接口调用，上述服务器以及flask项目部署好之后，直接用就好了。

### 4.2 小程序页面设计

一开始是按照常规方法，看了微信官方出的页面设计语言，也就是wxml那几个东西，其实和html差不太多，但是第一版出来的时候非常丑，之后比赛就给舍弃了。

后来在逛github的时候，发现了还有别人写好的**“组件”**可以使用，瞬间发现了新大陆，有了这个，设计那个页面就相当于搭积木了，需要什么功能，直接复制代码过去，然后根据需要改一改就好了，简直不要太方便，这里推荐两个，个人认为比较好看

```
https://doc.mini.talelin.com/component/

http://inmap.talkingdata.com/wx/index_prod.html#/docs/guide/start
```



至此，该项目说明完毕；