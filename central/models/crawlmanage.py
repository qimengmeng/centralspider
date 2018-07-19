# -*- coding: utf-8 -*-
from sqlalchemy import (
                        text,
                        Column,
                        ForeignKey,
                        UniqueConstraint,
                        Index,
)
from sqlalchemy.dialects.mysql import (
    INTEGER, TINYINT, TIMESTAMP, VARCHAR, ENUM, BIGINT
)


from basic_db import Base, TableArgsMixin
from values import VisibleValue



socialmedia_sites = ('twitter', 'weibo')


class SocialMedia(Base, TableArgsMixin):
    __tablename__ = "socialmedia"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    type = Column(VARCHAR(128), nullable=False, server_default="")
    site = Column(ENUM(*socialmedia_sites), nullable=False)
    ref_id = Column(INTEGER(unsigned=True), nullable=False,
                    server_default=text("0"))
    weibo_id = Column(VARCHAR(32), nullable=False)
    weibo_name = Column(VARCHAR(64), nullable=True, server_default=None)
    weibo_photo = Column(VARCHAR(64), nullable=False, server_default="")
    weibo_tweets = Column(INTEGER(unsigned=True), nullable=False,
                          server_default=text("0"))
    weibo_followers = Column(INTEGER(unsigned=True), nullable=False,
                             server_default=text("0"))
    weibo_following = Column(INTEGER(unsigned=True), nullable=False,
                             server_default=text("0"))
    weibo_brief = Column(VARCHAR(128), nullable=False, server_default="")

    visible = Column(TINYINT, nullable=False,
                     server_default=text(VisibleValue.SHOWN))

    created_at = Column(
        TIMESTAMP, nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at = Column(
        TIMESTAMP, nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )

    Index("ix__type__ref_id", type, ref_id)





