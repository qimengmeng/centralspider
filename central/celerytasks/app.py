# -*- coding: utf-8 -*-

from __future__ import absolute_import

from celery import Celery


tasks = [
    'celerytasks.spidertask',
]

celery_app = Celery('workapp', include=tasks)

# celery_app.config_from_object('celerytasks.config')
# celery_app.conf.update(
#     **{
#         'BROKER_URL': BROKER_URL,
#         'CELERY_RESULT_BACKEND': CELERY_RESULT_BACKEND,
#     }
# )









