# -*- coding:utf-8 -*-
import re
import sys
import random
import json

reload(sys)
sys.setdefaultencoding('utf8')

import logging
from bs4 import BeautifulSoup
from scrapy import Request


class TweetinteractRule(object):
    """微博互动量更新爬虫"""

    def __init__(self, **kwargs):
        self.spider = kwargs.get("spider")
        self.es_client = self.spider.es_client

        self.weibo_detail_url = kwargs['_source']['url']
        self.doc_id = kwargs["_id"]


    def err_report(self, failure):
       pass


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

        res = self.es_client.update(
            index='weibo',
            doc_type='weibo',
            id=self.doc_id,
            body={
                "doc": {
                    "stat": {
                        "up_num": int(up_num),
                        "retweet_num": int(retweet_num),
                        "comment_num": int(comment_num)
                    },
                 }
               }
            )

        logging.debug(res["result"])


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


