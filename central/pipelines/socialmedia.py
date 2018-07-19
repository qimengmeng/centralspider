# -*- coding: utf-8 -*-
import logging

from scrapy.exceptions import (
    DropItem,
)

from central.models import (
    SocialMedia,
)
from central.items.crawlmanage import (
    SMAccountItem,
)



class SocialmediaPipeline(object):

    collection_name = "socialmeida_"
    accept_spiders = ('central_socialmedia', )
    accept_items = (SMAccountItem, )
    necessary_keys = {
        'weibo_name', 'weibo_following',
        'weibo_followers', 'weibo_tweets',
    }

    def __init__(self):
        self.count = 0


    @classmethod
    def from_crawler(cls, crawler):

        return cls()

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
        producer = spider.producer
        mslogger = spider.mslogger

        if not self.is_acceptable(item, spider):
            return item

        item_dic = dict(item)
        available_item_columns = [k for k, v in item_dic.items() if v]
        difference = self.necessary_keys - set(available_item_columns)
        if difference:
            raise DropItem("item is invalid")

        socialmeida = item_dic.get('account')
        update_dic = {
            'site': socialmeida.site,
            'weibo_id': socialmeida.weibo_id,
            'ref_id': item_dic.get("ref_id"),
            'weibo_name': item_dic.get('weibo_name'),
            'weibo_followers': item_dic.get('weibo_followers'),
            'weibo_tweets': item_dic.get('weibo_tweets'),
            'weibo_following': item_dic.get('weibo_following'),
            'weibo_brief': item_dic.get('weibo_brief'),
        }

        for k, v in update_dic.iteritems():
            socialmeida.__setattr__(k, v)

        db_session.add(socialmeida)
        try:
            db_session.commit()
        except Exception as e:
            logging.info(e)
            db_session.rollback()