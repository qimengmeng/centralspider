# -*- coding: utf-8 -*-

import random

from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from central.wharehouse.user_agent import (USER_AGENT_LIST)



class RandomUserAgentMiddleware(UserAgentMiddleware):
    """方法说明
    随机指定一个user agent
    """
    def process_request(self, request, spider):
        ua = random.choice(USER_AGENT_LIST)
        request.headers.setdefault("User-Agent", ua)