from django.conf.urls import patterns, url

from .views import GameListView, PlayGameView, clear_view

urlpatterns = patterns('',
    url(
        r'^$',
        GameListView.as_view(),
        name = 'game_list'
    ),
    url(
        r'^(?P<pk>\d+)/$',
        PlayGameView.as_view(),
        name = 'play_game',
    ),
    url(
        r'^(?P<pk>\d+)/clear$',
        clear_view,
        name = 'clear',
    ),
)
