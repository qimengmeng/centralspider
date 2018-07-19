# -*- coding:utf-8 -*-

import logging
import os
import ConfigParser

from scrapy import signals


class Baseconfig(object):
    """类说明
    加载配置信息
    """

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        return ext


    def spider_opened(self, spider):

        mode = spider.settings.get("ENV_MODE")
        PWD = os.path.join(
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "configs"), "%s.txt" % mode
                        )

        config = ConfigParser.ConfigParser()
        config.read(PWD)

        spider.config = config

        logging.info("running spider:%s", spider.name)