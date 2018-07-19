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


def duration_seconds(dura):
    """方法说明
    播放时长数字化,转化为秒
    """
    try:
        dura = dura.split(':')
        if len(dura) == 3:
            return int(dura[0]) * 3600 + int(dura[1]) * 60 + int(dura[2])

        if len(dura) == 2:
            return int(dura[0]) * 60 + int(dura[1])

        if len(dura) == 1:
            return int(dura[0])

        return 0
    except:
        return 0


def approximate_datetime(timeobj, **kwargs):
    """把时间精确到某一精度"""
    priority = (
        'year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond'
    )
    for key in kwargs.keys():
        if key not in priority:
            raise ValueError
    accuracy = min(kwargs.keys(), key=lambda x: priority.index(x))
    new_attrs = []
    for attr in priority:
        if attr == accuracy:
            floor_value = kwargs.get(accuracy, 1)
            new_attrs.append(
                getattr(timeobj, attr)/floor_value*floor_value
            )
            break
        new_attrs.append(getattr(timeobj, attr))
    while len(new_attrs) < 3:
        new_attrs.append(1)
    return datetime(*new_attrs)


def is_new_video(start_tm):

    flage = False
    if start_tm:
        match_start = datetime.strptime(start_tm, "%Y-%m-%d %H:%M:%S")
        time_del = datetime.today() - match_start
        if time_del.days == 0:
            flage = True
    else:
        flage = False

    return flage


def is_new_article(publish_tm, days=0, hours=12):

    flage = False

    if publish_tm:
        publish = datetime.strptime(publish_tm, "%Y-%m-%d %H:%M:%S")
        time_del = datetime.today() - publish
        if (time_del.days == days) and (time_del.seconds <= (hours * 3600)):
            flage = True
    else:
        flage = False

    return flage


def get_old_day(days=7, format_str="%Y-%m-%d"):

    today = datetime.today()
    older = today - timedelta(days=days)

    return older.strftime(format_str), today.strftime(format_str)


def get_match_range_day(days=7, format_str="%Y-%m-%d"):

    today = datetime.today()
    older = today - timedelta(days=days)
    newer = today + timedelta(days=days)

    return older.strftime(format_str), newer.strftime(format_str)
