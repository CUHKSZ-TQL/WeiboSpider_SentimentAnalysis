# -*- coding: utf-8 -*-
from scrapy import Item, Field


class TweetsItem(Item):
    """ 微博信息 """
    _id = Field()  # 微博id1
    weibo_url = Field()  # 微博URL1
    created_at = Field()  # 微博发表时间1
    like_num = Field()  # 点赞数1
    repost_num = Field()  # 转发数1
    comment_num = Field()  # 评论数1
    content = Field()  # 微博内容1
    user_id = Field()  # 发表该微博用户的id1
    crawl_time = Field()  # 抓取时间戳1


class InformationItem(Item):
    """ 个人信息 """
    _id = Field()  # 用户ID
    nick_name = Field()  # 昵称
    gender = Field()  # 性别
    province = Field()  # 所在省
    city = Field()  # 所在城市
    brief_introduction = Field()  # 简介
    birthday = Field()  # 生日
    tweets_num = Field()  # 微博数
    follows_num = Field()  # 关注数
    fans_num = Field()  # 粉丝数
    sex_orientation = Field()  # 性取向
    sentiment = Field()  # 感情状况
    vip_level = Field()  # 会员等级
    authentication = Field()  # 认证
    person_url = Field()  # 首页链接
    crawl_time = Field()  # 抓取时间戳


class RelationshipsItem(Item):
    """ 用户关系，只保留与关注的关系 """
    _id = Field()
    fan_id = Field()  # 关注者,即粉丝的id
    followed_id = Field()  # 被关注者的id
    crawl_time = Field()  # 抓取时间戳


class CommentItem(Item):
    """
    微博评论信息
    爬去评论用户的id1，评论内容1，发表时间1，赞数1，是否回复1，
    回复id（为url编码要转），加上微博的id可以匹配

    """
    _id = Field()
    comment_user_id = Field()  # 评论用户的id
    content = Field()  # 评论的内容
    weibo_id = Field()  # 评论的微博id
    created_at = Field()  # 评论发表时间
    like_num = Field() # 赞数
    reply_id = Field() # 回复id
    crawl_time = Field()  # 抓取时间戳
    province = Field()
    city = Field()


