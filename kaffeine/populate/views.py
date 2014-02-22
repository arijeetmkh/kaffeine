from django.views.generic.base import View
from django.shortcuts import render_to_response
from django.template import RequestContext

from .utils import QueryFactory
from . import tasks as pt
import pdb

class SearchResults(View):
    template_name = "populate/results.html"

    def get(self, request):
        return render_to_response(self.template_name, {}, context_instance=RequestContext(request))

    def post(self, request):

        # t = QueryFactory(request.POST['searchInput'])
        # t.route_seletor()
        # t.query_controller()
        # data, errors = t.get_results_or_errors()
        # pdb.set_trace()

        async_task = pt.dispatch.subtask((request.POST['searchInput'],), countdown=5).apply_async()

        return render_to_response(self.template_name, {'id':async_task.id}, context_instance=RequestContext(request))