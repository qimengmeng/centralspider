# -*- coding:utf-8 -*-

import logging

from scrapy import signals
from elasticsearch import (
    Elasticsearch,
    ElasticsearchException
)
from elasticsearch_dsl.connections import connections

from central.esmappings import (
    SocialmediaType, TweetType
)




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
        USER = config.get("ELASTICSEARCH", "USER")
        PASSWORD = config.get("ELASTICSEARCH", "PASSWORD")

        #Elasticsearch ORM初始化连接
        # connections.create_connection(hosts=[URL], http_auth=(USER, PASSWORD))
        connections.create_connection(hosts=["127.0.0.1"])

        es_client = Elasticsearch([URL], http_auth=(USER, PASSWORD))
        spider.es_client = es_client

        logging.info("running spider:%s", spider.name)