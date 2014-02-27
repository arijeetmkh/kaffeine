from __future__ import absolute_import

from celery import shared_task
from celery.utils.log import get_task_logger
from . import utils as pu

logger = get_task_logger(__name__)

@shared_task()
def add(x,y):
    return [1,2,3,4,x,y]

@shared_task
def test(self):
    return self.request.args


@shared_task
def dispatch(searchInput):

    t = pu.QueryFactory(searchInput, logger)
    t.route_seletor()
    t.query_controller()
    logger.debug(t.query)
    return  t.get_results_or_errors()