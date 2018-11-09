# -*- coding:utf-8 -*-

from elasticsearch_dsl import (
    DocType, Date, Nested, Boolean,
    analyzer, Completion, Keyword, Text, Integer

)


class CrawlerLogType(DocType):
    # 爬虫日志格式类型

    level = Keyword()
    message = Text(analyzer="ik_max_word")
    time = Date()
    subscribers = Keyword()
    detail = Nested(
        properties={
            "website": Keyword(),
            "type": Keyword(),
        }
    )
    logger_name = Keyword()
    path = Keyword()
    host = Keyword()

    class Meta:
        index = "crawler_log"
        doc_type = "crawler_log"

        settings = {
            "number_of_shards": 5,
            }
