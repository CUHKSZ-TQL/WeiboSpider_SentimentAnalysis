# 微博用户的行为与情感分析
借助Python抓取微博数据，并对抓取的数据进行情绪分析

## 第一部分：微博数据抓取
参考自[https://github.com/nghuyong/WeiboSpider/tree/search](https://github.com/nghuyong/WeiboSpider/tree/search)

### （一）利用高级搜索抓取指定微博
本部分请参考文件夹`WeiboSpider`中的内容

**1.安装依赖：**

mongodb\
phantomjs\
redis\
requirements.txt\
（安装好mongodb之后需要新建数据库`sina`）

**2.构建账号池**

购买微博小号，购买链接[http://www.xiaohao.shop/](http://www.xiaohao.shop/)\
将账号密码复制到 `WeiboSpider/sina/account_build/account.txt\`
运行 `WeiboSpider/sina/account_build/login.py`
运行成功会显示cookie创建成功

**3.自定义检索条件**

修改 `WeiboSpider/sina/redis_init.py` 中的日期，关键词，运行该文件进行微博检索\
（本项目默认抓取热门微博，如需更改可将url中的sort设置为time）

**4.开始爬虫**

运行 `WeiboSpider/sina/spider/weibo_spider.py` 抓取目标数据\
建议采取多线程同时抓取，提高速度\
Mac用户在命令行中输入 `scrapy crawl weibo_spider` \
Windows用户在命令行中输入 `scrapy runspider weibo_spider.py` 
![multi](https://github.com/CUHKSZ-TQL/WeiboSpider_SentimentAnalysis/blob/master/WeiboSpider/Images/multi.png)
**5.检查抓取的数据**

数据会存储在`sina` `database`中，`collection`下会有`tweets`（微博）`comments`（评论）`account`（账号）
![tweets](https://github.com/CUHKSZ-TQL/WeiboSpider_SentimentAnalysis/blob/master/WeiboSpider/Images/tweets.png)
![comments](https://github.com/CUHKSZ-TQL/WeiboSpider_SentimentAnalysis/blob/master/WeiboSpider/Images/comments.png)

### （二）根据用户id抓取任意微博
本部分请参考文件夹`WeiboSpiderSimple`中的内容

**1.安装依赖：**

mongodb\
requirements.txt\

**2.替换cookie：**

访问 https://weibo.cn/ 并登陆，获取对应的cookie，将`WeiboSpiderSimple/sina/settings.py`中的cookie换成你自己获取到的cookie

**3.指定爬取的用户ID**

将`WeiboSpiderSimple/sina/spider/weibo_spider.py`中的`start_uids`换成你想抓取的对象的微博ID。

**4.开始爬虫**

执行`scrapy crawl weibo_spider`或者直接在pycharm当中运行`WeiboSpiderSimple/sina/spider/weibo_spider.py`

## 第二部分：探索性分析
见`EDA.py`

## 第三部分：评论情绪分析
见`Sentiment analysis.ipynb`
