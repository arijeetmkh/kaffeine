from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView

from .views import SearchResults, NewUser, logout_view
from .ajax import FetchResults

urlpatterns = patterns('',
                       url(r'^home/$', TemplateView.as_view(template_name="populate/prototype.html")),
                       url(r'^results/', SearchResults.as_view(), name='results'),
                       url(r'^ajax_results/$', FetchResults.as_view(), name='ajax_results'),
                       url(r'^welcome/$', NewUser.as_view(), name='new_user'),
                       url(r'^logout/$', logout_view, name='logout'),
)