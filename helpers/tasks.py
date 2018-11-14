# -*- coding:utf-8 -*-
import re
import json
import hashlib
from StringIO import StringIO

from boto import s3
from boto.s3.key import Key

from celery import Celery
from celery.utils.log import get_task_logger


from .common import download_buffer

celeryapp = Celery("workerapp")
tasklogger = get_task_logger(__name__)



@celeryapp.task(name="picture.tiny")
def picture_tiny(urls):

    res = map(lambda x: {"origin": ".jpg",
                         "thumbnail": ".thumbnail.jpg",
                         "tiny": ".tiny.jpg"}, urls)

    for url in urls:
        buffer = download_buffer(url)
        width, height = buffer.size

        format_ = buffer.format
        mimetype = "image/%s" % format_

        hash_value = hashlib.md5(url).hexdigest()
        image_name = '%s.jpg' % hash_value
        image_destination = re.sub(r'^(/+)|(/+)$', '', image_destination)

    pass






