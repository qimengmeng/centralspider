# -*- coding: utf-8 -*-



from scrapy.item import Item, Field



class NewsItem(Item):
    """类说明
    图文资讯
    """
    pubaccount_id = Field()
    title = Field()
    subtitle = Field()
    origin = Field()
    image = Field()
    orig_url = Field()
    content = Field()
    publish_tm = Field()
    ref_id = Field()

    tags = Field()
    author = Field()
    author_name = Field()
    column_content = Field()



class TweetItem(Item):
    """动态内容"""
    url = Field()
    publish = Field()
    website = Field()
    content = Field()
    weibo_id = Field()
    up_num = Field()
    retweet_num = Field()
    comment_num = Field()
    operation = Field()

    ###########
    # 头图
    # 1. 首选twitter card中的image，次选og中的image，三选正文中第一个图片
    # 2. 可以为空
    image_urls = Field()
    images = Field()
    image_paths = Field()

    ###########


class TweetImageItem(Item):
    """动态内容图片"""

    tweet_id = Field()
    image = Field()
    priority = Field()
    is_gif = Field()

