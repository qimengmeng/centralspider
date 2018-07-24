# -*- coding: utf-8 -*-
import base64


PROXY_DOMAIN = ['sina']

# 代理服务器
PROXYSERVER = "http://proxy.abuyun.com:9010"
# 代理隧道验证信息
PROXYUSER = "HR96J33U70UM8QID"
PROXYPASS = "3AF353FB2568CC67"



PROXYAUTH = "Basic " + base64.b64encode(PROXYUSER + ":" + PROXYPASS)

class ProxyMiddleware(object):
    """阿布云代理中间件"""
    def process_request(self, request, spider):

        request.meta["proxy"] = PROXYSERVER
        request.headers["Proxy-Authorization"] = PROXYAUTH
        request.headers["Cache-Control"] = "no-cache"