# -*- coding:utf-8 -*-


from elasticsearch_dsl import (
    DocType, Date, Nested, Boolean,
    analyzer, Completion, Keyword, Text, Integer

)

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}
ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])



class SocialmediaType(DocType):
    # 微博账户类型

    suggest = Completion(analyzer=ik_analyzer)
    site = Keyword()
    account_id = Keyword()
    account_domain = Keyword()
    weibo_name = Text(analyzer="ik_max_word")
    weibo_photo = Keyword()
    weibo_tweets = Integer()
    weibo_followers = Integer()
    weibo_following = Integer()
    weibo_brief = Text(analyzer="ik_max_word")
    thumb_image = Keyword()
    tags = Keyword()
    alpha = Keyword()


    class Meta:
        index = "account_weibo"
        doc_type = "account_weibo"

        settings = {
            "number_of_shards": 5,
            }



class TweetType(DocType):
    #微博类型

    suggest = Completion(analyzer=ik_analyzer)
    url = Keyword()
    publish_time = Date()
    publish_source = Keyword()
    content = Text(analyzer="ik_max_word")
    weibo_id = Keyword()
    up_num = Integer()
    retweet_num = Integer()
    comment_num = Integer()
    s3_images = Keyword()
    tiny_images = Keyword()
    thumb_images = Keyword()
    tags = Keyword()
    created_at = Date()
    publish_account = Nested(properties={
                                        "weibo_name": Keyword(),
                                        "weibo_photo": Keyword(),
                                        "account_id": Keyword(),
                                        "weibo_brief": Keyword()
                                        }

                                )

    class Meta:
        index = "weibo"
        doc_type = "weibo"

        settings = {
            "number_of_shards": 5,
        }

