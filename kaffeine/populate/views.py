from django.views.generic.base import View
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.views import logout

from . import tasks as pt
import pdb

class SearchResults(View):
    template_name = "populate/results.html"

    def get(self, request):
        return render_to_response(self.template_name, {}, context_instance=RequestContext(request))

    def post(self, request):

        # t = QueryFactory(request.POST['searchInput'], "dummy logger")
        # t.route_seletor()
        # t.query_controller()
        # res = t.get_results_or_errors()
        # pdb.set_trace()

        async_task = pt.dispatch.subtask((request.POST['searchInput'],)).apply_async()

        return render_to_response(self.template_name, {'id':async_task.id}, context_instance=RequestContext(request))
        # return render_to_response(self.template_name, {'id':res}, context_instance=RequestContext(request))

class NewUser(View):

    template_name = "populate/new_user.html"

    def get(self, request):

        # pdb.set_trace()
        # Create graph entries
        # graph_entry = pt.new_user_graph_entry.subtask((request.user,)).apply_async()
        graph_entry = pt.new_user_graph_entry(request.user)
        # Welcome Email + miscellaneous tasks

        return render_to_response(self.template_name, {}, context_instance=RequestContext(request))


def logout_view(request):
    logout(request)
    return HttpResponse("logged out")
