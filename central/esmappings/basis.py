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

    # suggest = Completion(analyzer=ik_analyzer)
    type = Keyword()
    name = Keyword()
    # account_domain = Keyword()
    screen_name = Text(analyzer="ik_max_word")
    icon = Keyword()
    tweets = Integer()
    followers = Integer()
    following = Integer()
    brief = Keyword()
    # thumb_image = Keyword()
    category = Keyword()
    alpha = Keyword()
    language = Keyword()
    country = Nested(
        properties={
            "id": Keyword(),
            "name": Text(analyzer="ik_max_word"),
        }
    )



    class Meta:
        index = "weibo_account"
        doc_type = "weibo_account"

        settings = {
            "number_of_shards": 5,
            }



class TweetType(DocType):
    #微博类型

    # suggest = Completion(analyzer=ik_analyzer)
    url = Keyword()
    publish_time = Date()
    title = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    description = Text(analyzer="ik_max_word")
    type = Keyword()
    entry_time = Date()
    images = Nested(
                properties={
                    "origin": Keyword(),
                    "thumbnail": Keyword(),
                    "tiny": Keyword()
                }
                            )
    stat = Nested(
        properties={
            "up_num": Integer(),
            "retweet_num": Integer(),
            "comment_num": Integer()
        }
    )
    tags = Nested(
        properties={
            "topic": Keyword(),
            "super_topic": Keyword(),
        }
    )
    source = Nested(
        properties={
             "name": Keyword(),
             "screen_name": Text(analyzer="ik_max_word"),
             "icon": Keyword()
        }
    )
    to_cms = Boolean()
    language = Keyword()
    translate = Text()
    # weibo_id = Keyword()

    class Meta:
        index = "weibo"
        doc_type = "weibo"

        settings = {
            "number_of_shards": 5,
        }

