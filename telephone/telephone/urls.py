from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from grunt import views

urlpatterns = patterns('',
    url(r'^$', views.GameListView.as_view(), name = 'games_list'),
    url(r'^new/$', views.NewGameView.as_view(), name = 'new_game'),

    # gameplay views
    url(r'^(?P<pk>\d+)/$', views.play_game, name = 'play'),
    url(r'^messages/$', views.respond, name = 'respond'),
    url(r'^(?P<pk>\d+)/accept$', views.accept, name = 'accept'),
    url(r'^(?P<pk>\d+)/complete/$', views.CompletionView.as_view(), name = 'complete'),
    url(r'^(?P<pk>\d+)/clear$', views.clear, name = 'clear'),

    # inspect views
    url(r'^(?P<pk>\d+)/inspect/$', views.InspectView.as_view(), name = 'inspect'),
    url(r'^(?P<pk>\d+)/message_data$', views.message_data, name = 'message_data'),
    url(r'^messages/(?P<pk>\d+)/sprout$', views.sprout, name = 'sprout'),
    url(r'^messages/(?P<pk>\d+)/close$', views.close, name = 'close'),
    url(r'^messages/(?P<pk>\d+)/upload/$', views.UploadMessageView.as_view(), name = 'upload'),
    url(r'^messages/download/$', views.download, name = 'download'),

    # admin site
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
