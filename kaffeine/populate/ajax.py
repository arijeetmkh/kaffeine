from . import tasks as pt
from . import models as pm

from django.http import HttpResponse
from django.views.generic import View

import json, pdb

class FetchResults(View):

    result_fields = ['id', 'name', 'subzone']
    job_id = None
    async_task = None
    response = None

    def __init__(self, **kwargs):

        self.response = {
            'ready':False,
            'status':"",
            'message':None,#not implemented
            'data':{
                'ids':None,
                'data':[]
            },
            'count':0
        }

        super(FetchResults, self).__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        self.job_id = request.GET['id']
        self.async_task = pt.dispatch.AsyncResult(self.job_id)
        if not self.check_ready():
            return self.response_return()
        self.set_status()
        self.get_results()
        return self.response_return()


    def check_ready(self):

        self.response['ready'] = self.async_task.ready()
        return self.async_task.ready()


    def set_status(self):
        self.response['status'] = self.async_task.status

    def get_results(self):

        self.response['data']['ids'] = self.async_task.get()
        self.response['count'] = len(self.response['data']['ids'])
        for restaurant in pm.RestaurantStatic.objects.filter(id__in=self.async_task.get()):
            append_dict = {}
            for field in self.result_fields:
                append_dict[field] = restaurant[field]
            self.response['data']['data'].append(append_dict)


    def response_return(self):
        return HttpResponse(json.dumps(self.response), content_type="application/json")