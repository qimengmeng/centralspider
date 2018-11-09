# -*- coding:utf-8 -*-

from celery import Celery
from celery.utils.log import get_task_logger

celeryapp = Celery("workerapp")
tasklogger = get_task_logger(__name__)







