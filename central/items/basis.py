# -*- coding: utf-8 -*-



from scrapy.item import Item, Field


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
    account = Field()
    s3_images = Field()
    thumb_images = Field()
    tiny_images = Field()
    tags = Field()
    images = Field()



class TweetImageItem(Item):
    """动态内容图片"""

    tweet_id = Field()
    image = Field()
    priority = Field()
    is_gif = Field()


class TweetHotsearchItem(Item):

    """微博热搜"""
    order_number = Field()
    keyword = Field()
    hot_degree = Field()
    hottime = Field()


