# -*- coding:utf-8 -*-

from datetime import (
        datetime, timedelta
)
import logging

from scrapy import Spider
from elasticsearch import helpers

from rules.tweetimage import TweetimageRule
from central.esmappings import (
    TweetType,
)


class TweetimageSpider(Spider):
    """
    微博互动量更新
    """

    name = 'central_tweetimage'
    custom_settings = {
        'COOKIES_ENABLED': True,
    }

    def __init__(self, **kw):
        super(TweetimageSpider, self).__init__(**kw)

    def start_requests(self):

        limit_datetime = (datetime.now()-timedelta(days=15)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        result = helpers.scan(client=self.es_client,
                                index='weibo',
                              query={
                                  "query": {
                                      "bool": {
                                          "filter": [
                                              {"range": {
                                                  "created_at": {"gte": limit_datetime}
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

            rule = TweetimageRule(**doc)

            yield self.make_requests_from_url(
                rule
            )

    def make_requests_from_url(self, rule):
        return rule.start()