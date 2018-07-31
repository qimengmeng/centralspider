# -*- coding: utf-8 -*-

import os


PWD = os.path.dirname(os.path.abspath(__file__))


###########
# 新闻网站列表
# 直接增加新闻网站的字典
# 字典包含新闻网站的名称、主站地址和监控的url列表

############
# 字段含义
# (1)语言lang：中文：0, 英文：1, 日语：2, 朝鲜语：3, 韩语：4
# (2)新闻类别 news_type: 自己：0, 社交：1,  网站：2
# (3)分类category： 门户：0, 通讯社：1, 政府：2
# (4)国别country：中国 0, 美国：1, 英国:2, 俄罗斯:3, 法国：4, 加拿大：5 ,
# 韩国：6, 叙利亚：7, 伊朗：8, 印度：9, 阿拉伯 10, 日本：11,  朝鲜：12,  澳大利亚：13

#动态号
SOCIALMEDIA = [
    # ---文字类型---
    #微博账号

    {
        "name": 'weibo_account',
        "site": 'weibo',
        "urls": [
        ],
        "allowed_domains": ["weibo.com", ],
    },
]

#动态内容
TWEET = [
    # ---文字类型---
    #微博动态

    {
        "name": 'weibo_tweet',
        "site": 'weibo',
        "urls": [
        ],
        "allowed_domains": ["weibo.com", ],

        "operation": {
                'lang': 0,
                'news_type': 2,
                'category': 0,
                'country': 0,
                'url_source': 'https://weibo.com/'
                    }
    },
]


HOTSEARCH = [
    # ---文字类型---
    #微博热搜

    {
        "name": 'weibo_hotsearch',
        "site": 'weibo',
        "urls": [
            "http://s.weibo.com/top/summary?cate=realtimehot",
        ],
        "allowed_domains": ["weibo.com", ],

        "operation": {
                'lang': 0,
                'news_type': 2,
                'category': 0,
                'country': 0,
                'url_source': 'https://weibo.com/'
                    }
    },
]