# -*- coding: utf-8 -*-
import logging
import json
import datetime

from scrapy.exceptions import (
    DropItem,
)
from kafka.errors import KafkaError

from central.items.basis import (
    TweetItem, TweetImageItem,
)

from central.pipelines.images_pipeline import (
    MyImagesPipeline,
)


class TweetPipeline(object):

    collection_name = "tweet_"
    accept_spiders = ('central_tweet', )
    accept_items = (TweetItem, TweetImageItem)
    necessary_keys = {
        'publish', 'content'
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
        mslogger = spider.mslogger
        producer = spider.producer

        if not self.is_acceptable(item, spider):
            return item

        item_dic = dict(item)
        available_item_columns = [k for k, v in item_dic.items() if v]
        difference = self.necessary_keys - set(available_item_columns)
        if difference:
            raise DropItem("item is invalid")

        # 重新封装
        params = {
            'url': item['url'],
            'publish_time': datetime.datetime.strptime(item['publish'], "%Y-%m-%d %H:%M:%S").strftime(
                "%Y-%m-%dT%H:%M:%S.000Z"),

            'news_type': item_dic["operation"]['news_type'],
            'category': item_dic["operation"]['category'],
            'country':  item_dic["operation"]['country'],
            'lang':  item_dic["operation"]['lang'],

            'share_url': '',
            'publish_source': item_dic['site'],
            'publish_account': '',
            'content': item_dic['content'],
            'top_image': '',
            's3_image': '',
            'thumb_image': '',
            'profile_image': '',
            'tag_output': '',
        }
        if len(item['image_urls']) > 0:
            params['top_image'] = item['image_urls'][0]
        if len(item['images']) > 0:
            params['s3_image'] = config.get('IMAGE', 'PREFIX') + item['images'][0]['path']
            # params['thumb_image'] = config.get('IMAGE', 'PREFIX') + 'thumbs/%s/%s.jpg' % (request.meta['path'], thumb_guid)

        # 转化为json
        message = json.dumps(params).encode('utf-8')

        try:
            producer.send('news_streaming', str(message))
            producer.flush()
        except KafkaError as e:
            print e


