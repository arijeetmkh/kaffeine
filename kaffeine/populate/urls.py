from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView

from .views import SearchResults, NewUser, RestaurantDetail
from .ajax import FetchResults

urlpatterns = patterns('populate.views',
                       url(r'^home/$', TemplateView.as_view(template_name="populate/prototype.html")),
                       url(r'^results/', SearchResults.as_view(), name='results'),
                       url(r'^ajax_results/(?P<page>\d{1})/$', FetchResults.as_view(), name='ajax_results'),
                       url(r'^welcome/$', NewUser.as_view(), name='new_user'),
                       url(r'^suggest/$', 'auto_suggest', name='suggestions'),
                       url(r'^logout/$', 'logout_view', name='logout'),
                       url(r'^restaurant/(?P<slug>\w{32})/$', RestaurantDetail.as_view(), name='restaurant_detail'),
                       url(r'user_like/$', 'like_view', {'remove':False}, name='like_view'),
                       url(r'user_dislike/$', 'like_view', {'remove':True}, name='like_view'),
)