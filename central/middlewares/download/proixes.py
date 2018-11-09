# -*- coding: utf-8 -*-
import base64

# 代理服务器
PROXYSERVER = "http-dyn.abuyun.com:9020"
# 代理隧道验证信息
PROXYUSER = "H41Y61C0Y0BG398D"
PROXYPASS = "17EB602A0A0D5AB0"

PROXYAUTH = "Basic " + base64.b64encode(PROXYUSER + ":" + PROXYPASS)

class ProxyMiddleware(object):
    """阿布云代理中间件"""
    def process_request(self, request, spider):

        request.meta["proxy"] = PROXYSERVER
        request.headers["Proxy-Authorization"] = PROXYAUTH
        request.headers["Cache-Control"] = "no-cache"