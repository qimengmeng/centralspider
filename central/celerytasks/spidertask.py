# -*- coding: utf-8 -*-

from __future__ import absolute_import
import sys
import os
import logging

sys.path.append('.')
sys.path.append('..')

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from .app import celery_app


settings = get_project_settings()

crawler = CrawlerProcess(settings)


@celery_app.task(name='tweet_spider')
def crawl_tweet(spider_name):
    """启动scrapy爬虫"""
    crawler.crawl(spider_name)
    crawler.start()
    logging.info(
        '{}crawl'.format(
            spider_name,
        )
    )

    return spider_name



@celery_app.task(name='socialmdia_spider')
def crawl_socialmedia(spider_name):
    """启动scrapy爬虫"""

    crawler.crawl(spider_name)
    crawler.start()
    logging.info(
        '{}crawl'.format(
            spider_name,
        )
    )

    return spider_name



