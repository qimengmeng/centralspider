# -*- coding: utf-8 -*-

import os
import re
import sys
import json
from datetime import (
    datetime, timedelta
)
import hashlib

reload(sys)
sys.setdefaultencoding('utf8')

import logging
import lxml
from lxml import etree
from lxml.html.clean import Cleaner
import w3lib
from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

from central.items.basis import (
    TweetItem,

)
from central.loggers import (
    crawler, parser
)

class WeiboTweetRule(object):
    """微博动态内容爬虫"""

    def __init__(self, **kwargs):
        self.account = kwargs.get('account')
        self.site = kwargs.get('site')
        self.operation = kwargs.get("operation")
        self.spider = kwargs.get("spider")

        self.home_page_url = "https://weibo.com/u/{}?is_ori=1".format(
                                                   self.account.ref_id)

        # self.home_page_url = "http://www.httphttpbinbin.org/"


    def err_report(self, failure):

        extra = {
           "detail": {
               "website": "weibo",
               "type": "request"
           },
           "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
           "subscribers": ["qimengmeng"],
        }

        if failure.check(HttpError):
            response = failure.value.response
            crawler.error('HttpError on {}'.format(response.url), extra=extra)
        elif failure.check(DNSLookupError):
            request = failure.request
            crawler.error('DNSLookupError on {}'.format(request.url), extra=extra)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            crawler.error('TimeoutError on {}'.format(request.url), extra=extra)
        else:
            crawler.error(repr(failure), extra=extra)


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
            extra = {
                "detail": {
                    "website": "weibo",
                    "type": "parse"
                },
                "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "subscribers": ["qimengmeng"],
            }
            parser.error(
                '微博账号{}列表页解析失败:{}'.format(
                     self.account.weibo_name,
                     response.url
                ),
                 extra=extra
            )
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



    def parse_weibo_text(self, response):
        meta = response.meta
        tweet_dic = meta.get('tweet_dic', '')

        weibo_html = response.body.decode(response.encoding)
        weibo_info_html = self.get_weibo_infos_right(weibo_html)
        each = BeautifulSoup(weibo_info_html, "lxml")

        try:
            retweet_num = each.find(attrs={'node-type': 'forward_btn_text'}).find_all("em")[1].get_text()
            retweet_num = int(retweet_num)
        except:
            retweet_num = 0

        try:
            comment_num = each.find(attrs={'node-type': 'comment_btn_text'}).find_all("em")[1].get_text()
            comment_num = int(comment_num)
        except:
            comment_num = 0

        try:
            up_num = each.find(attrs={'node-type': 'like_status'}).find_all("em")[1].get_text()
            up_num = int(up_num)
        except:
            up_num = 0

        try:
            weibo_base_html = each.find(
                attrs={'node-type': 'feed_content'}
            ).find(
                attrs={'node-type': 'feed_list_content'}
            )
        except Exception as e:

            self.mslogger.put_aws(
                {
                    "message": "微博详情解析出错，具体是{},详情页{}".format(
                                 e, str(each)
                                    ),
                    "detail": {
                        "website": "weibo",
                        "type": "parse"
                    },
                    "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    "subscribers": ["qimengmeng"],
                    "level": "error"


                }
            )

            return

        html = unicode(weibo_base_html)
        content, tags = self.wash_content(html)

        tweet_image_dics = self.get_tweet_image_dic(each)
        if not tweet_image_dics:
            images = []
        else:
            config = self.spider.config
            images = map(self._make_object, tweet_image_dics)

            image_source_url = map(lambda obj: obj.get("image"), tweet_image_dics)
            hash_value = map(lambda obj: hashlib.md5(obj.get("image")).hexdigest(), tweet_image_dics)
            params = {
                "image_source_url": image_source_url,
                "hash_value": hash_value,
                "thumbnail": "1",
                "tiny": "1",
                "prefix": config.get("IMAGE", "PREFIXDIR"),
                "bucket_name": "dw-temp"
            }

            self.put_aws(params)

        tweet_dic.update(
                {
                    "retweet_num": int(retweet_num),
                    "comment_num": int(comment_num),
                    "up_num": int(up_num),
                    "content": content,
                    "tags": tags,
                    "images": images
                }

            )

        tweet_item = TweetItem(**tweet_dic)

        yield tweet_item

    def put_aws(self, data):
        message = json.dumps(data).encode('utf-8')
        command = "aws kinesis put-record --stream-name %s --data '%s' --partition-key %s --region %s" \
                  % ("ImagesInternal", message, "partitionKey1", "cn-north-1")
        os.system(command)

    def _make_object(self, image_obj):

        config = self.spider.config
        hash_value = hashlib.md5(image_obj.get("image")).hexdigest()
        image_prifix = "{}{}/{}".format(
                                           config.get("IMAGE", "PREFIX"),
                                           config.get("IMAGE", "PREFIXDIR"),
                                            hash_value
                                           )

        obj = {
            "origin": "{}.jpg".format(image_prifix),
            "thumbnail": "{}.thumbnail.jpg".format(image_prifix),
            "tiny": "{}.tiny.jpg".format(image_prifix)
        }
        return obj

    def wash_content(self, html):

        cleaner = Cleaner(
            style=True,
            scripts=True,
            page_structure=False,
            safe_attrs_only=False,
            remove_tags=["div", "br"],
            kill_tags=["img"]

        )
        html = cleaner.clean_html(html)
        page = etree.HTML(html)
        tags = {
            "topic": [],
            "super_topic": []
        }

        for ele in page.getiterator("a"):
            text = ele.text
            childs = filter(lambda x: x.tag == "i", list(ele))
            supertopic = ele.xpath('./i[@class="W_ficon ficon_supertopic"]')
            if text and u"#" in text:
                tags["topic"].append(text.strip()[1:-1])
                for key in ele.attrib.keys():
                    ele.attrib.pop(key)
                ele.tag = "topic"
                ele.text = text.strip()[1:-1]
            elif text and u"@" in text:
                pass
            elif supertopic:
                tags["super_topic"].append(u"{}".format(childs[0].tail.strip()))
                for key in ele.attrib.keys():
                    ele.attrib.pop(key)
                ele.tag = "super"
                ele.text = childs[0].tail.strip()
                ele.remove(childs[0])
            else:
                ele.getparent().remove(ele)

        content = lxml.html.tostring(
            page, pretty_print=True, encoding='unicode')

        content = w3lib.html.remove_tags(content, keep=('topic', 'super')).strip()

        return content, tags


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

        #布隆过滤去重
        if self.spider.download_filter.check_and_update(ori_tweet_id):
            logging.debug('repeat tweet')
            return

        time_url = each.find(attrs={'node-type': 'feed_list_item_date'})
        publish_tm = time_url.get('title', '')
        publish_tm = self.format_time(publish_tm)
        weibo_url = time_url.get('href', '')
        if 'weibo.com' not in weibo_url:
            weibo_url = 'https://weibo.com{}'.format(weibo_url)

        weibo_url = re.search(r'(.*?)\?.*', weibo_url).group(1)

        tweet_dic = {

            "url": weibo_url,
            "publish": publish_tm,
            "website": self.site,
            "weibo_id": ori_tweet_id,
            "operation": self.operation,
            "account": self.account,
        }

        yield Request(
            weibo_url, callback=self.parse_weibo_text, errback=self.err_report,
            meta={'tweet_dic': tweet_dic}
        )

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

