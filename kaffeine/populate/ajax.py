from . import tasks as pt
from . import models as pm

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.views.generic import View

import json,pdb

class FetchResults(View):

    result_fields = ['id', 'name', 'subzone', 'cost', 'timings', 'address', 'cuisines']
    job_id = None
    async_task = None
    response = None

    def __init__(self, **kwargs):

        self.response = {
            'ready':False,
            'status':"",
            'message':None,#not implemented
            'data':{
                'data':[]
            },
            'pagination':{
                'page_range':None,
                'has_next':None,
                'has_previous':None,
                'num_pages':None,
                'next_page_number':None,
                'previous_page_number':None
            }
        }

        super(FetchResults, self).__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        self.job_id = request.GET.get('id', None)
        self.page = self.kwargs.get('page', 1)

        if self.job_id:
            self.async_task = pt.dispatch.AsyncResult(self.job_id)
            if not self.check_ready():
                return self.response_return()
            self.set_status()
            self.get_results(fresh=True)
        else:
            self.get_results()
        return self.response_return()


    def check_ready(self):

        self.response['ready'] = self.async_task.ready()
        return self.async_task.ready()


    def set_status(self):
        self.response['status'] = self.async_task.status

    def get_results(self, fresh=False):

        if fresh:
            results = self.async_task.get()
            self.request.session['results'] = results
        else:
            results = self.request.session.get('results', None)
            if not results:
                results = self.async_task.get()
        p = Paginator(results['data'], 20)
        self.response['pagination']['page_range'] = p.page_range
        try:
            page = p.page(int(self.page))
        except PageNotAnInteger:
            page = p.page(1)
        except EmptyPage:
            page = p.page(p.num_pages)

        self.response['pagination']['has_next'] = page.has_next()
        self.response['pagination']['has_previous'] = page.has_previous()
        self.response['pagination']['num_pages'] = p.num_pages

        if page.has_next():
            self.response['pagination']['next_page_number'] = page.next_page_number()
        if page.has_previous():
            self.response['pagination']['previous_page_number'] = page.previous_page_number()

        ids = map(lambda x:x[0], page.object_list)
        for i,restaurant in enumerate(sorted(pm.RestaurantStatic.objects.filter(id__in=ids), key=lambda x:ids.index(x.id))):
            append_dict = {'social':{}}
            for field in self.result_fields:
                append_dict[field] = restaurant[field]
            if page.object_list[i][1]:
                append_dict['social']['is_social'] = True
                append_dict['social']['data'] = page.object_list[i][1]
            else:
                append_dict['social']['is_social'] = False

            self.response['data']['data'].append(append_dict)


    def response_return(self):
        return HttpResponse(json.dumps(self.response), content_type="application/json")