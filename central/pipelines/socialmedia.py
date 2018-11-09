# -*- coding: utf-8 -*-
import logging
from xpinyin import Pinyin

from scrapy.exceptions import (
    DropItem,
)
from elasticsearch import (
    Elasticsearch,ElasticsearchException,helpers
)

from central.models import (
    SocialMedia,
)
from central.items.crawlmanage import (
    SMAccountItem,
)


pinyin = Pinyin()

class SocialmediaPipeline(object):

    collection_name = "socialmeida"
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
        self.es_client = spider.es_client

        if not self.is_acceptable(item, spider):
            return item

        item_dic = dict(item)
        available_item_columns = [k for k, v in item_dic.items() if v]
        difference = self.necessary_keys - set(available_item_columns)
        if difference:
            raise DropItem("item is invalid")

        socialmeida = item_dic.get('account')
        update_dic = {
            'weibo_id': item_dic.get("weibo_id"),
            'weibo_name': item_dic.get('weibo_name'),
            'weibo_followers': item_dic.get('weibo_followers'),
            'weibo_tweets': item_dic.get('weibo_tweets'),
            'weibo_following': item_dic.get('weibo_following'),
            'weibo_brief': item_dic.get('weibo_brief'),
            'weibo_photo': item_dic.get('weibo_photo'),
        }

        for k, v in update_dic.iteritems():
            socialmeida.__setattr__(k, v)

        db_session.add(socialmeida)
        try:
            db_session.commit()
        except Exception as e:
            logging.info(e)
            db_session.rollback()

        self.save_to_es(item_dic)


    def save_to_es(self, item_dic):

        socialmedia = item_dic.get('account')
        response = self.es_client.search(
            index="weibo_account",
            doc_type="weibo_account",
            body={
                "query": {
                    "term": {
                        "name": socialmedia.ref_id,
                        }
                     },
                "_source": ["name"]
                },
            )


        total = response["hits"]["total"]
        sources = response["hits"]["hits"]

        if total == 0:
            alpha = pinyin.get_pinyin(socialmedia.weibo_name, show_tone_marks=True)[0].upper()

            if alpha not in [unichr(ch) for ch in xrange(0x41, 0x5B)]:
                alpha = u'其他'

            body = {
                  "name": socialmedia.ref_id,
                  "screen_name": socialmedia.weibo_name,
                  "icon": socialmedia.weibo_photo,
                  "tweets": socialmedia.weibo_tweets,
                  "followers": socialmedia.weibo_followers,
                  "following": socialmedia.weibo_following,
                  "brief": socialmedia.weibo_brief,
                  "category": socialmedia.type.split(","),
                  "alpha": alpha,
                  "type": socialmedia.site,
                  "language": "zh",
                  "country": {
                      "id": "CHN",
                      "name": "China"
                  }
                    }

            res = self.es_client.index(
                        index='weibo_account',
                        doc_type='weibo_account',
                        body=body,
                        id=None
                    )
            logging.debug(res["result"])

        elif total == 1:

            source = sources[0]
            res = self.es_client.update(
                        index='weibo_account',
                        doc_type='weibo_account',
                        id=source.get("_id"),
                        body={
                            "doc": {
                              "tweets": socialmedia.weibo_tweets,
                              "followers": socialmedia.weibo_followers,
                              "following": socialmedia.weibo_following
                              }
                          }
                           )

            logging.debug(res["result"])

        else:
            raise

        logging.info("-----------")





