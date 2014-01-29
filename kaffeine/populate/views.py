from django.views.generic.base import View
from django.shortcuts import render_to_response
from django.template import RequestContext

from .utils import QueryFactory
import pdb

class SearchResults(View):
    template_name = "populate/results.html"

    def get(self, request):
        return render_to_response(self.template_name, {}, context_instance=RequestContext(request))

    def post(self, request):

        t = QueryFactory(request.POST['searchInput'])
        t.route_seletor()
        t.query_controller()
        pdb.set_trace()
        return render_to_response(self.template_name, {}, context_instance=RequestContext(request))