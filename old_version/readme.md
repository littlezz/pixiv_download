pixiv_download
===================
下载pixiv一个作者的所有插画  

目前情况
---------------
由于我以前的习惯不好, 现在默认的文件名改变之后下载失效了, 而且也不是简单改动就能修好的, 所以决定重写 ---11-27


Windows平台
==============
因为windows的命令行编码方式为gbk,无法输出一些特殊字符，所以win版本移除了彩色的输出,和名字的输出.功能没有删减.
另有封装好的可执行文件放在arch目录中.

快速开始
------------
打开程序后会进入一个简单的交互式命令行,下载好的在程序目录的collections文件夹内

- 打开程序,登陆,输入密码是不会显示符号的
- 输入`add` 后面跟作者的id,多个id空格隔开,随后作品会自动下载
- 输入`update` 自动更新之前添加过的作者的作品
- `del` + 作者id ,将作者从数据移除(不会删除图片)
- `exit` 退出程序
- `authors` 输出数据库中作者的信息
- `illusts` 输出数据库中作品的信息


截图
-----------------
![](https://github.com/littlezz/pixiv_download/blob/master/old_version/screenshot/windows_2.jpg)  
![](https://github.com/littlezz/pixiv_download/blob/master/old_version/screenshot/windows_3.jpg)  
![](https://github.com/littlezz/pixiv_download/blob/master/old_version/screenshot/windows_4.jpg)  _


* * *

Linux
=============

quickstart
------------
打开程序后会进入一个简单的交互式命令行,下载好的在程序目录的collections文件夹内

- 打开程序,登陆,输入密码是不会显示符号的
- 输入`add` 后面跟作者的id,多个id空格隔开,随后作品会自动下载
- 输入`update` 自动更新之前添加过的作者的作品
- `del` + 作者id ,将作者从数据移除(不会删除图片)
- `exit` 退出程序
- `authors` 输出数据库中作者的信息
- `illusts` 输出数据库中作品的信息
- `authors by [order_by]` 输出信息,按不同的方法排序,比如以作者的名字排序,输入`authors by name`
- `illusts by [order_by]` 同上,作品信息.


screenshot
--------------
![](https://github.com/littlezz/pixiv_download/blob/master/old_version/screenshot/add-operator.png)  
![](https://github.com/littlezz/pixiv_download/blob/master/old_version/screenshot/downloading.png)  
![](https://github.com/littlezz/pixiv_download/blob/master/old_version/screenshot/finish-report.png)

* * *

详细指令用法
-----------------

###authors [order_by]
list authors' info that in database
if you want special order,for example, order by author's name, use  
`authors by name`  
support order = `name`,`id`,`add_date`

###illusts [order_by]
list illusts' info that in database

like the command`authors`,  
support order = `id`,`author`,`title`,`add_date`

###add [author_id,]
将作者添加到数据库并下载其作品,随后可用update指令保持数据库中作者的作品更新

###del [author_id,]
删除作者id,并将有关下载记录移除.

###update [author_id,]
检查并更新数据库中作者的作品

###download [author_id,]
在交互命令行里输入 `download` 后接要下载的作者id 输入以空格隔开.

###exit
输入 exit 退出程序.


Required
----------------
- python3 
- requests >= 2.3.0
- beautifulsoup
- lxml

* * *

感想
-----------------
以前看到一个好的作者,打开作品列表,精挑细选,一张张的下载下来,有时候作品太多就只选自己最喜欢的,全部下载是绝无可能的.  
最近写了这个程序,完成的时候很激动,看着所有的作品好好的躺在文件夹里,非常兴奋.但是马上就觉得很寂寞,以前辛辛苦苦的手动一张张的下载,现在只需要打几个数字
然后猛按回车,接下来程序帮你做完一切,你可以去喝杯茶,看看片,聊聊天,等回来的时候图片就像尸体一样堆在相应的文件夹里,没有任何意义.然后脑中想的就是'看!多方便!','瞧,我能做到这样!'以及'我真tm牛逼!',
至于图片本身,根本懒得再点开,只是让他好好的躺再那儿,或者换个文件夹让他躺着.之前看到好的图片的喜悦早已当然无存,剩下的就只是方便快捷批量生产的空虚无聊.  
现在唯一能吸引我的估计就是程序运行是随机跳出的提示.

接下来会完成添加数据库的功能,届时可以使用update来保持自动更新下载作者的最新作品.后继的会增加下载动图的功能.  
啧啧,到时候联数字都不用敲的时候,不懂还有什么意义.可能到最后还是一张张的手动下载来得高兴.

### 一个月之后 ###

我去, 我已经看不懂我的程序了...  
我记得之前写的时候已经尽量清晰和加上注释了, 结果还是太年轻, 最重要的三个类我以为自己最清楚, 结果现在完全看不懂他们在干什么, 而且由于大量
装饰器 和多线程的关系, 简直就是一团糟, 醉了.

加上manga功能之后我要重写一次.

step
-----------

-  login success ---------------done
-  download all image from illustor with threading ---------->done
-  support auto check and update ------------->done!
-  ~~support download manga~~  
-  ~~support download animation and turn to gif format~~

To Do
-------------
- 多线程下载  ------->done
- ~~把装饰器修改为类的形式.~~
- 和数据库相关的操作不要使用多线程 ------>done
- 完成交互和输入的解析 --------->done
- 先完成单纯下载的版本 --------->done
- 完成错误的提示 ------->done
- 模块话,解决互相调用的问题 -------->done
- 完成数据库操作api  ----------->done
- 完成add,del指令的验证和对数据库的修改 ---------->done
- 写完add,del ---------------->done
- 在错误的提示加上前缀 ----------->done
- support update ----------->done
- 数据库中保存作者名字 ---------->done
- 更新时更新作者名字 ------------>done
- ~~恢复非200重连~~
- ~~让prompt格式更准确~~
- 在readme 中添加图片----------->done
- 记录作者和作品的加入时间 ------------->done
- 输出数据库信息是多种排序选择 --------->done
- ~~beta 2.0~~
- 加入时间的处理可能要再考虑一下更好的办法 
- 修正windows下文件夹名字中不能包含特殊字符的bug ----------->done
- support download manga
- 重构



update
------------
- 登陆成功 ------------------------------------------------------->2014-9-11
- 提取作者所有作品,解析网址成功 -------------------------------------> 9-12
- 带有重连的连接  ------------------------------------------------->9-13
- 多线程提取作品网址 ---------------------------------------------->9-14
- 多线程下载 ----------------------------------------------------->9-15
- 折腾多线程的数据库操作,决定使用单线程操作数据库. 提升重连.----------->9-16
- 简单的交互 ------------------------------------------------------>9-17
- 增加错误提示 ----------------------------------------------------->9-17
- 解决了互相调用问题 ----------------------------------------------->9-18
- 完成进度显示和错误提示,更加完善的重连功能. 增加操作后的总结功能--------------------------->9-18
- download only beta1.0   --------------------------------------------->9-18
- 修正一些提示的输出格式 -------------------------------------------->9-18
- 写一些数据库操作api, Downloader的方法重新组织了一下-------------------9-19
- 数据库操作 -------------->9-20
- 修正数据库api的错误 ---------->9-20
- 添加了对add,del,list 操作的检查. --------------->9-21
- support `add` , and `del`, `list`, `illusts`  -------------->9-22
- support `update` ----------------->9-23
- 在每个错误提示前加了'error'的前缀. 有色彩了现在! ----------->9-24
- 修改readme ------------>9-25
- 文件夹命名方式改变.add时,验证id正确性,并将作者昵称计入数据库,修复Error提示的'Error' 重复的bug, 暂时吧非200状态重连移除. ---->9-26
- 使用`update` 时同时更新 数据库中的名字. -------------->9-27
- 在404的状态下进行重连, 记录非200状态到`status_error.log` 中. ------------>9-28
- 记录作品加入的时间,在`iilusts` 中有显示 ------------------------------>9-28
- 将databaseapi从model中独立了出来,作者列表显示加入时间,修复可以update不存在的用户id的bug -------->9-29
- 将`list`指令改为`authors`,  输出信息可以按不同类别排序 ---------->9-30
- 小改动,加上了截图----------->10-1
- 暂时不弄动图了(<-弄不出)-------->10-2
- windows version --------------->10-8
- 移除特别的windows 版本，因为要修改的只有prompt，载如不同的prompt就可以了,修复下载失败依然添加数据库的bug,封装好的文件在arch目录下 ---------->10-9
- windows safe dirname -------------------> 11-16


version
----------------
正式版
pixiv download dev ~~V2.13~~