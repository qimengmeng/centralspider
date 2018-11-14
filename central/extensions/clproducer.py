# -*- coding:utf-8 -*-

import logging
import os
import imp

import celery
from scrapy import signals


class CeleryProducer(object):
    """类说明
    初始化celery异步任务生产者
    """

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        return ext


    def spider_opened(self, spider):

        mode = spider.settings.get("ENV_MODE")
        PWD = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                           "helpers/configs/%s.py" % mode
                        )

        celeryconfig = imp.load_source("celeryconfig", PWD)

        celeryapp = celery.Celery(
            config_source=celeryconfig
        )

        spider.celeryapp = celeryapp

        logging.info("running spider:%s", spider.name)