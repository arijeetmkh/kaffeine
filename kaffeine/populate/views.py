from django.views.generic.base import View
from django.shortcuts import render_to_response
from django.template import RequestContext

import pdb

class SearchResults(View):
    template_name = "populate/results.html"

    def get(self, request):
        return render_to_response(self.template_name, {}, context_instance=RequestContext(request))

    def post(self, request):


        return render_to_response(self.template_name, {}, context_instance=RequestContext(request))