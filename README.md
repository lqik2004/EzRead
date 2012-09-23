#EzRead

EzRead是一款自动从目标网站上获取网页内容并自动发送到Kindle的脚本  
目前EzRead支持的站点有：  
[gd560.com](http://www.gd560.com)  
**更多网站支持可以通过内置模板扩展**    
![](http://distilleryimage11.s3.amazonaws.com/624da6a2f5ab11e1a58222000a1cde8e_7.jpg)     
目录：  
![](https://img.skitch.com/20120908-ju943iw4qqhn2h3jgyh1r8hui9.jpg)  
可跳转：  
![](https://img.skitch.com/20120908-bd3jmeeyfqhw7j97ghgmeei2m7.jpg)  
封面：  
![](https://img.skitch.com/20120908-n193wh9fna32wkfb5wgbwyxjtq.jpg)    
中文文件名显示：  
![](https://img.skitch.com/20120908-xcwgbnb9gfwb87gjwnksswh1b5.jpg)  
###特点
* 干净的网页内容：过滤了无用的广告，评论，连接等信息，只保留阅读内容
* 不伤眼睛的阅读：通过网络同步到Kindle上，更环保，更舒服
* 完全自动化：当第一次设置好，每当小说更新Kindle都会自动收到转换好的文本
* 精美的排版：从1.2版本之后，可以自动生成带封面，带目录，可右键跳转章节的小说
* 多任务：可以通过设置跟踪多个小说

###更新日志
*v1.3 增加了多任务和模板支持，通过设置配置文件可以配置多个小说内容获取，同时增加了模板扩展，可自行编写获取模板，增加对更多网站的支持
* v1.2 在生成的mobi文件中增加了中文文件名，作者信息，封面，中文目录，目录跳转，右键跳转等特性
* v1.1 增加了生成mobi版本的功能，（需要配合KindleGen，可以从amazon官网下载适合你的命令行版本），支持Kindle显示中文文件名（仅限mobi版本）**强烈建议启用mobi生成**  

###需求
* 一台安装*nix的电脑
* 如果想使用KindleGen生成mobi的话，需要i386架构的电脑，否则请关闭mobi生成方法
* python2.5以上

###部署说明
1. 把源文件拷贝到所需要的目录
2. 安装feedparser，自行Google
3. 到安装目录创建一个名为：**sendkindle.cfg**的文件，在文件中我提供了sample，这里是邮箱的设置信息，只需要设置一次
4. 到Amazon.com你的账户中添加你刚才设置的Email，用来允许接受邮件发送
4. 打开**bookinfo.cfg**文件，按照其中的例子设置，更多的配置信息见下文
5. 到Amazon官网下载适合你系统的KindleGen
5. 在终端执行**python EzRead.py -s**，需要等待一段时间，如果出现了**sent email to youremailaddress**就说明发送成功了
6. 在kindle上等待收取推送
7. 阅读

###参数帮助  
EzRead支持命令行参数，可以使用EzRead.py -h查看帮助  
加入-k 标示使用KindleGen转换成Mobi格式，带目录带封面，中文文件名  
加入-s 标示当自动生成文件后自动发送到Kindle  
不添加参数则标示不开启对应功能  
示例：  
	python EzRead.py -ks  
先转换文本到mobi然后发送到Kindle  
	python EzRead.py -s  
不转换文本，直接发送每个文本到Kindle（注意：当文件超过20个不要使用这个方法，邮箱附件有数量限制，会发生错误）    
	python EzRead.py -k  
只转换文本，不发送    
	python EzRead.py  
不转换，不发送，只获取为文本文件

###自动更新部署说明
如果想自动收取《武动乾坤》的更新，那么可以再进一步  
使用crontab，把EzRead.py [options]加入进去，频率随你，几小时更新，一天更新，几天更新均可  
剩下的事情EzRead.py会帮你做好

**关于Contab的使用请自行Google**

###配置文件说明 
####Bookinfo.cfg
从1.3版本之后EzRead支持了多任务，多网站支持，为了更方便的扩展，重新设计了配置文件的内容，下面逐一讲解一下。  
如果使用过1.3版本之前的朋友，其中lasturl配置文件已经作废了，启用了新的更强大的**bookinfo.cfg**配置文件  
打开新的配置文件，你会看到如下图格式的文件  
![](https://www.evernote.com/shard/s13/sh/a53f21e4-cae8-45df-bc06-fb32f425e794/157f1f4277527cc89ea53fd5a0a01a93/res/b761b869-1810-49a1-aabc-7a2dbbab3b09/skitch.png)  
图中的配置文件设置了两本图书分别为《武动乾坤》和《神印王座》
"[wdqk]"和"[sywz]"称为**section**，用来区分书籍  
"filename_perfix"为文件名前缀，比如设置了SYWZ_，那么生成的文件名前缀就是SYWZ_  
"extendfile"是模板文件，它是一个用Python写成的模块，其中包含了几个固定方法，后文会介绍。可以在这里自定义使用的模板，需要注意模板文件需放在和源文件一个目录下，文件名不要加上扩展py[c]?  
"author"书籍作者  
"bookname"书名  
"url"它是EzRead每次生成书籍的起点，这部分一般只需要在初次设置即可，URL会在每次运行EzRead之后自动根据需要改变  

####模板文件  
项目中自带了**gd560.py**，它为[gd560](http://www.gd560.com)网站的模板。  
![](https://www.evernote.com/shard/s13/sh/20dcb0f1-0062-41ba-a3f7-4e5f4de8cc48/d12f98b89a774bb4209bb58191ec50c9/res/9dbfb0eb-cdbf-434c-955c-684c59c38c63/skitch.png)  
其中定义了  
* get_PG_Num  
* get_main_content  
* get_nextpage_url  
* get_title  
四个方法，它们的功能如下：  
**get_PG_Num **：获取唯一的字符，用来区分各章生成的文件（暂时不能出现中文），gd560.py使用了url中的最后一部分数字作为pg_num，你也可以使用其它的  
**get_main_content**：从self.text（当前url内容）中获取主要的文本部分html，gd560.py使用了正则表达式  
**get_nextpage_url**：获取下一页连接  
**get_title**：获取本章标题  
以上四个方法名称不能改变，而且需要有返回值，具体实现可以根据不同网站自行修改  


###吐槽--盛大锦书  
这也是我为什么要做这个脚本的原因  
一个月前，我被盛大的电话销售忽悠，然后订购了盛大锦书全键盘二代，499元，在我已经有了Kindle Keyboard的情况下依旧购买了一台，主要的目的就是看看国产阅读器到了一个什么样的程度，而盛大锦书又是我曾经一直看好的产品。  
当我拿到盛大锦书之后，用了一天，我写了[一篇文章](http://res0w.com/?p=798)，有兴趣的可以看一下。  
我觉得锦书这款产品，唯一可以让我去使用的就是起点中文网的大量小说，这是Kindle等一系列其他电纸书无法复制的东西，锦书无非是个入口而已，一个让人阅读舒服的媒介。  
于是我给起点账号充了100元，然后订阅了《武动乾坤》进行测试，说实在的锦书看起点小说的表现还是不错的，自动更新，离线阅读，无广告，无干扰，体验非常不错。在购买之后的十几天中我一直用锦书看《武动乾坤》这小说，也是我第一次为看小说付费。  
不过好景不长，在大概十几天前，我离线的《武动乾坤》都已经看完了，需要连接WIFI进行更新，这个时候我才发现每次连接WIFI就会死机，我猜测是WIFI模块坏掉了，于是锦书成了废品，《武动乾坤》我也没有再看过。  
对于我，一个没有WIFI的锦书意味着不能获取起点中文网的小说，那么它的存在价值也就为0了，坦白说这东西哪一点都不如Kindle，但我依旧用了十几天的原因就是因为内置起点的不可替代性同时也没有特别难用，没有了锦书独特的资源，我为什么要用它呢。  
由于懒得去维修，所以这个锦书尸体就放在那里，我就萌生了用Kindle看小说的想法，也就有了此脚本。  

**最后忠告大家：就目前来说国产电纸书的质量还是不行，请谨慎购买**
**********************
###反馈问题
有任何问题可以和lqik2004#gmail.com进行联系  
或者到我的博客[http://res0w.com](http://res0w.com)进行留言  
也可以Follow我的Twitter:[@lqik2004](https://twitter.com/lqik2004)  
另外，还可以在Github上关注我的其他项目

###许可证
本项目采用[LGPL](http://www.gnu.org/copyleft/lesser.html)许可  
![LGPL](http://www.gnu.org/graphics/lgplv3-147x51.png)  



