pixiv_download for win
============================
下载pixiv一个作者的所有插画,windows平台版本.  
因为windows的命令行太弱,无法输出一些特殊字符.win版本移除了彩色的输出,和名字的输出.功能没有删减.    
另有封装好的可执行文件放在arch目录中.  



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


详细指令用法
-----------------


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

* * *



step
-----------

-  login success ---------------done
-  download all image from illustor with threading ---------->done
-  support auto check and update ------------->done!
-  ~~support download manga~~  
-  ~~support download animation and turn to gif format~~

to do
-------------
- 考虑图形化.