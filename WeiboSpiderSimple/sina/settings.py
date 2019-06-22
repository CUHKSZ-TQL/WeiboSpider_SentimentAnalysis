# -*- coding: utf-8 -*-

BOT_NAME = 'sina'

SPIDER_MODULES = ['sina.spiders']
NEWSPIDER_MODULE = 'sina.spiders'

ROBOTSTXT_OBEY = False

# 请将Cookie替换成你自己的Cookie
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Cookie':'_T_WM=3a1ebd9f48ef0afad4b21475d24cb835; SCF=Ah7lY-weSHiHZFO8a4AhdU2M9DzE22Hi1QoPKL4FDYRvi7epp1I8ChH7iL1bxTV34tHOVdvDWLw7AvRlTvUyf4M.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhA2mCkVcNirjfFaHKuP7QR5JpX5K-hUgL.Fo-feoMXSh54S0z2dJLoIpLZ9PS0IgHki--4i-82iKysi--4iKL2iK.E; SUB=_2A25xbhv0DeRhGeBH41EQ8CjIwjqIHXVSkKW8rDV6PUJbkdANLWP2kW1NQb4OXQl-ufr2zOa73CnchCtzMHeg2EoR; SUHB=0auQJcCx50iY4E; _T_WL=1; _WEIBO_UID=6983106496'
}

# 当前是单账号，所以下面的 CONCURRENT_REQUESTS 和 DOWNLOAD_DELAY 请不要修改

CONCURRENT_REQUESTS = 16

DOWNLOAD_DELAY = 3

DOWNLOADER_MIDDLEWARES = {
    'weibo.middlewares.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None
}

ITEM_PIPELINES = {
    'sina.pipelines.MongoDBPipeline': 300,
}

# MongoDb 配置

LOCAL_MONGO_HOST = '127.0.0.1'
LOCAL_MONGO_PORT = 27017
DB_NAME = 'Sina'
