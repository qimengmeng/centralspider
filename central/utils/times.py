# -*- coding: utf-8 -*-
"""tiem utils"""
import time
from datetime import datetime
from datetime import timedelta


def timestamptostr(timestamp, format_str="%Y-%m-%d %H:%M:%S"):
    """方法说明
    将时间戳转换为字符串格式的日期
    """
    if isinstance(timestamp, basestring):
        try:
            timestamp = float(timestamp)
        except:
            timestamp = 0

    if not timestamp:
        return time.strftime(format_str)

    return time.strftime(format_str, time.localtime(timestamp))


def strtotimestamp(timestr, format_str="%Y-%m-%d %H:%M:%S"):
    """方法说明
    将字符串格式的日期转换为时间戳
    """
    for fstr in (format_str, "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return time.mktime(time.strptime(timestr, fstr))
        except:
            continue
    else:
        raise Exception(u"Error time format: ({})".format(timestr))


def struct_time(timestamp=None):
    """方法说明
    将时间戳转换为时间对象，以便获取单独的年月日等信息
    """
    return time.localtime() if timestamp is None else time.localtime(timestamp)


def target_time(format_str="%Y-%m-%d %H:%M:%S", base_time=None, **kw):
    """方法说明
    利用datetime获取指定时间差的时间
    datetime.timedelta([days[, seconds[, microseconds[, milliseconds[,
    minutes[, hours[, weeks]]]]]]])
    """
    if not base_time:
        base_time = datetime.now()
    target_time = base_time + timedelta(**kw)
    return target_time.strftime(format_str)

