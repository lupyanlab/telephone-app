from django.conf.urls import patterns, url

from .views import GamesView, NewGameView, PlayView, InspectView
from .views import accept, clear, message_data

urlpatterns = patterns('',
    url(
        r'^$',
        GamesView.as_view(),
        name = 'games',
    ),
    url(
        r'^new/$',
        NewGameView.as_view(),
        name = 'new_game',
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
    url(
        r'^(?P<pk>\d+)/message_data$',
        message_data,
        name = 'message_data',
    ),
    url(r'^(?P<pk>\d+)/accept$', accept, name = 'accept'),
    url(r'^(?P<pk>\d+)/clear$', clear, name = 'clear'),
)
