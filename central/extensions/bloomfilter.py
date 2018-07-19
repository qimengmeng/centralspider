# -*- coding:utf-8 -*-
import logging
import string

from scrapy import signals

from central.utils import BloomFilter


class Crawlfilter(object):
    """类说明
    布隆过滤器的开启
    """

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        return ext


    def spider_opened(self, spider):

        config = spider.config

        host = config.get('FILTER_REDIS', 'HOST')
        port = string.atoi(config.get('FILTER_REDIS', 'PORT'))
        db = config.get('FILTER_REDIS', 'DB')

        spider.download_filter = BloomFilter(host=host, port=port, db=db)

        logging.info("running spider:%s", spider.name)



