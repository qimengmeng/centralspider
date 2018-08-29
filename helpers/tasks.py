# -*- coding:utf-8 -*-

from celery import Celery
from celery.utils.log import get_task_logger
from imagehelpers import upload_image_tos3


celeryapp = Celery("workerapp")
tasklogger = get_task_logger(__name__)


@celeryapp.task(name="helpers.upload_image")
def upload_image(upload_url, images_post_params):


    return upload_image_tos3(upload_url, images_post_params)



