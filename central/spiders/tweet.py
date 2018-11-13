# -*- coding: utf-8 -*-
from datetime import datetime

from scrapy import Spider, signals
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

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(TweetSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_error, signal=signals.spider_error)
        return spider

    def __init__(self, **kw):
        super(TweetSpider, self).__init__(**kw)
        self.add_handler(self.logger.logger)
        logger = self.logger
        print logger

    def start_requests(self):
        for task in TWEET:
            if task.get('name') == "weibo_tweet":
                weibo_accounts = self.db_session.query(SocialMedia).filter(
                                                                        and_(
                                                                    SocialMedia.site == "weibo",
                                                                    SocialMedia.weibo_name != None,
                                                                        )

                                                                        ).all()
                # weibo_accounts = weibo_accounts[:1]
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

    def add_handler(self, logger):

        # test = logger.logger

        from pythonjsonlogger import jsonlogger
        from logstash import TCPLogstashHandler
        logHandler = TCPLogstashHandler('localhost', 5959, version=1)
        formatter = jsonlogger.JsonFormatter()
        logHandler.setFormatter(formatter)
        logger.addHandler(logHandler)

    def spider_error(self, failure, response, spider):

        message = "Error on {0};微博账号:{1}traceback: {2}".format(
                        response.url,
                        response.meta.get("redirect_urls", [""])[0],
                        failure.getTraceback()
                    )

        extra = {
            "detail": {
                "website": "weibo",
                "type": "parse"
            },
            "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "subscribers": ["qimengmeng"],
            "spider": self.logger.logger.name
        }



        self.logger.logger.error(
            message, extra=extra

        )

