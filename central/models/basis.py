# -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy import (
                        text,
                        Column,
                        ForeignKey,
                        UniqueConstraint,
                        Index,
)
from sqlalchemy.dialects.mysql import (
    INTEGER, TINYINT, TIMESTAMP, VARCHAR, ENUM, BIGINT, TEXT
)
from sqlalchemy.orm import deferred, relationship



from .basic_db import Base, TableArgsMixin
from .values import VisibleValue



class Tweet(Base, TableArgsMixin):
    __tablename__ = "tweet"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    socialmedia_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("socialmedia.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )
    site = Column(VARCHAR(32), nullable=False)
    has_image = Column(TINYINT, nullable=False,
                       server_default=sqlalchemy.text("0"))
    has_video = Column(TINYINT, nullable=False,
                       server_default=sqlalchemy.text("0"))
    text = Column(
        VARCHAR(1024, charset="utf8mb4", collation="utf8mb4_unicode_ci"),
        nullable=False, server_default=""
    )
    geo = Column(VARCHAR(128), nullable=False, server_default="")
    publish_tm = Column(TIMESTAMP, nullable=False,
                        server_default=sqlalchemy.text("CURRENT_TIMESTAMP"))
    marker = Column(VARCHAR(64), nullable=False, index=True, server_default="")
    visible = Column(TINYINT, nullable=False,
                     server_default=sqlalchemy.text(VisibleValue.SHOWN))

    created_at = Column(
        TIMESTAMP, nullable=False,
        server_default=sqlalchemy.text("CURRENT_TIMESTAMP")
    )
    updated_at = Column(
        TIMESTAMP, nullable=False,
        server_default=sqlalchemy.text(
            "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        )
    )

    social = relationship("SocialMedia", lazy="select",
                      foreign_keys=[socialmedia_id])
    Index("idx_socialmedia_id_updated_at", socialmedia_id, updated_at)










