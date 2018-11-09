# -*- coding:utf-8 -*-


import logging
import json

from scrapy.exceptions import (
    DropItem,
)

from central.items.basis import (
    TweetHotsearchItem,
)


class HotsearchPipeline(object):

    collection_name = "hotsearch_"
    accept_spiders = ('central_hotsearch', )
    accept_items = (TweetHotsearchItem,)
    necessary_keys = {
        "keyword", "hot_degree", "hottime", "order_number"
    }

    def __init__(self, ):
        self.count = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    ###########
    # 爬虫启动
    def open_spider(self, spider):

        logging.info("running spider:%s", spider.name)

    def close_spider(self, spider):
        if self.count:
            logging.info(
                "%s has process %s items", type(self).__name__, self.count
            )
        logging.info("closed spider:%s", spider.name)

    def is_acceptable(self, item, spider):
        if not item:
            return False

        if spider.name not in self.accept_spiders:
            return False

        if not isinstance(item, self.accept_items):
            return False

        self.count += 1
        return True

    def process_item(self, item, spider):

        db_session = spider.db_session
        config = spider.config

        if not self.is_acceptable(item, spider):
            return item

        item_dic = dict(item)
        available_item_columns = [k for k, v in item_dic.items() if v]
        difference = self.necessary_keys - set(available_item_columns)
        if difference:
            raise DropItem("item is invalid")

        # 重新封装
        params = {
            'url': item_dic.get('link'),
            'hottime': item_dic.get("hottime"),
            "keyword": item_dic.get("keyword"),
            "hot_degree": item_dic.get("hot_degree"),
            "order_number": item_dic.get("order_number")
        }

        # 转化为json
        message = json.dumps(params).encode('utf-8')

