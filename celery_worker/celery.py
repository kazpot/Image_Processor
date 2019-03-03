from __future__ import absolute_import
from celery import Celery

app = Celery('celery_worker',broker='amqp://admin:mypass@rabbit:5672/',include=['celery_worker.tasks'])
