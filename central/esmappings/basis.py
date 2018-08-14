# -*- coding:utf-8 -*-


from elasticsearch_dsl import (
    DocType, Date, Nested, Boolean,
    analyzer, Completion, Keyword, Text, Integer, Mapping,

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


    class Meta:
        index = "socialmedia"
        doc_type = "socialmedia"

        settings = {
            "number_of_shards": 5,
            }





class TweetType(DocType):
    #微博类型

    suggest = Completion(analyzer=ik_analyzer)
    socialmedia_id = Integer()
    url = Keyword()
    publish_time = Date()
    publish_source = Keyword()
    content = Text(analyzer="ik_max_word")
    weibo_id = Keyword()
    up_num = Integer()
    retweet_num = Integer()
    comment_num = Integer()
    s3_images = Keyword()
    thumb_images = Keyword()
    tags = Text(analyzer="ik_max_word")

    class Meta:
        index = "tweet"
        doc_type = "tweet"

        settings = {
            "number_of_shards": 5,
        }
