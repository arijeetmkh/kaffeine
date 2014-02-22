from __future__ import absolute_import

from celery import shared_task
from . import utils as pu


@shared_task()
def add(x,y):
    return [1,2,3,4,x,y]

@shared_task
def test(self):
    return self.request.args


@shared_task
def dispatch(searchInput):

    t = pu.QueryFactory(searchInput)
    t.route_seletor()
    t.query_controller()
    return  t.get_results_or_errors()