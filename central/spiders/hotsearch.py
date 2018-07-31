# -*- coding:utf-8 -*-


from scrapy import Spider

from central.seedconfig import HOTSEARCH
from rules.hotsearch import WeiboHotsearchRule


class HotsearchSpider(Spider):
    """
    微博热搜爬虫
    """

    name = 'central_hotsearch'
    custom_settings = {
        'COOKIES_ENABLED': True,
    }

    def __init__(self, **kw):
        super(HotsearchSpider, self).__init__(**kw)

    def start_requests(self):
        for task in HOTSEARCH:
            if task.get('name') == "weibo_hotsearch":

                for url in task.get('urls'):
                    task.update(
                            request_entry_url=url,
                            spider=self
                                )
                    rule = WeiboHotsearchRule(**task)
                    yield self.make_requests_from_url(
                        rule
                    )

    def make_requests_from_url(self, rule):
        return rule.start()