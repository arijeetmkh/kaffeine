from __future__ import absolute_import

from celery import shared_task
from celery.utils.log import get_task_logger
from . import utils as pu
from . import models as pm
from social.apps.django_app.default.models import UserSocialAuth

import pdb

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
    logger.info(t.query)
    return  t.get_results_or_errors()

@shared_task
def new_user_graph_entry(user):
    """
    Add a new user node if it doesnt already exist and connect it to friends
    """
    #Call to FB API for friend list
    extra = {
        'fields':'id,name',
        'limit':'5000'
    }
    response, success = pu.facebook_graph_api_query(endpoint='/me/friends', token=user.social_auth.first().tokens, **extra)
    if not success:
        #Raise a celery task failed exception with extra info
        pass
    #Call SQL DB to get users in our system from friends list
    existing_users = UserSocialAuth.objects.filter(uid__in=map(lambda x:x['id'], response['data']))
    #Call create node which will return node object
    #Call rel create in some loop logic to create friends
    pu.create_friends(user, existing_users)

    #ToDo Create users in the graph
    return response