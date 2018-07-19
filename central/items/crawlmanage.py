# -*- coding: utf-8 -*-



from scrapy.item import Item, Field




class SMAccountItem(Item):
    """动态账号"""
    type_ = Field()
    site = Field()
    ref_id = Field()
    weibo_id = Field()
    weibo_name = Field()
    weibo_photo = Field()
    weibo_tweets = Field()
    weibo_followers = Field()
    weibo_following = Field()
    weibo_brief = Field()
    account = Field()
