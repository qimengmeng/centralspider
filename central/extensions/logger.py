# -*- coding:utf-8 -*-

import logging

from scrapy import signals

from central.loggers.log_output import Logout


class MSLogger(object):
    """类说明
    自定义日志记录器
    """

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        return ext

    def spider_opened(self, spider):

        config = spider.config

        log_type = config.get("SCRAPY", "LOG_TYPE")
        diff = config.get("TIME", "DIFF")
        producer = spider.producer if log_type == 'product' else None

        mslogger = Logout(log_type=log_type, producer=producer, diff=diff)

        spider.mslogger = mslogger

        logging.info("running spider:%s", spider.name)