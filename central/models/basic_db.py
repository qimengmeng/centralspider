# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base



class TableArgsMixin(object):
    __table_args__ = {
        "mysql_engine": "InnoDB", "mysql_charset": "utf8",
        "mysql_row_format": "Compact"
    }

Base = declarative_base()

def to_dict(self):
    return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}

@classmethod
def get_all_table_cloumns(cls):

    return [c.name for c in cls.__table__.columns]

Base.to_dict = to_dict
Base.get_all_table_columns = get_all_table_cloumns


__all__ = ['eng', 'Base', 'db_session', 'metadata']
