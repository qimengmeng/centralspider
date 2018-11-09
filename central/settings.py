# -*- coding: utf-8 -*-

import os

BOT_NAME = 'central'

SPIDER_MODULES = ['central.spiders']
NEWSPIDER_MODULE = 'central.spiders'


###########
# 遵守爬虫协议，默认True
ROBOTSTXT_OBEY = False

###########
# 最大请求，默认16
CONCURRENT_REQUESTS = 32
# DOWNLOAD_TIMEOUT = 15
DOWNLOAD_DELAY = 0.1

RANDOMIZE_DOWNLOAD_DELAY = True


# Disable cookies (enabled by default)
COOKIES_ENABLED = False    # 禁用cookie，有些站点根据其发现爬虫轨迹


DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "central.middlewares.download.user_agent.RandomUserAgentMiddleware": 543,
    "central.middlewares.download.cookies.RandomCookieMiddleware": 544,
    "central.middlewares.download.proixes.ProxyMiddleware": 545,
}

SPIDER_MIDDLEWARES = {

        }

EXTENSIONS = {
    'scrapy.telnet.TelnetConsole': None,
    'central.extensions.baseconfig.Baseconfig': 499,
    'central.extensions.bloomfilter.Crawlfilter': 500,
    # 'central.extensions.mq.Kafkaqueue': 501,
    'central.extensions.db.Db': 503,
    'central.extensions.es.ESearch': 504,
    'central.extensions.clproducer.CeleryProducer': 505,
 }

# RETRY
RETRY_ENABLED = False
# RETRY_TIMES = 1   initial response + 5 retries = 6 requests
# RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

ITEM_PIPELINES = {
      "central.pipelines.socialmedia.SocialmediaPipeline": 601,
      "central.pipelines.tweet.TweetPipeline": 602,
      # "central.pipelines.hotsearch.HotsearchPipeline": 603,
}




#"development,test,production"
ENV_MODE = "test"
