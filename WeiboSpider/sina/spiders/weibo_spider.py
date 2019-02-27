#!/usr/bin/env python
# encoding: utf-8
import re
from lxml import etree
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.utils.project import get_project_settings
from scrapy_redis.spiders import RedisSpider
import sys
import time

sys.path.append('..')
from sina.items import TweetsItem, InformationItem, CommentItem
from sina.spiders.utils import time_fix
import time


class WeiboSpider(RedisSpider):
    name = "weibo_spider"
    base_url = "https://weibo.cn"
    redis_key = "weibo_spider:start_urls"

    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        "DOWNLOAD_DELAY": 2,
    }

    def parse(self, response):
        if response.url.endswith('page=1'):
            # 如果是第1页，一次性获取后面的所有页
            # />&nbsp:html中的空格占位符
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parse, dont_filter=True, meta=response.meta)
        """
        解析本页的数据
        """
        tree_node = etree.HTML(response.body)
        # 选取所有的div元素+属性class=c+拥有id属性
        tweet_nodes = tree_node.xpath('//div[@class="c" and @id]')
        for tweet_node in tweet_nodes:
            try:
                tweet_item = TweetsItem()
                tweet_item['crawl_time'] = int(time.time())
                # todo 转发和评论的url
                tweet_repost_url = tweet_node.xpath('.//a[contains(text(),"转发[")]/@href')[0]
                tweet_cmt_url = tweet_node.xpath('.//a[contains(text(),"评论[")]/@href')[0]
                # 发送微博的用户id
                user_tweet_id = re.search(r'/repost/(.*?)\?uid=(\d+)', tweet_repost_url)
                tweet_item['weibo_url'] = 'https://weibo.com/{}/{}'.format(user_tweet_id.group(2),
                                                                           user_tweet_id.group(1))
                tweet_item['user_id'] = user_tweet_id.group(2)
                # _id作为微博的id
                tweet_item['_id'] = '{}_{}'.format(user_tweet_id.group(2), user_tweet_id.group(1))
                create_time_info = tweet_node.xpath('.//span[@class="ct"]/text()')[-1]
                # 去掉时间后面的部分 比如来自新浪微博/来自iphone
                if "来自" in create_time_info:
                    tweet_item['created_at'] = time_fix(create_time_info.split('来自')[0].strip())
                else:
                    tweet_item['created_at'] = time_fix(create_time_info.strip())

                like_num = tweet_node.xpath('.//a[contains(text(),"赞[")]/text()')[-1]
                tweet_item['like_num'] = int(re.search('\d+', like_num).group())

                repost_num = tweet_node.xpath('.//a[contains(text(),"转发[")]/text()')[-1]
                tweet_item['repost_num'] = int(re.search('\d+', repost_num).group())
                comment_num = tweet_node.xpath(
                    './/a[contains(text(),"评论[") and not(contains(text(),"原文"))]/text()')[-1]
                tweet_item['comment_num'] = int(re.search('\d+', comment_num).group())
                tweet_content_node = tweet_node.xpath('.//span[@class="ctt"]')[0]

                # 检测有没有阅读全文:
                all_content_link = tweet_content_node.xpath('.//a[text()="全文"]')
                if all_content_link:
                    all_content_url = self.base_url + all_content_link[0].xpath('./@href')[0]
                    yield Request(all_content_url, callback=self.parse_all_content, meta={'item': tweet_item},
                                  priority=1)

                else:
                    all_content = tweet_content_node.xpath('string(.)').replace('\u200b', '').strip()
                    tweet_item['content'] = all_content[1:]
                    yield tweet_item
                    # todo

                # 爬取评论用户信息和评论内容
                if tweet_item['comment_num'] > 0:
                    yield Request(url=tweet_cmt_url, callback=self.parse_cmt_info, meta={'weibo_id': tweet_item['_id']},
                                  priority=3)

                # # 爬取发微博的用户信息
                # yield Request(url="https://weibo.cn/{}/info".format(tweet_item['user_id']),
                #               callback=self.parse_information, priority=1)

                # todo 爬去转发用户的信息
                # todo 爬去转发用户的id和评论，赞数，加上微博的id可以匹配

            except Exception as e:
                self.logger.error(e)

    def parse_cmt_info(self, response):
        if not response.url.__contains__('page'):
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                for page_num in range(2, all_page + 1):
                    page_url = response.url + '&page=' + str(page_num)
                    yield Request(page_url, self.parse_cmt_info,
                                  meta=response.meta, priority=2)  # todo 需不需要 meta=response.meta
        """
        解析评论页面
        """
        cmt_tree_node = etree.HTML(response.body)
        cmt_nodes = cmt_tree_node.xpath('//div[@class="c" and @id]')
        weibo_id = response.meta['weibo_id']
        for cmt_node in cmt_nodes:
            try:
                cmt = CommentItem()
                cmt['weibo_id'] = weibo_id

                cmt['_id'] = cmt_node.xpath('./@id')[0]
                user_url = cmt_node.xpath('.//a/@href')[0]
                cmt['comment_user_id'] = re.search(r'\d+', user_url).group()

                create_time_info = cmt_node.xpath('.//span[@class="ct"]/text()')[-1]
                # 去掉时间后面的部分 比如来自新浪微博/来自iphone
                if "来自" in create_time_info:
                    cmt['created_at'] = time_fix(create_time_info.split('来自')[0].strip())
                else:
                    cmt['created_at'] = time_fix(create_time_info.strip())
                isreply = cmt_node.xpath('.//span[@class="ctt"]/text()')
                # cmt['content'] = contents.xpath('string(.)').replace('\u200b', '').strip()
                # 去掉text()[0]的"："
                content_node = cmt_node.xpath('.//span[@class="ctt"]')[0]
                all_content = content_node.xpath('string(.)').replace('\u200b', '').strip()
                # todo
                # if isreply[0].__contains__('回复'):
                #     cmt_node['reply_id'] = content_node.xpath('.//a/@href')[0]
                #     print('+++++++++++++++++++')
                #     print(cmt_node['reply_id'])
                cmt['content'] = all_content

                like_num = cmt_node.xpath('.//span[@class="cc"]/a[contains(text(),"赞[")]/text()')[0]
                cmt['like_num'] = int(re.search(r'\d+', like_num).group())
                cmt['crawl_time'] = int(time.time())

                # 评论用户的信息
                yield Request(url="https://weibo.cn/{}/info".format(cmt['comment_user_id']),
                              callback=self.parse_info, priority=3, meta={'cmt_item': cmt})

            except Exception as e:
                print('error happened ar comment parsing')
                self.logger.error(e)

    def parse_all_content(self, response):
        # 有阅读全文的情况，获取全文
        tree_node = etree.HTML(response.body)
        tweet_item = response.meta['item']
        content_node = tree_node.xpath('//div[@id="M_"]//span[@class="ctt"]')[0]
        all_content = content_node.xpath('string(.)').replace('\u200b', '').strip()
        tweet_item['content'] = all_content[1:]
        yield tweet_item
        time.sleep(0.3)

    def parse_info(self, response):
        cmt_item = response.meta['cmt_item']
        selector = Selector(response)
        text1 = ";".join(selector.xpath('body/div[@class="c"]//text()').extract())
        place = re.findall('地区;?[：:]?(.*?);', text1)
        if place and place[0]:
            place = place[0].replace(u"\xa0", "").split(" ")
            cmt_item["province"] = place[0]
            if len(place) > 1:
                cmt_item["city"] = place[1]
        yield cmt_item

    #
    # # 默认初始解析函数
    # def parse_information(self, response):
    #     """ 抓取个人信息 """
    #     information_item = InformationItem()
    #     information_item['crawl_time'] = int(time.time())
    #     selector = Selector(response)
    #     information_item['_id'] = re.findall('(\d+)/info', response.url)[0]
    #     text1 = ";".join(selector.xpath('body/div[@class="c"]//text()').extract())  # 获取标签里的所有text()
    #     nick_name = re.findall('昵称;?[：:]?(.*?);', text1)
    #     gender = re.findall('性别;?[：:]?(.*?);', text1)
    #     place = re.findall('地区;?[：:]?(.*?);', text1)
    #     # brief_introduction = re.findall('简介;[：:]?(.*?);', text1)
    #     birthday = re.findall('生日;?[：:]?(.*?);', text1)
    #     # sex_orientation = re.findall('性取向;?[：:]?(.*?);', text1)
    #     sentiment = re.findall('感情状况;?[：:]?(.*?);', text1)
    #     vip_level = re.findall('会员等级;?[：:]?(.*?);', text1)
    #     authentication = re.findall('认证;?[：:]?(.*?);', text1)
    #     if nick_name and nick_name[0]:
    #         information_item["nick_name"] = nick_name[0].replace(u"\xa0", "")
    #     if gender and gender[0]:
    #         information_item["gender"] = gender[0].replace(u"\xa0", "")
    #     if place and place[0]:
    #         place = place[0].replace(u"\xa0", "").split(" ")
    #         information_item["province"] = place[0]
    #         if len(place) > 1:
    #             information_item["city"] = place[1]
    #     # if brief_introduction and brief_introduction[0]:
    #     #     information_item["brief_introduction"] = brief_introduction[0].replace(u"\xa0", "")
    #     if birthday and birthday[0]:
    #         information_item['birthday'] = birthday[0]
    #     # if sex_orientation and sex_orientation[0]:
    #     #     if sex_orientation[0].replace(u"\xa0", "") == gender[0]:
    #     #         information_item["sex_orientation"] = "同性恋"
    #     #     else:
    #     #         information_item["sex_orientation"] = "异性恋"
    #     if sentiment and sentiment[0]:
    #         information_item["sentiment"] = sentiment[0].replace(u"\xa0", "")
    #     if vip_level and vip_level[0]:
    #         information_item["vip_level"] = vip_level[0].replace(u"\xa0", "")
    #     if authentication and authentication[0]:
    #         information_item["authentication"] = authentication[0].replace(u"\xa0", "")
    #     request_meta = response.meta
    #     request_meta['item'] = information_item
    #     yield Request(self.base_url + '/u/{}'.format(information_item['_id']),
    #                   callback=self.parse_further_information,
    #                   meta=request_meta, priority=3)
    #
    # def parse_further_information(self, response):
    #     text = response.text
    #     information_item = response.meta['item']
    #     tweets_num = re.findall('微博\[(\d+)\]', text)
    #     if tweets_num:
    #         information_item['tweets_num'] = int(tweets_num[0])
    #     follows_num = re.findall('关注\[(\d+)\]', text)
    #     if follows_num:
    #         information_item['follows_num'] = int(follows_num[0])
    #     fans_num = re.findall('粉丝\[(\d+)\]', text)
    #     if fans_num:
    #         information_item['fans_num'] = int(fans_num[0])
    #     yield information_item
    #     time.sleep(0.1)


if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl('weibo_spider')
    process.start()
