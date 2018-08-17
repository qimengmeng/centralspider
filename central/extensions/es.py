# -*- coding:utf-8 -*-

import logging

from scrapy import signals
from elasticsearch import (
    Elasticsearch,
    ElasticsearchException
)
from elasticsearch_dsl.connections import connections


class ESearch(object):
    """类说明
    搜索引擎连接
    """

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        return ext

    def spider_opened(self, spider):

        config = spider.config

        URL = config.get("ELASTICSEARCH", "URL")

        #Elasticsearch ORM初始化连接
        connections.create_connection(hosts=[URL])

        es_client = Elasticsearch([URL])
        spider.es_client = es_client

        logging.info("running spider:%s", spider.name)