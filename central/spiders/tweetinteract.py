# -*- coding:utf-8 -*-

from datetime import (
        datetime, timedelta
)
import logging

from scrapy import Spider
from elasticsearch import helpers

from rules.tweetinteract import TweetinteractRule
from central.esmappings import (
    TweetType,
)


class TweetinteractSpider(Spider):
    """
    微博互动量更新
    """

    name = 'central_tweetinteract'
    custom_settings = {
        'COOKIES_ENABLED': True,
    }

    def __init__(self, **kw):
        super(TweetinteractSpider, self).__init__(**kw)

    def start_requests(self):

        limit_datetime = (datetime.now()-timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        result = helpers.scan(client=self.es_client,
                                index='weibo',
                              query={
                                  "_source": ["url", ],
                                  "query": {
                                      "bool": {
                                          "filter": [
                                              {"range": {
                                                  "publish_time": {"gte": limit_datetime}
                                              }}
                                          ]
                                      }
                                  }
                              },
                              scroll='5m')

        for doc in result:
            doc.update(
                        spider=self
                    )

            rule = TweetinteractRule(**doc)

            yield self.make_requests_from_url(
                rule
            )

    def make_requests_from_url(self, rule):
        return rule.start()