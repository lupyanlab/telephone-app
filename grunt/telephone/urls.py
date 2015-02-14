from django.conf.urls import patterns, url

from .views import GameListView, PlayGameView, accept, clear

urlpatterns = patterns('',
    url(
        r'^$',
        GameListView.as_view(),
        name = 'game_list'
    ),
    url(
        r'^(?P<pk>\d+)/$',
        PlayGameView.as_view(),
        name = 'play',
    ),
    url(r'^(?P<pk>\d+)/accept$', accept, name = 'accept'),
    url(r'^(?P<pk>\d+)/clear$', clear, name = 'clear'),
)
