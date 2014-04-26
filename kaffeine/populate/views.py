from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.views import logout
from django.views.decorators.csrf import csrf_exempt

from . import models as pm, utils as pu
from . import tasks as pt
import pdb, elasticsearch, json, requests

class SearchResults(View):
    template_name = "populate/results.html"

    def get(self, request):
        return render_to_response(self.template_name, {}, context_instance=RequestContext(request))

    def post(self, request):

        # t = pu.QueryFactory(request.POST['searchInput'], "dummy logger")
        # t.route_seletor()
        # # t.query_controller()
        # # res = t.get_results_or_errors()
        async_task = pt.dispatch.subtask((request.POST['searchInput'],)).apply_async()
        # pdb.set_trace()
        return render_to_response(self.template_name, {'id':async_task.id}, context_instance=RequestContext(request))
        # return render_to_response(self.template_name, {}, context_instance=RequestContext(request))


class RestaurantDetail(DetailView):

    model = pm.RestaurantStatic
    template_name = "populate/detail.html"
    context_object_name = "object"

    def get_object(self, queryset=None):
        #ToDo Handle any fetch errors
        return pm.RestaurantStatic.objects.get(id=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(RestaurantDetail, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            user_node, graph_db = pu.get_current_user_node(self.request.user, return_conn=True)
            restaurant = graph_db.find("Restaurant", "_id", self.kwargs['slug']).next()
            context['user_like'] = bool(list(user_node.match_outgoing("LIKES", restaurant, 1)))
        return context

class NewUser(View):

    template_name = "populate/new_user.html"

    def get(self, request):

        # pdb.set_trace()
        # Create graph entries
        # graph_entry = pt.new_user_graph_entry.subtask((request.user,)).apply_async()
        graph_entry = pt.new_user_graph_entry(request.user)
        # Welcome Email + miscellaneous tasks

        return render_to_response(self.template_name, {}, context_instance=RequestContext(request))


def auto_suggest(request):
    """
    Ajax endpoint
    Segregate requests based on label param
    """
    if request.GET.get('label', None):
        # Perform Graph Query
        RAW_CYPHER_QUERY = "http://127.0.0.1:7475/db/data/cypher"

        headers = {
            'content-type':'application/json',
            'encoding':'utf-8'
        }
        payload = {
            "query":"MATCH (:" + request.GET.get('label', '') + ")-[t]->() RETURN labels(startnode(t)), type(t), labels(endnode(t))",
            "params":{}
        }
        r = requests.post(RAW_CYPHER_QUERY, data=json.dumps(payload), headers=headers)
        return HttpResponse(content=r.text, content_type='application/json')
    else:
        # Perform Elastic Query

        es = elasticsearch.Elasticsearch()
        response = es.search(
            index=request.GET.get('index', '_all'),
            body={
                "query":{
                    "bool":{
                        "must":[
                            {"fuzzy":{"static.name":{"value":request.GET.get('inputPhrase', '')}}}
                        ],
                        "must_not":[],
                        "should":[]
                    }
                },
                "from":0,
                "size":10,
                "sort":[],
                "facets":{}
            }
        )
        # pdb.set_trace()
        return HttpResponse(content=json.dumps(response), content_type='application/json')

@csrf_exempt
def like_view(request, remove=False):
    """
    Call utility function to connect restaurant to user and send JSON response
    """
    try:
        body = json.loads(request.body)
        id = body['id']
        pu.like_connection(id, request.user, remove)
        content = {
            'success':True
        }
    except Exception as err:
        content = {
            'success':False,
            'error':{
                'message':err.message
            }
        }
        return HttpResponse(status=500, content_type='application/json', content=json.dumps(content))

    return HttpResponse(status=200, content_type='application/json', content=json.dumps(content))

def logout_view(request):
    logout(request)
    return HttpResponse("logged out")