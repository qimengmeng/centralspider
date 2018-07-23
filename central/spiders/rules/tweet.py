# -*- coding: utf-8 -*-

import re
import requests
import sys
import random
from datetime import datetime
from datetime import timedelta
from lxml import etree

reload(sys)
sys.setdefaultencoding('utf8')

from scrapy import Request
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

from central.items.basis import (
    TweetItem

)

class WeiboTweetRule(object):
    """微博动态内容爬虫"""

    def __init__(self, **kwargs):
        self.account = kwargs.get('account')
        self.site = kwargs.get('site')
        self.operation = kwargs.get("operation")
        self.spider = kwargs.get("spider")

        self.mslogger = self.spider.mslogger

        self.home_page_url = "https://weibo.cn/u/{}?filter=0&page=1".format(
                                                   self.account.ref_id)

        self.detail_url = "https://weibo.cn/comment/{}?ckAll=1"
        self.cookie = {
            'SUB': ''.join([
                '_2A',
                ''.join(random.sample(
                    '250azrYDeRhGeBN6VAZ8SjNzDiIHXVXASsQrDV8PUNbmtAKLWXakW8GBWrXgTJrCbRqCqiZIO1pnAEgKg',
                    50
                )
                ),
                '..'
            ])
        }


    def err_report(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:
        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)


    def start(self):

        return Request(
            self.home_page_url,
            callback=self.parse,
            errback=self.err_report,
            dont_filter=True,
        )

    def parse(self, response):

        html = str(response.body.decode(response.encoding))

        selector = etree.HTML(html)
        feed_list = selector.xpath("//div[@class='c']")

        for feed in feed_list:
            if not feed.attrib.get('id'):
                continue
            item = self.get_weibo_info(feed)

            yield item

    # 获取用户微博内容及对应的发布时间、点赞数、转发数、评论数
    def get_weibo_info(self, feed):

        # 微博内容
        str_t = feed.xpath("div/span[@class='ctt']")
        weibo_content = str_t[0].xpath("string(.)").encode(
            sys.stdout.encoding, "ignore").decode(
            sys.stdout.encoding)
        weibo_content = weibo_content[:-1]
        weibo_id = feed.xpath("@id")[0][2:]

        # 查重开启并且确认重复
        # if self.spider.download_filter.check_and_update(weibo_id):
        #     return

        a_link = feed.xpath(
            "div/span[@class='ctt']/a/@href")
        if a_link:
            if (a_link[-1] == "/comment/" + weibo_id or
                                "/comment/" + weibo_id + "?" in a_link[-1]):
                weibo_link = "https://weibo.cn" + a_link[-1]
                wb_content = self.get_long_weibo(weibo_link)
                if wb_content:
                    weibo_content = wb_content


        # 微博发布时间
        str_time = feed.xpath("div/span[@class='ct']")
        str_time = str_time[0].xpath("string(.)").encode(
            sys.stdout.encoding, "ignore").decode(
            sys.stdout.encoding)
        publish_time = str_time.split(u'来自')[0]
        if u"刚刚" in publish_time:
            publish_time = datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S')
        elif u"分钟" in publish_time:
            minute = publish_time[:publish_time.find(u"分钟")]
            minute = timedelta(minutes=int(minute))
            publish_time = (
                datetime.now() - minute).strftime(
                "%Y-%m-%d %H:%M:%S")
        elif u"今天" in publish_time:
            today = datetime.now().strftime("%Y-%m-%d")
            time = publish_time[3:]
            publish_time = today + " " + time
        elif u"月" in publish_time:
            year = datetime.now().strftime("%Y")
            month = publish_time[0:2]
            day = publish_time[3:5]
            time = publish_time[7:12]
            publish_time = (
                year + "-" + month + "-" + day + " " + time)
        else:
            publish_time = publish_time[:16]


        str_footer = feed.xpath("div")[-1]

        image_urls = []
        if str(str_footer.xpath("a[2]/text()")[0]).strip() == u"原图":
            top_image_url = str_footer.xpath("a[2]/@href")[0]
            image_urls.append(top_image_url)
        pattern = r"\d+\.?\d*"
        str_footer = str_footer.xpath("string(.)").encode(
            sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
        str_footer = str_footer[str_footer.rfind(u'赞'):]
        guid = re.findall(pattern, str_footer, re.M)

        # 点赞数
        up_num = int(guid[0])

        # 转发数
        retweet_num = int(guid[1])

        # 评论数
        comment_num = int(guid[2])

        tweet_dic = {

            "url": self.detail_url.format(weibo_id),
            "publish": publish_time,
            "website": self.site,
            "content": weibo_content,
            "weibo_id": weibo_id,
            "up_num": up_num,
            "retweet_num": retweet_num,
            "comment_num": comment_num,
            "operation": self.operation,
            "image_urls": image_urls,

        }

        return TweetItem(**tweet_dic)

    def get_long_weibo(self, weibo_link):

        html = requests.get(weibo_link, cookies=self.cookie).content
        selector = etree.HTML(html)
        info = selector.xpath("//div[@class='c']")[1]
        wb_content = info.xpath("div/span[@class='ctt']")[0].xpath(
            "string(.)").encode(sys.stdout.encoding, "ignore").decode(
            sys.stdout.encoding)
        wb_content = wb_content[1:]
        return wb_content

