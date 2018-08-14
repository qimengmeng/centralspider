# -*- coding: utf-8 -*-
import re
import datetime
import logging
import json
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import requests
from bs4 import BeautifulSoup
from scrapy import (
    Request, FormRequest
)

from central.items.crawlmanage import (
                    SMAccountItem,
)

class WeiboAccountRule(object):
    """微博动态账号爬虫"""

    def __init__(self, **kwargs):
        self.account = kwargs.get('account')
        self.site = kwargs.get('site')
        self.home_page_url = "https://www.weibo.com/u/{}".format(
                                                        self.account.ref_id)
        self.spider = kwargs.get("spider")
        self.date_time = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")

    def err_report(self, failure):
        pass

    def start(self):

        return Request(
            self.home_page_url,
            callback=self.parse,
            errback=self.err_report,
            dont_filter=True,
        )

    def get_userid(self, html):
        pattern = re.compile(r'\$CONFIG\[\'oid\'\]=\'(.*)\';')
        m = pattern.search(html)
        return m.group(1) if m else ''

    def get_username(self, html):
        pattern = re.compile(r'\$CONFIG\[\'onick\'\]=\'(.*)\';')
        m = pattern.search(html)
        return m.group(1) if m else ''

    def get_userdomain(self, html):
        """
        :param html:
        :return:用户类型
        """
        pattern = re.compile(r'uid=.*?&domain=([^\\"&]*).*?&pid=')
        m = pattern.search(html)
        return m.group(1) if m else ''

    def get_headimg(self, html):
        """
        Get the head img url of current user
        :param html: page source
        :return: head img url
        """
        soup = BeautifulSoup(self._get_header(html), 'lxml')
        try:
            headimg = self.url_for(
                soup.find(attrs={'class': 'photo_wrap'}).find
                (attrs={'class': 'photo'})['src']
            )
        except AttributeError:
            headimg = ''
        return headimg

    def _get_header(self, html):
        soup = BeautifulSoup(html, "lxml")
        scripts = soup.find_all('script')
        pattern = re.compile(r'FM.view\((.*)\)')
        cont = ''
        for script in scripts:
            try:
                m = pattern.search(script.string)
            except Exception as e:
                logging.info(e)
                continue
            if m and 'pl.header.head.index' in script.string:
                all_info = m.group(1)
                cont = json.loads(all_info)['html']
        return cont

    def get_fans_status(self, html):
        """
        :param html:
        :return: 返回粉丝数,微博数
        """
        cont = self.get_left(html)
        if cont == '':
            return 0
        soup = BeautifulSoup(cont, 'html.parser')
        try:
            following_num = int(soup.find_all('strong')[0].get_text())
            fans_num = int(soup.find_all('strong')[1].get_text())
            tweet_num = int(soup.find_all('strong')[2].get_text())
            return (following_num, fans_num, tweet_num)
        except Exception:
            return

    def get_left(self, html):
        """
        The left part of the page, which is public
        """
        soup = BeautifulSoup(html, "lxml")
        scripts = soup.find_all('script')
        pattern = re.compile(r'FM.view\((.*)\)')
        cont = ''
        l_id = ''
        # first ensure the left part

        for script in scripts:
            if not script.string:
                continue
            m = pattern.search(script.string)
            if m and 'WB_frame_b' in script.string:
                all_info = m.group(1)
                cont = json.loads(all_info)['html']
                lsoup = BeautifulSoup(cont, 'lxml')
                l_id = lsoup.find(attrs={'class': 'WB_frame_b'}).div['id']
        for script in scripts:
            m = pattern.search(script.string)
            if m and l_id in script.string:
                all_info = m.group(1)
                try:
                    cont = json.loads(all_info)['html']
                except KeyError:
                    return ''
        return cont

    def get_intro_infos(self, html):

        soup = BeautifulSoup(html, "lxml")
        scripts = soup.find_all('script')
        pattern = re.compile(r'FM.view\((.*)\)')
        cont = ''
        for script in scripts:
            m = pattern.search(script.string)
            if m and 'Pl_Core_UserInfo__' in script.string:
                all_info = m.group(1)
                try:
                    cont = json.loads(all_info)['html']
                except KeyError:
                    return ''
        return cont

    def get_intro(self, html):
        """
         :param html:
         :return: 返回个人简介
        """
        cont = self.get_intro_infos(html)
        if cont == '':
            return ''
        soup = BeautifulSoup(cont, 'html.parser')
        try:
            intro = soup.find(attrs={'class': 'info'}).find('span').get_text()
        except Exception:
            return ''
        return intro

    def crawl_person_infos(self, response):
        html = response.body.decode(response.encoding)
        name = self.get_username(html)
        account_id = self.get_userid(html)
        photo = self.get_headimg(html)
        user_domain = self.get_userdomain(html)

        try:
            person_infos = self.get_fans_status(html)
            if not person_infos:
                return
            following, followers, tweets = person_infos
        except Exception as e:
            logging.error(e)
            return
        brief = self.get_intro(html)
        if not (name and account_id and photo):
            return
        user_dic = {
            'weibo_name': name,
            'ref_id': account_id,
            'weibo_id': user_domain,
            'weibo_photo': photo,
            'site': self.site,
            'weibo_followers': followers,
            'weibo_tweets': tweets,
            'weibo_following': following,
            'weibo_brief': brief,
            'account': self.account,
        }
        return SMAccountItem(**user_dic)

    def parse(self, response):

        user_item = self.crawl_person_infos(response)
        if not user_item:
            logging.warning(
                '{}的用户主页微博数据未采集成功，请检查原因'.format(response.url)
            )
            return

        config = self.spider.config
        upload_url = config.get("IMAGE", "UPLOAD_URL")
        data = {
                       "image_source_url": user_item.get("weibo_photo"),
                       "image_destination": "WeiboImages/%s" % user_item.get("ref_id"),
                       "thumbnail": "true",
                       "blur": "false",
                   }

        rep = requests.post(url=upload_url, data=data).json()

        rep = eval(rep)
        status_code = rep.get("status")

        if int(status_code) == 200:
            user_item["weibo_photo"] = rep.get("paths").get("image")
            user_item["thumb_image"] = rep.get("paths").get("thumbnail")
            yield user_item

        else:
            return



    def url_for(self, url):
        if 'http' not in url:
            return 'http:{}'.format(url)
        else:
            return url
