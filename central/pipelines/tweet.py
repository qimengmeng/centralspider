# -*- coding: utf-8 -*-
import logging
import json
import datetime

from scrapy.exceptions import (
    DropItem,
)
from boto import kinesis

from central.items.basis import (
    TweetItem, TweetImageItem,
)

class TweetPipeline(object):

    collection_name = "tweet_"
    accept_spiders = ('central_tweet', )
    accept_items = (TweetItem, TweetImageItem)
    necessary_keys = {
        'url', 'content'
    }

    def __init__(self, ):
        self.count = 0


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
        self.data_stream_name = config.get("KINESIS", "DATA_STREAM_NAME")


        if not self.is_acceptable(item, spider):
            return item

        item_dic = dict(item)
        available_item_columns = [k for k, v in item_dic.items() if v]
        difference = self.necessary_keys - set(available_item_columns)
        if difference:
            raise DropItem("item is invalid")

        account = item_dic.get("account")
        # 重新封装
        params = {
            "index": "weibo",
            "type": "weibo",
            "_source": {

                'url': item_dic.get('url'),
                'publish_time': datetime.datetime.strptime(item_dic.get('publish'), "%Y-%m-%d %H:%M:%S").strftime(
                    "%Y-%m-%dT%H:%M:%S.000Z"),
                # "weibo_id": item_dic.get("weibo_id"),
                "stat": {
                    "up_num": item_dic.get("up_num"),
                    "retweet_num": item_dic.get("retweet_num"),
                    "comment_num": item_dic.get("comment_num")
                    },
                "type": item_dic.get('website'),
                "source": {
                        "screen_name": account.weibo_name,
                        "icon": account.weibo_photo,
                        "name": account.ref_id,
                                },
                "title": item_dic.get('content'),
                "tags": item_dic.get("tags"),
                "images": item_dic.get("images"),
                "entry_time": (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "content": "",
                "description": "",
                "to_cms": False,
                "language": "zh",
                "translate": ""

            }

        }

        # 转化为json
        message = json.dumps(params).encode('utf-8')

        self.put_aws(message)
        logging.debug("------")

    def put_aws(self, data):
        kinesis_client = kinesis.connect_to_region('cn-north-1')
        kinesis_client.put_record(self.data_stream_name, data=data, partition_key='partitionKey1')







