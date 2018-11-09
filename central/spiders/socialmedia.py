# -*- coding: utf-8 -*-

from scrapy import Spider

from central.seedconfig import SOCIALMEDIA
from rules.socialmedia import WeiboAccountRule
from central.models import (
    SocialMedia
)


class SocialmediaSpider(Spider):
    """
    动态账户爬虫
    """

    name = 'central_socialmedia'
    custom_settings = {
        'COOKIES_ENABLED': True,
    }

    def __init__(self, **kw):
        super(SocialmediaSpider, self).__init__(**kw)

    def start_requests(self):
        for task in SOCIALMEDIA:
            if task.get('name') == "weibo_account":
                weibo_accounts = self.db_session.query(SocialMedia).filter(SocialMedia.site == "weibo").all()
                for weibo_account in weibo_accounts:
                    task.update(
                        account=weibo_account,
                        spider=self
                    )
                    rule = WeiboAccountRule(**task)
                    yield self.make_requests_from_url(
                            rule
                        )


    def make_requests_from_url(self, rule):
        return rule.start()

