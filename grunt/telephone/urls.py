from django.conf.urls import patterns, url

from .views import CallsView, PlayView, InspectView
from .views import accept, clear

urlpatterns = patterns('',
    url(
        r'^$',
        CallsView.as_view(),
        name = 'calls',
    ),
    url(
        r'^(?P<pk>\d+)/$',
        PlayView.as_view(),
        name = 'play',
    ),
    url(
        r'^(?P<pk>\d+)/inspect/$',
        InspectView.as_view(),
        name = 'inspect',
    ),
    url(r'^(?P<pk>\d+)/accept$', accept, name = 'accept'),
    url(r'^(?P<pk>\d+)/clear$', clear, name = 'clear'),
)
