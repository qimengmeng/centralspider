# -*- coding: utf-8 -*-


import random


class RandomCookieMiddleware(object):
    """方法说明
        随机指定一个cookies
        """
    def process_request(self, request, spider):
        if spider.name in ['central_socialmedia', 'central_tweet']:
            ck = {
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

            request.cookies = ck
