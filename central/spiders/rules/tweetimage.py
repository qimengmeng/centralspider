# -*- coding:utf-8 -*-

import re
import sys
import json

reload(sys)
sys.setdefaultencoding('utf8')

import requests
import logging
import celery
from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


class TweetimageRule(object):
    """微博图片异步上传任务爬虫"""

    def __init__(self, **kwargs):
        self.spider = kwargs.get("spider")
        self.es_client = self.spider.es_client

        self.mslogger = self.spider.mslogger
        self._celeryapp = self.spider.celeryapp

        self.weibo_detail_url = kwargs['_source']['url']
        self.doc_id = kwargs["_id"]
        self.doc = kwargs["_source"]


    def err_report(self, failure):
        # log all failures
        self.spider.logger.error(repr(failure))

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
            self.weibo_detail_url,
            callback=self.parse,
            errback=self.err_report,
            dont_filter=True,
        )


    def parse(self, response):

        weibo_html = response.body.decode(response.encoding)
        weibo_info_html = self.get_weibo_infos_right(weibo_html)
        each = BeautifulSoup(weibo_info_html, "lxml")
        tweet_image_dics = self.get_tweet_image_dic(each)
        config = self.spider.config
        upload_url = config.get("IMAGE", "UPLOAD_URL")

        images_info = []

        for image_dic in tweet_image_dics:

            data = {
                "image_source_url": image_dic.get("image"),
                "image_destination": "WeiboImages/%s" % self.doc.get("publish_account").get("account_id"),
                "thumbnail": "true",
                "blur": "false",
                "tiny": "true",
            }
            images_info.append(data)


        if images_info:

            celery_task_timeout = 7200


            result = self._celeryapp.send_task(
                "helpers.upload_image",
                args=[upload_url, images_info]
            )

            try:
                result.get(propagate=True, timeout=celery_task_timeout)

                s3_images, thumb_images, tiny_images = result.result

            except celery.exceptions.TimeoutError:
                # We've waited a pretty long period of time before we
                # claim this task failed.
                logging.warn("%s: Celery task timedout in [%s]",
                             self, result.status)
                result.revoke(terminate=False)

                raise Exception("Celery task timedout")

            res = self.es_client.update(
                index='weibo',
                doc_type='weibo',
                id=self.doc_id,
                body={
                    "doc": {
                        "s3_images": s3_images,
                        "thumb_images": thumb_images,
                        "tiny_images": tiny_images
                        }
                   }
                )

            logging.debug(res["result"])


    def get_tweet_image_dic(self, each):
        weibo_base_html = each.find(
            attrs={'node-type': 'feed_content'}
        ).find_all(
            attrs={'class': 'WB_pic'}
        )

        # 只取9张
        weibo_base_html = weibo_base_html[0:9]

        tweet_image_dics = []
        for num in range(len(weibo_base_html), 0, -1):
            image_url = weibo_base_html[len(weibo_base_html) - num].find("img").get("src")

            # 替换图片清晰度参数
            image_url = self.replace_image_pixel(image_url)
            image_url = self.url_for(image_url)
            priority = num
            is_gif = 1 if image_url.endswith('.gif') else 0
            tweet_image_dic = {
                'image': image_url,
                'priority': priority,
                'is_gif': is_gif,
            }
            tweet_image_dics.append(tweet_image_dic)
        return tweet_image_dics

    def replace_image_pixel(self, image_url):
        def replace_pixel(m):
            url = m.group()
            replace_url = 'sinaimg.cn/mw690/'
            return replace_url

        regex = 'sinaimg.cn/.*?/'
        retags = re.compile(regex, re.DOTALL | re.IGNORECASE)

        return retags.sub(replace_pixel, image_url)


    def url_for(self, url):
        if 'http' not in url:
            return 'http:{}'.format(url)
        else:
            return url


    def get_weibo_infos_right(self, html):
        """
        通过网页获取用户主页右边部分（即微博部分）字符串
        :param html:
        :return:
        """
        soup = BeautifulSoup(html, "lxml")
        scripts = soup.find_all('script')
        pattern = re.compile(r'FM.view\((.*)\)')

        # 如果字符串'fl_menu'(举报或者帮上头条)这样的关键字出现在script中，则是微博数据区域
        cont = ''
        for script in scripts:
            m = pattern.search(script.string)
            if m and 'fl_menu' in script.string:
                all_info = m.group(1)
                cont += json.loads(all_info).get('html', '')
        return cont
