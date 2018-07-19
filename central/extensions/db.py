# -*- coding:utf-8 -*-

import logging

from sqlalchemy import (
    create_engine,
)
from sqlalchemy.orm import (
        sessionmaker,
        scoped_session,
)
from scrapy import signals



class Db(object):
    """类说明
    数据库连接
    """

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        return ext

    def spider_opened(self, spider):

        config = spider.config

        SQLALCHEMY_DATABASE_URI = config.get("MYSQL", "SQLALCHEMY_DATABASE_URI")

        from central.models.basic_db import Base

        engine = create_engine(
            SQLALCHEMY_DATABASE_URI,
            pool_recycle=7200,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            encoding='utf-8',
            echo=False,

        )
        Session = scoped_session(sessionmaker(bind=engine))
        db_session = Session()

        spider.db_session = db_session

        logging.info("running spider:%s", spider.name)