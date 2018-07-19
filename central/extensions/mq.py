# -*- coding:utf-8 -*-

import logging

from scrapy import signals

from kafka import KafkaProducer
from kafka.errors import KafkaError




class Kafkaqueue(object):
    """类说明
    卡夫卡消息队列
    """

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        return ext


    def spider_opened(self, spider):

        mode = spider.settings.get("ENV_MODE")

        config = spider.config

        spider.producer = KafkaProducer(bootstrap_servers=config.get('KAFKA', 'SERVER'))

        logging.info("running spider:%s", spider.name)