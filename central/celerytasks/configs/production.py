# -*- coding: utf-8 -*-

import os
from datetime import timedelta

from celery.schedules import crontab
from celery import Celery, platforms
from kombu import Exchange, Queue


platforms.C_FORCE_ROOT = True

worker_log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)) + '/logs', 'celery.log')
beat_log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)) + '/logs', 'beat.log')










############################
#以下为通用配置
############################

# 某个程序中出现的队列，在broker中不存在，则立刻创建它
# CELERY_CREATE_MISSING_QUEUES = True

# 非常重要,有些情况下可以防止死锁
# CELERYD_FORCE_EXECV = True

CELERYD_PREFETCH_MULTIPLIER = 1

# 每个worker最多执行万10个任务就会被销毁，可防止内存泄露
CELERYD_MAX_TASKS_PER_CHILD = 10

# 单个任务的运行时间不超过此值，否则会被SIGKILL 信号杀死
# CELERYD_TASK_TIME_LIMIT = 3600

# BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
# 任务发出后，经过一段时间还未收到acknowledge , 就将任务重新交给其他worker执行
# CELERY_DISABLE_RATE_LIMITS = True

# CELERYD_CONCURRENCY = 10


CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True
CELERYD_LOG_FILE = worker_log_path
CELERYBEAT_LOG_FILE = beat_log_path
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_worker_hijack_root_logger = False
CELERY_QUEUES = (
    Queue('tweet_crawler', exchange=Exchange('tweet_crawler', type='direct'), routing_key='for_tweet'),
    Queue('socialmedia_crawler', exchange=Exchange('socialmedia_crawler', type='direct'), routing_key='for_socialmedia'),
)

# CELERY_ROUTES = (
#
#     {
#
#       'tweet_spider': {
#                              'queue': 'tweet_crawler',
#                              'routing_key': 'for_tweet',
#                                 },
#
#
#      'socialmedia_spider': {
#                                   'queue': 'socialmedia_crawler',
#                                   'routing_key': 'for_socialmedia',
#                                      },
#
#
#     }
#
# )


CELERYBEAT_SCHEDULE = {

    'crawl_tweet': {
        'task': 'tweet_spider',
        'schedule': crontab(minute=10),
        'args': ('central_tweet',),
        'options': {'queue': 'tweet_crawler', 'routing_key': 'for_tweet'},

    },
    'crawl_socialmedia': {
        'task': 'socialmedia_spider',
        'schedule': crontab(minute=30, hour=20),
        'args': ('central_socialmedia',),
        'options': {'queue': 'socialmedia_crawler', 'routing_key': 'for_socialmedia'},

    },

}
