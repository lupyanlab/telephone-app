from django.conf.urls import patterns, url

from . import views
from .views import CompletionView, accept, clear, sprout, close, UploadMessageView

urlpatterns = patterns('',
    url(
        r'^$',
        views.GamesView.as_view(),
        name = 'games',
    ),
    url(
        r'^new/$',
        views.NewGameView.as_view(),
        name = 'new_game',
    ),
    url(
        r'^(?P<pk>\d+)/$',
        views.play,
        name = 'play',
    ),
    url(
        r'^messages/$',
        views.respond,
        name = 'respond',
    ),
    url(
        r'^(?P<pk>\d+)/inspect/$',
        views.InspectView.as_view(),
        name = 'inspect',
    ),
    url(
        r'^(?P<pk>\d+)/message_data$',
        views.message_data,
        name = 'message_data',
    ),
    url(r'^(?P<pk>\d+)/complete/$', CompletionView.as_view(), name = 'complete'),
    url(r'^(?P<pk>\d+)/accept$', accept, name = 'accept'),
    url(r'^(?P<pk>\d+)/clear$', clear, name = 'clear'),
    url(r'^messages/(?P<pk>\d+)/sprout$', sprout, name = 'sprout'),
    url(r'^messages/(?P<pk>\d+)/close$', close, name = 'close'),
    url(r'^messages/(?P<pk>\d+)/upload/$', UploadMessageView.as_view(), name = 'upload'),
)
