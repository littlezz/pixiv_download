下载pixiv一个作者的所有插画

use
===========
打开程序后会进入一个简单的交互式命令行,下载好的在程序目录的collections文件夹内

login
--------
登陆时输入的密码不会显示,一股脑输入按回车就好


download
--------------
在交互命令行里输入 download 后接要下载的作者id 输入以空格隔开.

exit
---------
输入 exit 退出程序.



感想
==============
以前看到一个好的作者,打开作品列表,精挑细选,一张张的下载下来,有时候作品太多就只选自己最喜欢的,全部下载是绝无可能的.  
最近写了这个程序,完成的时候很激动,看着所有的作品好好的躺在文件夹里,非常兴奋.但是马上就觉得很寂寞,以前辛辛苦苦的手动一张张的下载,现在只需要打几个数字
然后猛按回车,接下来程序帮你做完一切,你可以去喝杯茶,看看片,聊聊天,等回来的时候图片就像尸体一样堆在相应的文件夹里,没有任何意义.然后脑中想的就是'看!多方便!','瞧,我能做到这样!'以及'我真tm牛逼!',
至于图片本身,根本懒得再点开,只是让他好好的躺再那儿,或者换个文件夹让他躺着.之前看到好的图片的喜悦早已当然无存,剩下的就只是方便快捷批量生产的空虚无聊.  
现在唯一能吸引我的估计就是程序运行是随机跳出的提示.

接下来会完成添加数据库的功能,届时可以使用update来保持自动更新下载作者的最新作品.后继的会增加下载动图的功能.  
啧啧,到时候联数字都不用敲的时候,不懂还有什么意义.可能到最后还是一张张的手动下载来得高兴.








step
=======

-  login success ---------------done
-  download all image from illustor with threading ---------->done
-  support auto check and update
-  support download manga
-  support download animation and turn to gif format

To Do
==============
- 多线程下载  ------->done
- ~~把装饰器修改为类的形式.~~
- 和数据库相关的操作不要使用多线程
- 完成交互和输入的解析 --------->done
- 先完成单纯下载的版本 --------->done
- 完成错误的提示 ------->done
- 模块话,解决互相调用的问题 -------->done
- 完成数据库操作api 

update
============
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

version
==============
download only beta 1.0