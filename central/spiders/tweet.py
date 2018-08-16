# -*- coding: utf-8 -*-

from scrapy import Spider
from sqlalchemy import and_


from rules.tweet import (
    WeiboTweetRule,
)
from central.seedconfig import TWEET
from central.models import (
    SocialMedia,
)



class TweetSpider(Spider):
    """
    动态资讯爬虫
    """

    name = 'central_tweet'
    custom_settings = {
        'COOKIES_ENABLED': True,
    }

    def __init__(self, **kw):
        super(TweetSpider, self).__init__(**kw)

    def start_requests(self):
        for task in TWEET:
            if task.get('name') == "weibo_tweet":
                weibo_accounts = self.db_session.query(SocialMedia).filter(
                                                                        and_(
                                                                    SocialMedia.site == "weibo",
                                                                    SocialMedia.weibo_name != None,
                                                                        )

                                                                        ).all()
                weibo_accounts = weibo_accounts[0:20]
                for weibo_account in weibo_accounts:
                    task.update(
                        account=weibo_account,
                        spider=self
                    )
                    rule = WeiboTweetRule(**task)
                    yield self.make_requests_from_url(
                        rule
                    )


    def make_requests_from_url(self, rule):

        return rule.start()
