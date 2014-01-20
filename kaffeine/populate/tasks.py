from __future__ import absolute_import

from celery import shared_task


@shared_task
def add(x,y):
    return [1,2,3,4,x,y]

