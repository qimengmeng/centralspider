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
DOWNLOAD_TIMEOUT = 15
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

EXTENSIONS = {
    'scrapy.telnet.TelnetConsole': None,
    'central.extensions.baseconfig.Baseconfig': 499,
    'central.extensions.bloomfilter.Crawlfilter': 500,
    'central.extensions.mq.Kafkaqueue': 501,
    'central.extensions.logger.MSLogger': 502,
    'central.extensions.db.Db': 503,
 }

# RETRY
RETRY_TIMES = 5  # initial response + 5 retries = 6 requests
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

ITEM_PIPELINES = {
      "central.pipelines.images_pipeline.MyImagesPipeline": 600,
      "central.pipelines.socialmedia.SocialmediaPipeline": 601,
      # "central.pipelines.tweet.TweetPipeline": 206,
}



IMAGES_STORE = 's3://dw-temp/Images/'
IMAGES_EXPIRES = 1
IMAGES_STORE_S3_ACL = 'public-read'
AWS_ACCESS_KEY_ID = 'AKIAPF5JUFSZ6Q4HXMCA'
AWS_SECRET_ACCESS_KEY = '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'

# 图片缩略图
IMAGES_THUMBS = {
	'thumbs': (200, 999999),
}

#"development,test,production"
ENV_MODE = "test"