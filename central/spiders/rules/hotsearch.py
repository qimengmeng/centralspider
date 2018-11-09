# -*- coding:utf-8 -*-

import re
import sys
from datetime import datetime
from urllib import unquote

reload(sys)
sys.setdefaultencoding('utf8')

from scrapy import Request

from central.items.basis import (
    TweetHotsearchItem

)


class WeiboHotsearchRule(object):
    """微博热搜爬虫"""

    find_hot_district_xpath = "<script>(.*?)</script>"

    def __init__(self, **kwargs):

        self.request_entry_url = kwargs.get('request_entry_url')
        self.account = kwargs.get('account')
        self.site = kwargs.get('site')
        self.operation = kwargs.get("operation")
        self.spider = kwargs.get("spider")

    def err_report(self, failure):
       pass

    def start(self):

        return Request(
            self.request_entry_url,
            callback=self.parse,
            errback=self.err_report,
        )

    def parse(self, response):

        html = response.body.decode(response.encoding)

        html = re.findall(WeiboHotsearchRule.find_hot_district_xpath, html)[-2]

        keyword_lis = re.findall(r'class=\\"star_name\\">.*?<a href=\\"\\/weibo\\/(.*?)&Refer=[top|new]', html)
        keyword_lis.pop(0)
        hot_degree_lis = re.findall(r'class=\\"star_num\\"><span>(.*?)<\\/span>', html)
        order_number_lis = range(1, len(keyword_lis)+1)

        for order_number, keyword, hot_degree in zip(order_number_lis, keyword_lis, hot_degree_lis):


            hot_search_dic = {

                "keyword": unquote(str(keyword.replace('25', ''))),
                "hot_degree": hot_degree,
                "hottime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "order_number": order_number,
                "link": "http://s.weibo.com/weibo/" + keyword.replace('25', ''),

            }

            yield TweetHotsearchItem(**hot_search_dic)



