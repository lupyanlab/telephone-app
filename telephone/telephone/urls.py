from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    url(r'^grunt/', include('grunt.urls')),
)

# Route for media files in local development.
if settings.DEBUG:
    # This serves static files and media files.
    urlpatterns += staticfiles_urlpatterns()
    # In case media is not served correctly
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                'document_root': settings.MEDIA_ROOT,
            }),
    )
