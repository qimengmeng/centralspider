# -*- coding: utf-8 -*-

import re
import sys
import random
import json
from datetime import (
    datetime, timedelta
)

reload(sys)
sys.setdefaultencoding('utf8')

import requests
import logging
from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

from central.items.basis import (
    TweetItem, TweetImageItem,

)

class WeiboTweetRule(object):
    """微博动态内容爬虫"""

    def __init__(self, **kwargs):
        self.account = kwargs.get('account')
        self.site = kwargs.get('site')
        self.operation = kwargs.get("operation")
        self.spider = kwargs.get("spider")

        self.mslogger = self.spider.mslogger

        self.home_page_url = "https://weibo.com/u/{}?is_ori=1".format(
                                                   self.account.ref_id)

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
        html = response.body.decode(response.encoding)
        cont = self.get_weibo_infos_right(html)

        if not cont:
            return
        # 获取所有微博信息列表
        soup = BeautifulSoup(cont, "lxml")
        feed_list = soup.find_all(attrs={'action-type': 'feed_list_item'})
        for data in feed_list:
            for item in self.get_weibo_info_detail(data, cont):
                yield item


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



    def get_tweet_image_dic(self, each):
        weibo_base_html = each.find(
            attrs={'node-type': 'feed_content'}
        ).find_all(
            attrs={'class': 'WB_pic'}
        )

        # 只取9张
        weibo_base_html = weibo_base_html[0:9]

        tweet_image_items = []
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
            tweet_image_item = TweetImageItem(**tweet_image_dic)
            tweet_image_items.append(tweet_image_item)
        return tweet_image_items


    def replace_image_pixel(self, image_url):
        def replace_pixel(m):
            url = m.group()
            replace_url = 'sinaimg.cn/mw690/'
            return replace_url

        regex = 'sinaimg.cn/.*?/'
        retags = re.compile(regex, re.DOTALL | re.IGNORECASE)

        return retags.sub(replace_pixel, image_url)


    def parse_weibo_text(self, response):
        meta = response.meta
        tweet_dic = meta.get('tweet_dic', '')

        weibo_html = response.body.decode(response.encoding)
        weibo_info_html = self.get_weibo_infos_right(weibo_html)
        each = BeautifulSoup(weibo_info_html, "lxml")

        retweet_num = each.find(attrs={'node-type': 'forward_btn_text'}).find_all("em")[1].get_text()
        comment_num = each.find(attrs={'node-type': 'comment_btn_text'}).find_all("em")[1].get_text()
        up_num = each.find(attrs={'node-type': 'like_status'}).find_all("em")[1].get_text()

        try:
            weibo_base_html = each.find(
                attrs={'node-type': 'feed_content'}
            ).find(
                attrs={'node-type': 'feed_list_content'}
            )
        except Exception as e:
            logging.error(
                '本次解析微博详情页出错，具体是{},详情页{}'.format(
                    e, str(each)
                )
            )
            return

        content = str(weibo_base_html)

        tweet_dic.update(
                {
                    "retweet_num": retweet_num,
                    "comment_num": comment_num,
                    "up_num": up_num,
                    "content": content,
                }

            )

        tweet_item = TweetItem(**tweet_dic)

        yield tweet_item

    def get_weibo_info_detail(self, each, html):

        weibo_pattern = 'mid=(\\d+)'
        m = re.search(weibo_pattern, str(each))
        if m:
            ori_tweet_id = m.group(1)
        else:
            logging.warning(
                '未提取到页面的微博id,页面源码是{}'.format(html)
            )
            return

        if self.spider.download_filter.check_and_update(ori_tweet_id):
            return

        tweet_image_items = self.get_tweet_image_dic(each)
        time_url = each.find(attrs={'node-type': 'feed_list_item_date'})
        publish_tm = time_url.get('title', '')
        publish_tm = self.format_time(publish_tm)
        weibo_url = time_url.get('href', '')
        if 'weibo.com' not in weibo_url:
            weibo_url = 'https://weibo.com{}'.format(weibo_url)

        weibo_url = re.search(r'(.*?)\?.*', weibo_url).group(1)
        images_info = self.parse_img(tweet_image_items)
        s3_images = map(lambda x: x.get("image"), images_info)
        thumb_images = map(lambda x: x.get("thumbnail"), images_info)

        tweet_dic = {

            "url": weibo_url,
            "publish": publish_tm,
            "website": self.site,
            "weibo_id": ori_tweet_id,
            "operation": self.operation,
            "account": self.account,
            "s3_images": s3_images,
            "thumb_images": thumb_images
        }

        yield Request(
            weibo_url, callback=self.parse_weibo_text, errback=self.err_report,
            meta={'tweet_dic': tweet_dic}
        )

    def parse_img(self, image_items):
        config = self.spider.config
        upload_url = config.get("IMAGE", "UPLOAD_URL")

        images_info = []

        for image_item in image_items:
            data = {
                "image_source_url": image_item.get("image"),
                "image_destination": "WeiboImages/%s" % self.account.ref_id,
                "thumbnail": "true",
                "blur": "false",
            }

            rep = requests.post(url=upload_url, data=data).json()

            rep = eval(rep)
            status_code = rep.get("status")

            if int(status_code) == 200:
                images_info.append(rep.get("paths"))

        return images_info


    def url_for(self, url):
        if 'http' not in url:
            return 'http:{}'.format(url)
        else:
            return url

    def format_time(self, publish_time):

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
            time = publish_time[3:].strip()
            publish_time = today + " " + time + ":00"
        elif u"月" in publish_time:
            year = datetime.now().strftime("%Y")
            month = publish_time[0:2]
            day = publish_time[3:5]
            time = publish_time[7:12].strip() + ":00"
            publish_time = (
                year + "-" + month + "-" + day + " " + time)
        else:
            publish_time = publish_time[:16].strip() + ":00"

        return publish_time

